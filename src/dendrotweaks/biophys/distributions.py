from typing import Callable, Dict, List
from numpy import  ndarray, full_like
from numpy import exp, sin, polyval
import warnings
# Define simple functions and store them alongside their defaults in FUNCTIONS
def constant(position, value=0):
    """
    Constant function that returns a constant value for any position.

    Parameters
    ----------
    position : float or numpy.ndarray
        The position at which to evaluate the function.
    value : float
        The constant value to return.

    Returns
    -------
    float or numpy.ndarray
        The value of the constant function at the given position.
    """
    if isinstance(position, ndarray):
        return full_like(position, value, dtype=float)
    else:
        return value


def uniform(position, value=0):
    """
    Constant function that returns a constant value for any position.

    Parameters
    ----------
    position : float or numpy.ndarray
        The position at which to evaluate the function.
    value : float
        The constant value to return.

    Returns
    -------
    float or numpy.ndarray
        The value of the constant function at the given position.
    """
    if isinstance(position, ndarray):
        return full_like(position, value, dtype=float)
    else:
        return value


def linear(position, slope=1, intercept=0):
    """
    Linear function that returns a linearly changing value for any position.

    Parameters
    ----------
    position : float or numpy.ndarray
        The position at which to evaluate the function.
    slope : float
        The slope of the linear function.
    intercept : float
        The intercept of the linear function.

    Returns
    -------
    float or numpy.ndarray
        The value of the linear function at the given position.
    """
    return slope * position + intercept

def exponential(distance: float, vertical_shift:float = 0, scale_factor: float =1, growth_rate: float=1, horizontal_shift: float = 0) -> float:
    """
    Exponential distribution function.

    Args:
        distance (float): The distance parameter.
        vertical_shift (float): The vertical shift parameter.
        scale_factor (float): The scale factor parameter.
        growth_rate (float): The growth rate parameter.
        horizontal_shift (float): The horizontal shift parameter.

    Returns:
        The result of the exponential equation: vertical_shift + scale_factor * exp(growth_rate * (distance - horizontal_shift)).
    """
    return vertical_shift + scale_factor * exp(growth_rate * (distance - horizontal_shift))

def sigmoid(distance: float, vertical_shift=0, scale_factor=1, growth_rate=1, horizontal_shift=0) -> float:
    """
    Sigmoid distribution function.

    Args:
        distance (float): The distance parameter.
        vertical_shift (float): The vertical shift parameter.
        scale_factor (float): The scale factor parameter.
        growth_rate (float): The growth rate parameter.
        horizontal_shift (float): The horizontal shift parameter.

    Returns:
        The result of the sigmoid equation: vertical_shift + scale_factor / (1 + exp(-growth_rate * (distance - horizontal_shift))).
    """
    return vertical_shift + scale_factor / (1 + exp(-growth_rate*(distance - horizontal_shift)))


def sinusoidal(distance: float, amplitude: float, frequency: float, phase: float) -> float:
    """
    Sinusoidal distribution function.

    Args:
        distance (float): The distance parameter.
        amplitude (float): The amplitude parameter.
        frequency (float): The frequency parameter.
        phase (float): The phase parameter.

    Returns:
        The result of the sinusoidal equation: amplitude * sin(frequency * distance + phase).
    """
    return amplitude * sin(frequency * distance + phase)

def gaussian(distance: float, amplitude: float, mean: float, std: float) -> float:
    """
    Gaussian distribution function.

    Args:
        distance (float): The distance parameter.
        amplitude (float): The amplitude parameter.
        mean (float): The mean parameter.
        std (float): The standard deviation parameter.

    Returns:
        The result of the gaussian equation: amplitude * exp(-((distance - mean) ** 2) / (2 * std ** 2)).
    """
    return amplitude * exp(-((distance - mean) ** 2) / (2 * std ** 2))


def step(distance: float, max_value: float,  min_value: float, start: float, end: float) -> float:
    """
    Step distribution function.

    Args:
        distance (float): The distance parameter.
        min_value (float): The minimum value parameter.
        max_value (float): The maximum value parameter.
        start (float): The start parameter.
        end (float): The end parameter.

    Returns:
        The result of the step equation: min_value if distance < start, max_value if distance > end, and a linear interpolation between min_value and max_value if start <= distance <= end.
    """
    if start < distance < end:
        return max_value
    else:
        return min_value

def polynomial(distance: float, coeffs: List[float]) -> float:
    """
    Polynomial distribution function.

    Args:
        distance (float): The distance parameter.
        coefficients (List[float]): The coefficients of the polynomial.

    Returns:
        The result of the polynomial equation: sum(coefficients[i] * distance ** i for i in range(len(coefficients))).
    """
    return polyval(coeffs, distance)

# aka ParametrizedFunction
class Distribution:
    """
    A callable class for creating and managing distribution functions.

    Parameters
    ----------
    function_name : str
        The name of the function to use.
    \**parameters
        The parameters to use for the function.

    Attributes
    ----------
    function : Callable
        The function to use for evaluation.
    parameters : dict
        The parameters to use for the function.

    Examples
    --------

    >>> func = Distribution('uniform', value=0)
    >>> func(5)
    0
    """

    FUNCTIONS = {
        'constant': {'func': constant, 'defaults': {'value': 0}},
        'uniform': {'func': uniform, 'defaults': {'value': 0}},
        'linear': {'func': linear, 'defaults': {'slope': 1, 'intercept': 0}},
        'exponential': {'func': exponential, 'defaults': {'vertical_shift': 0, 'scale_factor': 1, 'growth_rate': 1, 'horizontal_shift': 0}},
        'sigmoid': {'func': sigmoid, 'defaults': {'vertical_shift': 0, 'scale_factor': 1, 'growth_rate': 1, 'horizontal_shift': 0}},
        'sinusoidal': {'func': sinusoidal, 'defaults': {'amplitude': 1, 'frequency': 1, 'phase': 0}},
        'gaussian': {'func': gaussian, 'defaults': {'amplitude': 1, 'mean': 0, 'std': 1}},
        'step': {'func': step, 'defaults': {'max_value': 1, 'min_value': 0, 'start': 0, 'end': 1}},
        'polynomial': {'func': polynomial, 'defaults': {'coeffs': [1, 0]}},

    }

    @staticmethod
    def from_dict(data: Dict[str, any]) -> 'Distribution':
        """
        Creates a new Distribution from a dictionary.

        Parameters
        ----------
        data : dict
            The dictionary containing the function data.

        Returns
        -------
        Distribution
            The new Distribution instance.
        """
        return Distribution(data['function'], **data['parameters'])

    def __init__(self, function_name: str, **parameters: Dict[str, float]) -> None:
        """
        Creates a new parameterized function.

        Parameters
        ----------
        function_name : str
            The name of the function to use.
        \**parameters
            The parameters to use for the function.
        """
        func_data = self.FUNCTIONS[function_name]
        self.function = func_data['func']
        # Merge defaults with user parameters
        valid_params = {k: v for k, v in parameters.items()
                        if k in func_data['defaults']}
        self.parameters = {**func_data['defaults'], **valid_params}

    def __repr__(self):
        """
        Returns a string representation of the function.

        Returns
        -------
        str
            The string representation of the function.
        """
        return f'{self.function.__name__}({self.parameters})'

    def __call__(self, position):
        """
        Calls the function with a given position.

        Parameters
        ----------
        position : float or numpy.ndarray
            The position at which to evaluate the function.

        Returns
        -------
        float or numpy.ndarray
            The value of the function at the given position.
        """
        return self.function(position, **self.parameters)

    @property
    def function_name(self):
        """
        Returns the name of the function.

        Returns
        -------
        str
            The name of the function.
        """
        return self.function.__name__

    @property
    def degree(self):
        """
        Returns the degree of the polynomial function (if applicable).

        Returns
        -------
        int
            The degree of the function.
        """
        if self.function_name == 'polynomial':
            return len(self.parameters['coeffs']) - 1
        else:
            return None

    def update_parameters(self, **new_params):
        """
        Updates the parameters of the function.

        Parameters
        ----------
        \**new_params
            The new parameters to update the function with.
        """
        valid_params = {k: v for k, v in new_params.items()
                        if k in self.parameters}
        # if any of the new parameters are invalid, raise an error
        if len(valid_params) != len(new_params):
            invalid_params = set(new_params) - set(valid_params)
            warnings.warn(f'\nIgnoring invalid parameters: {invalid_params}.\nSupported parameters: {list(self.parameters.keys())}')
        self.parameters.update(valid_params)

    def to_dict(self):
        """
        Exports the function to a dictionary format.

        Returns
        -------
        dict
            A dictionary representation of the function.
        """
        return {
            'function': self.function.__name__,
            'parameters': self.parameters
        }