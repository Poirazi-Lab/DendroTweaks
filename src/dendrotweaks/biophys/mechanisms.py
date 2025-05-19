from typing import Dict
import numpy as np
import matplotlib.pyplot as plt



class Mechanism():
    """
    A class representing a mechanism in a neuron model. 
    
    A mechanism is a set of differential equations that 
    describe the kinetics of a channel
    or a pump in the neuron membrane

    Parameters
    ----------
    name : str
        The name of the mechanism.

    Attributes
    ----------
    name : str
        The name of the mechanism.
    params : dict
        A dictionary of the parameters of the mechanism.
    range_params : dict
        A dictionary of the range parameters of the mechanism added
        under the RANGE statement in the MOD file.
    """

    def __init__(self, name):
        self.name = name
        self.params = {}
        self.range_params = {}
        self.current_available = False

    @property
    def params_with_suffix(self):
        """
        The parameters of the mechanism with the suffix
        — the name of the mechanism.

        Returns
        -------
        dict
            A dictionary of the parameters of the mechanism with the suffix and their values.
        """
        return {f"{param}_{self.name}":value for param, value in self.params.items()}

    @property
    def range_params_with_suffix(self):
        """
        The range parameters of the mechanism with the suffix
        — the name of the mechanism. The range parameters are the parameters
        defined in the RANGE block of the NMODL file.

        Returns
        -------
        dict
            A dictionary of the range parameters of the mechanism with the suffix and their values.
        """
        return {f"{param}_{self.name}":value for param, value in self.range_params.items()}

    def to_dict(self):
        """
        Return the mechanism as a dictionary.
        """
        return {
            'name': self.name,
            'params': self.params
        }

    def __repr__(self):
        return f"<Mechanism({self.name})>"




class IonChannel(Mechanism):
    """
    A class representing an ion channel in a neuron model.

    Parameters
    ----------
    name : str
        The name of the channel.

    Attributes
    ----------
    independent_var_name : str
        The name of the independent variable for the channel kinetics e.g. 'v', 'cai'.
    params : dict
        A dictionary of the parameters of the channel kinetics and distribution.
    range_params : dict
        A dictionary of the range parameters of the channel kinetics added
        under the RANGE statement in the MOD file.
    temperature : float
        The temperature in degrees Celsius.
    tadj : float
        The temperature adjustment factor for the channel kinetics.
    """
    
    def __init__(self, name):
        super().__init__(name)
        self.tadj = 1

    def set_tadj(self, temperature):
        """
        Set the temperature adjustment factor for the channel kinetics.

        Parameters
        ----------
        temperature : float
            The temperature in degrees Celsius.

        Notes
        -----
        The temperature adjustment factor is calculated as:
        tadj = q10 ** ((temperature - reference_temp) / 10)
        where q10 is the temperature coefficient and reference_temp is the
        temperature at which the channel kinetics were measured.
        """
        q10 = self.params.get("q10")
        reference_temp = self.params.get("temp")
        if q10 is None or reference_temp is None:
            self.tadj = 1
        else:
            self.tadj = q10 ** ((temperature - reference_temp) / 10)

    def get_data(self, x=None, temperature: float = 37, verbose=True) -> Dict[str, Dict[str, float]]:
        """
        Get the data for the channel kinetics as a dictionary. The data
        includes the steady state values and time constants of the channel,
        as well as the independent variable values.

        Parameters
        ----------
        x : np.array, optional
            The independent variable for the channel kinetics. If None, the
            default values will be used. The default is None.
        temperature : float, optional
            The temperature in degrees Celsius. The default is 37.

        Returns
        -------
        Dict[str, Dict[str, np.ndarray]]
            A dictionary of states with their steady state values and time constants:
            {
            'state1': {'inf': np.array, 'tau': np.array},
            'state2': {'inf': np.array, 'tau': np.array},
            ...
            'x': np.array
            }
        """

        if x is None:
            if self.independent_var_name == 'v':
                x = np.linspace(-100, 100, 100)
            elif self.independent_var_name == 'cai':
                x = np.logspace(-6, 2, 100)
        
        self.set_tadj(temperature)
        self.temperature = temperature
        states = self.compute_kinetic_variables(x)
        # TODO: Fix the issue with returning state as a constant
        # for some channels (e.g. tau in Poirazi Na_soma)
        data = {
            state_name: {
                'inf': np.full_like(x, states[i]) if np.isscalar(states[i]) else states[i],
                'tau': np.full_like(x, states[i + 1]) if np.isscalar(states[i + 1]) else states[i + 1]
                }
            for i, state_name in zip(range(0, len(states), 2),
                                     self.states)
        }
        data.update({'x': x})
        if verbose: print(f'Got data for {self.independent_var_name} '
               f'in range {x[0]} to {x[-1]} at {temperature}°C')
        return data

    def plot_kinetics(self, ax=None, linestyle='solid', **kwargs) -> None:
        """
        Plot the kinetics of the channel.

        Parameters
        ----------
        ax : matplotlib.axes.Axes, optional
            The axes to plot the kinetics on. If None, a new figure
            will be created. The default is None.
        linestyle : str, optional
            The line style for the plots. The default is 'solid'.
        **kwargs : dict
            Additional keyword arguments to pass to the get_data method.
        """

        if ax is None:
            fig, ax = plt.subplots(1, 2, figsize=(10, 5))

        data = self.get_data(**kwargs)
        x = data.pop('x')

        for state_name, state in data.items():
            ax[0].plot(x, state['inf'], label=f'{state_name}Inf', linestyle=linestyle)
            ax[1].plot(x, state['tau'], label=f'{state_name}Tau', linestyle=linestyle)

        ax[0].set_title('Steady state')
        ax[1].set_title('Time constant')
        ax[0].set_xlabel('Voltage (mV)' if self.independent_var_name == 'v' else 'Ca2+ concentration (mM)')
        ax[1].set_xlabel('Voltage (mV)' if self.independent_var_name == 'v' else 'Ca2+ concentration (mM)')
        ax[0].set_ylabel('Open probability (1)')
        ax[1].set_ylabel('Time constant (ms)')
        ax[0].legend()
        ax[1].legend()




class StandardIonChannel(IonChannel):
    """
    A class representing a voltage-gated ion channel with a standard 
    set of kinetic parameters and equations grounded in the transition-state
    theory. The model is based on the Hodgkin-Huxley formalism.

    Parameters
    ----------
    name : str
        The name of the channel.
    state_powers : dict
        A dictionary of the state variables and their powers in the
        differential equations of the channel kinetics.
    ion : str, optional
        The ion that the channel is permeable to. The default is None.
    

    Attributes
    ----------
    ion : str
        The ion that the channel is permeable to e.g. 'na', 'k'.
    independent_var_name : str
        The name of the independent variable for the channel kinetics e.g. 'v', 'cai'.
    params : dict
        A dictionary of the parameters of the channel kinetics and distribution.
    range_params : dict
        A dictionary of the range parameters of the channel kinetics added 
        under the RANGE statement in the MOD file.
    temperature : float
        The temperature in degrees Celsius.
    """

    STANDARD_PARAMS = [
        'vhalf', 'sigma', 'k', 'delta', 'tau0'
    ]

    @staticmethod
    def steady_state(v, vhalf, sigma):
        """
        Compute the steady state value of the channel.

        Parameters
        ----------
        v : np.array
            The voltage values to compute the steady state value for.
        vhalf : float
            The half-activation voltage.
        sigma : float
            The slope factor.
        
        Returns
        -------
        np.array
            The steady state value of the channel at the given voltage values.
        """
        return 1 / (1 + np.exp(-(v - vhalf) / sigma))

    def time_constant(self, v, vhalf, sigma, k, delta, tau0):
        """
        Compute the time constant of the channel.

        Parameters
        ----------
        v : np.array
            The voltage values to compute the time constant for.
        vhalf : float
            The half-activation voltage.
        sigma : float
            The slope factor.
        k : float
            The maximum rate parameter.
        delta : float
            The skew parameter of the time constant curve (unitless)
        tau0 : float
            The rate-limiting factor (minimum time constant) 

        Returns
        -------
        np.array
            The time constant of the channel at the given voltage values.
        """
        return 1 / (self.alpha_prime(v, vhalf, sigma, k, delta) + self.beta_prime(v, vhalf, sigma, k, delta)) + tau0

    @staticmethod
    def alpha_prime(v, vhalf, sigma, k, delta):
        return k * np.exp(delta * (v - vhalf) / sigma)

    @staticmethod
    def beta_prime(v, vhalf, sigma, k, delta):
        return k * np.exp(-(1 - delta) * (v - vhalf) / sigma)

    @staticmethod
    def t_adj(temperature, q10=2.3, reference_temp=23):
        """
        Compute the temperature adjustment factor for the channel kinetics.

        Parameters
        ----------
        temperature : float
            The temperature in degrees Celsius.
        q10 : float, optional
            The temperature coefficient. The default is 2.3.
        reference_temp : float, optional
            The reference temperature at which the channel kinetics were measured.
            The default is 23.

        Returns
        -------
        float
            The temperature adjustment factor.
        """
        return q10 ** ((temperature - reference_temp) / 10)

    def compute_state(self, v, vhalf, sigma, k, delta, tau0, tadj=1):
        """
        Compute the steady state value and time constant of the channel
        for the given voltage values.

        Parameters
        ----------
        v : np.array
            The voltage values to compute the channel kinetics for.
        vhalf : float
            The half-activation voltage.
        sigma : float
            The slope factor.
        k : float
            The maximum rate parameter.
        delta : float
            The skew parameter of the time constant curve (unitless)
        tau0 : float
            The rate-limiting factor (minimum time constant) 
        tadj : float, optional
            The temperature adjustment factor. The default is 1.

        Returns
        -------
        np.array
            A list of steady state values and time constants for the channel.
        """
        inf = self.steady_state(v, vhalf, sigma)
        tau = self.time_constant(v, vhalf, sigma, k, delta, tau0) / tadj
        return inf, tau


    def __init__(self, name, state_powers, ion=None):
        super().__init__(name)
        
        self.ion = ion
        self.independent_var_name = 'v'

        self._state_powers = state_powers

        # self.range_params = [f'{param}_{state}' for state in state_powers
        #             for param in self.STANDARD_PARAMS]

        self.params = {
            'gbar': 0.0,
            **{
            f'{param}_{state}': None
            for state in state_powers
            for param in self.STANDARD_PARAMS
            }
        }
        self.range_params = {k:v for k, v in self.params.items()}

        self.temperature = 37


    @property
    def states(self):
        """
        A list of state variable names of the channel.
        """
        return [state for state in self._state_powers]


    def compute_kinetic_variables(self, v):
        """
        Compute the steady state values and time constants of the channel
        for the given voltage values.

        Parameters
        ----------
        v : np.array
            The voltage values to compute the channel kinetics for.

        Returns
        -------
        list
            A list of steady state values and time constants for each state
            of the channel.
        """
        
        results = []

        for state in self.states:

            vhalf = self.params[f'vhalf_{state}']
            sigma = self.params[f'sigma_{state}']
            k = self.params[f'k_{state}']
            delta = self.params[f'delta_{state}']
            tau0 = self.params[f'tau0_{state}']

            inf = self.steady_state(v, vhalf, sigma)
            tau = self.time_constant(v, vhalf, sigma, k, delta, tau0) / self.tadj

            results.extend([inf, tau])
            
        return results


    def fit(self, data, prioritized_inf=True, round_params=3):
        """
        Fit the standardized set of parameters of the model to the data 
        of the channel kinetics. 
        
        Parameters
        ----------
        data : dict
            A dictionary containing the data for the channel kinetics. The
            dictionary should have the following structure:
            {
            'x': np.array, # The independent variable
            'state1': {'inf': np.array, 'tau': np.array},
            'state2': {'inf': np.array, 'tau': np.array},
            ...
            }
        prioritized_inf : bool, optional
            Whether to prioritize the fit to the 'inf' data. If True, an
            additional fit will be performed to the 'inf' data only. The
            default is True.
        round_params : int, optional
            The number of decimal places to round the fitted parameters to.
            The default is 3.
        """
        from symfit import exp, variables, parameters, Model, Fit

        x = data.pop('x')

        for state, state_data in data.items():
            v, inf, tau = variables('v, inf, tau')
            initial_values = [1, 0.5, 0, 10, 0] if state_data['inf'][0] < state_data['inf'][-1] else [1, 0.5, 0, -10, 0]
            k, delta, vhalf, sigma, tau0 = parameters('k, delta, vhalf, sigma, tau0', value=initial_values)
            
            model = Model({
                inf: 1 / (1 + exp(-(v - vhalf) / sigma)),
                tau: 1 / (k * exp(delta * (v - vhalf) / sigma) + k * exp(-(1 - delta) * (v - vhalf) / sigma)) + tau0,
            })

            fit = Fit(model, v=x, inf=state_data['inf'], tau=state_data['tau'])
            fit_result = fit.execute()

            if prioritized_inf:
                vhalf.value, sigma.value = fit_result.params['vhalf'], fit_result.params['sigma']
                model_inf = Model({inf: 1 / (1 + exp(-(v - vhalf) / sigma))})
                fit_inf = Fit(model_inf, v=x, inf=state_data['inf'])
                fit_result_inf = fit_inf.execute()
                fit_result.params.update(fit_result_inf.params)

            if round_params:
                fit_result.params = {key: round(value, round_params) for key, value in fit_result.params.items()}

            for param in ['k', 'delta', 'tau0', 'vhalf', 'sigma']:
                value = fit_result.params[param]
                self.params[f'{param}_{state}'] = value
                self.range_params[f'{param}_{state}'] = value
    
    
    def to_dict(self):
        """
        Return the mechanism as a dictionary.
        """
        return {
            'suffix': self.name,
            'ion': self.ion,
            'range_params': [
                (param, self.params[param], get_unit(param))
                for param in self.params
            ],
            'state_vars': {
                var: power for var, power in self._state_powers.items()
            },
        }

    @staticmethod
    def get_unit(param):
        """
        Get the unit of a parameter based on its name.

        Parameters
        ----------
        param : str
            The name of the parameter.

        Returns
        -------
        str
            The unit of the parameter.
        """
        if param.startswith('vhalf_'): return 'mV'
        elif param.startswith('sigma_'): return 'mV'
        elif param.startswith('k_'): return '1/ms'
        elif param.startswith('delta_'): return '1'
        elif param.startswith('tau0_'): return 'ms'


class LeakChannel(Mechanism):
    """
    A class representing a leak channel in a neuron model.

    Parameters
    ----------
    name : str
        The name of the channel.

    Attributes
    ----------
    params : dict
        A dictionary of the parameters of the channel kinetics and distribution.
    range_params : dict
        A dictionary of the range parameters of the channel kinetics added 
        under the RANGE statement in the MOD file.
    """

    def __init__(self):
        super().__init__(name='Leak')
        self.params = {'gbar': 0.0, 'e': -70}
        self.range_params = {'gbar': 0.0, 'e': -70}


class CaDynamics(Mechanism):
    """
    A class representing a calcium dynamics mechanism in a neuron model.

    Attributes
    ----------
    params : dict
        A dictionary of the parameters of the calcium dynamics mechanism.
    range_params : dict
        A dictionary of the range parameters of the calcium dynamics mechanism
        added under the RANGE statement in the MOD file.
    """

    def __init__(self):
        super().__init__('CaDyn')
        self.params = {
            'depth': 0.1,  # um: Depth of calcium shell
            'taur': 80,    # ms: Time constant for calcium removal
            'cainf': 1e-4, # mM: Steady-state calcium concentration
            'gamma': 0.05,
            'kt': 0.0,
            'kd': 0.0
        }
        self.range_params = {
            'depth': 0.1,
            'taur': 80,
            'cainf': 1e-4,
            'gamma': 0.05,
            'kt': 0.0,
            'kd': 0.0
        }