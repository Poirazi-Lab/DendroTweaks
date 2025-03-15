import neuron
from neuron import h
from numpy import polyval
h.load_file('stdrun.hoc')
import numpy as np

import os

class Cell():
    """
    A class representing a biophysical NEURON model of a single neuron.
    """

    def __init__(self, swc_file):
        self.name = swc_file.split('/')[-1].replace('.swc', '').replace('.asc', '')
        self._load_morphology(swc_file)
        self.distribute_passive()
        self.set_geom_nseg()
        self.insert_mechanisms()
        self.distribute_parameters()
        
    ### Morphology methods ###

    def _load_morphology(self, fname):
        if fname.endswith('.swc'):
            self._load_swc(fname)
        else:
            raise ValueError(f"File type not supported: {fname}")

    def _load_swc(self, swc_file):
        h.load_file('import3d.hoc')
        swc_importer = h.Import3d_SWC_read()
        swc_importer.input(swc_file)
        imported_cell = h.Import3d_GUI(swc_importer, False)
        imported_cell.instantiate(self)

    def set_geom_nseg(self, d_lambda=0.1, f=100):
        for sec in self.all:
            sec.nseg = int((sec.L/(d_lambda*h.lambda_f(f, sec=sec)) + 0.9)/2)*2 + 1
        
    def distance(self, seg, from_seg=None):
        if from_seg is None:
            from_seg = self.soma[0](0.5)
        return h.distance(from_seg, seg)

    def domain_distance(self, seg):
        parent = self._find_parent_with_different_domain(seg.sec)
        if parent:
            return h.distance(parent(1), seg)
        return 0
    
    def _find_parent_with_different_domain(self, sec):
        parentseg = sec.parentseg()
        if not parentseg:
            return None
        parent = parentseg.sec
        while parent:
            if get_domain(parent(0.5)) != get_domain(sec(0.5)):
                return parent
            parentseg = parent.parentseg()
            if not parentseg:
                return None
            parent = parentseg.sec
        return None

    @property
    def all_segments(self):
        return [seg for sec in self.all for seg in sec]

    def insert_mechanisms(self):
        {% for domain, mechanisms in domains_to_mechs.items() %}
        for sec in self.{{ domain }}:
            {% for mechanism in mechanisms %}
                sec.insert('{{ mechanism }}')
            {%- endfor %}
        {% endfor %}

    def set_param(self, seg, param, mech, value):
        if param == 'Ra':
            setattr(seg.sec, param, value)
        if param == 'cm':
            setattr(seg, param, value)
        else:
            if seg.sec.has_membrane(mech):
                setattr(seg, param, value)
            else:
                if param in ['ena', 'ek', 'eca']:
                    if hasattr(seg, param):
                        setattr(seg, param, value)
                
    def distribute_passive(self):

        for seg in self.all_segments:

            domain = get_domain(seg)
            distance = self.distance(seg)
            domain_distance = self.domain_distance(seg)
            diam = seg.diam
            section_diam = seg.sec.diam

            {% for param, mech in params_to_mechs.items() -%}
            {% if param in ['cm', 'Ra']%}
            {% set groups = param_dict[param] -%}
            {% for group_name, distribution in groups.items() -%}
            {% set group = groups_dict[group_name] -%}
            if domain in {{ params_to_valid_domains[param][group_name] }}:
                {% if group.select_by -%}
                {% set min_val = group.min_value if group.min_value is not none else 0 -%}
                {% if group.max_value is not none -%}
                if {{ min_val }} < {{ group.select_by }} <= {{ group.max_value }}:
                {% else -%}
                if {{ min_val }} < {{ group.select_by }}:
                {% endif %}
                    {% if distribution.function_name == "constant" -%}
                    self.set_param(seg, "{{ param }}", "{{ mech }}", {{ distribution.parameters.value }})
                    {% elif distribution.function_name == "linear" -%}
                    self.set_param(seg, "{{ param }}", "{{ mech }}", linear(distance, slope={{ distribution.parameters.slope }}, intercept={{ distribution.parameters.intercept }}))
                    {% elif distribution.function_name == "polynomial" -%}
                    self.set_param(seg, "{{ param }}", "{{ mech }}", polyval(distance, coeffs={{ distribution.parameters.coeffs }}))
                    {% else -%}
                    self.set_param(seg, "{{ param }}", "{{ mech }}", {{ distribution.function_name }}(distance, **{{ distribution.parameters }}))
                    {% endif %}
                {% else -%}
                    {% if distribution.function_name == "constant" -%}
                    self.set_param(seg, "{{ param }}", "{{ mech }}", {{ distribution.parameters.value }})
                    {% elif distribution.function_name == "linear" -%}
                    self.set_param(seg, "{{ param }}", "{{ mech }}", linear(distance, slope={{ distribution.parameters.slope }}, intercept={{ distribution.parameters.intercept }}))
                    {% elif distribution.function_name == "polynomial" -%}
                    self.set_param(seg, "{{ param }}", "{{ mech }}", polyval(distance, coeffs={{ distribution.parameters.coeffs }}))
                    {% else -%}
                    self.set_param(seg, "{{ param }}", "{{ mech }}", {{ distribution.function_name }}(distance, **{{ distribution.parameters }}))
                    {% endif %}
                {% endif %}
            {% endfor -%}
            {% endif -%}
            {% endfor %}

    def distribute_parameters(self):

        for seg in self.all_segments:

            domain = get_domain(seg)
            distance = self.distance(seg)
            domain_distance = self.domain_distance(seg)
            diam = seg.diam
            section_diam = seg.sec.diam

            {% for param, mech in params_to_mechs.items() -%}
            {% if param not in ['cm', 'Ra']%}
            {% set groups = param_dict[param] -%}
            {% for group_name, distribution in groups.items() -%}
            {% set group = groups_dict[group_name] -%}
            if domain in {{ params_to_valid_domains[param][group_name] }}:
                {% if group.select_by -%}
                {% set min_val = group.min_value if group.min_value is not none else 0 -%}
                {% if group.max_value is not none -%}
                if {{ min_val }} < {{ group.select_by }} <= {{ group.max_value }}:
                {% else -%}
                if {{ min_val }} < {{ group.select_by }}:
                {% endif %}
                    {% if distribution.function_name == "constant" -%}
                    self.set_param(seg, "{{ param }}", "{{ mech }}", {{ distribution.parameters.value }})
                    {% elif distribution.function_name == "linear" -%}
                    self.set_param(seg, "{{ param }}", "{{ mech }}", linear(distance, slope={{ distribution.parameters.slope }}, intercept={{ distribution.parameters.intercept }}))
                    {% elif distribution.function_name == "polynomial" -%}
                    self.set_param(seg, "{{ param }}", "{{ mech }}", polyval(distance, coeffs={{ distribution.parameters.coeffs }}))
                    {% else -%}
                    self.set_param(seg, "{{ param }}", "{{ mech }}", {{ distribution.function_name }}(distance, **{{ distribution.parameters }}))
                    {% endif %}
                {% else -%}
                    {% if distribution.function_name == "constant" -%}
                    self.set_param(seg, "{{ param }}", "{{ mech }}", {{ distribution.parameters.value }})
                    {% elif distribution.function_name == "linear" -%}
                    self.set_param(seg, "{{ param }}", "{{ mech }}", linear(distance, slope={{ distribution.parameters.slope }}, intercept={{ distribution.parameters.intercept }}))
                    {% elif distribution.function_name == "polynomial" -%}
                    self.set_param(seg, "{{ param }}", "{{ mech }}", polyval(distance, coeffs={{ distribution.parameters.coeffs }}))
                    {% else -%}
                    self.set_param(seg, "{{ param }}", "{{ mech }}", {{ distribution.function_name }}(distance, **{{ distribution.parameters }}))
                    {% endif %}
                {% endif %}
            {% endfor -%}
            {% endif -%}
            {% endfor %}

    def add_stimuli(self):
        self.add_iclamps()
        self.add_synapses()

    def add_recordings(self):
        recordings = []
        {% for seg, rec in recordings.items() %}
        rec = h.Vector()
        rec.record(self.{{seg._section.domain}}[{{seg._section.domain_idx}}]({{seg.x}})._ref_v)
        recordings.append(rec)
        {% endfor %}
        return recordings

    def add_iclamps(self):
        iclamps = []
        {% for seg, iclamp in iclamps.items() %}
        iclamp = h.IClamp(self.{{seg._section.domain}}[{{seg._section.domain_idx}}]({{seg.x}}))
        iclamp.delay = {{ iclamp.delay }}
        iclamp.dur = {{ iclamp.dur }}
        iclamp.amp = {{ iclamp.amp }}
        iclamps.append(iclamp)
        {% endfor %}
        return iclamps


def get_domain(seg):
    sec = seg.sec
    sec_name = sec.name()
    domain_name = sec_name.split('.')[-1].split('[')[0]
    return domain_name

def linear(x, slope=0, intercept=0):
    return slope * x + intercept

def sinusoidal(x, amplitude=0, frequency=1, phase=0):
    return amplitude * np.sin(frequency * x + phase)
    # return amplitude * np.sin(2 * np.pi * frequency * x + phase)


def init_simulation(cvode=False, temperature=37, dt=0.025, v_init=-70):
    h.CVode().active(cvode)
    h.celsius = temperature
    h.dt = dt
    h.stdinit()
    h.init()
    h.finitialize(v_init)
    if h.cvode.active():
        h.cvode.re_init()
    else:
        h.fcurrent()
    h.frecord_init()


def run(duration=300, **kwargs):
    init_simulation(**kwargs)
    h.continuerun(duration)


def load_mechanisms(path_to_mod, recompile=False):

    if recompile:
        cwd = os.getcwd()
        os.chdir(path_to_mod)
        os.system('nrnivmodl')
        os.chdir(cwd)
        print(f'Compiled mod files in "{path_to_mod}"')

    neuron.load_mechanisms(path_to_mod)
    print(f'Loaded mod files from "{path_to_mod}"')