import os
from typing import List, Dict
import shutil

class PathManager:
    """
    A manager class for handling file and directory paths related to models data.

    Parameters
    ----------
    path_to_model : str
        The path to the model directory.

    Attributes
    ----------
    path_to_model : str
        The path to the model directory.
    paths : Dict[str, str]
        A dictionary of paths for different file types.
    """
    def __init__(self, path_to_model: str):
        if not os.path.isdir(path_to_model):
            raise FileNotFoundError(f"Directory {path_to_model} does not exist.")
        self.path_to_model = path_to_model
        self.paths = {
            'default_mod': os.path.join(self.path_to_data, 'Default'),
            'templates': os.path.join(self.path_to_data, 'Templates'),
            'morphology': os.path.join(self.path_to_model, 'morphology'),
            'biophys': os.path.join(self.path_to_model, 'biophys'),
            'mod': os.path.join(self.path_to_model, 'biophys', 'mod'),
            'python': os.path.join(self.path_to_model, 'biophys', 'python'),
            'stimuli': os.path.join(self.path_to_model, 'stimuli'),
        }
        self._ensure_paths_exist()


    def _ensure_paths_exist(self):
        """
        Ensure all necessary paths exist.
        """
        os.makedirs(self.path_to_model, exist_ok=True)
        for path in self.paths.values():
            os.makedirs(path, exist_ok=True)
        # if empty, copy default mod files
        if not os.listdir(self.paths['default_mod']):
            self.copy_default_mod_files()
        if not os.listdir(self.paths['templates']):
            self.copy_template_files()


    @property
    def path_to_data(self):
        """
        The path to the data directory, which is always the parent directory of path_to_model.
        """
        return os.path.abspath(os.path.join(self.path_to_model, os.pardir))


    def __repr__(self):
        return f"PathManager({self.path_to_model})"


    def copy_default_mod_files(self):
        """
        Copy default mod files to the data directory.
        """
        DEFAULT_MOD_DIR = os.path.join(os.path.dirname(__file__), 'biophys', 'default_mod')
        for file_name in os.listdir(DEFAULT_MOD_DIR):
            source = os.path.join(DEFAULT_MOD_DIR, file_name)
            destination = os.path.join(self.paths['default_mod'], file_name)
            shutil.copyfile(source, destination)


    def copy_template_files(self):
        """
        Copy template files to the data directory.
        """
        TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'biophys', 'default_templates')
        for file_name in os.listdir(TEMPLATES_DIR):
            source = os.path.join(TEMPLATES_DIR, file_name)
            destination = os.path.join(self.paths['templates'], file_name)
            shutil.copyfile(source, destination)


    def remove_folder(self, relative_path: str) -> None:
        """
        Remove a folder and all its contents.

        Parameters
        ----------
        relative_path : str
            The absolute path to the folder to be removed.
        """
        folder_path = self.get_abs_path(relative_path)
        if os.path.isdir(folder_path):
            shutil.rmtree(folder_path, ignore_errors=True)


    def _resolve_root(self, relative_path: str) -> tuple[str, str]:
        """
        Given a relative path like 'stimuli/depolarizing/protocol.json',
        resolve the absolute root and the remainder.
        """
        relative_path = os.path.normpath(relative_path.strip())
        parts = relative_path.split(os.sep)
        root_key = parts[0]

        base_root = self.paths.get(root_key)
        if base_root is None:
            raise KeyError(
                f"Unknown top-level folder '{root_key}'. "
                f"Known roots: {list(self.paths.keys())}"
            )

        remainder = os.path.join(*parts[1:]) if len(parts) > 1 else ""
        return base_root, remainder


    def get_abs_path(self, relative_path: str, create_dirs: bool = False) -> str:
        """
        Get the absolute path to a file or directory based on a relative path.

        Parameters
        ----------
        relative_path : str
            Path relative to one of the registered roots.
        create_dirs : bool, default False
            If True, create the parent directories if they don't exist.

        Returns
        -------
        str
            Absolute path in OS-native format.

        Examples
        --------
        >>> pm = PathManager('/path/to/model')
        >>> pm.get_abs_path('stimuli/depolarizing/protocol.json')
        '/path/to/model/stimuli/depolarizing/protocol.json'
        """
        base_root, remainder = self._resolve_root(relative_path)
        abs_path = os.path.join(base_root, remainder)

        if create_dirs and remainder:
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)

        return abs_path

    def list_folders(self, relative_path: str) -> List[str]:
        """
        List all folders in a given directory.

        Parameters
        ----------
        relative_path : str
            Path relative to one of the registered roots.

        Returns
        -------
        List[str]
            A list of folder names.

        Examples
        --------
        >>> pm = PathManager('/path/to/model')
        >>> pm.list_folders('stimuli')
        ['depolarizing_current', 'hyperpolarizing_current']
        """
        abs_path = self.get_abs_path(relative_path)

        if not os.path.isdir(abs_path):
            return []

        return [f for f in os.listdir(abs_path) if os.path.isdir(os.path.join(abs_path, f))]


    def list_files(self, relative_path: str, extension: str | None = None) -> List[str]:
        """
        List all files in a given directory with an optional extension filter.
        If the extension is None, su
        
        Parameters
        ----------
        relative_path : str
            Path relative to one of the registered roots.
        extension : str
            The file extension to filter by (e.g., 'mod', 'swc').
        
        Returns
        -------
        List[str]
            A list of file names.
        """
        abs_path = self.get_abs_path(relative_path)
        if extension and not extension.startswith('.'): 
            extension = f".{extension}"
        if not os.path.isdir(abs_path):
            return []
        return [f.replace(extension, '') 
                for f in os.listdir(abs_path) if f.endswith(extension)]


    def list_morphologies(self, extension: str = '.swc') -> List[str]:
        """
        List all SWC files.
        
        Returns
        -------
        List[str]
            A list of SWC file names.
        """
        return self.list_files('morphology', extension=extension)


    def list_stimuli(self) -> List[str]:
        """
        List all JSON files.
        
        Returns
        -------
        List[str]
            A list of JSON file names.
        """
        return self.list_folders('stimuli')


    def list_biophys(self):
        """
        List all biophysics files.
        
        Returns
        -------
        List[str]
            A list of biophysics file names.
        """
        return self.list_files('biophys', extension='.json')


    def print_directory_tree(self, subfolder=None) -> None:
        """
        Print a directory tree for a given file type.
        
        Parameters
        ----------
        file_type : str
            The type of file (e.g., 'mod', 'swc').
        """
        base_path = self.paths.get('model') if not subfolder else self.paths.get(subfolder)
        if not base_path or not os.path.isdir(base_path):
            print(f"Directory for {file_type} does not exist.")
            return

        def print_tree(path, prefix=""):
            items = os.listdir(path)
            for idx, item in enumerate(sorted(items)):
                is_last = idx == len(items) - 1
                connector = "└──" if is_last else "├──"
                item_path = os.path.join(path, item)
                print(f"{prefix}{connector} {item}")
                if os.path.isdir(item_path) and not item.startswith('x86_64'):
                    extension = "│   " if not is_last else "    "
                    print_tree(item_path, prefix + extension)

        print_tree(base_path)


    def get_channel_paths(self, mechanism_name: str, 
                          python_template_name: str = None) -> Dict[str, str]:
        """
        Get all necessary paths for creating a channel.

        Parameters
        ----------
        mechanism_name : str
            The name of the mechanism.
        python_template_name : str, optional
            The name of the Python template file.

        Returns
        -------
        Dict[str, str]
            A dictionary of paths.
        """
        python_template_name = python_template_name or "default"
        return {
            'path_to_mod_file': self.get_abs_path(f'mod/{mechanism_name}.mod'),
            'path_to_python_file': self.get_abs_path(f'python/{mechanism_name}.py'),
            'path_to_python_template': self.get_abs_path(f'templates/{python_template_name}.py'),
        }


    def get_standard_channel_paths(self, mechanism_name: str,
                                   python_template_name: str = None,
                                   mod_template_name: str = None) -> Dict[str, str]:
        """
        Get all necessary paths for creating a standard channel.

        Parameters
        ----------
        mechanism_name : str
            The name of the mechanism.
        python_template_name : str, optional
            The name of the Python template file.
        mod_template_name : str, optional
            The name of the MOD template file.

        Returns
        -------
        Dict[str, str]
            A dictionary of paths.
        """
        python_template_name = python_template_name or "default"
        mod_template_name = mod_template_name or "standard_channel"
        return {
            # **self.get_channel_paths(mechanism_name, python_template_name),
            'path_to_mod_template': self.get_abs_path(f'templates/{mod_template_name}.mod'),
            'path_to_standard_mod_file': self.get_abs_path(f'mod/std{mechanism_name}.mod'),
        }