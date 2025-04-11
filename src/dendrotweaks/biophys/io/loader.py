import os
import sys
import shutil
import subprocess
import neuron
from neuron import h


class MODFileLoader():

    def __init__(self):
        self._loaded_mechanisms = set()
        self.verbose = False

    def _log(self, message):
        """Print a message if verbose mode is enabled."""
        if self.verbose:
            print(message)
              
    # LOADING METHODS

    def _get_mechanism_dir(self, path_to_mod_file: str) -> str:
        """
        Get the subdirectory for the given mod file.

        Parameters
        ----------
        path_to_mod_file : str
            Path to the .mod file.

        Returns
        -------
        str
            Path to the subdirectory for the mechanism.
        """
        mechanism_name = os.path.basename(path_to_mod_file).replace('.mod', '')
        parent_dir = os.path.dirname(path_to_mod_file)
        if sys.platform.startswith('win'):
            return os.path.join(parent_dir, mechanism_name, mechanism_name)
        else:
            return os.path.join(parent_dir, mechanism_name)

    def _clean_mechanism_dir(self, mechanism_dir: str) -> None:
        
        if sys.platform.startswith('win'):
            parent_dir = os.path.dirname(mechanism_dir)
            shutil.rmtree(parent_dir)
        else:
            shutil.rmtree(mechanism_dir)


    def load_mechanism(self, path_to_mod_file: str, 
                       recompile: bool = False) -> None:
        """
        Load a mechanism from the specified mod file.
        Uses the NEURON neuron.load_mechanisms method to make
        the mechanism available in the hoc interpreter.
        Creates a temporary directory for the mechanism files
        to be able to dynamically load mechanisms.

        Parameters
        ----------
        path_to_mod_file : str
            Path to the .mod file.
        recompile : bool
            Force recompilation even if already compiled.
        """
        mechanism_name = os.path.basename(path_to_mod_file).replace('.mod', '')
        mechanism_dir = self._get_mechanism_dir(path_to_mod_file)      

        if self.verbose: print(f"{'=' * 60}\nLoading mechanism {mechanism_name} to NEURON...")

        # Check if the mechanism is already loaded
        if mechanism_name in self._loaded_mechanisms:
            self._log(f'Mechanism "{mechanism_name}" already loaded')
            return

        if recompile and os.path.exists(mechanism_dir):
            self._clean_mechanism_dir(mechanism_dir)

        self._separate_and_compile(mechanism_name, mechanism_dir, path_to_mod_file)

        # Load the mechanism
        self._load_mechanism(mechanism_name, mechanism_dir)


    # HELPER METHODS

    def _separate_and_compile(self, mechanism_name, mechanism_dir, path_to_mod_file):
        """
        Separate the mechanism files into their own directory and compile them.
        Separation is done to enable dynamic loading of mechanisms.
        Compilation is done using the appropriate command based on the platform.
        
        Parameters
        ----------
        mechanism_name : str
            Name of the mechanism.
        mechanism_dir : str
            Directory to store the mechanism files.
        path_to_mod_file : str
            Path to the .mod file.
        """

        if sys.platform.startswith('win'):
            dll_file = os.path.join(os.path.dirname(mechanism_dir), 'nrnmech.dll')
            if not os.path.exists(dll_file):
                self._log(f'Compiling mechanism "{mechanism_name}"...')
                os.makedirs(mechanism_dir, exist_ok=True)
                shutil.copy(path_to_mod_file, mechanism_dir)
                self._compile_files(mechanism_dir, ["mknrndll"], shell=True)
        else:
            x86_64_dir = os.path.join(mechanism_dir, 'x86_64')
            if not os.path.exists(x86_64_dir):
                self._log(f'Compiling mechanism "{mechanism_name}"...')
                os.makedirs(mechanism_dir, exist_ok=True)
                shutil.copy(path_to_mod_file, mechanism_dir)
                self._compile_files(mechanism_dir, ["nrnivmodl"])


    def _load_mechanism(self, mechanism_name: str, mechanism_dir: str) -> None:
        """
        Load the mechanism into NEURON using neuron.load_mechanisms.
        This method checks if the mechanism is already loaded
        and only loads it if not.
        Parameters
        ----------
        mechanism_name : str
            Name of the mechanism.
        mechanism_dir : str
            Directory containing the compiled mechanism files.
        """

        if hasattr(h, mechanism_name):
            self._log(f'Mechanism "{mechanism_name}" already exists in hoc')
        else:
            try:
                neuron.load_mechanisms(mechanism_dir)
            except Exception as e:
                print(f"Failed to load mechanism {mechanism_name}: {e}")
                return
        self._loaded_mechanisms.add(mechanism_name)
        self._log(f'Loaded mechanism "{mechanism_name}"')
        

    
    def _compile_files(self, path, command, shell=False):
        """
        Compile the MOD files in the specified directory.

        Parameters
        ----------
        path : str or Path
            Directory containing MOD files to compile.
        command : list
            Compilation command to execute. Either "mknrndll" or "nrnivmodl".
        shell : bool
            Whether to use shell=True for subprocess.run
            (Windows compatibility).

        Returns
        -------
        bool
            True if compilation succeeded, False otherwise.
        """
        path_str = str(path)

        try:
            result = subprocess.run(
                command,
                cwd=path_str,
                check=True,
                capture_output=True,
                text=True,
                shell=shell
            )

            self._log("Compilation successful.")
            if self.verbose and result.stdout:
                print(result.stdout)
            return

        except subprocess.CalledProcessError as e:
            print(f"Compilation failed with return code {e.returncode}")
            if self.verbose:
                if e.stdout:
                    print("Compiler output:\n", e.stdout)
                if e.stderr:
                    print("Compiler errors:\n", e.stderr)
            return
