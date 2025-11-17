import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.signal import find_peaks, peak_widths
from scipy.optimize import curve_fit


# =============================================================================
# PASSIVE PROPERTIES
# =============================================================================

def get_somatic_data(model):
    """
    Get the somatic voltage, time, time step, and injected current.

    Parameters
    ----------
    model : Model
        The neuron model.

    Returns
    -------
    tuple
        A tuple containing the voltage, time, time step, and injected current.
    """
    soma = model.sec_tree.root
    seg = soma(0.5)
    iclamp = model.iclamps[seg]

    v = np.array(model.simulator.recordings['v'][seg])
    t = np.array(model.simulator.t)
    dt = model.simulator.dt

    return v, t, dt, iclamp


def calculate_input_resistance(model):
    """
    Calculate the input resistance of the neuron model.
        
    This function determines the input resistance by calculating the ratio 
    between the voltage change and the injected current. The voltage change 
    is measured as the difference between the membrane potential at the onset 
    and offset of the current injection.

    Parameters
    ----------
    model : Model
        The neuron model.

    Returns
    -------
    dict
        A dictionary containing the onset and offset voltages, the input resistance, and the injected current.
    """
    
    v, t, dt, iclamp = get_somatic_data(model)

    amp = iclamp.amp
    start_ts = int(iclamp.delay / dt)
    stop_ts = int((iclamp.delay + iclamp.dur) / dt)
    v_onset = v[int(start_ts)]
    v_offset = v[int(stop_ts)]
    
    R_in = (v_offset - v_onset) / amp
    print(f"Input resistance: {R_in:.2f} MOhm")

    return {
        'onset_voltage': v_onset,
        'offset_voltage': v_offset,
        'input_resistance': R_in,
        'current_amplitude': amp
    }


def _double_exp_decay(t, A1, tau1, A2, tau2):
    return A1 * np.exp(-t / tau1) + A2 * np.exp(-t / tau2)

def calculate_time_constant(model):
    """
    Estimate the passive membrane time constant (τm) by fitting
    a double exponential to the somatic voltage decay and selecting
    the slowest τ component.

    Parameters
    ----------
    model : Model
        The neuron model (assumes Ih is disabled).

    Returns
    -------
    dict
        A dictionary with τm (slowest), both τs, and fit details.
    """
    v, t, dt, iclamp = get_somatic_data(model)

    start_ts = int(iclamp.delay / dt)
    stop_ts = int((iclamp.delay + iclamp.dur) / dt)
    min_ts = np.argmin(v[start_ts:stop_ts]) + start_ts
    v_min = v[min_ts]
    v_decay = v[start_ts: min_ts] - v_min
    t_decay = t[start_ts: min_ts] - t[start_ts]

    # Fit double exponential
    try:
        popt, _ = curve_fit(
            _double_exp_decay, t_decay, v_decay, 
            p0=[1, 10, 0.5, 100], 
            bounds=(0, [np.inf, 1000, np.inf, 1000])
        )
        A1, tau1, A2, tau2 = popt
        tau_slowest = max(tau1, tau2)
    except RuntimeError:
        print("Fit failed. Could not estimate time constant.")
        return None

    print(f"Time constant {tau_slowest:.2f} ms. Estimated from double exp fit (slowest component)")

    return {
        'time_constant': tau_slowest,
        'start_time': start_ts * dt,
        'tau1': tau1,
        'tau2': tau2,
        'A1': A1,
        'A2': A2,
        'decay_time': t_decay,
        'decay_voltage': v_decay
    }


def calculate_passive_properties(model):
    """
    Calculate the passive properties of the neuron model.

    Parameters
    ----------
    model : Model
        The neuron model.   

    Returns
    -------
    dict
        A dictionary containing the input resistance, time constant, and the exponential fit.
    """

    data_rin = calculate_input_resistance(model)
    data_tau = calculate_time_constant(model)

    return {**data_rin, **data_tau}

def plot_passive_properties(data, ax=None):
        
    if ax is None:
        _, ax = plt.subplots()

    R_in = data['input_resistance']
    tau = data['time_constant']
    v_onset = data['onset_voltage']
    v_offset = data['offset_voltage']
    t_decay = data['decay_time']
    v_decay = data['decay_voltage']
    start_t = data['start_time']

    ax.set_title(f"R_in: {R_in:.2f} MOhm, Tau: {tau:.2f} ms")
    ax.axhline(v_onset, color='gray', linestyle='--', label='V onset')
    ax.axhline(v_offset, color='gray', linestyle='--', label='V offset')
    
    # Shift the exp_decay output along the y-axis
    fit_curve = _double_exp_decay(t_decay, data['A1'], data['tau1'], data['A2'], data['tau2']) + v_offset
    label = f'Double exp fit (tau1 = {data["tau1"]:.1f} ms, tau2 = {data["tau2"]:.1f} ms)'

    ax.plot(t_decay + start_t, fit_curve, color='red', label='Exp. fit', linestyle='--')
    ax.legend()


# =============================================================================
# ACTIVE PROPERTIES
# =============================================================================

def detect_somatic_spikes(model, **kwargs):
    """
    Detect somatic spikes in the model and calculate spike amplitudes and widths.
    
    Returns:
        dict: A dictionary containing spike metrics.
    """
    soma = model.sec_tree.root
    seg = soma(0.5)
            
    v = np.array(model.simulator.recordings['v'][seg])
    t = np.array(model.simulator.t)
    dt = model.simulator.dt

    baseline = np.median(v)
    height = kwargs.get('height', baseline)
    distance = kwargs.get('distance', int(2/dt))
    prominence = kwargs.get('prominence', 50)
    wlen = kwargs.get('wlen', int(20/dt))
    
    peaks, properties = find_peaks(v, height=height, distance=distance, prominence=prominence, wlen=wlen)
    half_widths, _, left_bases, right_bases = peak_widths(v, peaks, rel_height=0.5)
    half_widths *= dt
    left_bases *= dt
    right_bases *= dt

    return {
        'spike_times': t[peaks],
        'spike_values': properties['peak_heights'],
        'half_widths': half_widths,
        'amplitudes': properties['prominences'],
        'left_bases': left_bases,
        'right_bases': right_bases,
        'stimulus_duration': model.iclamps[seg].dur
    }


def plot_somatic_spikes(data, ax=None, show_metrics=False):
    """Plot detected spikes on the provided axis or create a new figure.
    
    Args:
        model: The neuron model
        ax: Optional matplotlib axis for plotting
        
    Returns:
        matplotlib.axes.Axes: The plot axis
    """

    spike_times = data['spike_times']
    spike_values = data['spike_values']
    half_widths = data['half_widths']
    amplitudes = data['amplitudes']
    right_bases = data['right_bases']
    left_bases = data['left_bases']
    duration_ms = data['stimulus_duration']

    n_spikes = len(spike_times)

    if n_spikes == 0:
        return    

    print(f"Detected {n_spikes} spikes")
    print(f"Average spike half-width: {np.mean(half_widths):.2f} ms")
    print(f"Average spike amplitude: {np.mean(amplitudes):.2f} mV")
    print(f"Spike frequency: {n_spikes / duration_ms * 1000:.2f} Hz")
    
    ax.plot(spike_times, spike_values, 'o', color='red')
    ax.set_xlabel('Time (ms)')
    ax.set_ylabel('Amplitude (mV)')
    ax.set_title(f'Somatic spikes ({len(spike_times)} detected)')
    
    if show_metrics:
        for t, v, w, a, lb, rb in zip(spike_times, spike_values, half_widths, amplitudes, left_bases, right_bases):
            # plot spike amplitude
            ax.plot([t, t], [v, v - a], color='red', linestyle='--')
            # plot spike width
            ax.plot([t - 10*w/2, t + 10*w/2], [v - a/2, v - a/2], color='lawngreen', linestyle='--')


def calculate_fI_curve(model, duration=1000, prerun_time=0, min_amp=0, max_amp=1, n=5, **kwargs):
    """
    Calculate the frequency-current (f-I) curve of the neuron model.

    Parameters
    ----------
    model : Model
        The neuron model.
    duration : int
        Duration of the simulation in ms.
    min_amp : float
        Minimum amplitude of the current injection in nA.
    max_amp : float
        Maximum amplitude of the current injection in nA.
    n : int
        Number of amplitudes to test.

    Returns
    -------
    dict
        A dictionary containing the current amplitudes, firing rates, and voltages.
    """

    seg = model.seg_tree.root
    duration = duration
    
    amps = np.round(np.linspace(min_amp, max_amp, n), 4)
    iclamp = model.iclamps[seg]
    rates = []
    vs = {}
    for amp in amps:
        iclamp.amp = amp
        model.run(duration=duration, prerun_time=prerun_time)
        spike_data = detect_somatic_spikes(model, **kwargs)
        n_spikes = len(spike_data['spike_times'])
        rate = n_spikes / iclamp.dur * 1000
        rates.append(rate)
        vs[amp] = model.simulator.recordings['v'][seg]

    return {
        'current_amplitudes': amps,
        'firing_rates': rates,
        'voltages': vs,
        'time': model.simulator.t
    }


def plot_fI_curve(data, ax=None, vshift=200, **kwargs):
    """
    Plot the f-I curve and somatic voltage traces.

    Parameters
    ----------
    data : dict
        A dictionary containing the current amplitudes, firing rates, and voltages.
        Can be obtained from `calculate_fI_curve`.
    ax : matplotlib.axes.Axes, optional
        The axes to plot on. If two axes are provided, the first will show the somatic voltage traces and the second will show the f-I curve.
        If a single axis is provided, it will show the f-I curve only.
        If None, a new figure will be created.
    vshift : int, optional
        The vertical shift for the somatic voltage traces. Default is 200.
    """

    if ax is None:
        _, ax = plt.subplots(1, 2, figsize=(5, 5))

    amps = data['current_amplitudes']
    rates = data['firing_rates']
    vs = data['voltages']
    t = data['time']

    if isinstance(ax, (list, np.ndarray)):        
        for i, (amp, v) in enumerate(vs.items()):
            ax[0].plot(t, np.array(v) - i*vshift, label=f'{amp} nA')
        ax[0].set_title('Somatic spikes')
        ax[0].legend()
        ax[0].axis('off')
        ax = ax[1]
    
    ax.plot(amps, rates, color='gray', zorder=0)
    for a, r in zip(amps, rates):
        ax.plot(a, r, 'o', zorder=1)
    ax.set_xlabel('Current (nA)')
    ax.set_ylabel('Firing rate (Hz)')
    ax.set_title('f-I curve')


# =============================================================================
# DENDRITIC PROPERTIES
# =============================================================================

def calculate_voltage_attenuation(model):
    """
    Calculate the voltage attenuation along the dendrites.

    Parameters
    ----------
    model : Model
        The neuron model.

    Returns
    -------
    dict
        A dictionary containing the path distances, minimum voltages, and voltage attenuations
    """

    # Assuming one stimulation site and multiple recording sites including the stimulated site
    stimulated_segs = list(model.iclamps.keys())
    if len(stimulated_segs) != 1:
        print("Only one stimulation site is supported")
        return None
    recorded_segs = list(model.recordings['v'].keys())
    if len(recorded_segs) < 2:
        print("At least two recording sites are required")
        return None

    print(f"Stimulating segment: {stimulated_segs[0]}")
    print(f"Recording segments: {recorded_segs}")

    stimulated_seg = stimulated_segs[0]

    iclamp = model.iclamps[stimulated_seg]
    amp = iclamp.amp

    if amp >= 0:
        print("Stimulus amplitude must be negative")
        return None

    path_distances = [seg.path_distance() for seg in recorded_segs]

    start_ts = int(iclamp.delay / model.simulator.dt)
    stop_ts = int((iclamp.delay + iclamp.dur) / model.simulator.dt)

    voltage_at_stimulated = np.array(model.simulator.recordings['v'][stimulated_seg])[start_ts:stop_ts]
    voltages = [np.array(model.simulator.recordings['v'][seg])[start_ts:stop_ts] for seg in recorded_segs]


    # Calculate voltage displacement from the resting potential
    delta_v_at_stimulated = voltage_at_stimulated[0] - voltage_at_stimulated[-2]# np.min(voltage_at_stimulated)
    delta_vs = [v[0] - v[-2] for v in voltages] # np.min(v) for v in voltages]

    min_voltages = [np.min(v) for v in voltages]
    end_voltages = [v[-2] for v in voltages]

    attenuation = [dv / delta_v_at_stimulated for dv in delta_vs]

    return {
        'path_distances': path_distances,
        'min_voltages': min_voltages,
        'end_voltages': end_voltages,
        'attenuation': attenuation
    }


def plot_voltage_attenuation(data, ax=None):

    path_distances = data['path_distances']
    attenuation = data['attenuation']

    if ax is None:
        _, ax = plt.subplots()

    ax.plot(path_distances, attenuation, 'o-')
    ax.set_ylim(-0.1, 1.1)
    ax.set_xlabel('Path distance (um)')
    ax.set_ylabel('Voltage attenuation')
    ax.set_title('Voltage attenuation')

def calculate_dendritic_nonlinearity(model, duration=1000, prerun_time=0, max_weight=None, n=None):
    """Calculate the expected and observed voltage changes for a range of synaptic weights.

    Parameters
    ----------
    model : Model
        The neuron model.
    duration : int
        Duration of the simulation in ms.
    max_weight : int
        Maximum synaptic weight to test.

    Returns
    -------
    dict
        A dictionary containing the expected and observed voltage changes.
    """

    recorded_segs = list(model.recordings['v'].keys())
    seg = recorded_segs[0]

    populations = list(model.populations.values())
    if len(populations) != 1:
        print("Only one population is supported")
        return None
    population = populations[0]
    if population.N != 1:
        print("Only one synapse should be placed on the dendrite")
        return None

    start_ts = int(population.input_params['start'] / model.simulator.dt)

    vs = {}
    delta_vs = []
    min_weight = 1
    if max_weight is None or min_weight is None or n is None:
        max_weight = population.input_params['weight']
        n = max_weight + 1

    weights = np.linspace(min_weight, max_weight, n, dtype=int)
    weights = np.unique(weights)

    for w in weights:
        population.update_input_params(weight=w)
        model.run(duration=duration, prerun_time=prerun_time)
        v = np.array(model.simulator.recordings['v'][seg])
        v_start = v[start_ts]
        v_max = np.max(v[start_ts:])
        delta_v = v_max - v_start
        delta_vs.append(delta_v)
        vs[w] = v
    unitary_delta_v = delta_vs[0]
    expected_delta_vs = [w * unitary_delta_v for w in weights]

    return {
        'expected_response': expected_delta_vs,
        'observed_response': delta_vs,
        'voltages': vs,
        'weights': weights,
        'time': model.simulator.t
    }


def plot_dendritic_nonlinearity(data, ax=None, vshift=200, **kwargs):
    """
    Plot the dendritic nonlinearity based on expected and observed voltage changes.

    Parameters
    ----------
    data : dict
        A dictionary containing the expected and observed voltage changes.
        Can be obtained from `calculate_dendritic_nonlinearity`.
    ax : matplotlib.axes.Axes, optional
        The axes to plot on. If two axes are provided, the first will show the voltage traces and the second will show the dendritic nonlinearity.
        If a single axis is provided, it will show the dendritic nonlinearity only.
        If None, a new figure will be created.
    vshift : int, optional
        The vertical shift for the voltage traces.
    """
    
    if ax is None:
        _, ax = plt.subplots(1, 2, figsize=(10, 5))

    expected_delta_vs = data['expected_response']
    delta_vs = data['observed_response']
    vs = data['voltages']
    t = data['time']

    if isinstance(ax, (list, np.ndarray)):        
        for i, (weight, v) in enumerate(vs.items()):
            ax[0].plot(t, np.array(v) - i*vshift, label=f'{weight} synapses')
        ax[0].set_title('Voltage traces')
        ax[0].legend()
        ax[0].axis('off')
        ax = ax[1]
    
    ax.plot(expected_delta_vs, delta_vs, zorder=1)
    ax.plot(expected_delta_vs, expected_delta_vs, color='gray', linestyle='--', zorder=0)
    for ep, ob in zip(expected_delta_vs, delta_vs):
        ax.plot(ep, ob, 'o', zorder=2)
    ax.set_xlabel('Expected voltage change (mV)')
    ax.set_ylabel('Observed voltage change (mV)')
    ax.set_title('Dendritic nonlinearity')
    

def calculate_sag_ratio(model):
    """
    Calculate the sag ratio of the neuron model.

    Parameters
    ----------
    model : Model
        The neuron model.

    Returns
    -------
    dict
        A dictionary containing the sag ratio and intermediate values.
    """
    v, t, dt, iclamp = get_somatic_data(model)

    start_ts = int(iclamp.delay / dt)
    stop_ts = int((iclamp.delay + iclamp.dur) / dt)
    min_ts = np.argmin(v[start_ts:stop_ts]) + start_ts
    v_min = np.min(v[start_ts: min_ts])

    a = v[stop_ts] - v_min
    b = v[start_ts] - v_min

    sag_ratio = a / b if b != 0 else np.nan

    print(f"Sag ratio: {a:.2f}/{b:.2f} = {sag_ratio:.2f}")
    return {
        'a': a,
        'b': b,
        'sag_ratio': sag_ratio,
    }

