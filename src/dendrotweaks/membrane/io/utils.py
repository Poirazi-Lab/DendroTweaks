import os
import sys
from typing import List, Tuple


from dendrotweaks.membrane.io.converter import MODFileConverter
from dendrotweaks.membrane.io.code_generators import NMODLCodeGenerator
from dendrotweaks.membrane.mechanisms import Mechanism, IonChannel, StandardIonChannel


def create_channel(path_to_mod_file: str,
                   path_to_python_file: str,
                   path_to_python_template: str,
                   verbose: bool = False) -> IonChannel:
    """
    Creates an ion channel from a .mod file.

    Parameters
    ----------
    path_to_mod_file : str
        The path to the .mod file.
    path_to_python_file : str
        The path to the Python file.
    path_to_python_template : str
        The path to the Python template file.
    verbose : bool, optional
        Whether to print verbose output.
    """
    # Convert mod to python
    converter = MODFileConverter()
    converter.convert(path_to_mod_file, 
                      path_to_python_file, 
                      path_to_python_template,
                      verbose=verbose)

    # Import and instantiate the channel
    class_name = os.path.basename(path_to_python_file).replace('.py', '')
    module_name = class_name
    package_path = os.path.dirname(path_to_python_file)
    
    if package_path not in sys.path:
        sys.path.append(package_path)
    
    # Dynamic import
    from importlib import import_module
    module = import_module(module_name)
    ChannelClass = getattr(module, class_name)
    
    return ChannelClass()


def standardize_channel(channel: IonChannel, 
                        path_to_mod_template: str = None,
                        path_to_standard_mod_file: str = None) -> StandardIonChannel:
    """
    Standardize a channel and optionally generate a MOD file.

    Parameters
    ----------
    channel : IonChannel
        The channel to standardize.
    path_to_mod_template : str, optional
        The path to the .mod template file, if a MOD file should be generated.
    path_to_standard_mod_file : str, optional
        The path to save the standardized .mod file, if a MOD file should be generated.

    Returns
    -------
    StandardIonChannel
        A standardized version of the input channel.

    Note
    ----
    Temperature-dependence is taken into account by performing
    a fit to the data at the temperature specified in the parameters
    of the original channel model.
    """
    standard_channel = StandardIonChannel(name=channel.name, 
                                          state_powers=channel._state_powers, 
                                          ion=channel.ion)

    standard_channel.params.update({'q10': channel.params.get('q10'),
                                    'temp': channel.params.get('temp')})

    fit_temperature = channel.params.get('temp') or 23

    standard_channel.set_tadj(fit_temperature)
    # Fit the standard channel to the data
    data = channel.get_data(temperature=fit_temperature)
    standard_channel.fit(data)

    # Optionally generate a MOD file
    
    generator = NMODLCodeGenerator()
    content = generator.generate(standard_channel, path_to_mod_template)
    generator.write_file(path_to_standard_mod_file)

    return standard_channel


def create_standard_channel(path_to_mod_file: str,
                           path_to_python_file: str,
                           path_to_python_template: str,
                           path_to_mod_template: str,
                           path_to_standard_mod_file: str,
                           verbose: bool = False) -> StandardIonChannel:
    """
    Creates a standardized channel and fits it to the data of the unstandardized channel.

    Parameters
    ----------
    path_to_mod_file : str
        The path to the .mod file.
    path_to_python_file : str
        The path to the Python file.
    path_to_python_template : str
        The path to the Python template file.
    path_to_mod_template : str
        The path to the .mod template file.
    path_to_standard_mod_file : str
        The path to save the standardized .mod file.
    verbose : bool, optional
        Whether to print verbose output.
    """
    # First create the regular channel
    channel = create_channel(path_to_mod_file, 
                            path_to_python_file, 
                            path_to_python_template,
                            verbose=verbose)
    
    # Then standardize it
    return standardize_channel(channel, path_to_mod_template, path_to_standard_mod_file)