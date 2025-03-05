import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def get_node_data(nodes):

    data = {
        'idx': [node.idx for node in nodes],
        'depth': [node.depth for node in nodes],
        'length': [node.length for node in nodes],
        'diam': [node.diam for node in nodes],
        'area': [node.area for node in nodes],
        'n_children': [len(node.children) for node in nodes]
    }

    return pd.DataFrame(data)


def calculate_section_statistics(sections, param_name=None):
    
    df = get_node_data(sections)

    depth_counts = df['depth'].value_counts().sort_index()
    stats = {
        'N_sections': len(df),
        'N_bifurcations': (df['n_children'] == 2).sum(),
        'N_terminations': (df['n_children'] == 0).sum(),
        'depth': {
            'min': df['depth'].min(),
            'max': df['depth'].max(),
            'counts': depth_counts.to_dict(),
        },
        'diam': {
            'min': np.round(df['diam'].min(), 2),
            'max': np.round(df['diam'].max(), 2),
            'mean': np.round(df['diam'].mean(), 2),
            'std': np.round(df['diam'].std(), 2)
        },
        'length': {
            'min': np.round(df['length'].min(), 2),
            'max': np.round(df['length'].max(), 2),
            'mean': np.round(df['length'].mean(), 2),
            'std': np.round(df['length'].std(), 2)
        },
        'area': {
            'min': np.round(df['area'].min(), 2),
            'max': np.round(df['area'].max(), 2),
            'mean': np.round(df['area'].mean(), 2),
            'std': np.round(df['area'].std(), 2)
        },
        'total_length': np.round(df['length'].sum(), 2),
        'total_area': np.round(df['area'].sum(), 2)
    }

    return stats


def calculate_cell_statistics(tree):

    all_sections = []
    for domain in tree.domains.values():
        all_sections.extend(domain.sections)

    return calculate_section_statistics(all_sections)


def calculate_domain_statistics(tree, domain_names=None, param_name=None):

    if domain_names is None:
        return calculate_cell_statistics(tree)
    if not isinstance(domain_names, list):
        raise ValueError("domain_names must be a list of strings")

    domains = [domain for domain in tree.domains.values() if domain.name in domain_names]

    stats = {}

    for domain in domains:
        stats[domain.name] = calculate_section_statistics(domain.sections)

    return stats
        

def calculate_segment_statistics(model, segments):

    df = model.get_node_data(segments)

    stats = {
        'N_segments': len(df),
        'N_bifurcations': (df['n_children'] == 2).sum(),
        'N_terminations': (df['n_children'] == 0).sum(),
        'diam': (np.round(df['diam'].mean(), 2), np.round(df['diam'].std(), 2), np.round(df['diam'].min(), 2), np.round(df['diam'].max(), 2)),
        'length': (np.round(df['length'].mean(), 2), np.round(df['length'].std(), 2), np.round(df['length'].min(), 2), np.round(df['length'].max(), 2)),
        'area': (np.round(df['area'].mean(), 2), np.round(df['area'].std(), 2), np.round(df['area'].min(), 2), np.round(df['area'].max(), 2)),
        'total_lenght': np.round(df['length'].sum(), 2),
        'total_area': np.round(df['area'].sum(), 2)
    }


def update_histogram(model, param_name, segments, **kwargs):
    if param not in ['diam', 'length', 'area']:
        raise ValueError(f"Invalid parameter: {param}")
    values = [seg.get_param_value(param_name) for seg in segments]
    hist, edges = np.histogram(values, **kwargs)
    return hist, edges

