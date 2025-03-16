from dendrotweaks.morphology.trees import Tree
from dendrotweaks.morphology.point_trees import PointTree
from dendrotweaks.morphology.sec_trees import SectionTree

import numpy as np
import warnings

# def custom_warning_formatter(message, category, filename, lineno, file=None, line=None):
#     return f"WARNING: {message}\n({os.path.basename(filename)}, line {lineno})\n"

# warnings.formatwarning = custom_warning_formatter


def validate_tree(tree):
    """
    Validate the toplogical structure of a tree graph.

    Parameters
    ----------
    tree : Tree
        The tree to validate.
    """
    # Check for unique node ids
    check_unique_ids(tree)
    check_unique_root(tree)
    check_unique_children(tree)
    

    # Check for connectivity
    check_connections(tree)
    check_loops(tree)
    check_bifurcations(tree)
    # validate_order(self.tree)

    if isinstance(tree, PointTree):
        validate_point_tree(tree)

    if isinstance(tree, SectionTree):
        validate_section_tree(tree)

    # Check if the tree is sorted
    print("Checking if the tree is sorted...")
    if not tree.is_sorted:
        warnings.warn("Tree is not sorted")
    
    print("***Validation complete.***")


# -----------------------------------------------------------------------------
# Indicies
# -----------------------------------------------------------------------------

def check_unique_ids(tree):
    print("Checking for unique node ids...")
    node_ids = {node.idx for node in tree._nodes}
    if len(node_ids) != len(tree._nodes):
        warnings.warn(f"Tree contains {len(tree._nodes) - len(node_ids)} duplicate node ids.")


def check_unique_children(tree):
    print("Checking for duplicate children...")
    for node in tree._nodes:
        children = node.children
        if len(children) != len(set(children)):
            warnings.warn(f"Node {node} contains duplicate children.")


def check_unique_root(tree):
    print("Checking for unique root node...")
    root_nodes = {node for node in tree._nodes
        if node.parent is None or node.parent_idx in {None, -1, '-1'}
    }
    if len(root_nodes) > 1:
        warnings.warn(f"Found {len(root_nodes)} root nodes.")
    elif len(root_nodes) == 0:
        warnings.warn("Tree does not contain a root node.")


# -----------------------------------------------------------------------------
# Connectivity
# -----------------------------------------------------------------------------

def check_connections(tree):
    """
    Validate the parent-child relationships in the tree.

    1. Ensure that every node is listed as a child of its parent.
    2. Ensure that the parent of each child matches the node.
    """
    print("Checking tree connectivity...")
    if not tree.is_connected:
        not_connected = set(tree._nodes) - set(tree.root.subtree)
        warnings.warn(f"The following nodes are not connected to the root node: {not_connected}")

    for node in tree._nodes:
        parent = node.parent
        
        # Validate that the node is in its parent's children list.
        if parent is not None:
            if node not in parent.children:
                warnings.warn(
                    f"Validation Warning: Node {node} is not listed in the children of its parent {parent}. "
                    f"Expected parent.children to include {node}, but it does not."
                )

        # Validate that the parent of each child is the current node.
        for child in node.children:
            if child.parent is not node:
                warnings.warn(
                    f"Validation Warning: Node {child} has an incorrect parent. "
                    f"Expected parent {node}, but found {child.parent}."
                )


def check_loops(tree):
    print("Checking for loops...")
    for node in tree._nodes:
        for descendant in node.subtree:
            if node in descendant.children:
                warnings.warn(f"Node {node} is a descendant of itself. Loop detected at node {descendant}.")

def check_bifurcations(tree):
    print("Checking for bifurcations with more than 2 children...")
    bifurcation_issues = {node: len(node.children) for node in tree.bifurcations if len(node.children) > 2 and node is not tree.root}
    if bifurcation_issues:
        issues_str = "\n".join([f"Node {node.idx:<6} has {count} children" for node, count in bifurcation_issues.items()])
        warnings.warn(f"Tree contains bifurcations with more than 2 children:\n{issues_str}")
    

# =============================================================================
# Point-specific validation
# =============================================================================

def validate_point_tree(point_tree):
    """
    Validate the geometry of a point tree.

    Parameters
    ----------
    point_tree : PointTree
        The point tree to validate.
    """

    # Check for NaN values in the DataFrame
    print("Checking for NaN values...")
    nan_counts = point_tree.df.isnull().sum()
    if nan_counts.sum() > 0:
        warnings.warn(f"Found {nan_counts} NaN values in the DataFrame")

    # Check for bifurcations in the soma
    print("Checking for bifurcations in the soma...")
    bifurcations_without_root = [pt for pt in point_tree.bifurcations 
        if pt is not point_tree.root]
    bifurcations_within_soma = [pt for pt in bifurcations_without_root
        if pt.type_idx == 1]
    if bifurcations_within_soma:
        warnings.warn(f"Soma must be non-branching. Found bifurcations: {bifurcations_within_soma}")


    if point_tree._is_extended:
        print("Checking the extended tree for geometric continuity...")
        non_overlapping_children = [
            (pt, child) for pt in bifurcations_without_root for child in pt.children
            if not child.overlaps_with(pt)
        ]
        if non_overlapping_children:
            issues_str = "\n".join([f"Child {child} does not overlap with parent {pt}" for pt, child in non_overlapping_children])
            warnings.warn(f"Found non-overlapping children:\n{issues_str} for bifurcations")
        

# =============================================================================
# Section-specific validation
# =============================================================================

def validate_section_tree(section_tree):
    """
    Validate a section tree.

    Parameters
    ----------
    section_tree : SectionTree
        The section tree to validate.
    """

    print("Checking that all points in a section belong to the same domain...")
    for sec in section_tree:
        if not all(pt.domain == sec.domain for pt in sec.points):
            warnings.warn('All points in a section must belong to the same domain.')

    print("Checking that all sections have a non-zero length...")
    if any(sec.length == 0 for sec in section_tree):
        warnings.warn('Found sections with zero length.')

    print("Checking that all sections (except soma) have 0 or 2 children...")
    if any(len(sec.children) not in {0, 2} and sec is not section_tree.root for sec in section_tree):
        warnings.warn('Found sections with an incorrect number of children.')

    print("Checking that the root section has domain soma...")
    if not section_tree.root.domain == 'soma':
        warnings.warn('Root section must have domain soma.')


# =============================================================================
# Validation utilities
# =============================================================================

def shuffle_indices_for_testing(df):
    idx_range = int(df['Index'].max() - df['Index'].min()) + 1
    random_mapping = {k:v for k, v in zip(df['Index'], np.random.permutation(idx_range))}
    df['Index'] = df['Index'].map(random_mapping)
    df.loc[df['Parent'] != -1, 'Parent'] = df['Parent'].map(random_mapping)
    return df