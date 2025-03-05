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
    A population of "virtual" presynaptic neurons.
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
            'noise': 1,
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
        return f"{self.syn_type}_{self.idx}"

    def update_kinetic_params(self, params:dict):
        self.kinetic_params.update(**params)
        for syns in self.synapses.values():
            for syn in syns:
                for key, value in params.items():
                    if hasattr(syn._ref_syn, key):
                        setattr(syn._ref_syn, key, value)

    def update_input_params(self, params: dict):
        self.input_params.update(**params)
        self.create_inputs()

    # ALLOCATION METHODS

    def _calculate_n_per_seg(self):
        """Assigns each section a random number of synapses 
        so that the sum of all synapses is equal to N synapses.
        returns a dict {sec:n_syn}"""
        n_per_seg = {seg: 0 for seg in self.segments}
        for i in range(self.N):
            seg = np.random.choice(self.segments)
            n_per_seg[seg] += 1
        return n_per_seg

    def allocate_synapses(self, n_per_seg=None):
        """Assigns each synapse a section and a location on that section."""
        self.synapses = {}
        if n_per_seg is not None:
            self.n_per_seg = n_per_seg
        else:
            self.n_per_seg = self._calculate_n_per_seg()
        syn_type = self.syn_type
        for seg, n in self.n_per_seg.items():
            self.synapses[seg.idx] = [Synapse(syn_type, seg) for _ in range(n)]

        self.update_kinetic_params(params=self.kinetic_params)


    # CREATION METHODS

    def create_inputs(self):
        """Creates and references the synapses in a simulator."""
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
        return {
                'name': self.name,
                'syn_type': self.syn_type,
                'N': self.N,
                'input_params': {**self.input_params},
                'kinetic_params': {**self.kinetic_params},
        }

    def to_csv(self):
        return {
            'syn_type': [self.syn_type] * len(self.n_per_seg),
            'name': [self.name] * len(self.n_per_seg),
            'sec_idx': [seg._section.idx for seg in self.n_per_seg.keys()],
            'loc': [seg.x for seg in self.n_per_seg.keys()],
            'n_per_seg': list(self.n_per_seg.values())
        }
        

    def clean(self):
        for seg in self.segments:
            for syn in self.synapses[seg.idx]:
                if syn._ref_stim is not None:
                    syn._clear_stim()
                if syn._ref_con is not None:
                    syn._clear_con()
                syn = None
            self.synapses.pop(seg.idx)