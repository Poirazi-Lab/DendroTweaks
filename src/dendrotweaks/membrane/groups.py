from typing import List, Callable, Dict

from dendrotweaks.morphology.trees import Node
from dendrotweaks.morphology.sec_trees import Section
from dendrotweaks.morphology.seg_trees import Segment
from dendrotweaks.membrane.mechanisms import Mechanism
from dendrotweaks.membrane.distributions import Distribution
from dendrotweaks.utils import timeit
from dataclasses import dataclass, field, asdict
from typing import List, Tuple, Dict, Optional

# TODO: Sec or seg? Layering or partitioning? Make the user choose.

# Group first approach:

# Pros:
# - Better UX logic, the user first defines the domain and then its parameters.
# - Better output JSON, no need to duplicate nodes. G x N instead of P x G x N.

# Cons:
# - Need to modify the UI.
# - No layering, each node belongs to one and only one group (not necessarily!).

class SectionGroup:
    """
    A group of sections often representing a domain.

    Parameters
    ----------
    name : str
        The name of the group.
    sections : List[Section]
        The list of sections in the group.
    """

    def __init__(self, name, sections):

        self.name = name
        self.params = {
            'domain': None,
            'diam': None,
            'distance': None,
        }
        self._sections = sections
        self.mechanisms = ['Independent']

    @property
    def sections(self):
        return self._sections

    @sections.setter
    def sections(self, sections):
        raise AttributeError('Sections cannot be set directly.')

    def to_dict(self) -> Dict:
        """
        Exports the group to a dictionary format.

        Returns
        -------
        dict
            The group in dictionary format.
        """
        return {
            'name': self.name,
            'mechanisms': [mechanism_name for mechanism_name in self.mechanisms],
            # 'sections': [sec.idx for sec in self.sections],
        }

    def __repr__(self):
        return f'Group("{self.name}", {len(self.sections)})'






@dataclass
class SegmentGroup:
    name: str
    domains: List[str]
    select_by: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None

    def _get_segment_value(self, segment) -> Optional[float]:
        if self.select_by == 'diam':
            return segment.diam
        elif self.select_by == 'section_diam':
            return segment._section._ref.diam
        elif self.select_by == 'absolute_distance':
            return segment.path_distance()
        elif self.select_by == 'domain_distance':
            return segment.path_distance(within_domain=True)
        return None

    def __contains__(self, segment) -> bool:
        if segment.domain not in self.domains:
            return False
        if self.select_by is None:
            return True
        
        segment_value = self._get_segment_value(segment)
        return (
            (self.min_value is None or segment_value > self.min_value) and
            (self.max_value is None or segment_value <= self.max_value)
        )

    def __repr__(self):
        filters = (
            f"{self.select_by}({self.min_value}, {self.max_value})"
            if self.select_by is not None and (self.min_value is not None or self.max_value is not None) else ""
        )
        return f'SegmentGroup("{self.name}", domains={self.domains}' + (f", {filters}" if filters else "") + ')'

    def to_dict(self) -> Dict:
        result = {
            'name': self.name,
            'domains': self.domains,
            'select_by': self.select_by,
            'min_value': self.min_value,
            'max_value': self.max_value,
        }
        return {k: v for k, v in result.items() if v is not None}

    @staticmethod
    def from_dict(data: Dict) -> 'SegmentGroup':
        return SegmentGroup(**data)

