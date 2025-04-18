import pprint
from typing import List

ALLOWED_INDEPENDENT_VARS = ['cai', 'v']

# Assumptions:
# - Kinetic variables include the state variable name and 
# the substrings inf or tau (e.g., minf, mtau). Order, case, and additional characters
# do not matter (e.g., mInf, tau_M are also valid).
# - The channel is either voltage or calcium dependent, and 
# the independent variable is either v or cai.
# - Temperature adjustment coefficient is referred to as tadj and calculated as:
# tadj = q10^((celsius - temp)/10), where q10 is the temperature coefficient, 
# temp is the reference temperature, and celsius is the current temperature.



class AbstracSyntaxTree():
    """
    A class to represent the abstract syntax tree of a .mod file.

    Attributes
    ----------
    functions : List[Functional]
        A list of Functional objects representing the FUNCTION blocks in the .mod file.
    procedures : List[Functional]
        A list of Functional objects representing the PROCEDURE blocks in the .mod file.
    """

    def __init__(self, ast_dict: dict):
        # ast_dict = {k: v[0]
        #        if len(v) == 1 and k not in ['FUNCTION', 'PROCEDURE'] else v
        #        for k, v in ast_dict.items()}
        self.functions = [Functional(func, has_return=True)
                          for func in ast_dict.get('FUNCTION', [])]
        self.procedures = [Functional(proc, has_return=False)
                           for proc in ast_dict.get('PROCEDURE', [])]
        self._ast = ast_dict

    def __getitem__(self, key):
        return self._ast[key]

    def __setitem__(self, key, value):
        self._ast[key] = value

    def __repr__(self):
        return pprint.pformat(self._ast, sort_dicts=False)

    @property
    def title(self):
        return ''.join(self['TITLE']).strip()

    @property
    def comment(self):
        return ''.join(self['COMMENT']).strip()

    # NEURON block
    @property
    def suffix(self):
        if self['NEURON'] is not None:
            return self['NEURON']['suffix']

    @property
    def ion(self):
        if self['NEURON'].get('useion'):
            ions = [ion['ion']
                    for ion in self['NEURON']['useion'] if ion.get('write', '')]
            if len(ions) == 1:
                return ions[0]
            elif len(ions) == 0:
                return None
            else:
                raise Exception('Multiple ions not supported')
        else:
            return None

    # PARAMETER block
    @property
    def params(self):
        """
        Returns a dictionary of the parameters in the PARAMETER block.
        """
        return {param['name']: param['value'] for param in self['PARAMETER']}

    @property
    def range_params(self):
        """
        Returns a dictionary of the range parameters in the PARAMETER block.
        """
        return {k:v for k, v in self.params.items()
                if k in self['NEURON']['range']}

    @property
    def current_available(self):
        """
        Returns True if the current is available in the mechanism.
        """
        return 'i' in self['NEURON']['range']

    # ASSIGNED block
    @property
    def assigned_vars(self):
        """
        Returns a list of the assigned variables in the ASSIGNED block.
        """
        return [assigned['name'] for assigned in self['ASSIGNED']]

    @property
    def independent_var_name(self):
        """
        Returns the name of the independent variable.
        Prefers 'cai' over 'v' if both are present.
        """
        independent_vars = [var for var in self.assigned_vars 
                            if any(indep_var in var.lower() 
                                   for indep_var in ALLOWED_INDEPENDENT_VARS)]
        if 'cai' in independent_vars:
            return 'cai'
        elif 'v' in independent_vars:
            return 'v'
        raise Exception('Independent variable not found')

    def is_voltage_dependent(self):
        """
        Returns True if the mechanism is voltage dependent.
        """
        for var in self.assigned_vars:
            if 'v' in var.lower():
                return True
        return False

    def is_ca_dependent(self):
        """
        Returns True if the mechanism is calcium dependent.
        """
        for var in self.assigned_vars:
            if 'cai' in var.lower():
                return True
        return False

    # STATE block
    @property
    def state_vars(self):
        """
        Returns a dictionary of the state variables in the STATE block.
        """
        return self['STATE']


class Functional():
    """
    A class to represent abstract syntax tree of a
    FUNCTION or PROCEDURE block in a .mod file.

    Attributes
    ----------
    has_return : bool
        Whether the block has a return statement (is a FUNCTION block) 
        or not (is a PROCEDURE block).
    """

    def __init__(self, func_ast, has_return=True):
        self._ast = func_ast
        self.has_return = has_return

    def __getitem__(self, key):
        return self._ast[key]

    def get(self, key, default=None):
        return self._ast.get(key, default)

    def __setitem__(self, key, value):
        self._ast[key] = value

    def __repr__(self):
        return pprint.pformat(self._ast, sort_dicts=False)

    # Signature\
    @property
    def name(self):
        return self['signature']['name']

    @name.setter
    def name(self, value):
        self['signature']['name'] = value

    @property
    def params(self):
        return [param['name'] for param in self['signature'].get('params', [])]

    # Locals
    @property
    def local_vars(self):
        local_vars = []
        if self.has_return:
            local_vars.append(self['signature']['name'])
        local_vars.extend([arg['name'] for arg in self['signature'].get('args', [])])
        local_vars.extend(self.get('locals', []))
        return local_vars

    @property
    def signature(self):
        return self['signature']

    @property
    def statements(self):
        return self['statements']
