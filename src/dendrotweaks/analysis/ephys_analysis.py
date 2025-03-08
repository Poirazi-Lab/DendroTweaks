import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.signal import find_peaks, peak_widths
from scipy.optimize import curve_fit


# =============================================================================
# PASSIVE PROPERTIES
# =============================================================================

def get_somatic_data(model):
    seg = model.seg_tree.root
    iclamp = model.iclamps[seg]

    v = np.array(model.simulator.vs[seg])
    t = np.array(model.simulator.t)
    dt = model.simulator.dt

    return v, t, dt, iclamp


def calculate_input_resistance(model):
    
    v, t, dt, iclamp = get_somatic_data(model)

    v_min = np.min(v)
    
    amp = iclamp.amp
    start_ts = iclamp.delay / dt
    end_ts = int((iclamp.delay + iclamp.dur) / dt)
    v_onset = v[int(start_ts)]
    v_offset = v[int(end_ts)]
    
    R = (v_onset - v_offset) / amp
    print(f"Input resistance: {R:.2f} MOhm")

    return {
        'v_onset': v_onset,
        'v_offset': v_offset,
        'R': R,
        'I': amp
    }


def exp_decay(t, A, tau):
    return A * np.exp(-t / tau)


def calculate_time_constant(model):
    v, t, dt, iclamp = get_somatic_data(model)

    start_ts = int(iclamp.delay / dt)
    stop_ts = int((iclamp.delay + iclamp.dur) / dt)
    min_ts = np.argmin(v[start_ts:stop_ts]) + start_ts
    v_min = np.min(v[start_ts: min_ts])
    v_decay = v[start_ts: min_ts] - v_min
    t_decay = t[start_ts: min_ts] - t[start_ts]
    popt, _ = curve_fit(exp_decay, t_decay, v_decay, p0=[1, 100])
    tau = popt[1]
    A = popt[0]
    print(f"Membrane time constant: {tau:.2f} ms")
    return {
        'tau': tau,
        'A': A,
        'start_t': start_ts * dt,
        't_decay': t_decay,
        'v_decay': v_decay
    }


def plot_passive_properties(model, ax=None):
    data_rm = calculate_input_resistance(model)
    data_tau = calculate_time_constant(model)
    
    if ax is None:
        _, ax = plt.subplots()

    ax.set_title(f"Rm: {data_rm['R']:.2f} MOhm, Tau: {data_tau['tau']:.2f} ms")
    ax.axhline(data_rm['v_onset'], color='gray', linestyle='--', label='V onset')
    ax.axhline(data_rm['v_offset'], color='gray', linestyle='--', label='V offset')
    
    # Shift the exp_decay output along the y-axis
    shifted_exp_decay = exp_decay(data_tau['t_decay'], data_tau['A'], data_tau['tau']) + data_rm['v_offset']
    ax.plot(data_tau['t_decay'] + data_tau['start_t'], shifted_exp_decay, color='red', label='Exp. fit')
    ax.legend()


# =============================================================================
# ACTIVE PROPERTIES
# =============================================================================

def detect_somatic_spikes(model, **kwargs):
    """Detect somatic spikes in the model and calculate metrics.
    
    Returns:
        dict: A dictionary containing spike metrics.
    """
    seg = model.seg_tree.root
            
    v = np.array(model.simulator.vs[seg])
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


def calculate_fI_curve(model, duration=1000, min_amp=0, max_amp=1, n=5, **kwargs):
    
    seg = model.seg_tree.root
    duration = duration
    
    amps = np.round(np.linspace(min_amp, max_amp, n), 4)
    iclamp = model.iclamps[seg]
    rates = []
    vs = {}
    for amp in amps:
        iclamp.amp = amp
        model.simulator.run(duration)
        spike_data = detect_somatic_spikes(model, **kwargs)
        n_spikes = len(spike_data['spike_times'])
        rate = n_spikes / iclamp.dur * 1000
        rates.append(rate)
        vs[amp] = model.simulator.vs[seg]
    return amps, rates, vs


def plot_fI_curve(model, ax=None, **kwargs):

    if ax is None:
        _, ax = plt.subplots(1, 2, figsize=(5, 5))

    amps, rates, vs = calculate_fI_curve(model, **kwargs)
    t = model.simulator.t

    for i, (amp, v) in enumerate(vs.items()):
        ax[0].plot(t, np.array(v) - i*200, label=f'{amp} nA')
    # ax[0].set_xlabel('Time (ms)')
    # ax[0].set_ylabel('Voltage (mV)')
    ax[0].set_title('Somatic spikes')
    ax[0].legend()
    ax[0].spines['top'].set_visible(False)
    ax[0].spines['right'].set_visible(False)
    ax[0].spines['bottom'].set_visible(False)
    ax[0].spines['left'].set_visible(False)
    ax[0].set_xticks([])
    ax[0].set_yticks([])
    
    ax[1].plot(amps, rates, color='gray', zorder=0)
    for a, r in zip(amps, rates):
        ax[1].scatter(a, r, s=50, edgecolor='white')
    ax[1].set_xlabel('Current (nA)')
    ax[1].set_ylabel('Firing rate (Hz)')
    ax[1].set_title('f-I curve')


# =============================================================================
# DENDRITIC PROPERTIES
# =============================================================================

def calculate_voltage_attenuation(model):

    # Assuming one stimulation site and multiple recording sites including the stimulated site
    stimulated_segs = list(model.iclamps.keys())
    if len(stimulated_segs) != 1:
        print("Only one stimulation site is supported")
        return None
    recorded_segs = list(model.recordings.keys())
    if len(recorded_segs) < 2:
        print("At least two recording sites are required")
        return None

    stimulated_seg = stimulated_segs[0]

    iclamp = model.iclamps[stimulated_seg]
    amp = iclamp.amp

    if amp >= 0:
        print("Stimulus amplitude must be negative")
        return None

    path_distances = [seg.path_distance() for seg in recorded_segs]

    start_ts = int(iclamp.delay / model.simulator.dt)
    stop_ts = int((iclamp.delay + iclamp.dur) / model.simulator.dt)

    voltage_at_stimulated = np.array(model.simulator.vs[stimulated_seg])[start_ts:stop_ts]
    voltages = [np.array(model.simulator.vs[seg])[start_ts:stop_ts] for seg in recorded_segs]

    # Calculate voltage displacement from the resting potential
    delta_v_at_stimulated = voltage_at_stimulated[0] - np.min(voltage_at_stimulated)
    delta_vs = [v[0] - np.min(v) for v in voltages]

    min_voltages = [np.min(v) for v in voltages]

    attenuation = [dv / delta_v_at_stimulated for dv in delta_vs]

    return path_distances, min_voltages, attenuation


def plot_voltage_attenuation(model, ax=None):

    path_distances, min_voltages, attenuation = calculate_voltage_attenuation(model)

    if ax is None:
        _, ax = plt.subplots()

    ax.plot(path_distances, attenuation, 'o-')
    ax.set_ylim(-0.1, 1.1)
    ax.set_xlabel('Path distance (um)')
    ax.set_ylabel('Voltage attenuation')
    ax.set_title('Voltage attenuation')

def calculate_dendritic_nonlinearity(model, duration=1000, max_weight=None, n=None):
    """Calculate the expected and observed voltage changes for a range of synaptic weights.

    Parameters
    ----------
    model : Model
        The neuron model.
    duration : int
        Duration of the simulation in ms.
    max_weight : int
        Maximum synaptic weight to test.
    """

    recorded_segs = list(model.recordings.keys())
    seg = recorded_segs[0]

    populations = [pop for pops in model.populations.values() for pop in pops.values()]
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
        model.simulator.run(duration)
        v = np.array(model.simulator.vs[seg])
        v_start = v[start_ts]
        v_max = np.max(v[start_ts:])
        delta_v = v_max - v_start
        delta_vs.append(delta_v)
        vs[w] = v
    unitary_delta_v = delta_vs[0]
    expected_delta_vs = [w * unitary_delta_v for w in weights]

    return expected_delta_vs, delta_vs, vs


def plot_dendritic_nonlinearity(model, ax=None, **kwargs):
    
    if ax is None:
        _, ax = plt.subplots(1, 2, figsize=(10, 5))

    expected_delta_vs, delta_vs, vs = calculate_dendritic_nonlinearity(model, **kwargs)
    t = model.simulator.t

    for i, (weight, v) in enumerate(vs.items()):
        ax[0].plot(t, np.array(v) - i*200, label=f'{weight} synapses')
    ax[0].set_title('Voltage traces')
    ax[0].legend()
    ax[0].spines['top'].set_visible(False)
    ax[0].spines['right'].set_visible(False)
    ax[0].spines['bottom'].set_visible(False)
    ax[0].spines['left'].set_visible(False)
    ax[0].set_xticks([])
    ax[0].set_yticks([])

    ax[1].plot(expected_delta_vs, delta_vs, 'o-')
    ax[1].plot(expected_delta_vs, expected_delta_vs, color='gray', linestyle='--')
    ax[1].set_xlabel('Expected voltage change (mV)')
    ax[1].set_ylabel('Observed voltage change (mV)')
    ax[1].set_title('Dendritic nonlinearity')
    



