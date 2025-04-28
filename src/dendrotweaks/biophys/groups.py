from typing import List, Callable, Dict

from dendrotweaks.utils import timeit
from dataclasses import dataclass, field, asdict
from typing import List, Tuple, Dict, Optional


@dataclass
class SegmentGroup:
    """
    A group of segments that share a common property.

    Parameters
    ----------
    name : str
        The name of the segment group.
    domains : List[str]
        The domains the segments belong to.
    select_by : Optional[str]
        The property to select the segments by. Can be:
        - 'diam': the diameter of the segment.
        - 'section_diam': the diameter of the section the segment belongs to.
        - 'distance': the distance of the segment from the root.
        - 'domain_distance': the distance of the segment from the root within the domain.
    min_value : Optional[float]
        The minimum value of the property.
    max_value : Optional[float]
        The maximum value of the property.

    Examples
    --------
    Create a segment group that selects segments by diameter:

    >>> group = SegmentGroup('group1', domains=['dend'], select_by='diam', min_value=1, max_value=2)
    >>> group
    SegmentGroup("group1", domains=['dend'], diam(1, 2))

    Check if a segment is in the group:

    >>> segment in group
    True
    """
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
        elif self.select_by == 'distance':
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
        """
        Convert the SegmentGroup to a dictionary.
        """
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
        """
        Create a SegmentGroup from a dictionary.
        """
        return SegmentGroup(**data)

