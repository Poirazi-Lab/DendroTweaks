"""
This module contains functions for reducing dendritic subtrees into single cylinders.
The module incorporates code from neuron_reduce, which implements the algorithm described in:
Amsalem, O., Eyal, G., Rogozinski, N. et al. An efficient analytical reduction of detailed nonlinear neuron models. Nat Commun 11, 288 (2020). https://doi.org/10.1038/s41467-019-13932-6
The original code can be found at: https://github.com/orena1/neuron_reduce. Licensed under MIT License.
"""


import math
import cmath

from neuron_reduce.subtree_reductor_func import calculate_nsegs_from_lambda, calculate_nsegs_from_manual_arg

def apply_params_to_section(section: "Section", cable_params: "CableParams", nseg: int):
    '''Apply new cable parameters to the given section in the model'''
    # Geometry
    section._ref.L = cable_params.length
    section._ref.diam = cable_params.diam
    # Segmentation
    section.nseg = nseg
    # Passive properties
    section._ref.cm = cable_params.cm
    section._ref.Ra = cable_params.ra
    section._ref.gbar_Leak = 1.0 / cable_params.rm
    section._ref.e_Leak = cable_params.e_pas
    remove_intermediate_points(section)
    update_section_geometry(section)
    

def remove_intermediate_points(sec: "Section") -> None:
    '''Removes all intermediate points in the section, keeping only start and end points'''
    point_tree = sec._tree._point_tree
    
    first_point, *intermediate_points, last_point = sec.points
    
    for point in intermediate_points:
        point_tree.remove_node(point)
    
    point_tree.sort()
    sec.points = [first_point, last_point]


def update_section_geometry(sec: "Section"):
    '''Updates section geometry by adjusting the end point to maintain section length and direction'''
    length = sec.L
    
    if len(sec.points) != 2:
        raise ValueError("Section must have only two points (the start and end points)")
    
    first_point, last_point = sec.points
    
    # Calculate the vector from first to last point
    vector = (
        last_point.x - first_point.x,
        last_point.y - first_point.y,
        last_point.z - first_point.z
    )
    
    # Calculate the current distance
    distance = math.sqrt(sum(component**2 for component in vector))
    
    # Scale the vector to match the desired length
    scale = length / distance
    
    # Update last point coordinates
    last_point.x = first_point.x + vector[0] * scale
    last_point.y = first_point.y + vector[1] * scale
    last_point.z = first_point.z + vector[2] * scale
    
    # Set radius for all points
    radius = round(sec.diam / 2, 3)
    for point in sec.points:
        point.r = radius

        
def _get_subtree_biophysical_properties(subtree_root_ref, frequency):
    ''' gets the biophysical cable properties (Rm, Ra, Rc) and q
    for the subtree to be reduced according to the properties of the root section of the subtree
    '''
    section = subtree_root_ref.sec

    rm = 1.0 / section.gbar_Leak  # in ohm * cm^2
    # in secs, with conversion of the capacitance from uF/cm2 to F/cm2
    RC = rm * (float(section.cm) / 1000000)

    # defining q=sqrt(1+iwRC))
    angular_freq = 2 * math.pi * frequency   # = w
    q_imaginary = angular_freq * RC
    q = complex(1, q_imaginary)   # q=1+iwRC
    q = cmath.sqrt(q)		# q = sqrt(1+iwRC)

    return (section.cm,
            rm,
            section.Ra,  # in ohm * cm
            section.e_Leak,
            q)


def calculate_nsegs(new_cable_properties, total_segments_manual):

    new_cable_properties = [new_cable_properties]

    if total_segments_manual > 1:
        print('the number of segments in the reduced model will be set to `total_segments_manual`')
        new_cables_nsegs = calculate_nsegs_from_manual_arg(new_cable_properties,
                                                           total_segments_manual)
    else:
        new_cables_nsegs = calculate_nsegs_from_lambda(new_cable_properties)
        if total_segments_manual > 0:
            print('from lambda')
            original_cell_seg_n = (sum(i.nseg for i in list(original_cell.basal)) +
                                   sum(i.nseg for i in list(
                                       original_cell.apical))
                                   )
            min_reduced_seg_n = int(
                round((total_segments_manual * original_cell_seg_n)))
            if sum(new_cables_nsegs) < min_reduced_seg_n:
                logger.debug(f"number of segments calculated using lambda is {sum(new_cables_nsegs)}, "
                             "the original cell had {original_cell_seg_n} segments.  "
                             "The min reduced segments is set to {total_segments_manual * 100}% of reduced cell segments")
                logger.debug("the reduced cell nseg is set to %s" %
                             min_reduced_seg_n)
                new_cables_nsegs = calculate_nsegs_from_manual_arg(new_cable_properties,
                                                                   min_reduced_seg_n)
        else:
            # print('Automatic segmentation')
            pass

    return new_cables_nsegs[0]