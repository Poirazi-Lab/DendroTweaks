"""
Utility functions for dendrotweaks package.
"""

import time
import numpy as np
import os
import zipfile
import urllib.request

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

def get_domain_color(domain):
    base_domain = domain.split('_')[0]
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
    Download the examples from the dendrotweaks GitHub repository.

    Parameters
    ----------
    path_to_destination : str
        The path to the destination folder where the examples will be downloaded.
    """
    if not os.path.exists(path_to_destination):
        os.makedirs(path_to_destination)

    repo_url = "https://github.com/Poirazi-Lab/dendrotweaks/archive/refs/heads/main.zip"
    zip_path = os.path.join(path_to_destination, "examples.zip")

    print(f"Downloading examples from {repo_url}...")
    urllib.request.urlretrieve(repo_url, zip_path)

    print(f"Extracting examples to {path_to_destination}")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(path_to_destination)

    os.remove(zip_path)  # Clean up the zip file
    print(f"Examples downloaded successfully to {path_to_destination}/.")
