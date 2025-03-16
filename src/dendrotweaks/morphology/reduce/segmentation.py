"""
This module contains functions for reducing dendritic subtrees into single cylinders.
The module incorporates code from neuron_reduce, which implements the algorithm described in:
Amsalem, O., Eyal, G., Rogozinski, N. et al. An efficient analytical reduction of detailed nonlinear neuron models. Nat Commun 11, 288 (2020). https://doi.org/10.1038/s41467-019-13932-6
The original code can be found at: https://github.com/orena1/neuron_reduce. Licensed under MIT License.
"""

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


def calculate_nsegs_from_manual_arg(new_cable_properties, total_segments_wanted):
    '''Calculates the number of segments for each section in the reduced model
    according to the given total_segments_wanted and the given
    new_dends_electrotonic_length (the electrotonic lengths of all the new
    sections).  Called when the user chooses to give to the program the
    approximate total number of segments that the reduced model should have
    (non-default calculation).
    '''
    # minus one for the one segment of the soma:
    total_segments_in_dendrites = total_segments_wanted - 1

    # total electrotonic length of reduced dendritic cables
    sum_of_lengths = sum(prop.electrotonic_length
                         for prop in new_cable_properties)

    # the num of segments assigned to each section is in proportion to the
    # section's relative contribution to the total electrotonic length in the
    # model
    dends_nsegs = []
    for prop in new_cable_properties:
        new_length = prop.electrotonic_length
        new_nseg_to_put = int(round((float(new_length) / sum_of_lengths) *
                              total_segments_in_dendrites))
        if new_nseg_to_put < 1:
            new_nseg_to_put = 1
        dends_nsegs.append(new_nseg_to_put)
    return dends_nsegs
    

def calculate_nsegs_from_lambda(new_cable_properties):
    '''calculate the number of segments for each section in the reduced model
    according to the length (in microns) and space constant (= lambda - in
    microns) that were previously calculated for each section and are given in
    subtree_dimensions.  According to this calculation, a segment is formed for
    every 0.1 * lambda in a section. (lambda = space constant = electrotonic length unit).
    '''
    dends_nsegs = []
    for cable in new_cable_properties:
        # for every unit of electronic length (length/space_constant such units)
        # ~10 segments are formed
        dends_nsegs.append(int((float(cable.length) / cable.space_const) * 10 / 2) * 2 + 1)
    return dends_nsegs