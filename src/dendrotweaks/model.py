from typing import List, Union, Callable
import os
import json
import matplotlib.pyplot as plt
import numpy as np
import quantities as pq

from dendrotweaks.morphology.point_trees import PointTree
from dendrotweaks.morphology.sec_trees import NeuronSection, Section, SectionTree, Domain
from dendrotweaks.morphology.seg_trees import NeuronSegment, Segment, SegmentTree
from dendrotweaks.simulators import NeuronSimulator
from dendrotweaks.biophys.groups import SegmentGroup
from dendrotweaks.biophys.mechanisms import Mechanism, LeakChannel, CaDynamics
from dendrotweaks.biophys.io import create_channel, standardize_channel, create_standard_channel
from dendrotweaks.biophys.io import MODFileLoader
from dendrotweaks.morphology.io import create_point_tree, create_section_tree, create_segment_tree
from dendrotweaks.stimuli.iclamps import IClamp
from dendrotweaks.biophys.distributions import Distribution
from dendrotweaks.stimuli.populations import Population
from dendrotweaks.utils import calculate_lambda_f, dynamic_import
from dendrotweaks.utils import get_domain_color, timeit

from collections import OrderedDict, defaultdict
from numpy import nan
# from .logger import logger

from dendrotweaks.path_manager import PathManager
import dendrotweaks.morphology.reduce as rdc

import pandas as pd

import warnings

POPULATIONS = {'AMPA': {}, 'NMDA': {}, 'AMPA_NMDA': {}, 'GABAa': {}}

def custom_warning_formatter(message, category, filename, lineno, file=None, line=None):
    return f"WARNING: {message}\n({os.path.basename(filename)}, line {lineno})\n"

warnings.formatwarning = custom_warning_formatter

INDEPENDENT_PARAMS = {
    'cm': 1, # uF/cm2
    'Ra': 100, # Ohm cm
    'ena': 50, # mV
    'ek': -77, # mV
    'eca': 140 # mV
}

DOMAIN_TO_GROUP = {
    'soma': 'somatic',
    'axon': 'axonal',
    'dend': 'dendritic',
    'apic': 'apical',
}


class Model():
    """
    A model object that represents a neuron model.

    Parameters
    ----------
    name : str
        The name of the model.
    simulator_name : str
        The name of the simulator to use (either 'NEURON' or 'Jaxley').
    path_to_data : str
        The path to the data files where swc and mod files are stored.

    Attributes
    ----------
    path_to_model : str
        The path to the model directory.
    path_manager : PathManager
        The path manager for the model.
    mod_loader : MODFileLoader
        The MOD file loader.
    simulator_name : str
        The name of the simulator to use. Default is 'NEURON'.
    point_tree : PointTree
        The point tree representing the morphological reconstruction.
    sec_tree : SectionTree
        The section tree representing the morphology on the section level.
    mechanisms : dict
        A dictionary of mechanisms available for the model.
    domains_to_mechs : dict
        A dictionary mapping domains to mechanisms inserted in them.
    params : dict
        A dictionary mapping parameters to their distributions.
    d_lambda : float
        The spatial discretization parameter.
    seg_tree : SegmentTree
        The segment tree representing the morphology on the segment level.
    iclamps : dict
        A dictionary of current clamps in the model.
    populations : dict
        A dictionary of "virtual" populations forming synapses on the model.
    simulator : Simulator
        The simulator object to use.
    """

    def __init__(self, path_to_model,
                simulator_name='NEURON',) -> None:

        # Metadata
        self.path_to_model = path_to_model
        self._name = os.path.basename(os.path.normpath(path_to_model))
        self.morphology_name = ''
        self.version = ''
        self.path_manager = PathManager(path_to_model)
        self.simulator_name = simulator_name
        self._verbose = False

        # File managers
        self.mod_loader = MODFileLoader()

        # Morphology
        self.point_tree = None
        self.sec_tree = None

        # Mechanisms
        self.mechanisms = {}
        self.domains_to_mechs = {}

        # Parameters
        self.params = {
            'cm': {'all': Distribution('constant', value=1)}, # uF/cm2
            'Ra': {'all': Distribution('constant', value=35.4)}, # Ohm cm
        }

        self.params_to_units = {
            'cm': pq.uF/pq.cm**2,
            'Ra': pq.ohm*pq.cm,
        }

        # Groups
        self._groups = []

        # Distributions
        # self.distributed_params = {}

        # Segmentation
        self.d_lambda = 0.1
        self.seg_tree = None

        # Stimuli
        self.iclamps = {}
        self.populations = POPULATIONS

        # Simulator
        if simulator_name == 'NEURON':
            self.simulator = NeuronSimulator()
        elif simulator_name == 'Jaxley':
            self.simulator = JaxleySimulator()
        else:
            raise ValueError(
                'Simulator name not recognized. Use NEURON or Jaxley.')


    # -----------------------------------------------------------------------
    # PROPERTIES
    # -----------------------------------------------------------------------

    @property
    def name(self):
        """
        The name of the directory containing the model.
        """
        return self._name

    @property
    def verbose(self):
        """
        Whether to print verbose output.
        """
        return self._verbose

    @verbose.setter
    def verbose(self, value):
        self._verbose = value
        self.mod_loader.verbose = value


    @property
    def domains(self):
        """
        The morphological or functional domains of the model.
        Reference to the domains in the section tree.
        """
        return self.sec_tree.domains


    @property
    def recordings(self):
        """
        The recordings of the model. Reference to the recordings in the simulator.
        """
        return self.simulator.recordings


    @recordings.setter
    def recordings(self, recordings):
        self.simulator.recordings = recordings


    @property
    def groups(self):
        """
        The dictionary of segment groups in the model.
        """
        return {group.name: group for group in self._groups}


    @property
    def groups_to_parameters(self):
        """
        The dictionary mapping segment groups to parameters.
        """
        groups_to_parameters = {}
        for group in self._groups:
            groups_to_parameters[group.name] = {}
            for mech_name, params in self.mechs_to_params.items():
                if mech_name not in group.mechanisms:
                    continue
                groups_to_parameters[group.name] = params
        return groups_to_parameters

    @property
    def mechs_to_domains(self):
        """
        The dictionary mapping mechanisms to domains where they are inserted.
        """
        mechs_to_domains = defaultdict(set)
        for domain_name, mech_names in self.domains_to_mechs.items():
            for mech_name in mech_names:
                mechs_to_domains[mech_name].add(domain_name)
        return dict(mechs_to_domains)


    @property
    def parameters_to_groups(self):
        """
        The dictionary mapping parameters to groups where they are distributed.
        """
        parameters_to_groups = defaultdict(list)
        for group in self._groups:
            for mech_name, params in self.mechs_to_params.items():
                if mech_name not in group.mechanisms:
                    continue
                for param in params:
                    parameters_to_groups[param].append(group.name)
        return dict(parameters_to_groups)


    @property
    def params_to_mechs(self):
        """
        The dictionary mapping parameters to mechanisms to which they belong.
        """
        params_to_mechs = {}
        # Sort mechanisms by length (longer first) to ensure specific matches
        sorted_mechs = sorted(self.mechanisms, key=len, reverse=True)
        for param in self.params:
            matched = False
            for mech in sorted_mechs:
                suffix = f"_{mech}"  # Define exact suffix
                if param.endswith(suffix):
                    params_to_mechs[param] = mech
                    matched = True
                    break
            if not matched:
                params_to_mechs[param] = "Independent"  # No match found
        return params_to_mechs


    @property
    def mechs_to_params(self):
        """
        The dictionary mapping mechanisms to parameters they contain.
        """
        mechs_to_params = defaultdict(list)
        for param, mech_name in self.params_to_mechs.items():
            mechs_to_params[mech_name].append(param)
        return dict(mechs_to_params)


    @property 
    def conductances(self):
        """
        A filtered dictionary of parameters that represent conductances.
        """
        return {param: value for param, value in self.params.items()
                if param.startswith('gbar')}
    # -----------------------------------------------------------------------
    # METADATA
    # -----------------------------------------------------------------------

    def info(self):
        """
        Print information about the model.
        """
        info_str = (
            f"Model: {self.name}\n"
            f"Path to data: {self.path_manager.path_to_data}\n"
            f"Simulator: {self.simulator_name}\n"
            f"Groups: {len(self.groups)}\n"
            f"Avaliable mechanisms: {len(self.mechanisms)}\n"
            f"Inserted mechanisms: {len(self.mechs_to_params) - 1}\n"
            # f"Parameters: {len(self.parameters)}\n"
            f"IClamps: {len(self.iclamps)}\n"
        )
        print(info_str)


    @property
    def df_params(self):
        """
        A DataFrame of parameters and their distributions.
        """
        data = []
        for mech_name, params in self.mechs_to_params.items():
            for param in params:
                for group_name, distribution in self.params[param].items():
                    data.append({
                        'Mechanism': mech_name,
                        'Parameter': param,
                        'Group': group_name,
                        'Distribution': distribution if isinstance(distribution, str) else distribution.function_name,
                        'Distribution params': {} if isinstance(distribution, str) else distribution.parameters,
                    })
        df = pd.DataFrame(data)
        return df

    def print_directory_tree(self, *args, **kwargs):
        """
        Print the directory tree.
        """
        return self.path_manager.print_directory_tree(*args, **kwargs)

    def list_morphologies(self, extension='swc'):
        """
        List the morphologies available for the model.
        """
        return self.path_manager.list_files('morphology', extension=extension)

    def list_biophys(self, extension='json'):
        """
        List the biophysical configurations available for the model.
        """
        return self.path_manager.list_files('biophys', extension=extension)

    def list_mechanisms(self, extension='mod'):
        """
        List the mechanisms available for the model.
        """
        return self.path_manager.list_files('mod', extension=extension)

    def list_stimuli(self, extension='json'):
        """
        List the stimuli configurations available for the model.
        """
        return self.path_manager.list_files('stimuli', extension=extension)

    # ========================================================================
    # MORPHOLOGY
    # ========================================================================

    def load_morphology(self, file_name, soma_notation='3PS', 
        align=True, sort_children=True, force=False) -> None:
        """
        Read an SWC file and build the SWC and section trees.

        Parameters
        ----------
        file_name : str
            The name of the SWC file to read.
        soma_notation : str, optional
            The notation of the soma in the SWC file. Can be '3PS' (three-point soma) or '1PS'. Default is '3PS'.
        align : bool, optional
            Whether to align the morphology to the soma center and align the apical dendrite (if present).
        sort_children : bool, optional
            Whether to sort the children of each node by increasing subtree size
            in the tree sorting algorithms. If True, the traversal visits 
            children with shorter subtrees first and assigns them lower indices. If False, children
            are visited in their original SWC file order (matching NEURON's behavior).
        """
        # self.name = file_name.split('.')[0]
        self.morphology_name = file_name.replace('.swc', '')
        path_to_swc_file = self.path_manager.get_file_path('morphology', file_name, extension='swc')
        point_tree = create_point_tree(path_to_swc_file)
        # point_tree.remove_overlaps()
        point_tree.change_soma_notation(soma_notation)
        point_tree.sort(sort_children=sort_children, force=force)
        if align:    
            point_tree.shift_coordinates_to_soma_center()
            point_tree.align_apical_dendrite()
            point_tree.round_coordinates(8)
        self.point_tree = point_tree

        sec_tree = create_section_tree(point_tree)
        sec_tree.sort(sort_children=sort_children, force=force)
        self.sec_tree = sec_tree

        self.create_and_reference_sections_in_simulator()
        seg_tree = create_segment_tree(sec_tree)
        self.seg_tree = seg_tree

        self._add_default_segment_groups()
        self._initialize_domains_to_mechs()

        d_lambda = self.d_lambda
        self.set_segmentation(d_lambda=d_lambda)        
              

    def create_and_reference_sections_in_simulator(self):
        """
        Create and reference sections in the simulator.
        """
        if self.verbose: print(f'Building sections in {self.simulator_name}...')
        for sec in self.sec_tree.sections:
            sec.create_and_reference()
        n_sec = len([sec._ref for sec in self.sec_tree.sections 
                    if sec._ref is not None])
        if self.verbose: print(f'{n_sec} sections created.')

        


    def _add_default_segment_groups(self):
        self.add_group('all', list(self.domains.keys()))
        for domain_name in self.domains:
            group_name = DOMAIN_TO_GROUP.get(domain_name, domain_name)
            self.add_group(group_name, [domain_name])


    def _initialize_domains_to_mechs(self):
        for domain_name in self.domains:
            # Only if haven't been defined for the previous morphology
            # TODO: Check that domains match
            if not domain_name in self.domains_to_mechs: 
                self.domains_to_mechs[domain_name] = set()
        for domain_name, mech_names in self.domains_to_mechs.items():
            for mech_name in mech_names:
                mech = self.mechanisms[mech_name]
                self.insert_mechanism(mech, domain_name)


    def get_sections(self, filter_function):
        """Filter sections using a lambda function.
        
        Parameters
        ----------
        filter_function : Callable
            The lambda function to filter sections.
        """
        return [sec for sec in self.sec_tree.sections if filter_function(sec)]


    def get_segments(self, group_names=None):
        """
        Get the segments in specified groups.

        Parameters
        ----------
        group_names : List[str]
            The names of the groups to get segments from.
        """
        if not isinstance(group_names, list):
            raise ValueError('Group names must be a list.')
        return [seg for group_name in group_names for seg in self.seg_tree.segments if seg in self.groups[group_name]]
        
    # ========================================================================
    # SEGMENTATION
    # ========================================================================

    # TODO Make a context manager for this
    def _temp_clear_stimuli(self):
        """
        Temporarily save and clear stimuli.
        """
        self.export_stimuli(file_name='_temp_stimuli')
        self.remove_all_stimuli()
        self.remove_all_recordings()

    def _temp_reload_stimuli(self):
        """
        Load stimuli from a temporary file and clean up.
        """
        self.load_stimuli(file_name='_temp_stimuli')
        for ext in ['json', 'csv']:
            temp_path = self.path_manager.get_file_path('stimuli', '_temp_stimuli', extension=ext)
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def set_segmentation(self, d_lambda=0.1, f=100):
        """
        Set the number of segments in each section based on the geometry.

        Parameters
        ----------
        d_lambda : float
            The lambda value to use.
        f : float
            The frequency value to use.
        """
        self.d_lambda = d_lambda

        # Temporarily save and clear stimuli
        self._temp_clear_stimuli()

        # Pre-distribute parameters needed for lambda_f calculation
        for param_name in ['cm', 'Ra']:
            self.distribute(param_name)

        # Calculate lambda_f and set nseg for each section
        for sec in self.sec_tree.sections:
            lambda_f = calculate_lambda_f(sec.distances, sec.diameters, sec.Ra, sec.cm, f)
            nseg = max(1, int((sec.L / (d_lambda * lambda_f) + 0.9) / 2) * 2 + 1)
            sec._nseg = sec._ref.nseg = nseg

        # Rebuild the segment tree and redistribute parameters
        self.seg_tree = create_segment_tree(self.sec_tree)
        self.distribute_all()

        # Reload stimuli and clean up temporary files
        self._temp_reload_stimuli()


    # ========================================================================
    # MECHANISMS
    # ========================================================================

    def add_default_mechanisms(self, recompile=False):
        """
        Add default mechanisms to the model.

        Parameters
        ----------
        recompile : bool, optional
            Whether to recompile the mechanisms.
        """
        leak = LeakChannel()
        self.mechanisms[leak.name] = leak

        cadyn = CaDynamics()
        self.mechanisms[cadyn.name] = cadyn

        self.load_mechanisms('default_mod', recompile=recompile)


    def add_mechanisms(self, dir_name:str = 'mod', recompile=True) -> None:
        """
        Add a set of mechanisms from an archive to the model.

        Parameters
        ----------
        dir_name : str, optional
            The name of the archive to load mechanisms from. Default is 'mod'.
        recompile : bool, optional
            Whether to recompile the mechanisms.
        """
        # Create Mechanism objects and add them to the model
        for mechanism_name in self.path_manager.list_files(dir_name, extension='mod'):
            self.add_mechanism(mechanism_name, 
                               load=True, 
                               dir_name=dir_name, 
                               recompile=recompile)
            


    def add_mechanism(self, mechanism_name: str, 
                      python_template_name: str = 'default',
                      load=True, dir_name: str = 'mod', recompile=True
                      ) -> None:
        """
        Create a Mechanism object from the MOD file (or LeakChannel).

        Parameters
        ----------
        mechanism_name : str
            The name of the mechanism to add.
        python_template_name : str, optional
            The name of the Python template to use. Default is 'default'.
        load : bool, optional
            Whether to load the mechanism using neuron.load_mechanisms.
        """
        paths = self.path_manager.get_channel_paths(
            mechanism_name, 
            python_template_name=python_template_name
        )
        mech = create_channel(**paths)
        # Add the mechanism to the model
        self.mechanisms[mech.name] = mech
        # Update the global parameters

        if load:
            self.load_mechanism(mechanism_name, dir_name, recompile)
        


    def load_mechanisms(self, dir_name: str = 'mod', recompile=True) -> None:
        """
        Load mechanisms from an archive.

        Parameters
        ----------
        dir_name : str, optional
            The name of the archive to load mechanisms from.
        recompile : bool, optional
            Whether to recompile the mechanisms.
        """
        mod_files = self.path_manager.list_files(dir_name, extension='mod')
        for mechanism_name in mod_files:
            self.load_mechanism(mechanism_name, dir_name, recompile)


    def load_mechanism(self, mechanism_name, dir_name='mod', recompile=False) -> None:
        """
        Load a mechanism from the specified archive.

        Parameters
        ----------
        mechanism_name : str
            The name of the mechanism to load.
        dir_name : str, optional
            The name of the directory to load the mechanism from. Default is 'mod'.
        recompile : bool, optional
            Whether to recompile the mechanism.
        """
        path_to_mod_file = self.path_manager.get_file_path(
            dir_name, mechanism_name, extension='mod'
        )
        self.mod_loader.load_mechanism(
            path_to_mod_file=path_to_mod_file, recompile=recompile
        )


    def standardize_channel(self, channel_name, 
        python_template_name=None, mod_template_name=None, remove_old=True):
        """
        Standardize a channel by creating a new channel with the same kinetic
        properties using the standard equations.

        Parameters
        ----------
        channel_name : str
            The name of the channel to standardize.
        python_template_name : str, optional
            The name of the Python template to use.
        mod_template_name : str, optional
            The name of the MOD template to use. 
        remove_old : bool, optional
            Whether to remove the old channel from the model. Default is True.
        """

        # Get data to transfer
        channel = self.mechanisms[channel_name]
        channel_domain_names = [domain_name for domain_name, mech_names 
            in self.domains_to_mechs.items() if channel_name in mech_names]
        gbar_name = f'gbar_{channel_name}'
        gbar_distributions = self.params[gbar_name]
        # Kinetic variables cannot be transferred

        # Uninsert the old channel
        for domain_name in self.domains:
            if channel_name in self.domains_to_mechs[domain_name]:
                self.uninsert_mechanism(channel_name, domain_name)

        # Remove the old channel
        if remove_old:
            self.mechanisms.pop(channel_name)
              
        # Create, add and load a new channel
        paths = self.path_manager.get_standard_channel_paths(
            channel_name, 
            mod_template_name=mod_template_name
        )
        standard_channel = standardize_channel(channel, **paths)
        
        self.mechanisms[standard_channel.name] = standard_channel
        self.load_mechanism(standard_channel.name, recompile=True)

        # Insert the new channel
        for domain_name in channel_domain_names:
            self.insert_mechanism(standard_channel.name, domain_name)

        # Transfer data
        gbar_name = f'gbar_{standard_channel.name}'
        for group_name, distribution in gbar_distributions.items():
            self.set_param(gbar_name, group_name, 
                distribution.function_name, **distribution.parameters)


    # ========================================================================
    # DOMAINS
    # ========================================================================

    def define_domain(self, domain_name: str, sections, distribute=True):
        """
        Adds a new domain to the cell and ensures proper partitioning 
        of the section tree graph.

        This method does not automatically insert mechanisms into the newly 
        created domain. It is the user's responsibility to insert mechanisms 
        into the domain after its creation. However, if the domain already 
        exists and is being extended, mechanisms will be inserted automatically 
        into the newly added sections.

        Parameters
        ----------
        domain_name : str
            The name of the domain to be added or extended.
        sections : list[Section] or Callable
            The sections to include in the domain. If a callable is provided, 
            it should be a filter function applied to the list of all sections 
            in the model.
        distribute : bool, optional
            Whether to re-distribute the parameters after defining the domain. 
            Default is True.
        """
        if isinstance(sections, Callable):
            sections = self.get_sections(sections)

        if domain_name not in self.domains:
            domain = Domain(domain_name)
            self._add_domain_groups(domain.name)
            self.domains[domain_name] = domain
            self.domains_to_mechs[domain_name] = set()
        else:
            domain = self.domains[domain_name]

        sections_to_move = [sec for sec in sections 
            if sec.domain != domain_name]

        if not sections_to_move:
            warnings.warn(f'Sections already in domain {domain_name}.')
            return

        for sec in sections_to_move:
            old_domain = self.domains[sec.domain]
            old_domain.remove_section(sec)
            for mech_name in self.domains_to_mechs[old_domain.name]:
                # TODO: What if section is already in domain? Can't be as
                # we use a filtered list of sections.
                mech = self.mechanisms[mech_name]
                sec.uninsert_mechanism(mech)
            

        # Add sections to the new domain
        for sec in sections_to_move:
            domain.add_section(sec)
            # Important: here we insert mechanisms only if we extend the domain,
            # i.e. the domain already exists and has mechanisms.
            # If the domain is new, we DO NOT insert mechanisms automatically
            # and leave it to the user to do so.
            for mech_name in self.domains_to_mechs.get(domain.name, set()):
                mech = self.mechanisms[mech_name]
                sec.insert_mechanism(mech)

        self._remove_empty()

        if distribute:
            self.distribute_all()


    def _add_domain_groups(self, domain_name):
        """
        Manage groups when a domain is added.
        """
        # Add new domain to `all` group
        if self.groups.get('all'):
            self.groups['all'].domains.append(domain_name)
        # Create a new group for the domain
        group_name = DOMAIN_TO_GROUP.get(domain_name, domain_name)
        self.add_group(group_name, domains=[domain_name])
    

    def _remove_empty(self):
        self._remove_empty_domains()
        self._remove_uninserted_mechanisms()
        self._remove_empty_groups()


    def _remove_empty_domains(self):
        """
        """
        empty_domains = [domain for domain in self.domains.values() 
            if domain.is_empty()]
        for domain in empty_domains:
            warnings.warn(f'Domain {domain.name} is empty and will be removed.')
            self.domains.pop(domain.name)
            self.domains_to_mechs.pop(domain.name)
            for group in self._groups:
                if domain.name in group.domains:
                    group.domains.remove(domain.name)
            # self.groups['all'].domains.remove(domain.name)


    def _remove_uninserted_mechanisms(self):
        mech_names = list(self.mechs_to_params.keys())
        mechs = [self.mechanisms[mech_name] for mech_name in mech_names
             if mech_name != 'Independent']
        uninserted_mechs = [mech for mech in mechs
                    if mech.name not in self.mechs_to_domains]
        for mech in uninserted_mechs:
            warnings.warn(f'Mechanism {mech.name} is not inserted in any domain and will be removed.')
            self._remove_mechanism_params(mech)


    def _remove_empty_groups(self):
        empty_groups = [group for group in self._groups 
                        if not any(seg in group 
                        for seg in self.seg_tree)]
        for group in empty_groups:
            warnings.warn(f'Group {group.name} is empty and will be removed.')
            self.remove_group(group.name)


    # -----------------------------------------------------------------------
    # INSERT / UNINSERT MECHANISMS
    # -----------------------------------------------------------------------

    def insert_mechanism(self, mechanism_name: str, 
                         domain_name: str, distribute=True):
        """
        Insert a mechanism into all sections in a domain.

        Parameters
        ----------
        mechanism_name : str
            The name of the mechanism to insert.
        domain_name : str
            The name of the domain to insert the mechanism into.
        distribute : bool, optional
            Whether to distribute the parameters after inserting the mechanism.
        """
        mech = self.mechanisms[mechanism_name]
        domain = self.domains[domain_name]

        # domain.insert_mechanism(mech)
        self.domains_to_mechs[domain_name].add(mech.name)
        for sec in domain.sections:
            sec.insert_mechanism(mech)
        self._add_mechanism_params(mech)

        # TODO: Redistribute parameters if any group contains this domain
        if distribute:
            for param_name in self.params:
                self.distribute(param_name)
        

    def _add_mechanism_params(self, mech):
        """
        Update the parameters when a mechanism is inserted.
        By default each parameter is set to a constant value
        through the entire cell.
        """
        for param_name, value in mech.range_params_with_suffix.items():
            self.params[param_name] = {'all': Distribution('constant', value=value)}
        
        if hasattr(mech, 'ion') and mech.ion in ['na', 'k', 'ca']:
            self._add_equilibrium_potentials_on_mech_insert(mech.ion)


    def _add_equilibrium_potentials_on_mech_insert(self, ion: str) -> None:
        """
        """
        if ion == 'na' and not self.params.get('ena'):
            self.params['ena'] = {'all': Distribution('constant', value=50)}
        elif ion == 'k' and not self.params.get('ek'):
            self.params['ek'] = {'all': Distribution('constant', value=-77)}
        elif ion == 'ca' and not self.params.get('eca'):
            self.params['eca'] = {'all': Distribution('constant', value=140)}


    def uninsert_mechanism(self, mechanism_name: str, 
                            domain_name: str):
        """
        Uninsert a mechanism from all sections in a domain

        Parameters
        ----------
        mechanism_name : str
            The name of the mechanism to uninsert.
        domain_name : str
            The name of the domain to uninsert the mechanism from.
        """
        mech = self.mechanisms[mechanism_name]
        domain = self.domains[domain_name]

        # domain.uninsert_mechanism(mech)
        for sec in domain.sections:
            sec.uninsert_mechanism(mech)
        self.domains_to_mechs[domain_name].remove(mech.name)

        if not self.mechs_to_domains.get(mech.name):
            warnings.warn(f'Mechanism {mech.name} is not inserted in any domain and will be removed.')
            self._remove_mechanism_params(mech)

    
    def _remove_mechanism_params(self, mech):
        for param_name in self.mechs_to_params.get(mech.name, []):
            self.params.pop(param_name)

        if hasattr(mech, 'ion') and mech.ion in ['na', 'k', 'ca']:
            self._remove_equilibrium_potentials_on_mech_uninsert(mech.ion)


    def _remove_equilibrium_potentials_on_mech_uninsert(self, ion: str) -> None:
        """
        """
        for mech_name, mech in self.mechanisms.items():
            if hasattr(mech, 'ion'):
                if mech.ion == mech.ion: return

        if ion == 'na':
            self.params.pop('ena', None)
        elif ion == 'k':
            self.params.pop('ek', None)
        elif ion == 'ca':
            self.params.pop('eca', None)


    # ========================================================================
    # SET PARAMETERS
    # ========================================================================

    # -----------------------------------------------------------------------
    # GROUPS
    # -----------------------------------------------------------------------

    def add_group(self, name, domains, select_by=None, min_value=None, max_value=None):
        """
        Add a group of sections to the model.

        Parameters
        ----------
        name : str
            The name of the group.
        domains : list[str]
            The domains to include in the group.
        select_by : str, optional
            The parameter to select the sections by. Can be 'diam', 'distance', 'domain_distance'.
        min_value : float, optional
            The minimum value of the parameter.
        max_value : float, optional
            The maximum value of the
        """
        if self.verbose: print(f'Adding group {name}...')
        group = SegmentGroup(name, domains, select_by, min_value, max_value)
        self._groups.append(group)
        

    def remove_group(self, group_name):
        """
        Remove a group from the model.

        Parameters
        ----------
        group_name : str
            The name of the group to remove.
        """
        # Remove group from the list of groups
        self._groups = [group for group in self._groups 
                        if group.name != group_name]
        # Remove distributions that refer to this group
        for param_name, groups_to_distrs in self.params.items():
            groups_to_distrs.pop(group_name, None)


    def move_group_down(self, name):
        """
        Move a group down in the list of groups.

        Parameters
        ----------
        name : str
            The name of the group to move down.
        """
        idx = next(i for i, group in enumerate(self._groups) if group.name == name)
        if idx > 0:
            self._groups[idx-1], self._groups[idx] = self._groups[idx], self._groups[idx-1]
        for param_name in self.distributed_params:
            self.distribute(param_name)


    def move_group_up(self, name):
        """
        Move a group up in the list of groups.

        Parameters
        ----------
        name : str
            The name of the group to move up.
        """
        idx = next(i for i, group in enumerate(self._groups) if group.name == name)
        if idx < len(self._groups) - 1:
            self._groups[idx+1], self._groups[idx] = self._groups[idx], self._groups[idx+1]
        for param_name in self.distributed_params:
            self.distribute(param_name)


    # -----------------------------------------------------------------------
    # DISTRIBUTIONS
    # -----------------------------------------------------------------------

    def set_param(self, param_name: str,
                        group_name: str = 'all',
                        distr_type: str = 'constant',
                        **distr_params):
        """
        Set a parameter for a group of segments.

        Parameters
        ----------
        param_name : str
            The name of the parameter to set.
        group_name : str, optional
            The name of the group to set the parameter for. Default is 'all'.
        distr_type : str, optional
            The type of the distribution to use. Default is 'constant'.
        distr_params : dict
            The parameters of the distribution.
        """

        if 'group' in distr_params:
            raise ValueError("Did you mean 'group_name' instead of 'group'?")

        if param_name in ['temperature', 'v_init']:
            setattr(self.simulator, param_name, distr_params['value'])
            return

        for key, value in distr_params.items():
            if not isinstance(value, (int, float)) or value is nan:
                raise ValueError(f"Parameter '{key}' must be a numeric value and not NaN, got {type(value).__name__} instead.")

        self.set_distribution(param_name, group_name, distr_type, **distr_params)
        self.distribute(param_name)


    def set_distribution(self, param_name: str,
                         group_name: None,
                         distr_type: str = 'constant',
                         **distr_params):
        """
        Set a distribution for a parameter.

        Parameters
        ----------
        param_name : str
            The name of the parameter to set.
        group_name : str, optional
            The name of the group to set the parameter for. Default is 'all'.
        distr_type : str, optional
            The type of the distribution to use. Default is 'constant'.
        distr_params : dict
            The parameters of the distribution.
        """
        
        if distr_type == 'inherit':
            distribution = 'inherit'
        else:
            distribution = Distribution(distr_type, **distr_params)
        self.params[param_name][group_name] = distribution

    def distribute_all(self):
        """
        Distribute all parameters to the segments.
        """
        groups_to_segments = {group.name: [seg for seg in self.seg_tree if seg in group] 
                         for group in self._groups}
        for param_name in self.params:
            self.distribute(param_name, groups_to_segments)

    
    def distribute(self, param_name: str, precomputed_groups=None):
        """
        Distribute a parameter to the segments.

        Parameters
        ----------
        param_name : str
            The name of the parameter to distribute.
        precomputed_groups : dict, optional
            A dictionary mapping group names to segments. Default is None.
        """
        if param_name == 'Ra':
            self._distribute_Ra(precomputed_groups)
            return

        groups_to_segments = precomputed_groups
        if groups_to_segments is None:
            groups_to_segments = {group.name: [seg for seg in self.seg_tree if seg in group] 
                                for group in self._groups}

        param_distributions = self.params[param_name]

        for group_name, distribution in param_distributions.items():
            
            filtered_segments = groups_to_segments[group_name]

            if distribution == 'inherit':
                for seg in filtered_segments:
                    value = seg.parent.get_param_value(param_name)
                    seg.set_param_value(param_name, value)
            else:
                for seg in filtered_segments:
                    value = distribution(seg.path_distance())
                    seg.set_param_value(param_name, value)


    def _distribute_Ra(self, precomputed_groups=None):
        """
        Distribute the axial resistance to the segments.
        """

        groups_to_segments = precomputed_groups
        if groups_to_segments is None:
            groups_to_segments = {group.name: [seg for seg in self.seg_tree if seg in group] 
                                for group in self._groups}

        param_distributions = self.params['Ra']

        for group_name, distribution in param_distributions.items():
            
            filtered_segments = groups_to_segments[group_name]
            if distribution == 'inherit':
                raise NotImplementedError("Inheritance of Ra is not implemented.")
            else:
                for seg in filtered_segments:
                    value = distribution(seg._section.path_distance(0.5))
                    seg._section._ref.Ra = value


    def remove_distribution(self, param_name, group_name):
        """
        Remove a distribution for a parameter.

        Parameters
        ----------
        param_name : str
            The name of the parameter to remove the distribution for.
        group_name : str
            The name of the group to remove the distribution for.
        """
        self.params[param_name].pop(group_name, None)
        self.distribute(param_name)

    # def set_section_param(self, param_name, value, domains=None):

    #     domains = domains or self.domains
    #     for sec in self.sec_tree.sections:
    #         if sec.domain in domains:
    #             setattr(sec._ref, param_name, value)

    # ========================================================================
    # STIMULI
    # ========================================================================

    # -----------------------------------------------------------------------
    # ICLAMPS
    # -----------------------------------------------------------------------

    def add_iclamp(self, sec, loc, amp=0, delay=100, dur=100):
        """
        Add an IClamp to a section.

        Parameters
        ----------
        sec : Section
            The section to add the IClamp to.
        loc : float
            The location of the IClamp in the section.
        amp : float, optional
            The amplitude of the IClamp. Default is 0.
        delay : float, optional
            The delay of the IClamp. Default is 100.
        dur : float, optional
            The duration of the IClamp. Default is 100.
        """
        seg = sec(loc)
        if self.iclamps.get(seg):
            self.remove_iclamp(sec, loc)
        iclamp = IClamp(sec, loc, amp, delay, dur)
        print(f'IClamp added to sec {sec} at loc {loc}.')
        self.iclamps[seg] = iclamp


    def remove_iclamp(self, sec, loc):
        """
        Remove an IClamp from a section.

        Parameters
        ----------
        sec : Section
            The section to remove the IClamp from.
        loc : float
            The location of the IClamp in the section.
        """
        seg = sec(loc)
        if self.iclamps.get(seg):
            self.iclamps.pop(seg)


    def remove_all_iclamps(self):
        """
        Remove all IClamps from the model.
        """

        for seg in list(self.iclamps.keys()):
            sec, loc = seg._section, seg.x
            self.remove_iclamp(sec, loc)
        if self.iclamps:
            warnings.warn(f'Not all iclamps were removed: {self.iclamps}')
        self.iclamps = {}


    # -----------------------------------------------------------------------
    # SYNAPSES
    # -----------------------------------------------------------------------

    def _add_population(self, population):
        self.populations[population.syn_type][population.name] = population


    def add_population(self, segments, N, syn_type):
        """
        Add a population of synapses to the model.

        Parameters
        ----------
        segments : list[Segment]
            The segments to add the synapses to.
        N : int
            The number of synapses to add.
        syn_type : str
            The type of synapse to add.
        """
        idx = len(self.populations[syn_type])
        population = Population(idx, segments, N, syn_type)
        population.allocate_synapses()
        population.create_inputs()
        self._add_population(population)


    def update_population_kinetic_params(self, pop_name, **params):
        """
        Update the kinetic parameters of a population of synapses.

        Parameters
        ----------
        pop_name : str
            The name of the population.
        params : dict
            The parameters to update.
        """
        syn_type, idx = pop_name.rsplit('_', 1)
        population = self.populations[syn_type][pop_name]
        population.update_kinetic_params(**params)
        print(population.kinetic_params)

    
    def update_population_input_params(self, pop_name, **params):
        """
        Update the input parameters of a population of synapses.

        Parameters
        ----------
        pop_name : str
            The name of the population.
        params : dict
            The parameters to update.
        """
        syn_type, idx = pop_name.rsplit('_', 1)
        population = self.populations[syn_type][pop_name]
        population.update_input_params(**params)
        print(population.input_params)


    def remove_population(self, name):
        """
        Remove a population of synapses from the model.

        Parameters  
        ----------
        name : str
            The name of the population
        """
        syn_type, idx = name.rsplit('_', 1)
        population = self.populations[syn_type].pop(name)
        population.clean()
        
    def remove_all_populations(self):
        """
        Remove all populations of synapses from the model.
        """
        for syn_type in self.populations:
            for name in list(self.populations[syn_type].keys()):
                self.remove_population(name)
        if any(self.populations.values()):
            warnings.warn(f'Not all populations were removed: {self.populations}')
        self.populations = POPULATIONS

    def remove_all_stimuli(self):
        """
        Remove all stimuli from the model.
        """
        self.remove_all_iclamps()
        self.remove_all_populations()

    # ========================================================================
    # SIMULATION
    # ========================================================================

    def add_recording(self, sec, loc, var='v'):
        """
        Add a recording to the model.

        Parameters
        ----------
        sec : Section
            The section to record from.
        loc : float
            The location along the normalized section length to record from.
        var : str, optional
            The variable to record. Default is 'v'.
        """
        self.simulator.add_recording(sec, loc, var)
        print(f'Recording added to sec {sec} at loc {loc}.')


    def remove_recording(self, sec, loc, var='v'):
        """
        Remove a recording from the model.

        Parameters
        ----------
        sec : Section
            The section to remove the recording from.
        loc : float
            The location along the normalized section length to remove the recording from.
        """
        self.simulator.remove_recording(sec, loc, var)


    def remove_all_recordings(self, var=None):
        """
        Remove all recordings from the model.
        """
        self.simulator.remove_all_recordings(var=var)


    def run(self, duration=300):
        """
        Run the simulation for a specified duration.

        Parameters
        ----------
        duration : float, optional
            The duration of the simulation. Default is 300.
        """
        self.simulator.run(duration)

    def get_traces(self):
        return self.simulator.get_traces()

    def plot(self, *args, **kwargs):
        self.simulator.plot(*args, **kwargs)

    # ========================================================================
    # MORPHOLOGY
    # ========================================================================

    def remove_subtree(self, sec):
        """
        Remove a subtree from the model.

        Parameters
        ----------
        sec : Section
            The root section of the subtree to remove.
        """
        self.sec_tree.remove_subtree(sec)
        self.sec_tree.sort()
        self._remove_empty()


    def merge_domains(self, domain_names: List[str]):
        """
        Merge two domains into one.
        """
        domains = [self.domains[domain_name] for domain_name in domain_names]
        for domain in domains[1:]:
            domains[0].merge(domain)
        self.remove_empty()


    def reduce_subtree(self, root, reduction_frequency=0, total_segments_manual=-1, fit=True):
        """
        Reduce a subtree to a single section.

        Parameters
        ----------
        root : Section
            The root section of the subtree to reduce.
        reduction_frequency : float, optional
            The frequency of the reduction. Default is 0.
        total_segments_manual : int, optional
            The number of segments in the reduced subtree. Default is -1 (automatic).
        fit : bool, optional
            Whether to create distributions for the reduced subtree by fitting
            the calculated average values. Default is True.
        """

        domain_name = root.domain
        parent = root.parent
        domains_in_subtree = [self.domains[domain_name] 
            for domain_name in set([sec.domain for sec in root.subtree])]
        if len(domains_in_subtree) > 1:
            # ensure the domains have the same mechanisms using self.domains_to_mechs
            domains_to_mechs = {domain_name: mech_names for domain_name, mech_names
                in self.domains_to_mechs.items() if domain_name in [domain.name for domain in domains_in_subtree]}
            common_mechs = set.intersection(*domains_to_mechs.values())
            if not common_mechs:
                raise ValueError(
                    'The domains in the subtree have different mechanisms. '
                    'Please ensure that all domains in the subtree have the same mechanisms. '
                    'You may need to insert the missing mechanisms and set their conductances to 0 where they are not needed.'
                )
        
        inserted_mechs = {mech_name: mech for mech_name, mech
            in self.mechanisms.items()
            if mech_name in self.domains_to_mechs[domain_name]
        }

        subtree_without_root = [sec for sec in root.subtree if sec is not root]

        # Map original segment names to their parameters
        segs_to_params = rdc.map_segs_to_params(root, inserted_mechs)
        

        # Temporarily remove active mechanisms        
        for mech_name in inserted_mechs:
            if mech_name == 'Leak':
                continue
            for sec in root.subtree:
                mech = self.mechanisms[mech_name]
                sec.uninsert_mechanism(mech)

        # Disconnect
        root.disconnect_from_parent()

         # Calculate new properties of a reduced subtree
        new_cable_properties = rdc.get_unique_cable_properties(root._ref, reduction_frequency)
        new_nseg = rdc.calculate_nsegs(new_cable_properties, total_segments_manual)
        print(new_cable_properties)
        

         # Map segment names to their new locations in the reduced cylinder
        segs_to_locs = rdc.map_segs_to_locs(root, reduction_frequency, new_cable_properties)
        

        # Reconnect
        root.connect_to_parent(parent)

        # Delete the original subtree
        children = root.children[:]
        for child_sec in children:
            self.remove_subtree(child_sec)

        # Set passive mechanisms for the reduced cylinder:
        rdc.apply_params_to_section(root, new_cable_properties, new_nseg)
        

        # Reinsert active mechanisms
        for mech_name in inserted_mechs:
            if mech_name == 'Leak':
                continue
            for sec in root.subtree:
                mech = self.mechanisms[mech_name]
                sec.insert_mechanism(mech)
        
        # Replace locs with corresponding segs
        
        segs_to_reduced_segs = rdc.map_segs_to_reduced_segs(segs_to_locs, root)

        # Map reduced segments to lists of parameters of corresponding original segments
        reduced_segs_to_params = rdc.map_reduced_segs_to_params(segs_to_reduced_segs, segs_to_params)
        
        # Set new values of parameters
        rdc.set_avg_params_to_reduced_segs(reduced_segs_to_params)
        rdc.interpolate_missing_values(reduced_segs_to_params, root)

        if not fit:
            return

        root_segs = [seg for seg in root.segments]
        params_to_coeffs = {}
        for param_name in self.params:
            coeffs = self.fit_distribution(param_name, segments=root_segs, plot=False)
            params_to_coeffs[param_name] = coeffs

        
        # Create new domain
        reduced_domains = [domain_name for domain_name in self.domains if domain_name.startswith('reduced')]
        new_reduced_domain_name = f'reduced_{len(reduced_domains)}'
        group_name = new_reduced_domain_name
        self.define_domain(new_reduced_domain_name, sections=[root], distribute=False)
        

        # Reinsert active mechanisms after creating the new domain
        # The new domain by default has no mechanisms. Here we re-insert the
        # exact same mechanisms as in the original domain of the root section.
        for mech_name in inserted_mechs:
            mech = self.mechanisms[mech_name]
            root.insert_mechanism(mech)
        self.domains_to_mechs[new_reduced_domain_name] = set(inserted_mechs.keys())
        
               
        # # Fit distributions to data for the group
        for param_name, coeffs in params_to_coeffs.items():
            self._set_distribution(param_name, group_name, coeffs, plot=True)
        
        # # Distribute parameters
        self.distribute_all()

        return {
            'domain_name': new_reduced_domain_name, 
            'group_name': group_name,
            'segs_to_params': segs_to_params,
            'segs_to_locs': segs_to_locs,
            'segs_to_reduced_segs': segs_to_reduced_segs,
            'reduced_segs_to_params': reduced_segs_to_params,
            'params_to_coeffs': params_to_coeffs
        }


    def fit_distribution(self, param_name, segments, max_degree=6, tolerance=1e-7, plot=False):
        from numpy import polyfit, polyval
        values = [seg.get_param_value(param_name) for seg in segments]
        distances = [seg.path_distance() for seg in segments]
        sorted_pairs = sorted(zip(distances, values))
        distances, values = zip(*sorted_pairs)
        degrees = range(0, max_degree+1)
        for degree in degrees:
            coeffs = polyfit(distances, values, degree)
            residuals = values - polyval(coeffs, distances)
            if all(abs(residuals) < tolerance):
                break
        if not all(abs(residuals) < tolerance):
            warnings.warn(f'Fitting failed for parameter {param_name} with the provided tolerance.\nUsing the last valid fit (degree={degree}). Maximum residual: {max(abs(residuals))}')
        if plot and degree > 0:
            self.plot_param(param_name, show_nan=False)
            plt.plot(distances, polyval(coeffs, distances), label='Fitted', color='red', linestyle='--')
            plt.legend()
        return coeffs


    def _set_distribution(self, param_name, group_name, coeffs, plot=False):
        # Set the distribution based on the degree of the polynomial fit
        coeffs = np.where(np.round(coeffs) == 0, coeffs, np.round(coeffs, 10))
        if len(coeffs) == 1:
            self.params[param_name][group_name] = Distribution('constant', value=coeffs[0])
        elif len(coeffs) == 2:
            self.params[param_name][group_name] = Distribution('linear', slope=coeffs[0], intercept=coeffs[1])
        else:
            self.params[param_name][group_name] = Distribution('polynomial', coeffs=coeffs)
            

    # ========================================================================
    # PLOTTING
    # ========================================================================

    def plot_param(self, param_name, ax=None, show_nan=True):
        """
        Plot the distribution of a parameter in the model.

        Parameters
        ----------
        param_name : str
            The name of the parameter to plot.
        ax : matplotlib.axes.Axes, optional
            The axes to plot on. Default is None.
        show_nan : bool, optional
            Whether to show NaN values. Default is True.            
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 2))

        if param_name not in self.params:
            warnings.warn(f'Parameter {param_name} not found.')

        values = [(seg.path_distance(), seg.get_param_value(param_name)) for seg in self.seg_tree]
        colors = [get_domain_color(seg.domain) for seg in self.seg_tree]

        valid_values = [(x, y) for (x, y), color in zip(values, colors) if not pd.isna(y) and y != 0]
        zero_values = [(x, y) for (x, y), color in zip(values, colors) if y == 0]
        nan_values = [(x, 0) for (x, y), color in zip(values, colors) if pd.isna(y)]
        valid_colors = [color for (x, y), color in zip(values, colors) if not pd.isna(y) and y != 0]
        zero_colors = [color for (x, y), color in zip(values, colors) if y == 0]
        nan_colors = [color for (x, y), color in zip(values, colors) if pd.isna(y)]

        if valid_values:
            ax.scatter(*zip(*valid_values), c=valid_colors)
        if zero_values:
            ax.scatter(*zip(*zero_values), edgecolors=zero_colors, facecolors='none', marker='.')
        if nan_values and show_nan:
            ax.scatter(*zip(*nan_values), c=nan_colors, marker='x', alpha=0.5, zorder=0)
        plt.axhline(y=0, color='k', linestyle='--')

        ax.set_xlabel('Path distance')
        ax.set_ylabel(param_name)
        ax.set_title(f'{param_name} distribution')


    # ========================================================================
    # FILE EXPORT
    # ========================================================================

    def export_morphology(self, file_name):
        """
        Write the SWC tree to an SWC file.

        Parameters
        ----------
        version : str, optional
            The version of the morphology appended to the morphology name.
        """
        path_to_file = self.path_manager.get_file_path('morphology', file_name, extension='swc')
        
        self.point_tree.to_swc(path_to_file)


    def to_dict(self):
        """
        Return a dictionary representation of the model.

        Returns
        -------
        dict
            The dictionary representation of the model.
        """
        return {
            'metadata': {
            'name': self.name,
            },
            'd_lambda': self.d_lambda,
            'domains': {domain: sorted(list(mechs)) for domain, mechs in self.domains_to_mechs.items()},
            'groups': [
            group.to_dict() for group in self._groups
            ],
            'params': {
            param_name: {
                group_name: distribution if isinstance(distribution, str) else distribution.to_dict()
                for group_name, distribution in distributions.items()
            }
            for param_name, distributions in self.params.items()
            },
        }

    def from_dict(self, data):
        """
        Load the model from a dictionary.

        Parameters
        ----------
        data : dict
            The dictionary representation of the model.
        """
        if not self.name == data['metadata']['name']:
            raise ValueError('Model name does not match the data.')

        self.d_lambda = data['d_lambda']

        # Domains and mechanisms
        self.domains_to_mechs = {
            domain: set(mechs) for domain, mechs in data['domains'].items()
        }
        if self.verbose: print('Inserting mechanisms...')
        for domain_name, mechs in self.domains_to_mechs.items():
            for mech_name in mechs:
                self.insert_mechanism(mech_name, domain_name, distribute=False)
        # print('Distributing parameters...')
        # self.distribute_all()

        # Groups
        if self.verbose: print('Adding groups...')
        self._groups = [SegmentGroup.from_dict(group) for group in data['groups']]

        if self.verbose: print('Distributing parameters...')
        # Parameters
        self.params = {
            param_name: {
                group_name: distribution if isinstance(distribution, str) else Distribution.from_dict(distribution)
                for group_name, distribution in distributions.items()
            }
            for param_name, distributions in data['params'].items()
        }

        if self.verbose: print('Setting segmentation...')
        if self.sec_tree is not None:
            d_lambda = self.d_lambda
            self.set_segmentation(d_lambda=d_lambda)
            


    def export_biophys(self, file_name, **kwargs):
        """
        Export the biophysical properties of the model to a JSON file.

        Parameters
        ----------
        file_name : str
            The name of the file to write to.
        **kwargs : dict
            Additional keyword arguments to pass to `json.dump`.
        """        
        
        path_to_json = self.path_manager.get_file_path('biophys', file_name, extension='json')
        if not kwargs.get('indent'):
            kwargs['indent'] = 4

        data = self.to_dict()
        with open(path_to_json, 'w') as f:
            json.dump(data, f, **kwargs)


    def load_biophys(self, file_name, recompile=True):
        """
        Load the biophysical properties of the model from a JSON file.

        Parameters
        ----------
        file_name : str
            The name of the file to read from.
        recompile : bool, optional
            Whether to recompile the mechanisms after loading. Default is True.
        """
        self.add_default_mechanisms()
        

        path_to_json = self.path_manager.get_file_path('biophys', file_name, extension='json')

        with open(path_to_json, 'r') as f:
            data = json.load(f)

        for mech_name in {mech for mechs in data['domains'].values() for mech in mechs}:
            if mech_name in ['Leak', 'CaDyn', 'Independent']:
                continue
            self.add_mechanism(mech_name, dir_name='mod', recompile=recompile)            

        self.from_dict(data)


    def stimuli_to_dict(self):
        """
        Convert the stimuli to a dictionary representation.

        Returns
        -------
        dict
            The dictionary representation of the stimuli.
        """
        return {
            'metadata': {
                'name': self.name,
            },
            'simulation': {
                **self.simulator.to_dict(),
            },
            'stimuli': {
                'recordings': [
                    {
                        'name': f'rec_{i}',
                        'var': var
                    } 
                    for var, recs in self.simulator.recordings.items()
                    for i, _ in enumerate(recs)
                ],
                'iclamps': [
                    {
                        'name': f'iclamp_{i}',
                        'amp': iclamp.amp,
                        'delay': iclamp.delay,
                        'dur': iclamp.dur
                    }
                    for i, (seg, iclamp) in enumerate(self.iclamps.items())
                ],
                'populations': {
                    syn_type: [pop.to_dict() for pop in pops.values()]
                    for syn_type, pops in self.populations.items()
                }
            },
        }


    def _stimuli_to_csv(self, path_to_csv=None):
        """
        Write the model to a CSV file.

        Parameters
        ----------
        path_to_csv : str
            The path to the CSV file to write.
        """
        
        rec_data = {
            'type': [],
            'idx': [],
            'sec_idx': [],
            'loc': [],
        }
        for var, recs in self.simulator.recordings.items():
            rec_data['type'].extend(['rec'] * len(recs))
            rec_data['idx'].extend([i for i in range(len(recs))])
            rec_data['sec_idx'].extend([seg._section.idx for seg in recs])
            rec_data['loc'].extend([seg.x for seg in recs])

        iclamp_data = {
            'type': ['iclamp'] * len(self.iclamps),
            'idx': [i for i in range(len(self.iclamps))],
            'sec_idx': [seg._section.idx for seg in self.iclamps],
            'loc': [seg.x for seg in self.iclamps],
        }
        
        synapses_data = {
            'type': [],
            'idx': [],
            'sec_idx': [],
            'loc': [],
        }

        for syn_type, pops in self.populations.items():
            for pop_name, pop in pops.items():
                pop_data = pop.to_csv()
                synapses_data['type'] += pop_data['syn_type']
                synapses_data['idx'] += [int(name.rsplit('_', 1)[1]) for name in pop_data['name']]
                synapses_data['sec_idx'] += pop_data['sec_idx']
                synapses_data['loc'] += pop_data['loc']

        df = pd.concat([
            pd.DataFrame(rec_data),
            pd.DataFrame(iclamp_data),
            pd.DataFrame(synapses_data)
        ], ignore_index=True)
        df['idx'] = df['idx'].astype(int)
        df['sec_idx'] = df['sec_idx'].astype(int)
        if path_to_csv: df.to_csv(path_to_csv, index=False)

        return df
        

    def export_stimuli(self, file_name, **kwargs):
        """
        Export the stimuli to a JSON and CSV file.

        Parameters
        ----------
        file_name : str
            The name of the file to write to.
        **kwargs : dict
            Additional keyword arguments to pass to `json.dump`.
        """
        path_to_json = self.path_manager.get_file_path('stimuli', file_name, extension='json')

        data = self.stimuli_to_dict()

        if not kwargs.get('indent'):
            kwargs['indent'] = 4
        with open(path_to_json, 'w') as f:
            json.dump(data, f, **kwargs)

        path_to_stimuli_csv = self.path_manager.get_file_path('stimuli', file_name, extension='csv')
        self._stimuli_to_csv(path_to_stimuli_csv)


    def load_stimuli(self, file_name):
        """
        Load the stimuli from a JSON file.

        Parameters
        ----------
        file_name : str
            The name of the file to read from.
        """
        
        path_to_json = self.path_manager.get_file_path('stimuli', file_name, extension='json')
        path_to_stimuli_csv = self.path_manager.get_file_path('stimuli', file_name, extension='csv')

        with open(path_to_json, 'r') as f:
            data = json.load(f)

        if not self.name == data['metadata']['name']:
            raise ValueError('Model name does not match the data.')

        df_stimuli = pd.read_csv(path_to_stimuli_csv)

        self.simulator.from_dict(data['simulation'])

        # Clear all stimuli and recordings
        self.remove_all_stimuli()
        self.remove_all_recordings()

        # IClamps -----------------------------------------------------------

        df_iclamps = df_stimuli[df_stimuli['type'] == 'iclamp'].reset_index(drop=True, inplace=False)

        for i, row in df_iclamps.iterrows():
            self.add_iclamp(
            self.sec_tree.sections[row['sec_idx']], 
            row['loc'],
            data['stimuli']['iclamps'][i]['amp'],
            data['stimuli']['iclamps'][i]['delay'],
            data['stimuli']['iclamps'][i]['dur']
            )

        # Populations -------------------------------------------------------

        syn_types = ['AMPA', 'NMDA', 'AMPA_NMDA', 'GABAa']

        for syn_type in syn_types:

            df_syn = df_stimuli[df_stimuli['type'] == syn_type]
    
            for i, pop_data in enumerate(data['stimuli']['populations'][syn_type]):

                df_pop = df_syn[df_syn['idx'] == i]

                segments = [self.sec_tree.sections[sec_idx](loc) 
                            for sec_idx, loc in zip(df_pop['sec_idx'], df_pop['loc'])]
                
                pop = Population(idx=i, 
                                segments=segments, 
                                N=pop_data['N'], 
                                syn_type=syn_type)
                
                syn_locs = [(self.sec_tree.sections[sec_idx], loc) for sec_idx, loc in zip(df_pop['sec_idx'].tolist(), df_pop['loc'].tolist())]
                
                pop.allocate_synapses(syn_locs=syn_locs)
                pop.update_kinetic_params(**pop_data['kinetic_params'])
                pop.update_input_params(**pop_data['input_params'])
                self._add_population(pop)

        # Recordings ---------------------------------------------------------

        df_recs = df_stimuli[df_stimuli['type'] == 'rec'].reset_index(drop=True, inplace=False)
        for i, row in df_recs.iterrows():
            # TODO: This conditional statement is to account for a recent change
            # in the JSON structure. It should be removed in the future.
            if data['stimuli'].get('recordings'):
                var = data['stimuli']['recordings'][i]['var']
            else:
                var = 'v'
            self.add_recording(
                self.sec_tree.sections[row['sec_idx']], row['loc'], var
            )


    def export_to_NEURON(self, file_name, include_kinetic_params=True):
        """
        Export the model to a python file using NEURON.

        Parameters
        ----------
        file_name : str
            The name of the file to write to.
        """
        from dendrotweaks.model_io import render_template
        from dendrotweaks.model_io import get_params_to_valid_domains
        from dendrotweaks.model_io import filter_params
        from dendrotweaks.model_io import get_neuron_domain

        params_to_valid_domains = get_params_to_valid_domains(self)
        params = self.params if include_kinetic_params else filter_params(self)
        path_to_template = self.path_manager.get_file_path('templates', 'NEURON_template', extension='py')

        output = render_template(path_to_template,
        {
            'param_dict': params,
            'groups_dict': self.groups,
            'params_to_mechs': self.params_to_mechs,
            'domains_to_mechs': self.domains_to_mechs,
            'iclamps': self.iclamps,
            'recordings': self.simulator.recordings,
            'params_to_valid_domains': params_to_valid_domains,
            'domains_to_NEURON': {domain: get_neuron_domain(domain) for domain in self.domains},
        })

        if not file_name.endswith('.py'):
            file_name += '.py'
        path_to_model = self.path_manager.path_to_model
        output_path = os.path.join(path_to_model, file_name)
        with open(output_path, 'w') as f:
            f.write(output)

        
