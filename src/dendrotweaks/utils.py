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
    'tuft': '#A55194', #'#9467BD',
    'oblique': '#8C564B',
    'perisomatic': '#D55E00',
    # 'custom': '#BDBD22',
    'custom': '#D62728',
    'custom2': '#E377C2',
    'undefined': '#7F7F7F',
}



def timeit(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"  Elapsed time: {round(end-start, 3)} seconds")
        return result
    return wrapper


import numpy as np

def calculate_lambda_f(diameter, Ra, Cm, frequency=100):
    """
    Calculate the characteristic length constant (lambda_f) at which an e-fold (1/e) attenuation
    of voltage occurs along a neuronal cable, given the properties of the cable and signal frequency.
    
    Args:
        diameter (float): Diameter of the neuronal segment in micrometers (µm).
        Ra (float): Axial (internal) resistance in ohm*cm.
        Cm (float): Membrane capacitance per unit area in microfarads per square centimeter (µF/cm²).
        frequency (float): Frequency of the signal in hertz (Hz). Default is 100 Hz.
    
    Returns:
        float: The length constant (lambda_f) in micrometers (µm) at which voltage attenuation 
               reaches approximately 37% of its initial value.

    Notes:
        - This formula is valid in the high-frequency approximation, where the membrane resistance (Rm) 
          can be ignored (e.g., for high-frequency signals where capacitive effects dominate).

    References:
        - Hines & Carnevale (2001) NEURON: A Tool for Neuroscientists.
    """
    # Convert diameter from micrometers to centimeters
    diameter_cm = diameter * 1e-4  # 1 µm = 1e-4 cm
    
    # Ensure input values are positive
    if diameter_cm <= 0 or Ra <= 0 or Cm <= 0 or frequency <= 0:
        raise ValueError("All input values must be positive and non-zero.")
    
    # Calculate lambda_f using the formula in centimeters
    lambda_f_cm = 0.5 * np.sqrt(diameter_cm / (np.pi * frequency * Ra * Cm))
    
    # Convert the result back to micrometers and apply a factor of 1000 for scaling
    lambda_f_um = lambda_f_cm * 1e4 * 1000  # Adjust by factor of 1000 to match NEURON's output
    
    return lambda_f_um


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
