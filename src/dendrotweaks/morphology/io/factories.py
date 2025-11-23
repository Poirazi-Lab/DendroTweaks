# SPDX-FileCopyrightText: 2025 Poirazi Lab <dendrotweaks@dendrites.gr>
# SPDX-License-Identifier: MPL-2.0

from dendrotweaks.morphology.trees import Node, Tree
from dendrotweaks.morphology.point_trees import Point, PointTree
from dendrotweaks.morphology.sec_trees import NeuronSection, Section, SectionTree
from dendrotweaks.morphology.seg_trees import NeuronSegment, Segment, SegmentTree
from dendrotweaks.morphology.domains import Domain

from dendrotweaks.morphology.io.reader import SWCReader

from typing import List, Union
from pandas import DataFrame, isna

from dendrotweaks.morphology.io.validation import validate_tree



def create_point_tree(source: Union[str, DataFrame]) -> PointTree:
    """
    Create a point tree from either a file path or a DataFrame.
    
    Parameters
    ----------
    source : Union[str, DataFrame]
        The source of the SWC data. Can be a file path or a DataFrame.

    Returns
    -------
    PointTree
        The point tree representing the reconstruction of the neuron morphology.
    """
    if isinstance(source, str):
        reader = SWCReader()
        df = reader.read_file(source)
    elif isinstance(source, DataFrame):
        df = source
    else:
        raise ValueError("Source must be a file path (str) or a DataFrame.")

    nodes = [
        Point(row.Index, row.Type, 
              row.X, row.Y, row.Z, row.R, row.Parent, 
              domain_name=None if isna(row.Domain) else row.Domain,
              domain_color=None if isna(row.Color) else row.Color
              )
        for row in df.itertuples(index=False)
    ]
    point_tree =  PointTree(nodes)
    point_tree.remove_overlaps()

    return point_tree


def create_section_tree(point_tree: PointTree):
    """
    Create a section tree from a point tree.

    Parameters
    ----------
    point_tree : PointTree
        The point tree to create the section tree from by splitting it into sections.

    Returns
    -------
    SectionTree
        The section tree created representing the neuron morphology on a more abstract level.
    """

    point_tree.extend_sections()
    point_tree.sort()

    sections = _split_to_sections(point_tree)

    sec_tree = SectionTree(sections)
    sec_tree._point_tree = point_tree

    return sec_tree


def _split_to_sections(point_tree: PointTree) -> List[Section]:
    """
    Split the point tree into sections.
    """
    sections = []

    bifurcation_children = [
        child for b in point_tree.bifurcations for child in b.children]
    bifurcation_children = [point_tree.root] + bifurcation_children
    # Filter out the bifurcation children to enforce the original order
    bifurcation_children = [node for node in point_tree._nodes 
                            if node in bifurcation_children]

    # Assign a section to each bifurcation child
    for i, child in enumerate(bifurcation_children):
        section = NeuronSection(idx=i, parent_idx=-1, points=[child])
        sections.append(section)
        child._section = section
        # Propagate the section to the children until the next 
        # bifurcation or termination point is reached
        while child.children:
            next_child = child.children[0]
            if next_child in bifurcation_children:
                break
            next_child._section = section
            section.points.append(next_child)
            child = next_child

        section.parent = section.points[0].parent._section if section.points[0].parent else None
        section.parent_idx = section.parent.idx if section.parent else -1

    if point_tree.soma_notation == '3PS':
        sections = _merge_soma(sections, point_tree)

    return sections


def _merge_soma(sections: List[Section], point_tree: PointTree):
    """
    If soma has 3PS notation, merge it into one section.
    """

    true_soma = point_tree.root._section
    true_soma.idx = 0
    true_soma.parent_idx = -1

    # Find false soma sections
    false_somas = [sec for sec in sections 
        if sec.domain_name == 'soma' and sec is not true_soma]
    if len(false_somas) != 2:
        print(false_somas)
        raise ValueError('Soma must have exactly 2 children of domain soma.')

    # Reassign points from false somas to true soma
    for i, sec in enumerate(false_somas):
        if len(sec.points) != 1:
            raise ValueError('False somas must have exactly 1 point.')
        for pt in sec.points:
            pt._section = true_soma

    # Sort points in true soma according to the 3PS convention
    true_soma.points = [
        false_somas[0].points[0], 
        true_soma.points[0], 
        false_somas[1].points[0]
    ]

    # Rebuild section list without false somas
    kept_sections = [s for s in sections if s not in false_somas]
    kept_sections.sort(key=lambda s: s.idx)

    # Create mapping from old to new indices
    old_to_new = {sec.idx: i for i, sec in enumerate(kept_sections)}

    # Update indices
    for sec in kept_sections:
        sec.idx = old_to_new[sec.idx]

    # Update parent indices
    for sec in kept_sections:
        if sec is not true_soma:
            sec.parent_idx = sec.points[0].parent._section.idx
        
    return kept_sections


def create_segment_tree(sec_tree):
    """
    Create a segment tree from a section tree.

    Parameters
    ----------
    sec_tree : SectionTree
        The section tree to create the segment tree from by splitting it into segments.

    Returns
    -------
    SegmentTree
        The segment tree representing spatial discretization of the neuron morphology for numerical simulations.
    """

    segments = _create_segments(sec_tree)

    seg_tree = SegmentTree(segments)
    sec_tree._seg_tree = seg_tree

    return seg_tree


def _create_segments(sec_tree) -> List[Segment]:
    """
    Create a list of Segment objects from a SectionTree object.
    """

    segments = []  
    # TODO: Refactor this to use a stack instead of recursion
    def add_segments(sec, parent_idx, idx_counter):
        segs = {seg: idx + idx_counter for idx, seg in enumerate(sec._ref)}
        sec.segments = []
        for seg, idx in segs.items():
            segment = NeuronSegment(
                idx=idx, parent_idx=parent_idx, sim_seg=seg, section=sec)
            segments.append(segment)
            sec.segments.append(segment)

            parent_idx = idx
        
        idx_counter += len(segs)

        
        for child in sec.children:
            # IMPORTANT: This is needed since 0 and 1 segments are not explicitly
            # defined in the section segments list
            if child._ref.parentseg().x == 1:
                new_parent_idx = list(segs.values())[-1]
            elif child._ref.parentseg().x == 0:
                new_parent_idx = list(segs.values())[0]
            else:
                new_parent_idx = segs[child._ref.parentseg()]
            # Recurse for the child section
            idx_counter = add_segments(child, new_parent_idx, idx_counter)

        return idx_counter

    # Start with the root section of the sec_tree
    add_segments(sec_tree.root, parent_idx=-1, idx_counter=0)

    return segments


def create_domains(section_tree):
    """
    Create domains using the data from the sections (from the points in the sections).
    """

    unique_domain_precursors = set([
        (sec.domain_name, sec.type_idx, sec.domain_color)
        for sec in section_tree.sections
        ])

    domains = {
        name: Domain(name, type_idx, color) 
        for name, type_idx, color in sorted(unique_domain_precursors)
        }

    for sec in section_tree.sections:
        domains[sec.domain_name].add_section(sec)

    return domains