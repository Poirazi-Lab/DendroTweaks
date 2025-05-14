import re
import os
from jinja2 import Template

from abc import ABC, abstractmethod
from jinja2 import Environment, FileSystemLoader
from dendrotweaks.utils import write_file

# Configure the Jinja2 environment
# env = Environment(
#     loader=FileSystemLoader('static/data/templates'),  # Load templates from the 'templates' directory
#     trim_blocks=False,                      # Trim newlines after Jinja blocks
#     lstrip_blocks=False,                     # Strip leading whitespace from Jinja blocks
# )

EQUILIBRIUM_POTENTIALS = {
    'na': 60,
    'k': -80,
    'ca': 140
}

class CodeGenerator(ABC):

    @abstractmethod
    def generate(self, ast, path_to_template):
        pass

    def write_file(self, path_to_file):
        write_file(self.content, path_to_file)


class PythonCodeGenerator(CodeGenerator):
    """ A class to generate Python code from an AST using a Jinja2 template. """

    def __init__(self):
        self.content = None

    # MAIN METHOD

    def generate(self, ast, path_to_template):
        """
        Generate a Python class from the AST using a Jinja2 template.

        Parameters
        ----------
        ast : dict
            The AST representation of the channel
        path_to_template : str
            The path to the Jinja2 template file

        Returns
        -------
        str
            The Python code generated from the AST
        """

        # Read the template file
        with open(path_to_template, 'r') as file:
            template_string = file.read()

        # # Create a Jinja2 template from the string
        template = Template(template_string)
        # template = env.get_template(self.path_to_template)

        # Define the variables for the template
        variables = {
            'title': ast.title,
            # 'comment': ast.comment,
            'class_name': ast.suffix,
            'suffix': ast.suffix,
            'ion': ast.ion,
            'independent_var_name': ast.independent_var_name,
            'channel_params': ast.params,
            'range_params': ast.range_params,
            'current_available': ast.current_available,
            'state_vars': ast.state_vars,
            'functions': self._generate_functions(ast),
            'procedures': self._generate_procedures(ast),
            'procedure_calls': self._generate_procedure_calls(ast),
            'E_ion': EQUILIBRIUM_POTENTIALS.get(ast.ion, None)
        }

        # Render the template with the variables
        content = template.render(variables)

        if re.search(r'\bjnp\b', template_string):
            content = content.replace('np', 'jnp')

        self.content = content
            

    # HELPER METHODS

    def _generate_functions(self, ast, indent=8):
        functions = []

        for function in ast.functions:
            # Generate the signature
            signature_str = self._generate_signature(function.signature)

            # Generate the body
            body_str = self._generate_body(function.statements)
            for name in [function.name for function in ast.functions if function != function]:
                body_str = re.sub(r'\b' + re.escape(name) + r'\b', f"self.{name}", body_str)
            body_str = re.sub(r'\b' + re.escape('tadj') + r'\b', f"self.tadj", body_str)
            body_str = re.sub(r'\b' + re.escape('celsius') + r'\b', f"self.temperature", body_str)
            body_str += f"return {function.name}"
            body_str = '\n'.join(' ' * indent + line
                                 for line in body_str.splitlines())

            # Find the parameters that are used in the body
            params = [param for param in ast.params 
                      if param not in function.local_vars 
                      and param not in function.params
                      and re.search(r'\b' + re.escape(param) + r'\b', body_str)]

            functions.append({
                'signature': signature_str,
                'params': params,
                'body': body_str.strip()
            })
        
        return functions

    def _generate_procedures(self, ast, indent=8):

        if len(ast.procedures) != 1:
            raise ValueError("Only one procedure is supported")
        ast.procedures[0].name = 'compute_kinetic_variables'

        procedures = []

        for procedure in ast.procedures:
            # Generate the signature
            signature_str = self._generate_signature(procedure.signature, 
                                                     is_method=True,
                                                     extra_params=['celsius'],
                                                     default_params=True)

            # Generate the body
            body_str = self._generate_body(procedure.statements)
            for name in [function.name for function in ast.functions]:
                body_str = re.sub(r'\b' + re.escape(name) + r'\b', f"self.{name}", body_str)
            body_str = re.sub(r'\b' + re.escape('tadj') + r'\b', f"self.tadj", body_str)
            body_str = re.sub(r'\b' + re.escape('celsius') + r'\b', f"self.temperature", body_str)
            body_str += 'return ' + ', '.join([f"{state_var}Inf, {state_var}Tau"
                                              for state_var in ast.state_vars])
            body_str = '\n'.join(' ' * indent + line
                                    for line in body_str.splitlines())

            # Find the parameters that are used in the body
            params = [param for param in ast.params 
                      if param not in procedure.local_vars 
                      and re.search(r'\b' + re.escape(param) + r'\b', body_str)]

            procedures.append({
                'signature': signature_str,
                'params': params,
                'body': body_str.strip()
            })
        
        return procedures

    def _generate_signature(self, signature, is_method=True, extra_params=None, default_params=False):
        """
        Generate the signature string for a function using a Jinja2 template.
        The function AST representation is used to retrieve the function name
        and parameters:
        >>> def f_name(self, arg1, arg2, ...):

        Parameters
        ----------
        signature : dict
            The function signature as an AST dictionary
        is_method : bool
            Whether the function is a class method or not
        """
        signature_template = (
        "def {{ name }}({% if params %}{{ params | join(', ') }}{% endif %}):"
        )
        template = Template(signature_template)
        name = signature['name']
        params = [param['name'] for param in signature.get('params', [])]
        if params == [] and default_params:
            print(f"Warning: Procedure {name} has no parameters! Expected 'v' or 'cai'. Defaulting to 'v'.")
            params = ['v']
        if is_method:
            params = ['self'] + params

        return template.render(name=name, params=params)

    def _generate_body(self, statements, indent=12, skip_vars=['tadj']):
        python_code = ""
        # Add statements
        for statement in statements:
            # If the statement is an if-else statement
            if statement.get('condition', False):
                python_code += self._generate_conditionals(statement)
            else:
                if statement['assigned_var'] in skip_vars:
                    continue
                python_code += (f"{statement['assigned_var']} = {statement['expression']}\n")
        
        return python_code

    def _generate_conditionals(self, statement):
        """
        Generate the conditional statement for an if-else block using a Jinja2 template.
        """
        condition = statement['condition']
        if_statements = statement['if_statements']
        else_statements = statement.get('else_statements', [])
        else_statements = {statement['assigned_var']: statement['expression'] for statement in else_statements}
        
        conditional_code = ""
        for if_statement in statement['if_statements']:
            # Default to variable name if not in else_expressions
            else_statement = else_statements.get(
                if_statement['assigned_var'],
                if_statement["assigned_var"]
            )

            # Use a Jinja2 template to generate the conditional code
            conditional_template = (
            "conditions = [{{ condition }}, ~({{ condition }})]"
            "\nchoices = [{{ if_statement }}, {{ else_statement }}]"
            "\n{{ assigned_var }} = np.select(conditions, choices)"
            )
            template = Template(conditional_template)
            conditional_code += template.render(
                condition=condition,
                if_statement=if_statement['expression'],
                else_statement=else_statement,
                assigned_var=if_statement['assigned_var']
            )
            conditional_code += "\n"  # Add a newline between blocks

        return conditional_code
    
    def _generate_procedure_calls(self, ast):
        
        for procedure in ast.procedures:

            name = procedure.signature['name']
            params = [param['name'] for param in procedure.signature.get('params', [])]
            state_vars = list(ast.state_vars.keys())

            procedure_call_template = """{%- for state_var in state_vars -%}
            {{ state_var }}Inf, {{ state_var }}Tau{% if not loop.last %}, {% endif -%}
            {% endfor %} = self.{{ name }}({% if params %}{{ params | join(', ') }}{% endif %})
            """
            template = Template(procedure_call_template.strip())

            return template.render(
                name=name,
                params=params,
                state_vars=state_vars
            )



class NMODLCodeGenerator(CodeGenerator):
    """ A class to generate NMODL code from a StandardIonChannel"""

    def __init__(self):
        self.content = None

    def generate(self, channel, 
                path_to_template: str) -> None:
        """ 
        Generate NMODL code for a standardized ion channel 
        using a Jinja2 template.

        Parameters
        ----------
        channel : StandardIonChannel
            The standardized ion channel.
        path_to_template : str
            The path to the Jinja2 template file.
        """
        
        # Read the template file
        with open(path_to_template, 'r') as file:
            template_string = file.read()

        # Create a Jinja2 template from the string
        template = Template(template_string)

        def get_unit(param):
            if param.startswith('vhalf_'): return 'mV'
            elif param.startswith('sigma_'): return 'mV'
            elif param.startswith('k_'): return '1/ms'
            elif param.startswith('delta_'): return '1'
            elif param.startswith('tau0_'): return 'ms'
            elif param.startswith('temp'): return 'degC'
            elif param.startswith('q10'): return '1'
            elif param.startswith('gbar'): return 'S/cm2'
            else: return '1'

        # Define the variables for the template
        variables = {
            'suffix': channel.name,
            'ion': channel.ion,
            'params': [
                (param, channel.params[param], get_unit(param))
                for param in channel.params
            ],
            'range_params': [
                (param, channel.range_params[param], get_unit(param))
                for param in channel.range_params
            ],
            'has_tadj': ('q10' in channel.params and 'temp' in channel.params),
            'state_vars': {
                var: params['power'] for var, params in channel._state_powers.items()
            },
        }

        # Render the template with the variables
        content = template.render(variables)

        self.content = content
        return content