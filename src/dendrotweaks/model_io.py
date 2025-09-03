# Imports
import os
import json
from collections import defaultdict

import jinja2
import pandas as pd

# DendroTweaks imports
from dendrotweaks import __version__
from dendrotweaks.morphology.io import create_point_tree, create_section_tree, create_segment_tree
from dendrotweaks.biophys.io import create_channel, standardize_channel
from dendrotweaks.biophys.groups import SegmentGroup
from dendrotweaks.biophys.distributions import Distribution
from dendrotweaks.biophys.mechanisms import LeakChannel, CaDynamics
from dendrotweaks.biophys.mechanisms import FallbackChannel
from dendrotweaks.stimuli import Population
from dendrotweaks.utils import DOMAIN_TO_GROUP, DOMAINS_TO_NEURON

# Warnings configuration
import warnings

def custom_warning_formatter(message, category, filename, lineno, file=None, line=None):
    return f"WARNING: {message}\n({os.path.basename(filename)}, line {lineno})\n"

warnings.formatwarning = custom_warning_formatter

class IOMixin():
    """
    Mixin for the Model class to handle file I/O operations.
    """

    # -----------------------------------------------------------------------
    # DIRECTORY MANAGEMENT
    # -----------------------------------------------------------------------

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


    # -----------------------------------------------------------------------
    # MORPHOLOGY I/O
    # -----------------------------------------------------------------------

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
        path_to_swc_file = self.path_manager.get_abs_path(f'morphology/{file_name}.swc')
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


    def export_morphology(self, file_name):
        """
        Write the SWC tree to an SWC file.

        Parameters
        ----------
        version : str, optional
            The version of the morphology appended to the morphology name.
        """
        path_to_file = self.path_manager.get_abs_path(f'morphology/{file_name}')
        
        self.point_tree.to_swc(path_to_file)


    # =======================================================================
    # BIOPHYSICS I/O
    # ========================================================================

    # -----------------------------------------------------------------------
    # MECHANISMS
    # -----------------------------------------------------------------------

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
        try:
            mech = create_channel(**paths)
        except NotImplementedError as e:
            if "KINETIC" in str(e):
                warnings.warn(
                    f"Could not import the '{mechanism_name}' channel because it uses an unsupported KINETIC block."
                    " A minimal fallback channel will be created for simulation only, supporting only the 'gbar' parameter."
                )
                mech = FallbackChannel(mechanism_name)
            else:
                raise
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
        path_to_mod_file = self.path_manager.get_abs_path(
            f"{dir_name}/{mechanism_name}.mod"
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


    # -----------------------------------------------------------------------
    # CONFIGURATION
    # -----------------------------------------------------------------------

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
                'author': os.getlogin(),
                'software': f'dendrotweaks v{__version__}',
                'platform': os.uname().sysname,
                'comments': 'Automatically generated by DendroTweaks.',
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
        
        path_to_json = self.path_manager.get_abs_path(f'biophys/{file_name}.json', create_dirs=True)
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
        

        path_to_json = self.path_manager.get_abs_path(f'biophys/{file_name}.json')

        with open(path_to_json, 'r') as f:
            data = json.load(f)

        for mech_name in {mech for mechs in data['domains'].values() for mech in mechs}:
            if mech_name in ['Leak', 'CaDyn', 'Independent']:
                continue
            self.add_mechanism(mech_name, dir_name='mod', recompile=recompile)            

        self.from_dict(data)


    # =======================================================================
    # STIMULI I/O
    # ========================================================================

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
                'author': os.getlogin(),
                'software': f'dendrotweaks v{__version__}',
                'platform': os.uname().sysname,
                'comments': 'Automatically generated by DendroTweaks.',
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

    def _write_csv(self, df, path_to_csv):
        """
        Write a DataFrame to a CSV file.
        """
        if 'idx' in df.columns:
            df['idx'] = df['idx'].astype(int)
        if 'sec_idx' in df.columns:
            df['sec_idx'] = df['sec_idx'].astype(int)
        df.to_csv(path_to_csv, index=False)



    def _recordings_to_csv(self, path_to_csv=None):
        """
        Write the recordings to a CSV file.
        """
        rec_data = {
            'idx': [],
            'sec_idx': [],
            'loc': [],
        }

        for var, recs in self.simulator.recordings.items():
            rec_data['idx'].extend([i for i in range(len(recs))])
            rec_data['sec_idx'].extend([seg._section.idx for seg in recs])
            rec_data['loc'].extend([seg.x for seg in recs])

        df = pd.DataFrame(rec_data)
        if path_to_csv: self._write_csv(df, path_to_csv)
        return df


    def _iclamps_to_csv(self, path_to_csv=None):
        """
        Write the IClamp data to a CSV file.
        """
        iclamp_data = {
            'idx': [i for i in range(len(self.iclamps))],
            'sec_idx': [seg._section.idx for seg in self.iclamps],
            'loc': [seg.x for seg in self.iclamps],
        }
        df = pd.DataFrame(iclamp_data)
        if path_to_csv: self._write_csv(df, path_to_csv)
        return df
        

    def _synapses_to_csv(self, path_to_csv=None):
        """
        Write the synapse data to a CSV file.
        """
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

        df = pd.DataFrame(synapses_data)
        if path_to_csv: self._write_csv(df, path_to_csv)
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
        path_to_json = self.path_manager.get_abs_path(
            f'stimuli/{file_name}/config.json', 
            create_dirs=True
        )

        data = self.stimuli_to_dict()

        if not kwargs.get('indent'):
            kwargs['indent'] = 4
        with open(path_to_json, 'w') as f:
            json.dump(data, f, **kwargs)

        path_to_recordings_csv = self.path_manager.get_abs_path(f'stimuli/{file_name}/recordings.csv')
        path_to_iclamps_csv = self.path_manager.get_abs_path(f'stimuli/{file_name}/iclamps.csv')
        path_to_synapses_csv = self.path_manager.get_abs_path(f'stimuli/{file_name}/synapses.csv')

        self._recordings_to_csv(path_to_recordings_csv)
        self._iclamps_to_csv(path_to_iclamps_csv)
        self._synapses_to_csv(path_to_synapses_csv)


    def load_stimuli(self, file_name):
        """
        Load the stimuli from a JSON file.

        Parameters
        ----------
        file_name : str
            The name of the file to read from.
        """
        
        path_to_json = self.path_manager.get_abs_path(f'stimuli/{file_name}/config.json')
        path_to_recordings_csv = self.path_manager.get_abs_path(f'stimuli/{file_name}/recordings.csv')
        path_to_iclamps_csv = self.path_manager.get_abs_path(f'stimuli/{file_name}/iclamps.csv')
        path_to_synapses_csv = self.path_manager.get_abs_path(f'stimuli/{file_name}/synapses.csv')
        
        with open(path_to_json, 'r') as f:
            data = json.load(f)

        self.simulator.from_dict(data['simulation'])

        # Clear all stimuli and recordings
        self.remove_all_stimuli()
        self.remove_all_recordings()

        # IClamps -----------------------------------------------------------
        if path_to_iclamps_csv:

            df_iclamps = pd.read_csv(path_to_iclamps_csv)

            for row in df_iclamps.itertuples(index=False):
                self.add_iclamp(
                self.sec_tree.sections[row.sec_idx], 
                row.loc,
                data['stimuli']['iclamps'][row.idx]['amp'],
                data['stimuli']['iclamps'][row.idx]['delay'],
                data['stimuli']['iclamps'][row.idx]['dur']
                )

        # Populations -------------------------------------------------------

        if path_to_synapses_csv:

            df_all_syn = pd.read_csv(path_to_synapses_csv)

            syn_types = ['AMPA', 'NMDA', 'AMPA_NMDA', 'GABAa']

            for syn_type in syn_types:

                df_syn = df_all_syn[df_all_syn['type'] == syn_type]
        
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

        if path_to_recordings_csv:

            df_recs = pd.read_csv(path_to_recordings_csv)

            for row in df_recs.itertuples(index=False):
                var = data['stimuli']['recordings'][row.idx]['var']
                self.add_recording(
                self.sec_tree.sections[row.sec_idx], row.loc, var
                )

    # ========================================================================
    # EXPORT TO PLAIN SIMULATOR CODE
    # ========================================================================

    def export_to_NEURON(self, file_name, include_kinetic_params=True):
        """
        Export the model to a python file with plain NEURON code to reproduce the model.

        Parameters
        ----------
        file_name : str
            The name of the file to write to.
        """

        params_to_valid_domains = get_params_to_valid_domains(self)
        params = self.params if include_kinetic_params else filter_params(self)
        path_to_template = self.path_manager.get_abs_path('templates/NEURON_template.py', create_dirs=True)

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


    def export_to_Jaxley(self, file_name):
        raise NotImplementedError("Export to plain Jaxley code is not implemented yet.")


# =======================================================================
# HELPER FUNCTIONS
# =======================================================================

def filter_params(model):
    """
    Filter out kinetic parameters from the model.

    Parameters
    ----------
    model : Model
        The model to filter.

    Returns
    -------
    Model
        The model with kinetic parameters filtered out.
    """
    filtered_params = {
        param: {
            group_name: distribution 
            for group_name, distribution in distributions.items() 
            if param in list(model.conductances.keys()) + ['cm', 'Ra', 'ena', 'ek', 'eca']} 
            for param, distributions in model.params.items()}
    return filtered_params


def get_neuron_domain(domain_name):
    base_domain, _, idx = domain_name.partition('_')
    if base_domain in ['reduced', 'custom'] and idx.isdigit():
        return f'{DOMAINS_TO_NEURON[base_domain]}{idx}'
    return DOMAINS_TO_NEURON.get(base_domain, 'dend_0')

def render_template(path_to_template, context):
    """
    Render a Jinja2 template.

    Parameters
    ----------
    path_to_template : str
        The path to the Jinja2 template.
    context : dict
        The context to render the template with.
    """
    with open(path_to_template, 'r') as f:
        template = jinja2.Template(f.read())
    return template.render(context)


def get_params_to_valid_domains(model):
    
    params_to_valid_domains = defaultdict(dict)

    for param, mech in model.params_to_mechs.items():
        for group_name, distribution in model.params[param].items():
            group = model.groups[group_name]
            valid_domains = [get_neuron_domain(domain) for domain in group.domains if mech == 'Independent' or mech in model.domains_to_mechs[domain]]
            params_to_valid_domains[param][group_name] = valid_domains

    return dict(params_to_valid_domains)