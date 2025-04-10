import re
from typing import List, Dict
import os

class MODFileReader():
    """
    Reader class for .mod files.

    Provides methods to read and preprocess .mod files.
    Splits the content of the file into blocks for further parsing.

    Attributes
    ----------
    content : str
        The content of the MOD file.
    blocks : Dict[str, List[str]]
        The blocks of the MOD file corresponding to the
        NMODL blocks e.g. NEURON, PARAMETER, ASSIGNED, etc.
    unmatched : str
        The unmatched content in the MOD file after splitting into blocks.
    """

    BLOCK_TYPES = ['TITLE',
                  'COMMENT',
                  'NEURON',
                  'UNITS',
                  'PARAMETER',
                  'ASSIGNED',
                  'STATE',
                  'BREAKPOINT',
                  'DERIVATIVE',
                  'INITIAL',
                  'FUNCTION',
                  'PROCEDURE',
                  'KINETIC']

    def __init__(self):

        self._original_content = None
        self.content = None
        self.blocks = {}
        self.unmatched = None

    # READ

    def read_file(self, path_to_file: str) -> str:
        """
        Read the content of the file.

        Parameters
        ----------
        path_to_file : str
            The path to the file.
        """
        with open(path_to_file, 'r') as f:
            content = f.read()
        
        self._file_name = os.path.basename(path_to_file).replace('.mod', '')
        self._path_to_file = path_to_file
        self._original_content = content
        self.content = content
        
    # PREPROCESS

    def preprocess(self, remove_inline_comments=True, 
                   remove_unitsoff=True, remove_verbatim=True) -> None:
        """
        Preprocess the content of the file.
        """
        self.replace_suffix_with_name(overwirte=True)
        if remove_inline_comments:
            self.remove_inline_comments()
        if remove_unitsoff:
            self.remove_unitsoff()
        if remove_verbatim:
            self.remove_verbatim()

    def replace_suffix_with_name(self, overwirte=False) -> None:
        """
        Replace the suffix in the content of the file with the file name.

        Notes
        -----
        Suffix is a string of the form SUFFIX suffix

        Parameters
        ----------
        overwirte : bool, optional
            Whether to overwrite the content of the file with the modified content.
        """
        suffix_pattern = r'SUFFIX\s+\w+'
        match = re.search(suffix_pattern, self.content)
        # print(f"Replacing {match.group()} with SUFFIX {self._file_name}")
        self.content = re.sub(suffix_pattern, f'SUFFIX {self._file_name}', self.content)
        if overwirte:
            self._overwrite()

    def _overwrite(self) -> None:
        """
        Overwrite the content of the file with the modified content.
        """
        with open(self._path_to_file, 'w') as f:
            f.write(self.content)
        # print(f"Overwritten {self._path_to_file}")

    def remove_inline_comments(self) -> None:
        """
        Remove the rest of the line after ":" from the content of the file.
        """
        self.content = re.sub(r':.*', '', self.content)
        

    def remove_unitsoff(self) -> None:
        """
        Remove 'UNITSOFF' and 'UNITSON' from the content of the file.
        """
        self.content = re.sub(r'UNITSOFF|UNITSON', '', self.content)
        

    def remove_verbatim(self) -> None:
        """
        Remove 'VERBATIM' and 'ENDVERBATIM' and everything in between from the content of the file.
        """
        self.content = re.sub(r'VERBATIM.*?ENDVERBATIM', '', self.content, flags=re.DOTALL)
        

    def remove_suffix_from_gbar(self) -> None:
        """
        Remove the suffix from 'gbar' in the content of the file.

        Example
        -------
            gnabar -> gbar
        """
        self._content =  re.sub(r'\b\w*g\w*bar\w*\b', 'gbar', self._content)
        logger.info("Removed suffix from 'gbar' (e.g. gnabar -> gbar)")

    # SPLIT TO BLOCKS

    def get_blocks(self, verbose=True) -> Dict[str, List[str]]:
        """
        Split the content of the file into blocks and return them.

        Parameters
        ----------
        verbose : bool, optional
            Whether to print the
            blocks of the file.

        Returns
        -------
        Dict[str, List[str]]
            A dictionary of blocks where the key is the block name
        """
        for block_type in self.BLOCK_TYPES:
            matches = self._get_block_regex(block_type)
            self.blocks[block_type] = matches
        if verbose:
            message = f"Split content into blocks:\n"
            message += '\n'.join([f"    {len(block_content)} - {block_name}" 
                            for block_name, block_content in self.blocks.items()])
            print(message)
        self.find_unmatched_content()
        return self.blocks

    def _get_block_regex(self, block_name: str) -> List[str]:
        """
        Get the regex pattern for a specific block.

        Example
        -------
            NEURON {
                ...
            }

        Parameters:
        ------------
        block_name : str
            The name of the block e.g. 'NEURON', 'PARAMETER', etc.

        Returns
        -------
        List[str]
            A list of matches for the block.
        """
        if block_name == 'TITLE':
            pattern = r"(" + re.escape(block_name) + r"[\s\S]*?\n)"
        elif block_name == 'COMMENT':
            pattern = r"(" + re.escape(block_name) + r"[\s\S]*?ENDCOMMENT)"
        else:
            pattern = r"(\b" + re.escape(block_name) + r"\b[\s\S]*?\{(?:[^{}]*\{[^{}]*\})*[^{}]*?\})"
        matches = re.findall(pattern, self.content, re.DOTALL)
        return matches

    def find_unmatched_content(self, verbose:bool=False) -> None:
        """
        Find unmatched content in the content of the file.

        Parameters
        ----------
        verbose : bool, optional
            Whether to print the unmatched content.
        """
        unmatched = self.content
        for block_name, block in self.blocks.items():
            for block_content in block:
                unmatched = unmatched.replace(block_content, '')
        unmatched = unmatched.strip()
        if verbose:
            if unmatched: print(f"Unmatched content:\n{unmatched}")
            else: print("No unmatched content.")
        self._unmatched = unmatched