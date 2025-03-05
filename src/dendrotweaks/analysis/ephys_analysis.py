import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.signal import find_peaks, peak_widths
from scipy.optimize import curve_fit

def get_node_data(nodes):

    data = {
        'idx': [node.idx for node in nodes],
        'length': [node.length for node in nodes],
        'diam': [node.diam for node in nodes],
        'area': [node.area for node in nodes],
        'n_children': [len(node.children) for node in nodes]
    }

    return pd.DataFrame(data)


def calculate_section_statistics(sections, param_name=None):
    
    df = get_node_data(sections)

    stats = {
        'N_sections': len(df),
        'N_bifurcations': (df['n_children'] == 2).sum(),
        'N_terminations': (df['n_children'] == 0).sum(),
        'diam': {
            'min': np.round(df['diam'].min(), 2),
            'max': np.round(df['diam'].max(), 2),
            'mean': np.round(df['diam'].mean(), 2),
            'std': np.round(df['diam'].std(), 2)
        },
        'length': {
            'min': np.round(df['length'].min(), 2),
            'max': np.round(df['length'].max(), 2),
            'mean': np.round(df['length'].mean(), 2),
            'std': np.round(df['length'].std(), 2)
        },
        'area': {
            'min': np.round(df['area'].min(), 2),
            'max': np.round(df['area'].max(), 2),
            'mean': np.round(df['area'].mean(), 2),
            'std': np.round(df['area'].std(), 2)
        },
        'total_length': np.round(df['length'].sum(), 2),
        'total_area': np.round(df['area'].sum(), 2)
    }

    return stats


def calculate_cell_statistics(tree):

    all_sections = []
    for domain in tree.domains.values():
        all_sections.extend(domain.sections)

    return calculate_section_statistics(all_sections)


def calculate_domain_statistics(tree, domain_names=None, param_name=None):

    if domain_names is None:
        return calculate_cell_statistics(tree)
    if not isinstance(domain_names, list):
        raise ValueError("domain_names must be a list of strings")

    domains = [domain for domain in tree.domains.values() if domain.name in domain_names]

    stats = {}

    for domain in domains:
        stats[domain.name] = calculate_section_statistics(domain.sections)

    return stats
        

def calculate_segment_statistics(self, segments):

    df = self.get_node_data(segments)

    stats = {
        'N_segments': len(df),
        'N_bifurcations': (df['n_children'] == 2).sum(),
        'N_terminations': (df['n_children'] == 0).sum(),
        'diam': (np.round(df['diam'].mean(), 2), np.round(df['diam'].std(), 2), np.round(df['diam'].min(), 2), np.round(df['diam'].max(), 2)),
        'length': (np.round(df['length'].mean(), 2), np.round(df['length'].std(), 2), np.round(df['length'].min(), 2), np.round(df['length'].max(), 2)),
        'area': (np.round(df['area'].mean(), 2), np.round(df['area'].std(), 2), np.round(df['area'].min(), 2), np.round(df['area'].max(), 2)),
        'total_lenght': np.round(df['length'].sum(), 2),
        'total_area': np.round(df['area'].sum(), 2)
    }


def update_histogram(self, param_name, segments, **kwargs):
    if param not in ['diam', 'length', 'area']:
        raise ValueError(f"Invalid parameter: {param}")
    values = [seg.get_param_value(param_name) for seg in segments]
    hist, edges = np.histogram(values, **kwargs)
    return hist, edges


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
