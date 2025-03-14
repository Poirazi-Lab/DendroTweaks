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
        
        for sec in self.apic:
            
                sec.insert('Kv')
                sec.insert('CaHVA')
                sec.insert('Leak')
                sec.insert('Na')
                sec.insert('Km')
                sec.insert('CaLVA')
                sec.insert('Ka')
                sec.insert('KCa')
                sec.insert('CaDyn')
        
        for sec in self.soma:
            
                sec.insert('Kv')
                sec.insert('CaHVA')
                sec.insert('Leak')
                sec.insert('Na')
                sec.insert('Km')
                sec.insert('CaLVA')
                sec.insert('Ka')
                sec.insert('KCa')
                sec.insert('CaDyn')
        
        for sec in self.dend:
            
                sec.insert('Kv')
                sec.insert('CaHVA')
                sec.insert('Leak')
                sec.insert('Na')
                sec.insert('Km')
                sec.insert('CaLVA')
                sec.insert('Ka')
                sec.insert('KCa')
                sec.insert('CaDyn')
        
        for sec in self.axon:
            
                sec.insert('Leak')
        


    def distribute_parameters(self):

        for seg in self.all_segments:

            domain = get_domain(seg)
            distance = self.distance(seg)
            domain_distance = self.domain_distance(seg)
            diam = seg.diam
            sec_diam = seg.sec.diam

            if domain in ['apic', 'soma', 'dend', 'axon']:
                setattr(seg, "cm", 2)
                
                
            if domain in ['soma']:
                setattr(seg, "cm", 1)
                
                
            if domain in ['apic', 'soma', 'dend', 'axon']:
                setattr(seg, "Ra", 100)
                
                
            if domain in ['apic', 'soma', 'dend', 'axon']:
                setattr(seg, "gbar_Leak", 9.09090909090909e-05)
                
                
            if domain in ['apic', 'soma', 'dend', 'axon']:
                setattr(seg, "e_Leak", -79)
                
                
            if domain in ['apic', 'soma', 'dend', 'axon']:
                setattr(seg, "depth_CaDyn", 0.1)
                
                
            if domain in ['apic', 'soma', 'dend', 'axon']:
                setattr(seg, "tau_CaDyn", 50)
                
                
            if domain in ['apic', 'soma', 'dend', 'axon']:
                setattr(seg, "cainf_CaDyn", 0.0001)
                
                
            if domain in ['apic', 'soma', 'dend', 'axon']:
                setattr(seg, "gamma_CaDyn", 1)
                
                
            if domain in ['apic', 'soma', 'dend', 'axon']:
                setattr(seg, "gbar_Na", 0.0)
                
                
            if domain in ['soma']:
                setattr(seg, "gbar_Na", 0.0505)
                
                
            if domain in ['dend', 'apic']:
                setattr(seg, "gbar_Na", 0.0303)
                
                
            if domain in ['apic', 'soma', 'dend', 'axon']:
                setattr(seg, "Rma_Na", 0.182)
                
                
            if domain in ['apic', 'soma', 'dend', 'axon']:
                setattr(seg, "Rmb_Na", 0.14)
                
                
            if domain in ['apic', 'soma', 'dend', 'axon']:
                setattr(seg, "v12m_Na", -30)
                
                
            if domain in ['apic', 'soma', 'dend', 'axon']:
                setattr(seg, "qm_Na", 9.8)
                
                
            if domain in ['apic', 'soma', 'dend', 'axon']:
                setattr(seg, "Rhb_Na", 0.0091)
                
                
            if domain in ['apic', 'soma', 'dend', 'axon']:
                setattr(seg, "Rha_Na", 0.024)
                
                
            if domain in ['apic', 'soma', 'dend', 'axon']:
                setattr(seg, "v12ha_Na", -45)
                
                
            if domain in ['apic', 'soma', 'dend', 'axon']:
                setattr(seg, "v12hb_Na", -70)
                
                
            if domain in ['apic', 'soma', 'dend', 'axon']:
                setattr(seg, "qh_Na", 5)
                
                
            if domain in ['apic', 'soma', 'dend', 'axon']:
                setattr(seg, "v12hinf_Na", -60)
                
                
            if domain in ['apic', 'soma', 'dend', 'axon']:
                setattr(seg, "qhinf_Na", 6.2)
                
                
            if domain in ['apic', 'soma', 'dend', 'axon']:
                setattr(seg, "ena", 60)
                
                
            if domain in ['apic', 'soma', 'dend', 'axon']:
                setattr(seg, "gbar_KCa", 0.0)
                
                
            if domain in ['soma']:
                setattr(seg, "gbar_KCa", 0.00021)
                
                
            if domain in ['dend', 'apic']:
                setattr(seg, "gbar_KCa", 0.00021)
                
                
            if domain in ['apic', 'soma', 'dend', 'axon']:
                setattr(seg, "ek", -80)
                
                
            if domain in ['apic', 'soma', 'dend', 'axon']:
                setattr(seg, "gbar_Kv", 0.0)
                
                
            if domain in ['soma']:
                setattr(seg, "gbar_Kv", 0.005)
                
                
            if domain in ['dend', 'apic']:
                setattr(seg, "gbar_Kv", 0.00015)
                
                
            if domain in ['apic', 'soma', 'dend', 'axon']:
                setattr(seg, "v12_Kv", 25)
                
                
            if domain in ['apic', 'soma', 'dend', 'axon']:
                setattr(seg, "q_Kv", 9)
                
                
            if domain in ['apic', 'soma', 'dend', 'axon']:
                setattr(seg, "gbar_Ka", 0.0)
                
                
            if domain in ['soma']:
                setattr(seg, "gbar_Ka", 0.0054)
                
                
            if domain in ['dend', 'apic']:
                if 0 < section_diam < 0.8:
                
                    setattr(seg, "gbar_Ka", 0.108)
                    
                
            if domain in ['dend', 'apic']:
                if 0.8 < section_diam:
                
                    setattr(seg, "gbar_Ka", 0.0108)
                    
                
            if domain in ['apic', 'soma', 'dend', 'axon']:
                setattr(seg, "gbar_CaHVA", 0.0)
                
                
            if domain in ['soma']:
                setattr(seg, "gbar_CaHVA", 5e-06)
                
                
            if domain in ['dend']:
                setattr(seg, "gbar_CaHVA", linear(distance, slope=1e-08, intercept=5e-06))
                
                
            if domain in ['apic']:
                if 0 < domain_distance < 260:
                
                    setattr(seg, "gbar_CaHVA", sinusoidal(distance, **{'amplitude': 4.923e-06, 'frequency': 0.008758, 'phase': 0.8656}))
                    
                
            if domain in ['apic']:
                if 260 < domain_distance:
                
                    setattr(seg, "gbar_CaHVA", 2e-06)
                    
                
            if domain in ['apic', 'soma', 'dend', 'axon']:
                setattr(seg, "eca", 140)
                
                
            if domain in ['apic', 'soma', 'dend', 'axon']:
                setattr(seg, "gbar_Km", 0.0)
                
                
            if domain in ['soma']:
                setattr(seg, "gbar_Km", 0.0002794)
                
                
            if domain in ['dend', 'apic']:
                setattr(seg, "gbar_Km", 0.000127)
                
                
            if domain in ['apic', 'soma', 'dend', 'axon']:
                setattr(seg, "v12_Km", -30)
                
                
            if domain in ['apic', 'soma', 'dend', 'axon']:
                setattr(seg, "q_Km", 9)
                
                
            if domain in ['apic', 'soma', 'dend', 'axon']:
                setattr(seg, "gbar_CaLVA", 0.0)
                
                
            if domain in ['soma']:
                setattr(seg, "gbar_CaLVA", 3e-05)
                
                
            if domain in ['dend']:
                setattr(seg, "gbar_CaLVA", linear(distance, slope=6e-08, intercept=3e-05))
                
                
            if domain in ['apic']:
                if 0 < domain_distance < 260:
                
                    setattr(seg, "gbar_CaLVA", sinusoidal(distance, **{'amplitude': 2.9538e-05, 'frequency': 0.008758, 'phase': 0.8656}))
                    
                
            if domain in ['apic']:
                if 260 < domain_distance:
                
                    setattr(seg, "gbar_CaLVA", 1.2e-05)
                    
                
            

    def add_stimuli(self):
        self.add_iclamps()
        self.add_synapses()

    def add_recordings(self):
        recordings = {}
        
        rec = h.Vector()
        rec.record(self.soma[0](0.5)._ref_v)
        recordings[Segment(idx=0)] = rec
        
        return recordings

    def add_iclamps(self):
        iclamps = {}
        
        iclamp = h.IClamp(self.soma[0](0.5))
        iclamp.delay = 50.0
        iclamp.dur = 900.0
        iclamp.amp = 0.162
        iclamps[Segment(idx=0)] = iclamp
        
        return iclamps


def get_domain(seg):
    sec = seg.sec
    sec_name = sec.name()
    domain_name = sec_name.split('.')[-1]
    return domain_name

def linear(x, slope=0, intercept=0):
    return slope * x + intercept

def sinusoidal(x, amplitude=0, frequency=1, phase=0):
    return amplitude * np.sin(2 * np.pi * frequency * x + phase)


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


def run(duration=300):
    init_simulation()
    h.continuerun(duration)