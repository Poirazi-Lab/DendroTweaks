# Imports
import os

# DendroTweaks imports
from dendrotweaks.stimuli.populations import Population
from dendrotweaks.stimuli.iclamps import IClamp
from dendrotweaks.morphology.io import create_segment_tree
from dendrotweaks.prerun import prerun
from dendrotweaks.utils import calculate_lambda_f
from dendrotweaks.utils import POPULATIONS

# Warnings configuration
import warnings

def custom_warning_formatter(message, category, filename, lineno, file=None, line=None):
    return f"WARNING: {message}\n({os.path.basename(filename)}, line {lineno})\n"

warnings.formatwarning = custom_warning_formatter


class SimulationMixin:

    """Mixin class for model simulation functionalities."""

    @property
    def recordings(self):
        """
        The recordings of the model. Reference to the recordings in the simulator.
        """
        return self.simulator.recordings


    @recordings.setter
    def recordings(self, recordings):
        self.simulator.recordings = recordings


    # ========================================================================
    # SEGMENTATION
    # ========================================================================

    # TODO Make a context manager for this
    def _temp_clear_stimuli(self):
        """
        Temporarily save and clear stimuli.
        """
        self.export_stimuli(file_name='_temp_stimuli')
        self.remove_all_stimuli()
        self.remove_all_recordings()


    def _temp_reload_stimuli(self):
        """
        Load stimuli from a temporary file and clean up.
        """
        self.load_stimuli(file_name='_temp_stimuli')
        self.path_manager.remove_folder('stimuli/_temp_stimuli')


    def set_segmentation(self, d_lambda=0.1, f=100):
        """
        Set the number of segments in each section based on the geometry.

        Parameters
        ----------
        d_lambda : float
            The lambda value to use.
        f : float
            The frequency value to use.
        """
        self.d_lambda = d_lambda

        # Temporarily save and clear stimuli
        self._temp_clear_stimuli()

        # Pre-distribute parameters needed for lambda_f calculation
        for param_name in ['cm', 'Ra']:
            self.distribute(param_name)

        # Calculate lambda_f and set nseg for each section
        for sec in self.sec_tree.sections:
            lambda_f = calculate_lambda_f(sec.distances, sec.diameters, sec.Ra, sec.cm, f)
            nseg = max(1, int((sec.L / (d_lambda * lambda_f) + 0.9) / 2) * 2 + 1)
            sec._nseg = sec._ref.nseg = nseg

        # Rebuild the segment tree and redistribute parameters
        self.seg_tree = create_segment_tree(self.sec_tree)
        self.distribute_all()

        # Reload stimuli and clean up temporary files
        self._temp_reload_stimuli()


    # -----------------------------------------------------------------------
    # ICLAMPS
    # -----------------------------------------------------------------------

    def add_iclamp(self, sec, loc, amp=0, delay=100, dur=100):
        """
        Add an IClamp to a section.

        Parameters
        ----------
        sec : Section
            The section to add the IClamp to.
        loc : float
            The location of the IClamp in the section.
        amp : float, optional
            The amplitude of the IClamp. Default is 0.
        delay : float, optional
            The delay of the IClamp. Default is 100.
        dur : float, optional
            The duration of the IClamp. Default is 100.
        """
        seg = sec(loc)
        if self.iclamps.get(seg):
            self.remove_iclamp(sec, loc)
        iclamp = IClamp(sec, loc, amp, delay, dur)
        if self.verbose: print(f'IClamp added to sec {sec} at loc {loc}.')
        self.iclamps[seg] = iclamp


    def remove_iclamp(self, sec, loc):
        """
        Remove an IClamp from a section.

        Parameters
        ----------
        sec : Section
            The section to remove the IClamp from.
        loc : float
            The location of the IClamp in the section.
        """
        seg = sec(loc)
        if self.iclamps.get(seg):
            self.iclamps.pop(seg)


    def remove_all_iclamps(self):
        """
        Remove all IClamps from the model.
        """

        for seg in list(self.iclamps.keys()):
            sec, loc = seg._section, seg.x
            self.remove_iclamp(sec, loc)
        if self.iclamps:
            warnings.warn(f'Not all iclamps were removed: {self.iclamps}')
        self.iclamps = {}


    # -----------------------------------------------------------------------
    # SYNAPSES
    # -----------------------------------------------------------------------

    def _add_population(self, population):
        self.populations[population.syn_type][population.name] = population


    def add_population(self, segments, N, syn_type):
        """
        Add a population of synapses to the model.

        Parameters
        ----------
        segments : list[Segment]
            The segments to add the synapses to.
        N : int
            The number of synapses to add.
        syn_type : str
            The type of synapse to add.
        """
        idx = len(self.populations[syn_type])
        population = Population(idx, segments, N, syn_type)
        population.allocate_synapses()
        population.create_inputs()
        self._add_population(population)


    def update_population_kinetic_params(self, pop_name, **params):
        """
        Update the kinetic parameters of a population of synapses.

        Parameters
        ----------
        pop_name : str
            The name of the population.
        params : dict
            The parameters to update.
        """
        syn_type, idx = pop_name.rsplit('_', 1)
        population = self.populations[syn_type][pop_name]
        population.update_kinetic_params(**params)
        print(population.kinetic_params)

    
    def update_population_input_params(self, pop_name, **params):
        """
        Update the input parameters of a population of synapses.

        Parameters
        ----------
        pop_name : str
            The name of the population.
        params : dict
            The parameters to update.
        """
        syn_type, idx = pop_name.rsplit('_', 1)
        population = self.populations[syn_type][pop_name]
        population.update_input_params(**params)
        print(population.input_params)


    def remove_population(self, name):
        """
        Remove a population of synapses from the model.

        Parameters  
        ----------
        name : str
            The name of the population
        """
        syn_type, idx = name.rsplit('_', 1)
        population = self.populations[syn_type].pop(name)
        population.clean()
        

    def remove_all_populations(self):
        """
        Remove all populations of synapses from the model.
        """
        for syn_type in self.populations:
            for name in list(self.populations[syn_type].keys()):
                self.remove_population(name)
        if any(self.populations.values()):
            warnings.warn(f'Not all populations were removed: {self.populations}')
        self.populations = POPULATIONS


    def remove_all_stimuli(self):
        """
        Remove all stimuli from the model.
        """
        self.remove_all_iclamps()
        self.remove_all_populations()


    # ========================================================================
    # SIMULATION
    # ========================================================================

    def add_recording(self, sec, loc, var='v'):
        """
        Add a recording to the model.

        Parameters
        ----------
        sec : Section
            The section to record from.
        loc : float
            The location along the normalized section length to record from.
        var : str, optional
            The variable to record. Default is 'v'.
        """
        self.simulator.add_recording(sec, loc, var)
        if self.verbose: print(f'Recording added to sec {sec} at loc {loc}.')


    def remove_recording(self, sec, loc, var='v'):
        """
        Remove a recording from the model.

        Parameters
        ----------
        sec : Section
            The section to remove the recording from.
        loc : float
            The location along the normalized section length to remove the recording from.
        """
        self.simulator.remove_recording(sec, loc, var)


    def remove_all_recordings(self, var=None):
        """
        Remove all recordings from the model.
        """
        self.simulator.remove_all_recordings(var=var)


    def run(self, duration=300, prerun_time=0, truncate=True):
        """
        Run the simulation for a specified duration, optionally preceded by a prerun period
        to stabilize the model.

        Parameters
        ----------
        duration : float
            Duration of the main simulation (excluding prerun).
        prerun_time : float
            Optional prerun period to run before the main simulation.
        truncate : bool
            Whether to truncate prerun data after the simulation.
        """
        if duration <= 0:
            raise ValueError("Simulation duration must be positive.")
        if prerun_time < 0:
            raise ValueError("Prerun time must be non-negative.")

        total_time = duration + prerun_time

        if prerun_time > 0:
            with prerun(self, duration=prerun_time, truncate=truncate):
                self.simulator.run(total_time)
        else:
            self.simulator.run(duration)


    def get_traces(self):
        return self.simulator.get_traces()


    def plot(self, *args, **kwargs):
        self.simulator.plot(*args, **kwargs)