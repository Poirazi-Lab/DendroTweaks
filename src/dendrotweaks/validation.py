import numpy as np
from scipy.signal import find_peaks, peak_widths
from scipy.optimize import curve_fit
import logging

logger = logging.getLogger(__name__)

class MorphologicalValidation:
    def __init__(self, model):
        self.model = model

    def stats(self):
        diams = [seg.diam for seg in self.model.selected_segs]
        lengths = [sec.L for sec in self.model.selected_secs]
        areas = [seg.area() for seg in self.model.selected_segs]
        stats = {
            "N_soma_children": len(self.model.cell.soma[0].children()),
            "N_sections": len(self.model.selected_secs),
            "N_segments": len(self.model.selected_segs),
            "N_bifurcations": sum([1 for sec in self.model.selected_secs if len(sec.children()) == 2]),
            "average_diam": (np.round(np.mean(diams), 2), np.round(np.std(diams), 2)),
            "average_length": (np.round(np.mean(lengths), 2), np.round(np.std(lengths), 2)),
            "average_area": (np.round(np.mean(areas), 2), np.round(np.std(areas), 2)),
            "total_length": np.round(np.sum(lengths), 2),
            "total_area": np.round(np.sum(areas), 2)
        }
        return stats

    def update_histogram(self):
        areas = [seg.area() for seg in self.model.selected_segs]
        hist, edges = np.histogram(areas, bins='auto')
        return hist, edges


def detect_spikes(trace, dt):
    peaks, _ = find_peaks(trace, height=0, distance=10)
    widths, heights, left_ips, right_ips = peak_widths(trace, peaks, rel_height=0.5)
    widths = widths * dt
    amplitudes = 2 * (trace[peaks] - heights)
    spike_data = {
        "peaks": peaks * dt,
        "widths": widths,
        "amplitudes": amplitudes
    }
    return spike_data

class VoltageTraceValidation:
    def __init__(self, model):
        self.model = model

    def detect_somatic_spikes(self):
        seg = self.model.cell.soma[0](0.5)
        if self.model.simulator.recordings.get(seg):
            v = np.array(self.model.simulator.recordings[seg].to_python())
            t = np.array(self.model.simulator.t)

        peaks, _ = find_peaks(v, height=0, distance=10)
        widths, heights, left_ips, right_ips = peak_widths(v, peaks, rel_height=0.5)
        _dt = self.model.simulator.dt
        widths = widths * _dt
        amplitudes = 2 * (v[peaks] - heights)
        return t[peaks], widths, amplitudes

    def calculate_input_resistance(self):
        seg = self.model.cell.soma[0](0.5)
        if self.model.simulator.recordings.get(seg):
            v = np.array(self.model.simulator.recordings[seg].to_python())
            v_min = np.min(v)
            i = self.model.iclamps[seg].amp
            start_ts = self.model.iclamps[seg].delay / self.model.simulator.dt
            end_ts = int((self.model.iclamps[seg].delay + self.model.iclamps[seg].dur) / self.model.simulator.dt)
            v_onset = v[int(start_ts)]
            v_offset = v[int(end_ts)]
        else:
            return None
        
        R = (v_onset - v_offset) / i
        return v_onset, v_offset, i, R

    def calculate_time_constant(self):
        def exp_decay(t, A, tau):
            return A * np.exp(-t / tau)

        seg = self.model.cell.soma[0](0.5)
        if self.model.simulator.recordings.get(seg):
            v = np.array(self.model.simulator.recordings[seg].to_python())
        else:
            return None
        t = np.array(self.model.simulator.t)
        _dt = self.model.simulator.dt
        start_ts = int(self.model.iclamps[seg].delay / _dt)
        stop_ts = int((self.model.iclamps[seg].delay + self.model.iclamps[seg].dur) / _dt)
        min_ts = np.argmin(v[start_ts:stop_ts]) + start_ts
        v_min = np.min(v[start_ts: min_ts])
        v_decay = v[start_ts: min_ts] - v_min
        t_decay = t[start_ts: min_ts] - t[start_ts]
        popt, _ = curve_fit(exp_decay, t_decay, v_decay, p0=[1, 100])
        tau = popt[1]
        return tau

    def sag_ratio(self, seg):
        start_ts = int(self.model.iclamps[seg].delay / self.model.simulator.dt)
        stop_ts = int((self.model.iclamps[seg].delay + self.model.iclamps[seg].dur) / self.model.simulator.dt)
        if self.model.iclamps.get(seg):
            i = self.model.iclamps[seg].amp
            if i >= 0:
                return None
            else:
                v = np.array(self.model.simulator.recordings[seg])
                v_end = v[stop_ts]
                v_min = np.min(v)
                v_start = v[start_ts]
                sag_ratio = (v_end - v_min) / (v_start - v_min)
                return sag_ratio
        else:
            return None

    def attenuation(self, stimulated_seg, selected_segs):
        amp = self.model.iclamps[stimulated_seg].amp
        if amp >= 0:
            return None
        else:
            distances = [self.model.cell.distance_from_soma(seg) for seg in selected_segs]
            start_ts = int(self.model.iclamps[stimulated_seg].delay / self.model.simulator.dt)
            stop_ts = int((self.model.iclamps[stimulated_seg].delay + self.model.iclamps[stimulated_seg].dur) / self.model.simulator.dt)
            voltage_at_stimulated = np.array(self.model.simulator.recordings[stimulated_seg])[start_ts:stop_ts]
            voltages = [np.array(self.model.simulator.recordings[seg])[start_ts:stop_ts] for seg in selected_segs]
            delta_v_at_stimulated = voltage_at_stimulated[0] - np.min(voltage_at_stimulated)
            delta_vs = [v[0] - np.min(v) for v in voltages]
            min_voltages = [np.min(v) for v in voltages]
            attenuation = [dv / delta_v_at_stimulated for dv in delta_vs]
            return distances, min_voltages, attenuation

    def nonlinearity(self, seg, population, duration):
        start_ts = int(population.start / self.model.simulator.dt)
        delta_vs = []
        max_weight = population.weight
        for i in range(1, max_weight + 1):
            population.weight = i
            self.model.simulator.run(duration)
            vs = np.array(self.model.simulator.recordings[seg]).flatten()
            vs = np.array(vs).flatten()
            v_start = vs[start_ts]
            v_max = np.max(vs[start_ts:])
            delta_v = v_max - v_start
            delta_vs.append(delta_v)
        unitary_delta_v = delta_vs[0]
        expected_delta_vs = [i * unitary_delta_v for i in range(1, max_weight + 1)]
        return expected_delta_vs, delta_vs

    def fI_curve(self, seg, duration):
        firing = []
        for amp in range(0, 1001, 100):
            self.model.iclamps[seg].amp = amp * 1e-3
            self.model.simulator.run(duration)
            spike_times, _, _ = self.detect_somatic_spikes()
            firing.append(len(spike_times))
        return np.arange(0, 1001, 100), firing
