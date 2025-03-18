import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.spatial.transform import Rotation

from dendrotweaks.utils import timeit

from dendrotweaks.morphology.trees import Node, Tree

from dendrotweaks.utils import timeit
from dendrotweaks.utils import get_swc_idx, get_domain_name
from dendrotweaks.utils import get_domain_color

from contextlib import contextmanager
import random


class Point(Node):
    """
    A class representing a single point in a morphological reconstruction.

    Parameters
    ----------
    idx : str
        The unique identifier of the node.
    type_idx : int
        The type of the node according to the SWC specification (e.g. soma-1, axon-2, dendrite-3).
    x : float
        The x-coordinate of the node.
    y : float
        The y-coordinate of the node.
    z : float
        The z-coordinate of the node.
    r : float
        The radius of the node.
    parent_idx : str
        The identifier of the parent node.

    Attributes
    ----------
    idx : str
        The unique identifier of the node.
    type_idx : int
        The type of the node according to the SWC specification (e.g. soma-1, axon-2, dendrite-3).
    x : float
        The x-coordinate of the node.
    y : float
        The y-coordinate of the node.
    z : float
        The z-coordinate of the node.
    r : float
        The radius of the node.
    parent_idx : str
        The identifier of the parent node.
    """

    def __init__(self, idx: str, type_idx: int, 
                 x: float, y: float, z: float, r: float, 
                 parent_idx: str) -> None:
        super().__init__(idx, parent_idx)
        self.type_idx = type_idx
        self.x = x
        self.y = y
        self.z = z
        self.r = r
        self._section = None


    @property
    def domain(self):
        """
        The morphological or functional domain of the node.
        """
        return get_domain_name(self.type_idx)


    @domain.setter
    def domain(self, value):
        if isinstance(value, str):
            self.type_idx = get_swc_idx(value)
        elif value is None:
            self.type_idx = None


    @property
    def distance_to_parent(self):
        """
        The Euclidean distance from this node to its parent.
        """
        if self.parent:
            return np.sqrt((self.x - self.parent.x)**2 + 
                        (self.y - self.parent.y)**2 + 
                        (self.z - self.parent.z)**2)
        return 0


    def path_distance(self, within_domain=False, ancestor=None):
        """
        Compute the distance from this node to an ancestor node.
        
        Args:
            within_domain (bool): If True, stops when domain changes.
            ancestor (Node, optional): If provided, stops at this specific ancestor.
            
        Returns:
            float: The accumulated distance.
        """
        distance = 0
        node = self
        
        while node.parent:
            if ancestor and node.parent == ancestor:
                break  # Stop if we reach the specified ancestor

            if within_domain and node.parent.domain != node.domain:
                break  # Stop if domain changes
            
            distance += node.distance_to_parent
            node = node.parent

        return distance



    @property
    def df(self):
        """
        Return a DataFrame representation of the node.
        """
        return pd.DataFrame({'idx': [self.idx],
                             'type_idx': [self.type_idx],
                             'x': [self.x],
                             'y': [self.y],
                             'z': [self.z],
                             'r': [self.r],
                             'parent_idx': [self.parent_idx]})

    def info(self):
        """
        Print information about the node.
        """
        info = (
            f"Node {self.idx}:\n"
            f"  Type: {get_domain_name(self.type_idx)}\n"
            f"  Coordinates: ({self.x}, {self.y}, {self.z})\n"
            f"  Radius: {self.r}\n"
            f"  Parent: {self.parent_idx}\n"
            f"  Children: {[child.idx for child in self.children]}\n"
            f"  Siblings: {[sibling.idx for sibling in self.siblings]}\n"
            f"  Section: {self._section.idx if self._section else 'None'}"
        )
        print(info)

    def copy(self):
        """
        Create a copy of the node.

        Returns:
            Point: A copy of the node with the same attributes.
        """
        new_node = Point(self.idx, self.type_idx, self.x,
                            self.y, self.z, self.r, self.parent_idx)
        return new_node


    def overlaps_with(self, other, **kwargs) -> bool:
        """
        Check if the coordinates of this node overlap with another node.

        Args:
            other (Point): The other node to compare with.
            kwargs: Additional keyword arguments passed to np.allclose.

        Returns:
            bool: True if the coordinates overlap, False otherwise.
        """
        return np.allclose(
            [self.x, self.y, self.z], 
            [other.x, other.y, other.z], 
            **kwargs
        )



class PointTree(Tree):
    """
    A class representing a tree graph of points in a morphological reconstruction.

    Parameters
    ----------
    nodes : list[Point]
        A list of points in the tree.
    """

    def __init__(self, nodes: list[Point]) -> None:
        super().__init__(nodes)
        self._sections = []
        self._is_extended = False


    def __repr__(self):
        return f"PointTree(root={self.root!r}, num_nodes={len(self._nodes)})"


    # PROPERTIES

    @property
    def points(self):
        """
        The list of points in the tree. An alias for self._nodes.
        """
        return self._nodes

    # @property
    # def is_sectioned(self):
    #     return len(self._sections) > 0

    @property
    def soma_points(self):
        """
        The list of points representing the soma (type 1).
        """
        return [pt for pt in self.points if pt.type_idx == 1]

    @property
    def soma_center(self):
        """
        The center of the soma as the average of the coordinates of the soma points.
        """
        return np.mean([[pt.x, pt.y, pt.z] 
                        for pt in self.soma_points], axis=0)

    @property
    def apical_center(self):
        """
        The center of the apical dendrite as the average of the coordinates of the apical points.
        """
        apical_points = [pt for pt in self.points 
                        if pt.type_idx == 4]
        if len(apical_points) == 0:
            return None
        return np.mean([[pt.x, pt.y, pt.z] 
                       for pt in apical_points], axis=0)

    @property
    def soma_notation(self):
        """
        The type of soma notation used in the tree.
        - '1PS': One-point soma
        - '2PS': Two-point soma
        - '3PS': Three-point soma
        - 'contour': Soma represented as a contour
        """
        if len(self.soma_points) == 1:
            return '1PS'
        elif len(self.soma_points) == 2:
            return '2PS'
        elif len(self.soma_points) == 3:
            return '3PS'
        else:
            return 'contour'

    @property
    def df(self):
        """
        A DataFrame representation of the tree.
        """
        data = {
            'idx': [node.idx for node in self._nodes],
            'type_idx': [node.type_idx for node in self._nodes],
            'x': [node.x for node in self._nodes],
            'y': [node.y for node in self._nodes],
            'z': [node.z for node in self._nodes],
            'r': [node.r for node in self._nodes],
            'parent_idx': [node.parent_idx for node in self._nodes],
        }
        return pd.DataFrame(data)



    # SORTING METHODS

    def _sort_children(self):
        """
        Iterate through all nodes in the tree and sort their children based on
        the number of bifurcations (nodes with more than one child) in each child's
        subtree. Nodes with fewer bifurcations in their subtrees are placed earlier in the list
        of the node's children, ensuring that the shortest paths are traversed first.

        Returns
        -------
            None
        """
        for node in self._nodes:
            node.children = sorted(
                node.children, 
                key=lambda x: (x.type_idx, sum(1 for n in x.subtree if len(n.children) > 1)),
                reverse=False
            )

    # STANDARDIZATION METHODS

    def change_soma_notation(self, notation):
        """
        Convert the soma to 3PS notation.
        """
        if self.soma_notation == notation:
            return

        if self.soma_notation == '1PS':

            pt = self.soma_points[0]

            pt_left = Point(
                idx=2,
                type_idx=1,
                x=pt.x - pt.r,
                y=pt.y,
                z=pt.z,
                r=pt.r,
                parent_idx=pt.idx)

            pt_right = Point(
                idx=3,
                type_idx=1,
                x=pt.x + pt.r,
                y=pt.y,
                z=pt.z,
                r=pt.r,
                parent_idx=pt.idx)

            self.add_subtree(pt_right, pt)
            self.add_subtree(pt_left, pt)

        elif self.soma_notation == '3PS':
            raise NotImplementedError('Conversion from 1PS to 3PS notation is not implemented yet.')
            
        elif self.soma_notation =='contour':
            # if soma has contour notation, take the average
            # distance of the nodes from the center of the soma
            # and use it as radius, create 3 new nodes
            raise NotImplementedError('Conversion from contour is not implemented yet.')

        print('Converted soma to 3PS notation.')

    # GEOMETRICAL METHODS

    def round_coordinates(self, decimals=8):
        """
        Round the coordinates of all nodes to the specified number of decimals.

        Parameters
        ----------
        decimals : int, optional
            The number of decimals to round to, by default
        """
        for pt in self.points:
            pt.x = round(pt.x, decimals)
            pt.y = round(pt.y, decimals)
            pt.z = round(pt.z, decimals)
            pt.r = round(pt.r, decimals)

    def shift_coordinates_to_soma_center(self):
        """
        Shift all coordinates so that the soma center is at the origin (0, 0, 0).
        """
        soma_x, soma_y, soma_z = self.soma_center
        for pt in self.points:
            pt.x = round(pt.x - soma_x, 8)
            pt.y = round(pt.y - soma_y, 8)
            pt.z = round(pt.z - soma_z, 8)

    @timeit
    def rotate(self, angle_deg, axis='Y'):
        """Rotate the point cloud around the specified axis at the soma center using numpy.

        Parameters
        ----------
        angle_deg : float
            The rotation angle in degrees.
        axis : str, optional
            The rotation axis ('X', 'Y', or 'Z'), by default 'Y'.
        """

        # Get the rotation center point
        rotation_point = self.soma_center

        # Define rotation matrix based on the specified axis
        angle = np.radians(angle_deg)
        if axis == 'X':
            rotation_matrix = np.array([
                [1, 0, 0],
                [0, np.cos(angle), -np.sin(angle)],
                [0, np.sin(angle), np.cos(angle)]
            ])
        elif axis == 'Y':
            rotation_matrix = np.array([
                [np.cos(angle), 0, np.sin(angle)],
                [0, 1, 0],
                [-np.sin(angle), 0, np.cos(angle)]
            ])
        elif axis == 'Z':
            rotation_matrix = np.array([
                [np.cos(angle), -np.sin(angle), 0],
                [np.sin(angle), np.cos(angle), 0],
                [0, 0, 1]
            ])
        else:
            raise ValueError("Axis must be 'X', 'Y', or 'Z'")

        # Subtract rotation point to translate the cloud to the origin
        coords = np.array([[pt.x, pt.y, pt.z] for pt in self.points])
        coords -= rotation_point

        # Apply rotation
        rotated_coords = np.dot(coords, rotation_matrix.T)

        # Translate back to the original position
        rotated_coords += rotation_point

        # Update the coordinates of the points
        for pt, (x, y, z) in zip(self._nodes, rotated_coords):
            pt.x, pt.y, pt.z = x, y, z

    def align_apical_dendrite(self, axis='Y', facing='up'):
        """
        Align the apical dendrite with the specified axis.

        Parameters
        ----------
        axis : str, optional
            The axis to align the apical dendrite with ('X', 'Y', or 'Z'), by default 'Y'.
        facing : str, optional
            The direction the apical dendrite should face ('up' or 'down'), by default 'up'.
        """
        soma_center = self.soma_center
        apical_center = self.apical_center

        if apical_center is None:
            return

        # Define the target vector based on the axis and facing
        target_vector = {
            'X': np.array([1, 0, 0]),
            'Y': np.array([0, 1, 0]),
            'Z': np.array([0, 0, 1])
        }.get(axis.upper(), None)

        if target_vector is None:
            raise ValueError("Axis must be 'X', 'Y', or 'Z'")

        if facing == 'down':
            target_vector = -target_vector

        # Calculate the current vector
        current_vector = apical_center - soma_center

        # Check if the apical dendrite is already aligned
        if np.allclose(current_vector / np.linalg.norm(current_vector), target_vector):
            print('Apical dendrite is already aligned.')
            return

        # Calculate the rotation vector and angle
        rotation_vector = np.cross(current_vector, target_vector)
        rotation_angle = np.arccos(np.dot(current_vector, target_vector) / np.linalg.norm(current_vector))

        # Create the rotation matrix
        rotation_matrix = Rotation.from_rotvec(rotation_angle * rotation_vector / np.linalg.norm(rotation_vector)).as_matrix()

        # Apply the rotation to each point
        for pt in self.points:
            coords = np.array([pt.x, pt.y, pt.z]) - soma_center
            rotated_coords = np.dot(rotation_matrix, coords) + soma_center
            pt.x, pt.y, pt.z = rotated_coords


    # I/O METHODS
    def remove_overlaps(self):
        """
        Remove overlapping nodes from the tree.
        """
        nodes_before = len(self.points)

        overlapping_nodes = [
            pt for pt in self.traverse() 
            if pt.parent is not None and pt.overlaps_with(pt.parent)
        ]
        for pt in overlapping_nodes:
            self.remove_node(pt)

        self._is_extended = False
        nodes_after = len(self.points)
        if nodes_before != nodes_after:
            print(f'Removed {nodes_before - nodes_after} overlapping nodes.')


    def extend_sections(self):
        """
        Extend each section by adding a node in the beginning 
        overlapping with the parent node for geometrical continuity.
        """
        
        nodes_before = len(self.points)

        if self._is_extended:
            print('Tree is already extended.')
            return

        bifurcations_excluding_root = [
            b for b in self.bifurcations if b != self.root
        ]

        for pt in bifurcations_excluding_root:
            children = pt.children[:]
            for child in children:
                if child.overlaps_with(pt):
                    raise ValueError(f'Child {child} already overlaps with parent {pt}.')
                new_node = pt.copy()
                new_node.domain = child.domain
                self.insert_node_before(new_node, child)           

        self._is_extended = True
        nodes_after = len(self.points)
        print(f'Extended {nodes_after - nodes_before} nodes.')


    def to_swc(self, path_to_file):
        """
        Save the tree to an SWC file.
        """
        with remove_overlaps(self):
            df = self.df.astype({
                'idx': int,
                'type_idx': int,
                'x': float,
                'y': float,
                'z': float,
                'r': float,
                'parent_idx': int
            })
            df['idx'] += 1
            df.loc[df['parent_idx'] >= 0, 'parent_idx'] += 1
            df.to_csv(path_to_file, sep=' ', index=False, header=False)


    # PLOTTING METHODS

    def plot(self, ax=None, 
             show_nodes=True, show_edges=True, show_domains=True,
             annotate=False, projection='XY', 
             highlight_nodes=None, focus_nodes=None):
        """
        Plot a 2D projection of the tree.

        Parameters
        ----------
        ax : matplotlib.axes.Axes, optional
            The axes to plot on, by default None
        show_nodes : bool, optional
            Whether to plot the nodes, by default True
        show_edges : bool, optional
            Whether to plot the edges, by default True
        show_domains : bool, optional
            Whether to color the nodes based on their domains, by default True
        annotate : bool, optional
            Whether to annotate the nodes with their indices, by default False
        projection : str, optional
            The projection plane ('XY', 'XZ', or 'YZ'), by default 'XY'
        highlight_nodes : list, optional
            A list of nodes to highlight, by default None
        focus_nodes : list, optional
            A list of nodes to focus on, by default None
        """

        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 10))

        # Convert focus/highlight to sets for faster lookup
        focus_nodes = set(focus_nodes) if focus_nodes else None
        highlight_nodes = set(highlight_nodes) if highlight_nodes else None

        # Determine which points to consider
        points_to_plot = self.points if focus_nodes is None else [pt for pt in self.points if pt in focus_nodes]

        # Extract coordinates for projection
        coords = {axis: [getattr(pt, axis.lower()) for pt in points_to_plot] for axis in "XYZ"}

        # Draw edges efficiently
        if show_edges:
            point_set = set(points_to_plot)  # Convert list to set for fast lookup
            for pt1, pt2 in self.edges:
                if pt1 in point_set and pt2 in point_set:
                    ax.plot(
                        [getattr(pt1, projection[0].lower()), getattr(pt2, projection[0].lower())],
                        [getattr(pt1, projection[1].lower()), getattr(pt2, projection[1].lower())],
                        color='C1'
                    )

        # Assign colors based on domains
        if show_domains:
            for pt in points_to_plot:
                colors = [get_domain_color(pt.domain) for pt in points_to_plot]
        else:
            colors = 'C0'

        # Plot nodes
        if show_nodes:
            ax.scatter(coords[projection[0]], coords[projection[1]], s=10, c=colors, marker='.', zorder=2)

        # Annotate nodes if few enough
        if annotate and len(points_to_plot) < 50:
            for pt, x, y in zip(points_to_plot, coords[projection[0]], coords[projection[1]]):
                ax.annotate(f'{pt.idx}', (x, y), fontsize=8)

        # Highlight nodes correctly
        if highlight_nodes:
            for i, pt in enumerate(points_to_plot):
                if pt in highlight_nodes:
                    ax.plot(coords[projection[0]][i], coords[projection[1]][i], 'o', color='C3', markersize=5)

        # Set labels and aspect ratio
        ax.set_xlabel(projection[0])
        ax.set_ylabel(projection[1])
        if projection in {"XY", "XZ", "YZ"}:
            ax.set_aspect('equal')



    def plot_radii_distribution(self, ax=None, highlight=None, 
    domains=True, show_soma=False):
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 3))

        for pt in self.points:
            if not show_soma and pt.domain == 'soma':
                continue
            color = get_domain_color(pt.domain)
            if highlight and pt.idx in highlight:
                ax.plot(
                    pt.path_distance(), 
                    pt.r, 
                    marker='.', 
                    color='red', 
                    zorder=2
                )
            else:
                ax.plot(
                    pt.path_distance(), 
                    pt.r, 
                    marker='.', 
                    color=color, 
                    zorder=1
                )
        ax.set_xlabel('Distance from root')
        ax.set_ylabel('Radius')


@contextmanager
def remove_overlaps(point_tree):
    """
    Context manager for temporarily removing overlaps in the given point_tree.
    Is primarily used for saving the tree to an SWC file without overlaps.
    Restores the original state of the tree after the context block to ensure
    the geometrical continuity of the tree.
    """
    # Store whether the point_tree was already extended
    was_extended = point_tree._is_extended
    
    # Remove overlaps
    point_tree.remove_overlaps()
    point_tree.sort()
    
    try:
        # Yield control to the context block
        yield
    finally:
        # Restore the overlapping state if the point_tree was extended
        if was_extended:
            point_tree.extend_sections()
            point_tree.sort()
