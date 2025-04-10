import os
import sys
from typing import List, Tuple


from dendrotweaks.biophys.io.converter import MODFileConverter
from dendrotweaks.biophys.io.code_generators import NMODLCodeGenerator
from dendrotweaks.biophys.mechanisms import Mechanism, IonChannel, StandardIonChannel


def create_channel(path_to_mod_file: str,
                   path_to_python_file: str,
                   path_to_python_template: str,
                   verbose: bool = False) -> IonChannel:
    """
    Creates an ion channel from a .mod file.

    Parameters
    ----------
    path_to_mod_file : str
        The full path to the .mod file containing the channel mechanism.
    path_to_python_file : str
        The path to the output Python file to be generated.
    path_to_python_template : str
        The path to the jinja2 template file for the Python file.
    verbose : bool, optional
        Whether to print verbose output.

    Returns
    -------
    IonChannel
        The instantiated ion channel.
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
        The path to the jinja2 template file for the standard MOD file.
    path_to_standard_mod_file : str, optional
        The path to save the standardized MOD file.

    Returns
    -------
    StandardIonChannel
        A standardized version of the input channel.

    Note
    ----
    Temperature-dependence is taken into account by performing
    a fit to the data at the temperature specified in the parameters
    of the original channel model (the `temp` parameter). If no
    temperature is specified, the default temperature of 23 degrees
    Celsius is used.
    """
    standard_channel = StandardIonChannel(name=f"std{channel.name}", 
                                          state_powers=channel._state_powers, 
                                          ion=channel.ion)

    if 'q10' in channel.params:
        standard_channel.params['q10'] = channel.params['q10']
    if 'temp' in channel.params:
        standard_channel.params['temp'] = channel.params['temp']

    fit_temperature = channel.params.get('temp')

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
        The path to the original MOD file for an unstandardized channel.
    path_to_python_file : str
        The path to the output Python file to be generated.
    path_to_python_template : str
        The path to the jinja2 template file for the Python file.
    path_to_mod_template : str
        The path to the jinja2 template file for the standard MOD file.
    path_to_standard_mod_file : str
        The path to the output standardized MOD file.
    verbose : bool, optional
        Whether to print verbose output.

    Returns
    -------
    StandardIonChannel
        The standardized ion channel.
    """
    # First create the regular channel
    channel = create_channel(path_to_mod_file, 
                            path_to_python_file, 
                            path_to_python_template,
                            verbose=verbose)
    
    # Then standardize it
    return standardize_channel(channel, path_to_mod_template, path_to_standard_mod_file)