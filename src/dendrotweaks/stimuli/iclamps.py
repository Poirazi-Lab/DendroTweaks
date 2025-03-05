from neuron import h
h.load_file('stdrun.hoc')

class IClamp():
    """
    Creates a current clamp stimulus.

    Parameters
    ----------
    seg : neuron.Segment
        The segment where the stimulus is applied.
    amp : float
        The amplitude of the stimulus, in nA.
    delay : int
        The delay of the stimulus, in ms.
    dur : int
        The duration of the stimulus, in ms.
    """

    def __init__(self, sec, loc, amp=0, delay=100, dur=100):
        self.sec = sec
        self.loc = loc
        self._iclamp = h.IClamp(sec(loc)._ref)
        self._iclamp.amp = amp
        self._iclamp.delay = delay
        self._iclamp.dur = dur

    def __repr__(self):
        return f"<IClamp(sec[{self.sec.idx}]({self.loc:.2f}))>"
        
    @property
    def amp(self):
        return self._iclamp.amp

    @amp.setter
    def amp(self, new_amp):
        self._iclamp.amp = new_amp


    @property
    def delay(self):
        return self._iclamp.delay

    @delay.setter
    def delay(self, new_delay):
        self._iclamp.delay = new_delay

    @property
    def dur(self):
        return self._iclamp.dur

    @dur.setter
    def dur(self, new_dur):
        self._iclamp.dur = new_dur