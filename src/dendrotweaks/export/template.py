import neuron
from neuron import h
from numpy import polyval


class Cell():
    """
    A class representing a biophysical NEURON model of a single neuron.
    """

    def __init__(self, swc_file):
        self.name = swc_file.split('/')[-1].replace('.swc', '').replace('.asc', '')
        self._load_morphology(swc_file)
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
        if self.segments: del self.segments
        for sec in self.all:
            sec.nseg = int((sec.L/(d_lambda*h.lambda_f(f, sec=sec)) + 0.9)/2)*2 + 1
        
    def distance(self, seg, from_seg=None):
        if from_seg is None:
            from_seg = self.soma[0](0.5)
        return h.distance(from_seg, seg)

    @property
    def all_segments():
        return [seg for sec in self.all for seg in sec]

    def insert_mechanisms(self):
        {% for domain, mechanisms in domains_dict.items() %}
        for sec in self.{{ domain }}:
            {% for mechanism in mechanisms %}
                sec.insert('{{ mechanism }}')
            {%- endfor %}
        {% endfor %}


    def distribute_parameters(self):

        for seg in self.all_segments:

            domain = get_domain(seg)
            distance = self.distance(seg)
            domain_distance = self.domain_distance(seg)
            diam = seg.diam
            sec_diam = seg.sec.diam

            {% for param, groups in param_dict.items() -%}
            {% for group_name, distribution in groups.items() -%}
            {% set group = groups_dict[group_name] -%}
            if domain in {{ group.domains }}:
                {% if group.select_by -%}
                {% set min_val = group.min_value if group.min_value is not none else 0 -%}
                {% if group.max_value is not none -%}
                if {{ min_val }} < {{ group.select_by }} < {{ group.max_value }}:
                {% else -%}
                if {{ min_val }} < {{ group.select_by }}:
                {% endif %}
                    {% if distribution.function_name == "constant" -%}
                    setattr(seg, "{{ param }}", {{ distribution.parameters.value }})
                    {% elif distribution.function_name == "linear" -%}
                    setattr(seg, "{{ param }}", linear(distance, slope={{ distribution.parameters.slope }}, intercept={{ distribution.parameters.intercept }}))
                    {% elif distribution.function_name == "polynomial" -%}
                    setattr(seg, "{{ param }}", polyval(distance, coeffs={{ distribution.parameters.coeffs }}))
                    {% else -%}
                    setattr(seg, "{{ param }}", {{ distribution.function_name }}(distance, **{{ distribution.parameters }}))
                    {% endif %}
                {% else -%}
                {% if distribution.function_name == "constant" -%}
                    setattr(seg, "{{ param }}", {{ distribution.parameters.value }})
                {% elif distribution.function_name == "linear" -%}
                    setattr(seg, "{{ param }}", linear(distance, slope={{ distribution.parameters.slope }}, intercept={{ distribution.parameters.intercept }}))
                {% elif distribution.function_name == "polynomial" -%}
                    setattr(seg, "{{ param }}", polyval(distance, coeffs={{ distribution.parameters.coeffs }}))
                {% else -%}
                    setattr(seg, "{{ param }}", {{ distribution.function_name }}(distance, **{{ distribution.parameters }}))
                {% endif %}
                {% endif %}
            {% endfor -%}
            {% endfor %}


    def add_stimuli(self):
        self.add_iclamps()
        self.add_synapses()


def get_domain(seg):
    sec = seg.sec
    sec_name = sec.name()
    domain_name = sec_name.split('.')[-1]
    return domain_name

def linear(x, slope=0, intercept=0):
    return slope * x + intercept

def sinusoidal(x, amplitude=0, frequency=1, phase=0):
    return amplitude * np.sin(2 * np.pi * frequency * x + phase)