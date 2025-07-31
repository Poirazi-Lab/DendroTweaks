# Imports
from typing import List, Union, Callable
import os
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np
from numpy import nan
import pandas as pd
import quantities as pq

# DendroTweaks imports
from dendrotweaks.simulators import NeuronSimulator
from dendrotweaks.biophys.io import MODFileLoader
from dendrotweaks.morphology import Domain
from dendrotweaks.biophys.groups import SegmentGroup
from dendrotweaks.biophys.distributions import Distribution
from dendrotweaks.path_manager import PathManager
import dendrotweaks.morphology.reduce as rdc
from dendrotweaks.utils import INDEPENDENT_PARAMS, DOMAIN_TO_GROUP, POPULATIONS
from dendrotweaks.utils import DEFAULT_FIT_MODELS

# Mixins
from dendrotweaks.model_io import IOMixin
from dendrotweaks.model_simulation import SimulationMixin

# Warnings configuration
import warnings

def custom_warning_formatter(message, category, filename, lineno, file=None, line=None):
    return f"WARNING: {message}\n({os.path.basename(filename)}, line {lineno})\n"

warnings.formatwarning = custom_warning_formatter



class Model(IOMixin, SimulationMixin):
    """
    A model object that represents a neuron model.

    The class incorporates various mixins to separate concerns while
    maintaining a flat interface.

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


    # ========================================================================
    # MECHANISMS
    # ========================================================================

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
    # PARAMETERS
    # ========================================================================

    # -----------------------------------------------------------------------
    # SEGMENT GROUPS (Where)
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
    # DISTRIBUTIONS (How)
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


    # -----------------------------------------------------------------------
    # FITTING
    # -----------------------------------------------------------------------

    def fit_distribution(self, param_name: str, segments, candidate_models=None, plot=True):
        if candidate_models is None:
            candidate_models = DEFAULT_FIT_MODELS

        from dendrotweaks.utils import mse

        values = [seg.get_param_value(param_name) for seg in segments]
        if all(np.isnan(values)):
            return None

        distances = [seg.path_distance() for seg in segments]
        distances, values = zip(*sorted(zip(distances, values)))

        best_score = float('inf')
        best_model = None
        best_params = None
        best_pred = None

        results = []

        for name, model in candidate_models.items():
            try:
                params, pred_values = model['fit'](distances, values)
                score = model.get('score', mse)(values, pred_values)
                complexity = model.get('complexity', 1)(params)
                results.append((name, score, params, complexity, pred_values))
            except Exception as e:
                warnings.warn(f"Model {name} failed to fit: {e}")

        # Sort results by score and complexity
        results.sort(key=lambda x: (np.round(x[1], 10), x[3]))

        best_model, best_score, best_params, _, best_pred = results[0]

        if plot:
            self.plot_param(param_name, show_nan=False)
            plt.plot(distances, best_pred, label=f'Best Fit: {best_model}', color='red', linestyle='--')
            plt.legend()

        return {'model': best_model, 'params': best_params, 'score': best_score}


    def _set_distribution(self, param_name, group_name, fit_result, plot=False):
        if fit_result is None:
            warnings.warn(f"No valid fit found for parameter {param_name}. Skipping distribution assignment.")
            return

        model_type = fit_result['model']
        params = fit_result['params']

        if model_type == 'poly':
            coeffs = np.array(params)
            coeffs = np.where(np.round(coeffs) == 0, coeffs, np.round(coeffs, 10))
            if len(coeffs) == 1:
                self.params[param_name][group_name] = Distribution('constant', value=coeffs[0])
            elif len(coeffs) == 2:
                self.params[param_name][group_name] = Distribution('linear', slope=coeffs[0], intercept=coeffs[1])
            else:
                self.params[param_name][group_name] = Distribution('polynomial', coeffs=coeffs.tolist())

        elif model_type == 'step':
            start, end, min_value, max_value = params
            self.params[param_name][group_name] = Distribution('step', max_value=max_value, min_value=min_value, start=start, end=end)


    # -----------------------------------------------------------------------
    # PLOTTING
    # -----------------------------------------------------------------------

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
        from dendrotweaks.utils import get_domain_color

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
        ax.axhline(y=0, color='k', linestyle='--')

        ax.set_xlabel('Path distance')
        ax.set_ylabel(param_name)
        ax.set_title(f'{param_name} distribution')


    # ========================================================================
    # MORPHOLOGY
    # ========================================================================

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
            if not all(mech_names == common_mechs
                    for mech_names in domains_to_mechs.values()):
                raise ValueError(
                    'The domains in the subtree have different mechanisms. '
                    'Please ensure that all domains in the subtree have the same mechanisms. '
                    'You may need to insert the missing mechanisms and set their conductances to 0 where they are not needed.'
                )
        elif len(domains_in_subtree) == 1:
            common_mechs = self.domains_to_mechs[domain_name].copy()
        
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
        params_to_fits = {}
        # for param_name in self.params:
        common_mechs.add('Independent')
        for mech in common_mechs:
            for param_name in self.mechs_to_params[mech]:
                fit_result = self.fit_distribution(param_name, segments=root_segs, plot=False)
                params_to_fits[param_name] = fit_result

        
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
        for param_name, fit_result in params_to_fits.items():
            self._set_distribution(param_name, group_name, fit_result, plot=True)

        # # Distribute parameters
        self.distribute_all()

        return {
            'domain_name': new_reduced_domain_name, 
            'group_name': group_name,
            'segs_to_params': segs_to_params,
            'segs_to_locs': segs_to_locs,
            'segs_to_reduced_segs': segs_to_reduced_segs,
            'reduced_segs_to_params': reduced_segs_to_params,
            'params_to_fits': params_to_fits
        }