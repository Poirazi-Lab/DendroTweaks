from dendrotweaks.membrane.io.reader import MODFileReader
from dendrotweaks.membrane.io.parser import MODFileParser
from dendrotweaks.membrane.io.code_generators import PythonCodeGenerator

class MODFileConverter():
    """
    Converts a mod file to a Python file.
    """

    def __init__(self, config: dict = None):
        self.reader = MODFileReader()
        self.parser = MODFileParser()
        self.generator = PythonCodeGenerator()

    @property
    def mod_content(self):
        return self.reader.content

    @property
    def blocks(self):
        return self.reader.blocks

    @property
    def ast(self):
        return self.parser.ast

    @property
    def python_content(self):
        return self.code_generator.content
        
    # def convert(self, path_to_mod, path_to_python, path_to_template):
    #     """ Converts a mod file to a python file.

    #     Parameters
    #     ----------
    #     path_to_mod : str
    #         The path to the mod file.
    #     path_to_python : str
    #         The path to the python file.
    #     path_to_template : str
    #         The path to the template file.
    #     """

    #     self.read_file(path_to_mod) # generates self.mod_content
    #     self.preprocess() # generates self.blocks
    #     self.parse() # generates self.ast
    #     self.generate_python(path_to_template) # generates self.python_content
    #     self.write_file(path_to_python) # writes self.python_content to path_to_python

    def convert(self, path_to_mod_file: str, 
                path_to_python_file: str, 
                path_to_python_template: str, 
                path_to_json_file:str = None,
                verbose: bool = False) -> None:
        """ Converts a mod file to a python file.

        Parameters
        ----------
        path_to_mod : str
            The path to the mod file.
        path_to_python : str
            The path to the python file.
        path_to_template : str
            The path to the template file.
        path_to_json : str, optional
            The path to the json file.
        """

        if verbose: print(f"READING")
        self.reader.read_file(path_to_mod_file)
        self.reader.preprocess()
        blocks = self.reader.get_blocks(verbose)
        
        if verbose: print(f"\nPARSING")
        self.parser.parse(blocks, verbose)
        self.parser.postprocess()
        ast = self.parser.get_ast()
        
        if path_to_json_file:
            self.parser.write_file(path_to_json_file)
        
        if verbose: print(f"\nGENERATING")
        self.generator.generate(ast, path_to_python_template)
        self.generator.write_file(path_to_python_file)
