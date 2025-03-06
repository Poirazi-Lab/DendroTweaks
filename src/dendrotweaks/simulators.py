from collections import defaultdict
import warnings

import matplotlib.pyplot as plt
import neuron
from neuron import h
from neuron.units import ms, mV
h.load_file('stdrun.hoc')
# h.load_file('import3d.hoc')
# h.load_file('nrngui.hoc')
# h.load_file('import3d')

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

class Simulator:
    def __init__(self):
        self.vs = None
        self.t = None
        self.dt = None
        self.recordings = {}

    def plot_voltage(self, ax=None, segments=None, **kwargs):
        if ax is None:
            fig, ax = plt.subplots()
        if segments is None:
            segments = self.recordings.keys()
        for seg, v in self.vs.items():
            if segments and seg not in segments:
                continue
            ax.plot(self.t, v, label=f'{seg.domain} {seg.idx}', **kwargs)

        if len(segments) < 10:
            ax.legend()
        # ax.set_ylim(-100, 60)
        ax.set_xlabel('Time (ms)')
        ax.set_ylabel('Voltage (mV)')
        

class NEURONSimulator(Simulator):
    """
    A class to represent a NEURON simulator.
    """

    def __init__(self, temperature=37, v_init=-70, dt=0.025, cvode=False):
        super().__init__()
        
        self.temperature = temperature
        self.v_init = v_init * mV
        self._duration = 300

        self.dt = dt
        self._cvode = cvode


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
        if self.recordings.get(seg):
            self.remove_recording(sec, loc)
        self.recordings[seg] = h.Vector().record(getattr(seg._ref, f'_ref_{var}'))

    def remove_recording(self, sec, loc):
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
        if self.recordings.get(seg):
            self.recordings[seg] = None
            self.recordings.pop(seg)

    def remove_all_recordings(self):
        """
        Remove all recordings from the simulator.
        """
        for seg in self.recordings.keys():
            sec, loc = seg._section, seg.x
            self.remove_recording(sec, loc)
        if self.recordings:
            warnings.warn(f'Not all recordings were removed: {self.recordings}')
        self.recordings = {}


    def _init_simulation(self):
        h.CVode().active(self._cvode)
        h.celsius = self.temperature
        h.dt = self.dt
        h.stdinit()
        h.init()
        h.finitialize(self.v_init)
        if h.cvode.active():
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
        self._duration = duration


        # vs = list(self.recordings.values())
        Is = []

        # for v in self.recordings.values():
        #     # v = h.Vector().record(seg._ref_v)
        #     vs.append(v)

        t = h.Vector().record(h._ref_t)

        # if self.ch is None:
        #     pass
        # else:
        #     for seg in self.recordings.keys():
        #         if getattr(seg, f'_ref_i_{self.ch.suffix}', None) is None:
        #             logger.warning(
        #                 f'No current recorded for {self.ch.suffix} at {seg}. Make i a RANGE variable in mod file.')
        #             continue
        #         I = h.Vector().record(getattr(seg, f'_ref_i_{self.ch.suffix}'))
        #         Is.append(I)

        self._init_simulation()

        h.continuerun(duration * ms)

        self.t = t.to_python()
        self.vs = {seg: v.to_python() for seg, v in self.recordings.items()}
    

    def to_dict(self):
        """
        Convert the simulator to a dictionary.
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

    
