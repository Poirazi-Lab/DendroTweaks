from typing import List
from neuron import h
import numpy as np
from dendrotweaks.morphology.seg_trees import Segment

class Synapse():
    """
    A synapse object that can be placed on a section of a neuron.

    Contains references to the NEURON synapse object, the stimulus object (NetStim),
    and the connection object (NetCon).

    Parameters
    ----------
    syn_type : str
        The type of synapse to create e.g. 'AMPA', 'NMDA', 'AMPA_NMDA', 'GABA'.
    sec : Section
        The section on which the synapse is placed.
    loc : float
        The location on the section where the synapse is placed, between 0 and 1.

    Attributes
    ----------
    sec : Section
        The section on which the synapse is placed.
    loc : float
        The location on the section where the synapse is placed, between 0 and 1.
    """

    def __init__(self, syn_type: str, sec, loc=0.5) -> None:
        """
        Creates a new synapse object.
        """
        self._Model = getattr(h, syn_type)
        self.sec = sec
        self.loc = loc

        self._ref_syn = self._Model(self.seg._ref)
        self._ref_stim = None
        self._ref_con = None

    @property
    def seg(self):
        """
        The segment on which the synapse is placed.
        """
        return self.sec(self.loc)

    def __repr__(self):
        return f"<Synapse({self.sec}({self.loc:.3f}))>"

    @property
    def spike_times(self):
        """
        The spike times of the stimulus from the NetStim object.
        """
        if self._ref_stim is not None:
            return self._ref_stim[1].to_python()
        return []

    def _clear_stim(self):
        """
        Clears the stimulus (NetStim) object.
        """
        self._ref_stim[0] = None
        self._ref_stim[1] = None
        self._ref_stim.pop(0)
        self._ref_stim.pop(0)
        self._ref_stim = None

    def create_stim(self, **kwargs):
        """
        Creates a stimulus (NetStim) for the synapse.

        Parameters
        ----------
        **kwargs : dict
            Keyword arguments for the create_spike_times function.
        """

        if self._ref_stim is not None:
            self._clear_stim()

        spike_times = create_spike_times(**kwargs)
        spike_vec = h.Vector(spike_times)
        stim = h.VecStim()
        stim.play(spike_vec)

        self._ref_stim = [stim, spike_vec]

    def _clear_con(self):
        """
        Clears the connection (NetCon) object.
        """
        self._ref_con = None

    def create_con(self, delay, weight):
        """
        Create a connection (NetCon) between the stimulus and the synapse.

        Parameters
        ----------
        delay : int
            The delay of the connection, in ms.
        weight : float
            The weight of the connection.
        """
        if self._ref_con is not None:
            self._clear_con()
        self._ref_con = h.NetCon(self._ref_stim[0],
                                 self._ref_syn,
                                 0,
                                 delay,
                                 weight)


def create_spike_times(rate=1, noise=1, duration=300, delay=0):
    """
    Create a spike train with a given regularity.

    Parameters
    ----------
    rate : float
        The rate of the spike train, in Hz.
    noise : float
        A parameter between 0 and 1 that controls the regularity of the spike train. 
        0 corresponds to a regular spike train. 1 corresponds to a Poisson process.
    duration : int
        The total time to run the simulation for, in ms.
    delay : int
        The delay of the spike train, in ms.

    Returns
    -------
    np.array
        The spike times as a vector, in ms.
    """

    if noise == 1:
        return delay + generate_poisson_process(rate, duration)
    else:
        return delay + generate_jittered_spikes(rate, duration, noise)


def generate_poisson_process(lam, dur):
    """
    Generate a Poisson process.

    Parameters
    ----------
    lam : float
        The rate parameter (lambda) of the Poisson process, in Hz.
    dur : int
        The total time to run the simulation for, in ms.

    Returns
    -------
    np.array
        The spike times as a vector, in ms.    
    """
    dur_s = dur / 1000
    intervals = np.random.exponential(1/lam, int(lam*dur_s))
    spike_times = np.cumsum(intervals)
    spike_times = spike_times[spike_times <= dur_s]
    spike_times_ms = spike_times * 1000

    return spike_times_ms


def generate_jittered_spikes(rate, dur, noise):
    """
    Generate a jittered spike train.

    Parameters
    ----------
    rate : float
        The rate of the spike train, in Hz.
    dur : int
        The total time to run the simulation for, in ms.
    noise : float
        A parameter between 0 and 1 that controls the regularity of the spike train. 
        0 corresponds to a regular spike train. 1 corresponds to a Poisson process.


    Returns
    -------
    np.array
        The spike times as a vector, in ms.
    """
    dur_s = dur / 1000
    spike_times = np.arange(0, dur_s, 1/rate)

    # Add noise
    noise_values = np.random.normal(0, noise/rate, len(spike_times))
    spike_times += noise_values

    # Ensure spike times are within the duration and sort them
    spike_times = spike_times[(spike_times >= 0) & (spike_times <= dur_s)]
    spike_times.sort()

    spike_times_ms = spike_times * 1000

    return spike_times_ms
