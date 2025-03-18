"""
Utility functions for dendrotweaks package.
"""

import time
import numpy as np
import os
import zipfile
import urllib.request
import matplotlib.pyplot as plt

SWC_ID_TO_DOMAIN = {
    0: 'undefined',
    1: 'soma',
    11: 'perisomatic',
    2: 'axon',
    3: 'dend',
    31: 'basal',
    4: 'apic',
    41: 'trunk',
    42: 'tuft',
    43: 'oblique',
    5: 'custom',
    6: 'neurite',
    7: 'glia',
    8: 'reduced',
}

DOMAIN_TO_SWC_ID = {
    v: k for k, v in SWC_ID_TO_DOMAIN.items()
}

def get_swc_idx(domain_name):
    base_domain, _, idx = domain_name.partition('_')
    if base_domain == 'reduced':
        return int(f'8{idx}')
    elif base_domain == 'custom':
        return int(f'5{idx}')
    return DOMAIN_TO_SWC_ID.get(base_domain, 0)

def get_domain_name(swc_idx):
    if str(swc_idx).startswith('8'):
        return 'reduced_' + str(swc_idx)[1:]
    elif str(swc_idx).startswith('5'):
        return 'custom_' + str(swc_idx)[1:]
    return SWC_ID_TO_DOMAIN.get(swc_idx, 'undefined')

DOMAINS_TO_COLORS = {
    'soma': '#E69F00',
    'apic': '#0072B2',
    'dend': '#019E73',
    'basal': '#31A354',
    'axon': '#F0E442',
    'trunk': '#56B4E9',
    'tuft': '#A55194',
    'oblique': '#8C564B',
    'perisomatic': '#D55E00',
    'custom': '#D62728',
    'reduced': '#E377C2',
    'undefined': '#7F7F7F',
}

def get_domain_color(domain_name):
    base_domain, _, idx = domain_name.partition('_')
    return DOMAINS_TO_COLORS.get(base_domain, '#7F7F7F')



def timeit(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"  Elapsed time: {round(end-start, 3)} seconds")
        return result
    return wrapper


def calculate_lambda_f(distances, diameters, Ra=35.4, Cm=1, frequency=100):
    """
    Calculate the frequency-dependent length constant (lambda_f) according to NEURON's implementation,
    using 3D point data for accurate representation of varying diameter frusta.
    
    Args:
        distances (list/array): Cumulative euclidean distances between 3D points along the section from 0 to section length
        diameters (list/array): Corresponding diameters at each position in micrometers
        Ra (float): Axial resistance in ohm*cm
        Cm (float): Specific membrane capacitance in µF/cm²
        frequency (float): Frequency in Hz
    
    Returns:
        float: Lambda_f in micrometers
    """
    if len(distances) < 2 or len(diameters) < 2:
        raise ValueError("At least 2 points are required for 3D calculation")
    
    if len(distances) != len(diameters):
        raise ValueError("distances and diameters must have the same length")
    
    # Initialize variables
    lam = 0
    section_L = distances[-1]
    
    # Calculate the contribution of each frustum
    for i in range(1, len(distances)):
        # Frustum length
        frustum_length = distances[i] - distances[i-1]
        # Average of diameters at endpoints
        d1 = diameters[i-1]
        d2 = diameters[i]
        
        # Add frustum contribution to lambda calculation
        lam += frustum_length / np.sqrt(d1 + d2)
    
    # Apply the frequency-dependent factor
    lam *= np.sqrt(2) * 1e-5 * np.sqrt(4 * np.pi * frequency * Ra * Cm)
    
    # Return section_L/lam (electrotonic length of the section)
    return section_L / lam

if (__name__ == '__main__'):
    print('Executing as standalone script')


def dynamic_import(module_name, class_name):
    """
    Dynamically import a class from a module.

    Parameters
    ----------
    module_name : str
        Name of the module to import.
    class_name : str
        Name of the class to import.
    """

    from importlib import import_module

    import sys
    sys.path.append('app/src')
    print(f"Importing class {class_name} from module {module_name}.py")
    module = import_module(module_name)
    return getattr(module, class_name)


def list_folders(path_to_folder):
    folders = [f for f in os.listdir(path_to_folder)
            if os.path.isdir(os.path.join(path_to_folder, f))]
    sorted_folders = sorted(folders, key=lambda x: x.lower())
    return sorted_folders

    
def list_files(path_to_folder, extension):
    files = [f for f in os.listdir(path_to_folder)
            if f.endswith(extension)]
    return files


def write_file(content: str, path_to_file: str, verbose: bool = True) -> None:
    """
    Write content to a file.

    Parameters
    ----------
    content : str
        The content to write to the file.
    path_to_file : str
        The path to the file.
    verbose : bool, optional
        Whether to print a message after writing the file. The default is True.
    """
    if not os.path.exists(os.path.dirname(path_to_file)):
        os.makedirs(os.path.dirname(path_to_file))
    with open(path_to_file, 'w') as f:
        f.write(content)
    print(f"Saved content to {path_to_file}")


def read_file(path_to_file):
    with open(path_to_file, 'r') as f:
        content = f.read()
    return content


def download_example_data(path_to_destination):
    """
    Download the examples subfolder from the DendroTweaks GitHub repository.

    Parameters
    ----------
    path_to_destination : str
        The path to the destination folder where the examples will be downloaded.
    """
    if not os.path.exists(path_to_destination):
        os.makedirs(path_to_destination)

    repo_url = "https://github.com/Poirazi-Lab/DendroTweaks/archive/refs/heads/main.zip"
    zip_path = os.path.join(path_to_destination, "examples.zip")

    print(f"Downloading examples from {repo_url}...")
    urllib.request.urlretrieve(repo_url, zip_path)

    print(f"Extracting examples to {path_to_destination}")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for member in zip_ref.namelist():
            if member.startswith("DendroTweaks-main/examples/"):
                # Extract the file with the correct path
                member_path = os.path.relpath(member, "DendroTweaks-main/examples")
                target_path = os.path.join(path_to_destination, member_path)
                if member.endswith('/'):
                    os.makedirs(target_path, exist_ok=True)
                else:
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    with zip_ref.open(member) as source, open(target_path, 'wb') as target:
                        target.write(source.read())

    os.remove(zip_path)  # Clean up the zip file
    print(f"Examples downloaded successfully to {path_to_destination}/.")



def apply_dark_theme():
    """
    Apply a dark theme to matplotlib plots.
    """
    # dark theme
    plt.style.use('dark_background')

    # customize the style
    plt.rcParams.update({
        'figure.facecolor': '#131416',
        'axes.facecolor': '#131416',
        'axes.edgecolor': 'white',
        'axes.labelcolor': 'white',
        'xtick.color': 'white',
        'ytick.color': 'white',
        'text.color': 'white',
        'axes.prop_cycle': plt.cycler(color=plt.cm.tab10.colors),  # use standard matplotlib colors
    })