from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from dendrotweaks.utils import timeit
from typing import Union

class Node():
    """
    Represents a node in a tree.

    A node can be a 3D point in a neuron morphology,
    a segment, a section, or even a tree.

    Parameters
    ----------
    idx : Union[int, str]
        The index of the node.
    parent_idx : Union[int, str]
        The index of the parent node.

    Examples:
        >>> node = Node(0, -1)
        >>> node
        •0
    """

    def __init__(self, idx: Union[int, str], parent_idx: Union[int, str]) -> None:
        """
        Creates a node in a tree.

        Args:
            idx (Union[int, str]): The index of the node.
            parent_idx (Union[int, str]): The index of the parent node.
        """
        self.idx = int(idx)
        self.parent_idx = int(parent_idx)
        self._parent = None
        self.children = []
        self._tree = None

    def __repr__(self):
        class_name = type(self).__name__
        return f"{class_name}(idx={self.idx!r})"

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        self._parent = parent
        self.parent_idx = parent.idx if parent else -1


    @property
    def topological_type(self) -> str:
        """The topological type of the node based on the number of children.

        Returns:
            str: The topological type of the node: 'continuation', 'bifurcation', or 'termination'.
        """
        types = {0: 'termination', 1: 'continuation'}
        return types.get(len(self.children), 'bifurcation')

    # @property
    # def subtree(self) -> list:
    #     """
    #     Gets the subtree of the node (including the node itself).

    #     Returns:
    #         list: A list of nodes in the subtree.
    #     """
    #     subtree = [self]
    #     for child in self.children:
    #         subtree += child.subtree
    #     return subtree

    @property
    def subtree(self) -> list:
        """
        Gets the subtree of the node (including the node itself) using 
        an iterative depth-first traversal.
        
        Returns:
            list: A list of nodes in the subtree.
        """
        subtree = []
        stack = [self]  # Start from the current node

        while stack:
            node = stack.pop()
            subtree.append(node)
            stack.extend(node.children)  # Push children to stack

        return subtree

    @property
    def subtree_size(self):
        """
        Gets the size of the subtree of the node.

        Returns:
            int: The size of the subtree of the node.
        """
        return len(self.subtree)

    @property
    def depth(self):
        """
        Computes the depth of the node in the tree iteratively.
        """
        depth = 0
        node = self
        while node.parent:  # Traverse up to the root
            depth += 1
            node = node.parent
        return depth


    @property
    def siblings(self):
        """
        Gets the siblings of the node.

        Returns:
            list: A list of nodes that share the same parent as the node.
        """
        if self.parent is None:
            return []
        return [child for child in self.parent.children if child is not self]

    @property
    def nearest_neighbours(self):
        """
        Gets the nearest neighbours of the node.

        Returns:
            list: A list of nodes that share the same parent or children as the node.
        """
        return [self.parent] + self.children

    def connect_to_parent(self, parent):
        """
        Attach the node to a parent node.
        
        Warning
        -------
        This method should not be used directly when working with trees
        as it doesn't add the node to the tree's list of nodes. 
        Use the `Tree` class to insert nodes into the tree.

        Args:
            parent (Node): The parent node to attach the node to.
        """
        if parent in self.subtree:
            raise ValueError(f'Attaching a node will create a loop in the tree: {self} -> {parent}')
        self.parent = parent
        if self not in parent.children:
            parent.children.append(self)
        # parent.childrensorted(parent.children + [node], key=lambda x: x.idx)

    def disconnect_from_parent(self):
        """
        Detach the node from its parent.

        Examples
        --------
        for child in node.children: child.disconnect_from_parent()

        """
        if self.parent:
            self.parent.children.remove(self)
            self.parent = None

class Tree:
    """
    A class to represent a tree data structure.

    A tree graph is a hierarchical data structure that consists of nodes connected by edges.

    Parameters
    ----------
    nodes : list
        A list of nodes in the tree.

    Attributes
    ----------
    root : Node
        The root node of the tree.
    """

    def __init__(self, nodes: list) -> None:

        for node in nodes: node._tree = self
        self._nodes = nodes
        self.root = self._find_root()

        if not self.is_connected:
            self._connect_nodes()

    # MAGIC METHODS

    def __repr__(self):
        return f"Tree(root={self.root!r}, num_nodes={len(self._nodes)})"

    def __getitem__(self, idx):
        return self._nodes[idx]

    def __len__(self):
        return len(self._nodes)

    def __iter__(self):
        for node in self._nodes:
            yield node

    def __contains__(self, node):
        return node in self._nodes

    # PROPERTIES

    @property
    def is_connected(self):
        """
        Whether the tree is connected i.e. each node can be reached from the root.

        Returns
        -------
        bool 
            True if the root node's subtree contains exactly the same nodes
        as the entire tree. False otherwise.
        """
        nodes_set = set(self._nodes)
        subtree_set = set(self.root.subtree)
        return nodes_set == subtree_set

    @property
    def is_sorted(self):
        """
        Whether the nodes in the tree are sorted by index.

        Returns
        -------
        bool
            True if the nodes are sorted by index. False otherwise.
        """
        if not all([node.idx == i for i, node in enumerate(self._nodes, start=0)]):
            return False
        traversal_indices = [node.idx for node in self.traverse()]
        return traversal_indices == sorted(traversal_indices)

    @property
    def bifurcations(self):
        """
        The bifurcation nodes in the tree.

        Returns
        -------
        list
            A list of bifurcation nodes in the tree.
        """
        return [node for node in self._nodes if len(node.children) > 1]

    @property
    def terminations(self):
        return [node for node in self._nodes if len(node.children) == 0]

    @property
    def edges(self) -> list:
        """
        Returns a list of edges in the tree.

        Returns:
            list[tuple[Node, Node]]: A list of edges in the tree.
        """
        edges = []
        for node in self._nodes:
            if node.parent is not None:
                edges.append((node.parent, node))
        return edges

    # TREE CONSTRUCTION METHODS

    def _find_root(self):
        """
        Find the root node.

        Returns
        -------
        Node
            The root node of the tree.
        """
        ROOT_PARENT = {None, -1, '-1'}
        root_nodes = [node for node in self._nodes if node.parent_idx in ROOT_PARENT]

        if len(root_nodes) != 1:
            print('Root nodes:', root_nodes)
            raise ValueError(f'Tree must have exactly one root node. Found: {root_nodes}')

        return root_nodes[0]

    def _connect_nodes(self):
        """
        Efficiently builds the hierarchical tree structure for the nodes
        using a dictionary for fast parent lookups.
        """
        if self.is_connected:
            print('  Tree already connected.')
            return

        # Step 1: Create a dictionary for O(1) lookups
        node_map = {node.idx: node for node in self._nodes}

        # Step 2: Assign parent-child relationships in O(N) time
        for node in self._nodes:
            if node is not self.root and node.parent_idx in node_map:
                node.connect_to_parent(node_map[node.parent_idx])

        # Step 3: Ensure tree is fully connected
        if not self.is_connected:
            raise ValueError('Tree is not connected.')


    # TRAVERSAL METHODS

    def traverse(self, root=None):
        """
        Iterate over the nodes in the tree using a stack-based 
        depth-first traversal.

        Parameters
        ----------
        root : Node, optional
            The root node to start the traversal from. Defaults to None.
        """
        root = root or self.root
        stack = [root]
        visited = set()

        while stack:
            node = stack.pop()
            if node in visited:
                continue

            yield node
            visited.add(node)
            for child in reversed(node.children):
                stack.append(child)



    # SORTIONG METHODS

    def _sort_children(self):
        """
        Iterate through all nodes in the tree and sort their children based on
        the number of bifurcations (nodes with more than one child) in each child's
        subtree. Nodes with fewer bifurcations in their subtrees are placed earlier in the list
        of the node's children, ensuring that the shortest paths are traversed first.
        """

        # subtree_size_map = {node: len(self.get_subtree(node)) for node in self._nodes}

        for node in self._nodes:
            node.children = sorted(
                node.children, 
                key=lambda x: sum(1 for n in x.subtree if len(n.children) > 1),
                reverse=False
            )

    # @timeit
    def sort(self, sort_children=True, force=False):
        """
        Sort the nodes in the tree using a stack-based depth-first traversal.

        Parameters
        ----------
        sort_children : bool, optional
            Whether to sort the children of each node 
            based on the number of bifurcations in their subtrees. Defaults to True.
        force : bool, optional
            Whether to force the sorting of the tree even if it is already sorted. Defaults to False.
        """
        if self.is_sorted and not force:
            return

        if sort_children:
            self._sort_children()

        count = 0
        for node in self.traverse():
            node.idx = count
            node.parent_idx = node.parent.idx if node.parent else -1
            count += 1

        self._nodes = sorted(self._nodes, key=lambda x: x.idx)

        if not self.is_sorted:
            raise ValueError('Tree is not sorted.')
        print(f'Sorted {self}.')

    # INSERTION AND REMOVAL METHODS

    def remove_node(self, node):
        """
        Remove a node from the tree.

        Parameters
        ----------
        node : Node
            The node to remove.

        Raises
        ------
        ValueError
            If the tree is not sorted.
        """
        if node.parent is None:
            raise ValueError('Cannot remove the root node.')
        parent = node.parent
        children = node.children[:]
        for child in children:
            child.disconnect_from_parent()
            child.connect_to_parent(parent)
        node.disconnect_from_parent()
        self._nodes.remove(node)


    def remove_subtree(self, node):
        """
        Remove a subtree from the tree.

        Parameters
        ----------
        node : Node
            The root node of the subtree to remove.
        """
        node.disconnect_from_parent()
        for n in node.subtree:
            self._nodes.remove(n)


    def add_subtree(self, node, parent):
        """
        Add a subtree to the tree.

        Parameters
        ----------
        node : Node
            The root node of the subtree to add.
        parent : Node
            The parent node to attach the subtree to.
        """
        node.connect_to_parent(parent)
        self._nodes.extend(node.subtree)


    def insert_node_after(self, new_node, existing_node):
        """
        Insert a node after a given node in the tree.

        Parameters
        ----------
        new_node : Node
            The new node to insert.
        existing_node : Node
            The existing node after which to insert the new node.
        """
        if new_node in self._nodes:
            raise ValueError('Node already exists in the tree.')

        for child in existing_node.children:
            child.disconnect_from_parent()
            child.connect_to_parent(new_node)
        new_node.connect_to_parent(existing_node)

        self._nodes.append(new_node)


    def insert_node_before(self, new_node, existing_node):
        """
        Insert a node before a given node in the tree.

        Parameters
        ----------
        new_node : Node
            The new node to insert.
        existing_node : Node
            The existing node before which to insert the new node.
        """
        if new_node in self._nodes:
            raise ValueError('Node already exists in the tree.')
        new_node.connect_to_parent(existing_node.parent)
        existing_node.disconnect_from_parent()
        existing_node.connect_to_parent(new_node)
        
        self._nodes.append(new_node)


    def reposition_subtree(self, node, new_parent_node, origin=None):
        """
        Reposition a subtree in the tree.

        Parameters
        ----------
        node : Node
            The root node of the subtree to reposition.
        new_parent_node : Node
            The new parent node of the subtree.
        origin : Node, optional
            The origin node to use as the reference point for the repositioning. 
            Defaults to None.

        Note
        -----
        Treats differently the children of the root node.
        """
        if node.parent is None:
            raise ValueError('Cannot reposition the root node.')
        origin = origin or node.parent
        self.remove_subtree(node)
        shift_coordinates(node.subtree, 
                          origin=origin, 
                          target=new_parent_node)
        self.add_subtree(node, new_parent_node)


    # VISUALIZATION METHODS


    def topology(self):
        """
        Print the topology of the tree with a visual tree structure.
        """
        def print_node(node, prefix="", is_last=True):
            """Recursive function to print the node with branches."""
            # Print the current
            root_str = f"{node.parent_idx:6} |   "
            prefix = root_str + prefix
            print(prefix + '•' + str(node.idx))

            # Handle the children nodes
            num_children = len(node.children)
            for i, child in enumerate(node.children):
                is_last_child = (i == num_children - 1)
                branch = "└─" if is_last_child else "├─"
                prefix = prefix.replace("└─", "  ").replace("├─", "│ ")
                prefix = prefix.replace(root_str, "")
                print_node(child, prefix + branch, is_last_child)

        print('parent |   idx')
        print('-'*15)
        print_node(self.root)



def shift_coordinates(points, origin, target):
    """
    Shift the coordinates of a list of points from an origin to a target.
    """
    origin_vector = (origin.x, origin.y, origin.z)
    target_vector = (target.x, target.y, target.z)
    for pt in points:
        pt.x = pt.x - origin_vector[0] + target_vector[0]
        pt.y = pt.y - origin_vector[1] + target_vector[1]
        pt.z = pt.z - origin_vector[2] + target_vector[2]