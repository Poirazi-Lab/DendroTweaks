from dendrotweaks.morphology.trees import Node, Tree
import numpy as np

class Segment(Node):
    """
    A class representing a segment.

    A segment is a part of a section used to discretize the section
    in space for the purpose of numerical simulations.
    """

    def __init__(self, idx, parent_idx, neuron_seg, section) -> None:
        super().__init__(idx, parent_idx)
        self._section = section
        self._ref = neuron_seg


    # PROPERTIES

    @property
    def domain(self):
        """
        The morphological or functional domain of the segment.
        """
        return self._section.domain


    @property
    def x(self):
        """
        The position of the segment along the normalized section length (from NEURON).
        """
        return self._ref.x


    @property
    def area(self):
        """
        The area of the segment (from NEURON).
        """
        return self._ref.area()


    @property
    def diam(self):
        """
        The diameter of the segment (from NEURON).
        """
        return self._ref.diam


    @property
    def subtree_size(self):
        """
        The number of sections in the subtree rooted at the segment.
        """
        return self._section.subtree_size


    @property
    def Ra(self):
        """
        The axial resistance of the segment (from NEURON).
        """
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

    
    # PARAMETER SETTERS AND GETTERS

    def set_param_value(self, param_name, value):
        """
        Set the value of a parameter of the segment.

        Parameters
        ----------
        param_name : str
            The name of the parameter to set.
        value : float
            The value to set the parameter to.
        """
        if hasattr(self._ref, param_name):
            setattr(self._ref, param_name, value)


    def get_param_value(self, param_name):
        """
        Get the value of a parameter of the segment.

        Parameters
        ----------
        param_name : str
            The name of the parameter to get.

        Returns
        -------
        float
            The value of the parameter.
        """
        if hasattr(self, param_name):
            return getattr(self, param_name)
        elif hasattr(self._ref, param_name):
            return getattr(self._ref, param_name)
        else:
            return np.nan


class SegmentTree(Tree):
    """
    A class representing a tree graph of segments.
    """

    def __init__(self, segments: list[Segment]) -> None:
        super().__init__(segments)

    @property
    def segments(self):
        """
        The segments in the segment tree. Alias for self._nodes
        """
        return self._nodes