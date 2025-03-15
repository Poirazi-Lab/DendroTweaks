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
        
        for sec in self.axon:
            
                sec.insert('Leak')
        
        for sec in self.dend:
            
                sec.insert('Na')
                sec.insert('Leak')
                sec.insert('Ka')
                sec.insert('Kv')
                sec.insert('sNa')
                sec.insert('CaLVA')
                sec.insert('CaDyn')
                sec.insert('Km')
                sec.insert('KCa')
                sec.insert('CaHVA')
        
        for sec in self.soma:
            
                sec.insert('Na')
                sec.insert('Leak')
                sec.insert('Ka')
                sec.insert('Kv')
                sec.insert('sNa')
                sec.insert('CaLVA')
                sec.insert('CaDyn')
                sec.insert('Km')
                sec.insert('KCa')
                sec.insert('CaHVA')
        
        for sec in self.apic:
            
                sec.insert('Na')
                sec.insert('Leak')
                sec.insert('Ka')
                sec.insert('Kv')
                sec.insert('sNa')
                sec.insert('CaLVA')
                sec.insert('CaDyn')
                sec.insert('Km')
                sec.insert('KCa')
                sec.insert('CaHVA')
        

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

            
            if domain in ['axon', 'dend', 'soma', 'apic']:
                self.set_param(seg, "cm", "Independent", 2)
                    
                
            if domain in ['soma']:
                self.set_param(seg, "cm", "Independent", 1)
                    
                
            
            if domain in ['axon', 'dend', 'soma', 'apic']:
                self.set_param(seg, "Ra", "Independent", 100)
                    
                
            

    def distribute_parameters(self):

        for seg in self.all_segments:

            domain = get_domain(seg)
            distance = self.distance(seg)
            domain_distance = self.domain_distance(seg)
            diam = seg.diam
            section_diam = seg.sec.diam

            
            if domain in ['axon', 'dend', 'soma', 'apic']:
                self.set_param(seg, "gbar_Leak", "Leak", 9.09090909090909e-05)
                    
                
            
            if domain in ['axon', 'dend', 'soma', 'apic']:
                self.set_param(seg, "e_Leak", "Leak", -79)
                    
                
            
            if domain in ['dend', 'soma', 'apic']:
                self.set_param(seg, "depth_CaDyn", "CaDyn", 0.1)
                    
                
            
            if domain in ['dend', 'soma', 'apic']:
                self.set_param(seg, "tau_CaDyn", "CaDyn", 50)
                    
                
            
            if domain in ['dend', 'soma', 'apic']:
                self.set_param(seg, "cainf_CaDyn", "CaDyn", 0.0001)
                    
                
            
            if domain in ['dend', 'soma', 'apic']:
                self.set_param(seg, "gamma_CaDyn", "CaDyn", 1)
                    
                
            
            if domain in ['dend', 'soma', 'apic']:
                self.set_param(seg, "vhalf_m_sNa", "sNa", -32.571)
                    
                
            
            if domain in ['dend', 'soma', 'apic']:
                self.set_param(seg, "sigma_m_sNa", "sNa", 9.8)
                    
                
            
            if domain in ['dend', 'soma', 'apic']:
                self.set_param(seg, "k_m_sNa", "sNa", 1.882)
                    
                
            
            if domain in ['dend', 'soma', 'apic']:
                self.set_param(seg, "delta_m_sNa", "sNa", 0.541)
                    
                
            
            if domain in ['dend', 'soma', 'apic']:
                self.set_param(seg, "tau0_m_sNa", "sNa", 0.065)
                    
                
            
            if domain in ['dend', 'soma', 'apic']:
                self.set_param(seg, "vhalf_h_sNa", "sNa", -60.0)
                    
                
            
            if domain in ['dend', 'soma', 'apic']:
                self.set_param(seg, "sigma_h_sNa", "sNa", -6.2)
                    
                
            
            if domain in ['dend', 'soma', 'apic']:
                self.set_param(seg, "k_h_sNa", "sNa", 0.018)
                    
                
            
            if domain in ['dend', 'soma', 'apic']:
                self.set_param(seg, "delta_h_sNa", "sNa", 0.395)
                    
                
            
            if domain in ['dend', 'soma', 'apic']:
                self.set_param(seg, "tau0_h_sNa", "sNa", 0.797)
                    
                
            
            if domain in ['dend', 'soma', 'apic']:
                self.set_param(seg, "gbar_sNa", "sNa", 0.0)
                    
                
            
            if domain in ['dend', 'soma', 'apic']:
                self.set_param(seg, "q10_sNa", "sNa", 2.3)
                    
                
            
            if domain in ['dend', 'soma', 'apic']:
                self.set_param(seg, "temp_sNa", "sNa", 23)
                    
                
            
            if domain in ['axon', 'dend', 'soma', 'apic']:
                self.set_param(seg, "ena", "Independent", 60)
                    
                
            
            if domain in ['dend', 'soma', 'apic']:
                self.set_param(seg, "gbar_Na", "Na", 0.0)
                    
                
            if domain in ['soma']:
                self.set_param(seg, "gbar_Na", "Na", 0.0505)
                    
                
            if domain in ['dend', 'apic']:
                self.set_param(seg, "gbar_Na", "Na", 0.0303)
                    
                
            
            if domain in ['dend', 'soma', 'apic']:
                self.set_param(seg, "Rma_Na", "Na", 0.182)
                    
                
            
            if domain in ['dend', 'soma', 'apic']:
                self.set_param(seg, "Rmb_Na", "Na", 0.14)
                    
                
            
            if domain in ['dend', 'soma', 'apic']:
                self.set_param(seg, "v12m_Na", "Na", -30)
                    
                
            
            if domain in ['dend', 'soma', 'apic']:
                self.set_param(seg, "qm_Na", "Na", 9.8)
                    
                
            
            if domain in ['dend', 'soma', 'apic']:
                self.set_param(seg, "Rhb_Na", "Na", 0.0091)
                    
                
            
            if domain in ['dend', 'soma', 'apic']:
                self.set_param(seg, "Rha_Na", "Na", 0.024)
                    
                
            
            if domain in ['dend', 'soma', 'apic']:
                self.set_param(seg, "v12ha_Na", "Na", -45)
                    
                
            
            if domain in ['dend', 'soma', 'apic']:
                self.set_param(seg, "v12hb_Na", "Na", -70)
                    
                
            
            if domain in ['dend', 'soma', 'apic']:
                self.set_param(seg, "qh_Na", "Na", 5)
                    
                
            
            if domain in ['dend', 'soma', 'apic']:
                self.set_param(seg, "v12hinf_Na", "Na", -60)
                    
                
            
            if domain in ['dend', 'soma', 'apic']:
                self.set_param(seg, "qhinf_Na", "Na", 6.2)
                    
                
            
            if domain in ['dend', 'soma', 'apic']:
                self.set_param(seg, "gbar_KCa", "KCa", 0.0)
                    
                
            if domain in ['soma']:
                self.set_param(seg, "gbar_KCa", "KCa", 0.00021)
                    
                
            if domain in ['dend', 'apic']:
                self.set_param(seg, "gbar_KCa", "KCa", 0.00021)
                    
                
            
            if domain in ['axon', 'dend', 'soma', 'apic']:
                self.set_param(seg, "ek", "Independent", -80)
                    
                
            
            if domain in ['dend', 'soma', 'apic']:
                self.set_param(seg, "gbar_Kv", "Kv", 0.0)
                    
                
            if domain in ['soma']:
                self.set_param(seg, "gbar_Kv", "Kv", 0.005)
                    
                
            if domain in ['dend', 'apic']:
                self.set_param(seg, "gbar_Kv", "Kv", 0.00015)
                    
                
            
            if domain in ['dend', 'soma', 'apic']:
                self.set_param(seg, "v12_Kv", "Kv", 25)
                    
                
            
            if domain in ['dend', 'soma', 'apic']:
                self.set_param(seg, "q_Kv", "Kv", 9)
                    
                
            
            if domain in ['dend', 'soma', 'apic']:
                self.set_param(seg, "gbar_Ka", "Ka", 0.0)
                    
                
            if domain in ['soma']:
                self.set_param(seg, "gbar_Ka", "Ka", 0.0054)
                    
                
            if domain in ['dend', 'apic']:
                if 0 < section_diam <= 0.8:
                
                    self.set_param(seg, "gbar_Ka", "Ka", 0.108)
                    
                
            if domain in ['dend', 'apic']:
                if 0.8 < section_diam:
                
                    self.set_param(seg, "gbar_Ka", "Ka", 0.0108)
                    
                
            
            if domain in ['dend', 'soma', 'apic']:
                self.set_param(seg, "gbar_CaHVA", "CaHVA", 0.0)
                    
                
            if domain in ['soma']:
                self.set_param(seg, "gbar_CaHVA", "CaHVA", 5e-06)
                    
                
            if domain in ['dend']:
                self.set_param(seg, "gbar_CaHVA", "CaHVA", linear(distance, slope=1e-08, intercept=5e-06))
                    
                
            if domain in ['apic']:
                if 0 < distance <= 260:
                
                    self.set_param(seg, "gbar_CaHVA", "CaHVA", sinusoidal(distance, **{'amplitude': 4.923e-06, 'frequency': 0.008758, 'phase': 0.8656}))
                    
                
            if domain in ['apic']:
                if 260 < distance:
                
                    self.set_param(seg, "gbar_CaHVA", "CaHVA", 2e-06)
                    
                
            
            if domain in ['axon', 'dend', 'soma', 'apic']:
                self.set_param(seg, "eca", "Independent", 140)
                    
                
            
            if domain in ['dend', 'soma', 'apic']:
                self.set_param(seg, "gbar_Km", "Km", 0.0)
                    
                
            if domain in ['soma']:
                self.set_param(seg, "gbar_Km", "Km", 0.0002794)
                    
                
            if domain in ['dend', 'apic']:
                self.set_param(seg, "gbar_Km", "Km", 0.000127)
                    
                
            
            if domain in ['dend', 'soma', 'apic']:
                self.set_param(seg, "v12_Km", "Km", -30)
                    
                
            
            if domain in ['dend', 'soma', 'apic']:
                self.set_param(seg, "q_Km", "Km", 9)
                    
                
            
            if domain in ['dend', 'soma', 'apic']:
                self.set_param(seg, "gbar_CaLVA", "CaLVA", 0.0)
                    
                
            if domain in ['soma']:
                self.set_param(seg, "gbar_CaLVA", "CaLVA", 3e-05)
                    
                
            if domain in ['dend']:
                self.set_param(seg, "gbar_CaLVA", "CaLVA", linear(distance, slope=6e-08, intercept=3e-05))
                    
                
            if domain in ['apic']:
                if 0 < distance <= 260:
                
                    self.set_param(seg, "gbar_CaLVA", "CaLVA", sinusoidal(distance, **{'amplitude': 2.9538e-05, 'frequency': 0.008758, 'phase': 0.8656}))
                    
                
            if domain in ['apic']:
                if 260 < distance:
                
                    self.set_param(seg, "gbar_CaLVA", "CaLVA", 1.2e-05)
                    
                
            

    def add_stimuli(self):
        self.add_iclamps()
        self.add_synapses()

    def add_recordings(self):
        recordings = []
        
        rec = h.Vector()
        rec.record(self.soma[0](0.5)._ref_v)
        recordings.append(rec)
        
        return recordings

    def add_iclamps(self):
        iclamps = []
        
        iclamp = h.IClamp(self.soma[0](0.5))
        iclamp.delay = 50.0
        iclamp.dur = 900.0
        iclamp.amp = 0.162
        iclamps.append(iclamp)
        
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