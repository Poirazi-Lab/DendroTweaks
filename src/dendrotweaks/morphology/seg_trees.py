from dendrotweaks.morphology.trees import Node, Tree
import numpy as np

class Segment(Node):

    def __init__(self, idx, parent_idx, neuron_seg, section) -> None:
        """
        Create a wrapper for a NEURON segment.

        Parameters
        ----------
        idx : int
            The index of the segment.
        parent_idx : int
            The index of the parent segment.
        neuron_seg : h.Segment
            The NEURON segment object.
        section : h.Section
            The Section wrapper object.
        """
        super().__init__(idx, parent_idx)
        self._section = section
        self._ref = neuron_seg

    @property
    def domain(self):
        return self._section.domain

    @property
    def x(self):
        return self._ref.x

    @property
    def area(self):
        return self._ref.area()

    @property
    def diam(self):
        return self._ref.diam

    @property
    def subtree_size(self):
        return self._section.subtree_size

    @property
    def Ra(self):
        return self._section.Ra

    
    def path_distance(self, within_domain=False):
        return self._section.path_distance(self.x, 
            within_domain=within_domain)

    @property
    def absolute_distance(self):
        return self.path_distance(within_domain=False)

    @property
    def domain_distance(self):
        return self.path_distance(within_domain=True)

    # @property
    # def distance_to_parent_domain(self):
    #     return self._section.distance_to_parent_domain(self.x)

    def set_param_value(self, param_name, value):
        if hasattr(self._ref, param_name):
            setattr(self._ref, param_name, value)

    def get_param_value(self, param_name):
        if hasattr(self, param_name):
            return getattr(self, param_name)
        elif hasattr(self._ref, param_name):
            return getattr(self._ref, param_name)
        else:
            return np.nan


class SegmentTree(Tree):

    def __init__(self, segments: list[Segment]) -> None:
        super().__init__(segments)

    @property
    def segments(self):
        return self._nodes