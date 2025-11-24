import json
import os
import pandas as pd
import numpy as np
from dendrotweaks import __version__
from dendrotweaks.morphology.io.reader import SWCReader
from dendrotweaks.morphology.io.factories import create_point_tree, create_section_tree


# ============================================================================
# SECTION MAPPING
# ============================================================================

def _legacy_sort_key(node):
    """
    Sorting key function for legacy ordering.
    Legacy version sorted by (type_idx, bifurcation_count).
    """
    return (node.type_idx, sum(1 for n in node.subtree if len(n.children) > 1))


def _new_sort_key(node):
    """
    Sorting key function for new ordering.
    New version sorts only by bifurcation_count (removed type_idx).
    """
    return sum(1 for n in node.subtree if len(n.children) > 1)


def _apply_sort_to_tree(tree, sort_key_func):
    """
    Apply custom sorting to a tree's children.
    
    Parameters
    ----------
    tree : Tree
        The tree to sort.
    sort_key_func : callable
        Function that takes a node and returns a sort key.
    """
    for node in tree._nodes:
        node.children = sorted(node.children, key=sort_key_func)


def _create_tree_with_sort(df, use_legacy_sort=False):
    """
    Create and sort a tree with specified sorting behavior.
    
    Parameters
    ----------
    df : DataFrame
        The morphology data.
    use_legacy_sort : bool
        If True, use legacy sorting (type_idx, bifurcations).
        If False, use new sorting (bifurcations only).
    
    Returns
    -------
    SectionTree
        The sorted section tree.
    """
    point_tree = create_point_tree(df)
    point_tree.remove_overlaps()
    point_tree.extend_sections()
    
    # Apply appropriate sorting to point tree
    if use_legacy_sort:
        _apply_sort_to_tree(point_tree, _legacy_sort_key)
    else:
        _apply_sort_to_tree(point_tree, _new_sort_key)
    
    # Reassign indices after custom child sorting
    point_tree.sort(sort_children=False, force=True)
    
    sec_tree = create_section_tree(point_tree)
    
    # Apply appropriate sorting to section tree
    if use_legacy_sort:
        _apply_sort_to_tree(sec_tree, _legacy_sort_key)
    else:
        _apply_sort_to_tree(sec_tree, _new_sort_key)
    
    # Reassign indices after custom child sorting
    sec_tree.sort(sort_children=False, force=True)
    
    return sec_tree


def _sections_match(sec_old, sec_new):
    """Check if two sections have matching coordinates."""
    return all(
        np.allclose(pt_old.x, pt_new.x) and
        np.allclose(pt_old.y, pt_new.y) and
        np.allclose(pt_old.z, pt_new.z)
        for pt_old, pt_new in zip(sec_old.points, sec_new.points)
    )


def _map_sections(old_sec_tree, new_sec_tree):
    """Map section indices from old tree to new tree."""
    old_to_new_idx = {}
    
    for sec_old in old_sec_tree.sections:
        for sec_new in new_sec_tree.sections:
            if _sections_match(sec_old, sec_new):
                old_to_new_idx[sec_old.idx] = sec_new.idx
                break
    
    return old_to_new_idx


def _obtain_section_mapping(path_manager, morphology_name):
    """
    Obtain mapping from legacy section indices to new section indices.
    
    The mapping accounts for the difference in sorting behavior:
    - Legacy: sorts children by (type_idx, bifurcation_count)
    - New: sorts children by bifurcation_count only
    
    Parameters
    ----------
    path_manager : PathManager
        Path manager for file access.
    morphology_name : str
        Name of the morphology file.
    
    Returns
    -------
    dict
        Mapping from old section indices to new section indices.
    """
    reader = SWCReader()
    df = reader.read_file(path_manager.get_abs_path(f'morphology/{morphology_name}.swc'))
    
    # Create trees with different sorting strategies
    legacy_sec_tree = _create_tree_with_sort(df, use_legacy_sort=True)
    new_sec_tree = _create_tree_with_sort(df, use_legacy_sort=False)
    
    return _map_sections(legacy_sec_tree, new_sec_tree)


def _remap_csv_section_indices(path_manager, protocol_name, mapping):
    """
    Update sec_idx column in all CSV files based on provided mapping.
    
    Parameters
    ----------
    path_manager : PathManager
        Path manager for file access.
    protocol_name : str
        Name of the protocol folder.
    mapping : dict
        Mapping from old to new section indices.
    """
    protocol_path = path_manager.get_abs_path(f'stimuli/{protocol_name}')
    
    for filename in os.listdir(protocol_path):
        if not filename.endswith('.csv'):
            continue
        
        file_path = os.path.join(protocol_path, filename)
        df = pd.read_csv(file_path)
        
        if 'sec_idx' in df.columns:
            df['sec_idx'] = df['sec_idx'].map(mapping)
            df.to_csv(file_path, index=False)


# ============================================================================
# FORMAT CONVERSION
# ============================================================================

def _read_legacy_files(path_manager, protocol_name):
    """Read legacy JSON and CSV files."""
    path_to_json = path_manager.get_abs_path(f'stimuli/{protocol_name}.json')
    path_to_csv = path_manager.get_abs_path(f'stimuli/{protocol_name}.csv')
    
    with open(path_to_json, 'r') as f:
        legacy_data = json.load(f)
    
    df_stimuli = pd.read_csv(path_to_csv)
    
    return legacy_data, df_stimuli


def _build_metadata(model_name):
    """Create metadata dictionary for new format."""
    return {
        'name': model_name,
        'author': os.getlogin(),
        'software': f'dendrotweaks v{__version__}',
        'platform': os.uname().sysname,
        'comments': 'Converted from legacy format by DendroTweaks.',
    }


def _convert_populations(legacy_data, df_stimuli):
    """Convert population data from legacy to new format."""
    syn_types = ['AMPA', 'NMDA', 'AMPA_NMDA', 'GABAa']
    populations = {}
    
    pop_idx = 0
    for syn_type in syn_types:
        if syn_type not in legacy_data['stimuli']['populations']:
            continue
        
        for i, pop_data in enumerate(legacy_data['stimuli']['populations'][syn_type]):
            pop_name = f"{syn_type}_{i}"
            populations[pop_name] = {
                'idx': pop_idx,
                'N': pop_data['N'],
                'syn_type': syn_type,
                'kinetic_params': pop_data['kinetic_params'],
                'input_params': pop_data['input_params']
            }
            pop_idx += 1
    
    return populations


def _convert_recordings(legacy_data, df_stimuli):
    """Convert recordings from legacy to new format."""
    df_recs = df_stimuli[df_stimuli['type'] == 'rec'].reset_index(drop=True)
    
    if df_recs.empty:
        return None
    
    return pd.DataFrame({
        'sec_idx': df_recs['sec_idx'].astype(int),
        'loc': df_recs['loc'],
        'var': [legacy_data['stimuli']['recordings'][idx]['var'] 
                for idx in df_recs['idx']]
    })


def _convert_iclamps(legacy_data, df_stimuli):
    """Convert IClamps from legacy to new format."""
    df_iclamps = df_stimuli[df_stimuli['type'] == 'iclamp'].reset_index(drop=True)
    
    if df_iclamps.empty:
        return None
    
    iclamp_params = legacy_data['stimuli']['iclamps']
    
    return pd.DataFrame({
        'sec_idx': df_iclamps['sec_idx'].astype(int),
        'loc': df_iclamps['loc'],
        'amp': [iclamp_params[idx]['amp'] for idx in df_iclamps['idx']],
        'delay': [iclamp_params[idx]['delay'] for idx in df_iclamps['idx']],
        'dur': [iclamp_params[idx]['dur'] for idx in df_iclamps['idx']]
    })


def _convert_synapses(legacy_data, df_stimuli):
    """Convert synapses from legacy to new format."""
    syn_types = ['AMPA', 'NMDA', 'AMPA_NMDA', 'GABAa']
    synapses_data = {'sec_idx': [], 'loc': [], 'pop_idx': []}
    
    pop_idx = 0
    for syn_type in syn_types:
        if syn_type not in legacy_data['stimuli']['populations']:
            continue
        
        df_syn = df_stimuli[df_stimuli['type'] == syn_type]
        num_pops = len(legacy_data['stimuli']['populations'][syn_type])
        
        for i in range(num_pops):
            df_pop = df_syn[df_syn['idx'] == i]
            
            synapses_data['sec_idx'].extend(df_pop['sec_idx'].astype(int).tolist())
            synapses_data['loc'].extend(df_pop['loc'].tolist())
            synapses_data['pop_idx'].extend([pop_idx] * len(df_pop))
            
            pop_idx += 1
    
    # sort by sec_idx and loc and pop_idx
    if synapses_data['sec_idx']:
        sort_indices = np.lexsort((synapses_data['loc'], synapses_data['sec_idx'], synapses_data['pop_idx']))
        synapses_data = {
            key: [synapses_data[key][i] for i in sort_indices]
            for key in synapses_data
        }

    return pd.DataFrame(synapses_data) if synapses_data['sec_idx'] else None


def _write_json(data, path_manager, file_name):
    """Write JSON configuration file."""
    path = path_manager.get_abs_path(
        f'stimuli/{file_name}/config.json',
        create_dirs=True
    )
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)
    return path


def _write_csv(df, path_manager, file_name, csv_type):
    """Write CSV file if dataframe is not None."""
    if df is None:
        return None
    
    path = path_manager.get_abs_path(f'stimuli/{file_name}/{csv_type}.csv')
    df.to_csv(path, index=False)
    return path


def _print_summary(protocol_name, new_file_name, json_path, populations, 
                   df_recordings, df_iclamps, df_synapses):
    """Print conversion summary."""
    print()
    print(f"Conversion complete: {protocol_name} -> {new_file_name}")
    print(f"  - Config: {json_path}")
    print(f"  - Populations: {len(populations)}")
    print(f"  - Recordings: {len(df_recordings) if df_recordings is not None else 0}")
    print(f"  - IClamps: {len(df_iclamps) if df_iclamps is not None else 0}")
    print(f"  - Synapses: {len(df_synapses) if df_synapses is not None else 0}")


def convert_legacy_stimuli(path_manager, protocol_name, morphology_name=None, 
                           new_file_name=None, d_lambda=0.1):
    """
    Convert stimuli from legacy JSON and CSV format to new format.
    
    Parameters
    ----------
    path_manager : PathManager
        The path manager instance for handling file paths.
    protocol_name : str
        The name of the legacy protocol file to read from.
    morphology_name : str, optional
        The name of the morphology file for section index remapping.
        If provided, section indices will be remapped from legacy to new format.
    new_file_name : str, optional
        The name for the new format files. If None, uses protocol_name.
    """
    new_file_name = new_file_name or protocol_name
    
    # Read legacy files
    legacy_data, df_stimuli = _read_legacy_files(path_manager, protocol_name)
    
    # Convert data structures
    populations = _convert_populations(legacy_data, df_stimuli)
    df_recordings = _convert_recordings(legacy_data, df_stimuli)
    df_iclamps = _convert_iclamps(legacy_data, df_stimuli)
    df_synapses = _convert_synapses(legacy_data, df_stimuli)
    
    model_name = legacy_data.get('metadata', {}).get('name', 'unknown')

    # Build new JSON structure
    new_data = {
        'metadata': _build_metadata(model_name),
        'simulation': legacy_data['simulation'],
        'stimuli': {'populations': populations}
    }
    new_data['simulation']['d_lambda'] = d_lambda
    
    # Write new files
    json_path = _write_json(new_data, path_manager, new_file_name)
    _write_csv(df_recordings, path_manager, new_file_name, 'recordings')
    _write_csv(df_iclamps, path_manager, new_file_name, 'iclamps')
    _write_csv(df_synapses, path_manager, new_file_name, 'synapses')
    
    # Remap section indices if morphology provided
    if morphology_name:
        print(f"Remapping section indices using {morphology_name}...")
        mapping = _obtain_section_mapping(path_manager, morphology_name)
        _remap_csv_section_indices(path_manager, new_file_name, mapping)
        print(f"  - Remapped {len(mapping)} sections")
    
    # Print summary
    _print_summary(protocol_name, new_file_name, json_path, populations,
                   df_recordings, df_iclamps, df_synapses)