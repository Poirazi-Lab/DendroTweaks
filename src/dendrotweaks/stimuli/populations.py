from dendrotweaks.morphology.seg_trees import Segment
from dendrotweaks.stimuli.synapses import Synapse

from collections import defaultdict

from typing import List
import numpy as np

KINETIC_PARAMS = {
    'AMPA': {
        'gmax': 0.001,
        'tau_rise': 0.1,
        'tau_decay': 2.5,
        'e': 0
    },
    'NMDA': {
        'gmax': 0.7 * 0.001,
        'tau_rise': 2,
        'tau_decay': 30,
        'e': 0,
        'gamma': 0.062,
        'mu': 0.28,
    },
    'AMPA_NMDA': {
        'gmax_AMPA': 0.001,
        'gmax_NMDA': 0.7 * 0.001,
        'tau_rise_AMPA': 0.1,
        'tau_decay_AMPA': 2.5,
        'tau_rise_NMDA': 2,
        'tau_decay_NMDA': 30,
        'e': 0,
        'gamma': 0.062,
        'mu': 0.28,
    },
    'GABAa': {
        'gmax': 0.001,
        'tau_rise': 0.1,
        'tau_decay': 8,
        'e': -70
    }
}

class Population():
    """
    A population of "virtual" presynaptic neurons forming synapses on the
    explicitely modelled postsynaptic neuron. 

    The population is defined by the number of synapses N, the segments
    on which the synapses are placed, and the type of synapse. All synapses
    in the population share the same kinetic parameters. Global input parameters
    such as rate, noise, etc. are shared by all synapses in the population, 
    however, each synapse receives a unique input spike train.

    Parameters
    ----------
    idx : str
        The index of the population.
    segments : List[Segment]
        The segments on which the synapses are placed.
    N : int
        The number of synapses in the population.
    syn_type : str
        The type of synapse to create e.g. 'AMPA', 'NMDA', 'AMPA_NMDA', 'GABA'.

    Attributes
    ----------
    idx : str
        The index of the population.
    segments : List[Segment]
        The segments on which the synapses are placed.
    N : int
        The number of synapses in the population.
    syn_type : str
        The type of synapse to create e.g. 'AMPA', 'NMDA', 'AMPA_NMDA', 'GABA'.
    synapses : dict
        A dictionary of synapses in the population, where the key is the segment index.
    n_per_seg : dict
        A dictionary of the number of synapses allocated to each segment.
    input_params : dict
        The input parameters of the synapses in the population.
    kinetic_params : dict
        The kinetic parameters of the synapses in the population.
    """

    def __init__(self, idx: str, segments: List[Segment], N: int, syn_type: str) -> None:

        self.idx = idx
        self.segments = segments
        self.syn_type = syn_type

        self.N = N

        self.synapses = {}
        self.n_per_seg = {}

        self.input_params = {
            'rate': 1,
            'noise': 0,
            'start': 100,
            'end': 200,
            'weight': 1,
            'delay': 0
        }

        self.kinetic_params = KINETIC_PARAMS[syn_type]

    def __repr__(self):
        return f"<Population({self.name}, N={self.N})>"
    
    @property
    def name(self):
        """A unique name for the population."""
        return f"{self.syn_type}_{self.idx}"

    def update_kinetic_params(self, **params):
        """
        Update the kinetic parameters of the synapses.

        Parameters
        ----------
        **params : dict
            The parameters to update self.kinetic_params.
            Options are:
            - gmax: the maximum conductance of the synapse
            - tau_rise: the rise time of the synapse
            - tau_decay: the decay time of the synapse
            - e: the reversal potential of the synapse
            - gamma: the voltage dependence of the magnesium block (NMDA only)
            - mu: the sensitivity of the magnesium block to Mg2+ concentration (NMDA only)
        """
        self.kinetic_params.update(params)
        for syns in self.synapses.values():
            for syn in syns:
                for key, value in params.items():
                    if hasattr(syn._ref_syn, key):
                        setattr(syn._ref_syn, key, value)

    def update_input_params(self, **params):
        """
        Update the input parameters of the synapses.

        Parameters
        ----------
        **params : dict
            The parameters to update self.input_params.
            Options are:
            - rate: the rate of the input in Hz
            - noise: the noise level of the input
            - start: the start time of the input
            - end: the end time of the input
            - weight: the weight of the synapse
            - delay: the delay of the synapse
        """
        self.input_params.update(params)
        self.create_inputs()

    # ALLOCATION METHODS

    def _calculate_n_per_seg(self):
        """
        Assign each section a random number of synapses 
        so that the sum of all synapses is equal to N synapses.
        returns a dict {sec:n_syn}
        """
        n_per_seg = {seg: 0 for seg in self.segments}
        for i in range(self.N):
            seg = np.random.choice(self.segments)
            n_per_seg[seg] += 1
        return n_per_seg

    def allocate_synapses(self, n_per_seg=None):
        """
        Assign each synapse a section and a location on that section.

        Parameters
        ----------
        n_per_seg : dict, optional
            The number of synapses to allocate to each section.
            If not provided, synapses are allocated randomly
            to sections based on the number of segments in each section.
        """
        self.synapses = {}
        if n_per_seg is not None:
            self.n_per_seg = n_per_seg
        else:
            self.n_per_seg = self._calculate_n_per_seg()
        syn_type = self.syn_type
        for seg, n in self.n_per_seg.items():
            self.synapses[seg.idx] = [Synapse(syn_type, seg) for _ in range(n)]

        self.update_kinetic_params(**self.kinetic_params)


    # CREATION METHODS

    def create_inputs(self):
        """
        Create and reference the synapses in a simulator.
        
        This method should be called after the synapses have been allocated.
        """
        for syns in self.synapses.values():
            for syn in syns:

                syn.create_stim(
                    rate=self.input_params['rate'],
                    noise=self.input_params['noise'],
                    duration=self.input_params['end'] - self.input_params['start'],
                    delay=self.input_params['start']
                )

                syn.create_con(
                    delay=self.input_params['delay'],
                    weight=self.input_params['weight']
                )


    def to_dict(self):
        """
        Convert the population to a dictionary.
        """
        return {
                'name': self.name,
                'syn_type': self.syn_type,
                'N': self.N,
                'input_params': {**self.input_params},
                'kinetic_params': {**self.kinetic_params},
        }

    def to_csv(self):
        """
        Prepare the data about the location of synapses for saving to a CSV file.
        """
        return {
            'syn_type': [self.syn_type] * len(self.n_per_seg),
            'name': [self.name] * len(self.n_per_seg),
            'sec_idx': [seg._section.idx for seg in self.n_per_seg.keys()],
            'loc': [seg.x for seg in self.n_per_seg.keys()],
            'n_per_seg': list(self.n_per_seg.values())
        }
        

    def clean(self):
        """
        Clear the synapses and connections from the simulator.

        Removes all synapses, NetCon and NetStim objects.
        """
        for seg in self.segments:
            for syn in self.synapses[seg.idx]:
                if syn._ref_stim is not None:
                    syn._clear_stim()
                if syn._ref_con is not None:
                    syn._clear_con()
                syn = None
            self.synapses.pop(seg.idx)