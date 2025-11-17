"""
Utility functions for dendrotweaks package.
"""

import time
import numpy as np
import os
import zipfile
import urllib.request
import matplotlib.pyplot as plt


DOMAINS_TO_GROUPS = {
    'soma': 'somatic',
    'axon': 'axonal',
    'dend': 'dendritic',
    'apic': 'apical',
}

DOMAINS_TO_NEURON = {
    'soma': 'soma',
    'perisomatic': 'dend_11',
    'axon': 'axon',
    'apic': 'apic',
    'dend': 'dend',
    'basal': 'dend_31',
    'trunk': 'dend_41',
    'tuft': 'dend_42',
    'oblique': 'dend_43',
    'custom': 'dend_5',
    'reduced': 'dend_8',
    'undefined': 'dend_0',
}


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

def download_example_data(path_to_destination, include_templates=True, include_modfiles=True):
    """
    Download and extract specific folders from the DendroTweaks GitHub repository:
    - examples/                <- from examples subfolder (always included)
    - examples/Templates/      <- from src/dendrotweaks/biophys/default_templates (optional)
    - examples/Default/        <- from src/dendrotweaks/biophys/default_mod (optional)

    Parameters
    ----------
    path_to_destination : str
        The path to the destination folder where the data will be downloaded and extracted.

    include_templates : bool, optional
        If True, also extract default_templates/ into examples/Templates/.

    include_modfiles : bool, optional
        If True, also extract default_mod/ into examples/Default/.
    """
    if not os.path.exists(path_to_destination):
        os.makedirs(path_to_destination)

    repo_url = "https://github.com/Poirazi-Lab/DendroTweaks/archive/refs/heads/main.zip"
    zip_path = os.path.join(path_to_destination, "dendrotweaks_repo.zip")

    print(f"Downloading data from {repo_url}...")
    urllib.request.urlretrieve(repo_url, zip_path)

    print(f"Extracting relevant folders to {path_to_destination}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for member in zip_ref.namelist():
            target_path = None

            # === Always extract examples/ folder ===
            if member.startswith("DendroTweaks-main/examples/"):
                rel_path = os.path.relpath(member, "DendroTweaks-main/examples")
                target_path = os.path.join(path_to_destination, rel_path)

            # === Optionally extract Templates/ folder ===
            elif include_templates and member.startswith("DendroTweaks-main/src/dendrotweaks/biophys/default_templates/"):
                rel_path = os.path.relpath(member, "DendroTweaks-main/src/dendrotweaks/biophys/default_templates")
                target_path = os.path.join(path_to_destination, "Templates", rel_path)

            # === Optionally extract Default/ folder ===
            elif include_modfiles and member.startswith("DendroTweaks-main/src/dendrotweaks/biophys/default_mod/"):
                rel_path = os.path.relpath(member, "DendroTweaks-main/src/dendrotweaks/biophys/default_mod")
                target_path = os.path.join(path_to_destination, "Default", rel_path)

            if target_path:
                if member.endswith('/'):
                    os.makedirs(target_path, exist_ok=True)
                else:
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    with zip_ref.open(member) as source, open(target_path, 'wb') as target:
                        target.write(source.read())

    os.remove(zip_path)
    print(f"Data downloaded and extracted successfully to {path_to_destination}/.")

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

def mse(y_true, y_pred):
            return np.mean((np.array(y_true) - np.array(y_pred)) ** 2)

def poly_fit(x, y, max_degree=6, tolerance=1e-6):
    """
    Fit a polynomial to the data and return the coefficients and predicted values.
    """
    for degree in range(max_degree + 1):
        coeffs = np.polyfit(x, y, degree)
        y_pred = np.polyval(coeffs, x)
        if np.all(np.abs(np.array(y) - y_pred) < tolerance):
            break
    return coeffs, y_pred

def step_fit(x, y):
    """
    Fit a single step function with variable-width transition zone.
    Returns (high_val, low_val, start, end), and predicted y-values.
    """
    x = np.array(x)
    y = np.array(y)

    sort_idx = np.argsort(x)
    x = x[sort_idx]
    y = y[sort_idx]

    best_mse = float('inf')
    best_params = None
    best_pred = None

    n = len(x)
    for i in range(n - 1):
        for j in range(i + 1, n):
            start = x[i]
            end = x[j]
            inside = (x > start) & (x < end)
            outside = ~inside

            if not np.any(inside) or not np.any(outside):
                continue

            high_val = np.nanmean(y[inside])
            low_val = np.nanmean(y[outside])

            pred = np.where(inside, high_val, low_val)
            score = mse(y, pred)

            if score < best_mse:
                best_mse = score
                best_params = (start, end, low_val, high_val)
                best_pred = pred

    return best_params, best_pred

DEFAULT_FIT_MODELS = {
    'poly': {
        'fit': poly_fit,
        'score': mse,
        'complexity': lambda coeffs: len(coeffs) - 1  # degree of polynomial
    },
    'step': {
        'fit': step_fit,
        'score': mse,
        'complexity': lambda params: 4
    }
}