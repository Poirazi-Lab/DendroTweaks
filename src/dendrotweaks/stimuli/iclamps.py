from neuron import h
h.load_file('stdrun.hoc')

class IClamp():
    """
    A current clamp stimulus.

    Parameters
    ----------
    sec : Section
        The section to place the stimulus on.
    loc : float
        The location along the section to place the stimulus.
        Can be a float between 0 and 1.
    amp : float
        The amplitude of the stimulus, in nA.
    delay : int
        The delay of the stimulus, in ms.
    dur : int
        The duration of the stimulus, in ms.

    Attributes
    ----------
    sec : Section
        The section to place the stimulus on.
    loc : float
        The location along the section to place the stimulus.
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
        """
        The amplitude of the stimulus, in nA.
        """
        return self._iclamp.amp

    @amp.setter
    def amp(self, new_amp):
        self._iclamp.amp = new_amp


    @property
    def delay(self):
        """
        The delay of the stimulus, in ms.
        """
        return self._iclamp.delay

    @delay.setter
    def delay(self, new_delay):
        self._iclamp.delay = new_delay

    @property
    def dur(self):
        """
        The duration of the stimulus, in ms.
        """
        return self._iclamp.dur

    @dur.setter
    def dur(self, new_dur):
        self._iclamp.dur = new_dur