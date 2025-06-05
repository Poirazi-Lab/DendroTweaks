from collections import defaultdict
import warnings
from functools import cached_property

import matplotlib.pyplot as plt
import neuron
from neuron import h
from neuron.units import ms, mV
h.load_file('stdrun.hoc')
# h.load_file('import3d.hoc')
# h.load_file('nrngui.hoc')
# h.load_file('import3d')
import numpy as np

import contextlib

@contextlib.contextmanager
def push_section(section):
    section.push()
    yield
    h.pop_section()

def reset_neuron():

    # h('forall delete_section()')
    # h('forall delete_all()')
    # h('forall delete()')

    for sec in h.allsec():
        with push_section(sec):
            h.delete_section()

reset_neuron()            

# -------------------------------------------------------
# SIMULATOR
# -------------------------------------------------------

class Simulator:
    """
    A generic simulator class.
    """
    def __init__(self):
        self._t = None
        self.dt = None
        self._recordings = {'v': {}}

    def plot_var(self, var='v', ax=None, segments=None, **kwargs):
        if self._t is None:
            raise ValueError('Simulation has not been run yet.')
        if var not in self.recordings:
            raise ValueError(f'Variable {var} not recorded.')
        if ax is None:
            fig, ax = plt.subplots()
        if segments is None:
            segments = self.recordings[var].keys()
        for seg, x in self.recordings[var].items():
            if segments and seg not in segments:
                continue
            ax.plot(self.t, x, label=f'{var} {seg.domain} {seg.idx}', **kwargs)
        if len(segments) < 10:
            ax.legend()
        ax.set_xlabel('Time (ms)')
        if var == 'v':
            ax.set_ylabel('Voltage (mV)')
        elif var.startswith('i_'):
            ax.set_ylabel('Current (nA)')
        return ax

    def plot_voltage(self, **kwargs):
        """
        Plot the recorded voltages.
        """
        self.plot_var('v', **kwargs)
    
    def plot_currents(self, **kwargs):
        """
        Plot the recorded currents.
        """
        ax = kwargs.pop('ax', None)
        for var in self.recordings:
            if var.startswith('i_'):
                ax = self.plot_var(var, ax=ax, **kwargs)
            
        

class NeuronSimulator(Simulator):
    """
    A class to represent the NEURON simulator.

    Parameters
    ----------
    temperature : float
        The temperature of the simulation in Celsius.
    v_init : float
        The initial membrane potential of the neuron in mV.
    dt : float
        The time step of the simulation in ms.
    cvode : bool
        Whether to use the CVode variable time step integrator.

    Attributes
    ----------
    temperature : float
        The temperature of the simulation in Celsius.
    v_init : float
        The initial membrane potential of the neuron in mV.
    dt : float
        The time step of the simulation in ms.
    """

    def __init__(self, temperature=37, v_init=-70, dt=0.025, cvode=False):
        super().__init__()
        
        self.temperature = temperature
        self.v_init = v_init * mV
        self._duration = 300
        

        self.dt = dt
        self._cvode = cvode

    @cached_property
    def recordings(self):
        return {
            var:{ seg: vec.to_python() for seg, vec in recs.items() }
            for var, recs in self._recordings.items()
        }

    @cached_property
    def t(self):
        return self._t.to_python()

    def _clean_cache(self):
        """
        Clean the cache of the simulator.
        """
        try:
            del self.recordings
            del self.t
        except AttributeError:
            # Property hasn't been accessed yet, so no need to delete
            pass


    def add_recording(self, sec, loc, var='v'):
        """
        Add a recording to the simulator.

        Parameters
        ----------
        sec : Section
            The section to record from.
        loc : float
            The location along the normalized section length to record from.
        var : str
            The variable to record. Default is 'v' (voltage).
        """
        seg = sec(loc)
        if not hasattr(seg._ref, f'_ref_{var}'):
            raise ValueError(f'Segment {seg} does not have variable {var}.')
        if self._recordings.get(var, {}).get(seg):
            self.remove_recording(sec, loc, var)
        if var not in self._recordings:
            self._recordings[var] = {}
        self._recordings[var][seg] = h.Vector().record(getattr(seg._ref, f'_ref_{var}'))
        self._clean_cache()

    def remove_recording(self, sec, loc, var='v'):
        """
        Remove a recording from the simulator.

        Parameters
        ----------
        sec : Section
            The section to remove the recording from.
        loc : float 
            The location along the normalized section length to remove the recording from.
        """
        seg = sec(loc)
        if seg in self._recordings[var]:
            self._recordings[var][seg] = None
            self._recordings[var].pop(seg)
            if not self._recordings[var]:
                self._recordings.pop(var)
        self._clean_cache()

    def remove_all_recordings(self, var=None):
        """
        Remove all recordings from the simulator.
        """
        variables = [var] if var else list(self._recordings.keys())
        for variable in variables:
            for seg in list(self._recordings.get(variable, {}).keys()):
                self.remove_recording(seg._section, seg.x, variable)
            if self._recordings.get(variable):
                warnings.warn(f'Not all recordings were removed for variable {variable}: {self._recordings}')


    def _init_simulation(self):

        h.celsius = self.temperature

        if self._cvode:
            h.cvode.active(1)
        else:
            h.cvode.active(0)
            h.dt = self.dt

        h.finitialize(self.v_init)

        if self._cvode:
            h.cvode.re_init()
        else:
            h.fcurrent()

        h.frecord_init()


    def run(self, duration=300):
        """
        Run a simulation.

        Parameters
        ----------
        duration : float
            The duration of the simulation in milliseconds.
        """

        self._clean_cache()

        self._duration = duration

        self._t = h.Vector().record(h._ref_t)

        self._init_simulation()

        h.continuerun(duration * ms)
    

    def to_dict(self):
        """
        Convert the simulator to a dictionary.

        Returns
        -------
        dict
            A dictionary representation of the simulator.
        """
        return {
            'temperature': self.temperature,
            'v_init': self.v_init,
            'dt': self.dt,
            'duration': self._duration
        }

    def from_dict(self, data):
        """
        Create a simulator from a dictionary.

        Parameters
        ----------
        data : dict
            The dictionary representation of the simulator.
        """
        self.temperature = data['temperature']
        self.v_init = data['v_init']
        self.dt = data['dt']
        self._duration = data['duration']


class JaxleySimulator(Simulator):
    """
    A class to represent a Jaxley simulator.
    """

    def __init__(self):
        super().__init__()
        ...

    
