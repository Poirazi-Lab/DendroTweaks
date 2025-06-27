class prerun:
    """
    Context manager to prerun a simulation for a specified duration.
    This is useful to stabilize the model before running the main simulation.
    """
    def __init__(self, model, duration=300, truncate=True):
        self.model = model
        if duration <= 0:
            raise ValueError("Duration must be a positive number.")
        self.duration = duration
        self.truncate = truncate
        self._original_iclamp_delays = {}
        self._original_input_params = {}

    def __enter__(self):
        
        self._original_iclamp_delays = {k: v.delay for k, v in self.model.iclamps.items()}
        self._original_input_params = {
            (pk, sk): (pop.input_params['start'], pop.input_params['end'])
            for pk, pops in self.model.populations.items()
            for sk, pop in pops.items()
        }
        for iclamp in self.model.iclamps.values():
            iclamp.delay += self.duration
        
        for pops in self.model.populations.values():
            for pop in pops.values():
                start = pop.input_params['start'] + self.duration
                end = pop.input_params['end'] + self.duration
                pop.update_input_params(**{
                    'start': start,
                    'end': end
                })

        return self

    def __exit__(self, exc_type, exc_value, traceback):

        # Restore iClamp delays
        for seg, delay in self._original_iclamp_delays.items():
            self.model.iclamps[seg].delay = delay

        # Restore input timings
        for (pk, sk), (start, end) in self._original_input_params.items():
            self.model.populations[pk][sk].update_input_params(**{'start': start, 'end': end})
    
        duration_timepoints = int(self.duration / self.model.simulator.dt)
        if len(self.model.simulator.t) > duration_timepoints and self.truncate:
            self._truncate()
        
    def _truncate(self):
        """Truncate the simulation time and recordings to the specified duration."""

        onset = int(self.duration / self.model.simulator.dt)

        self.model.simulator.t = self.model.simulator.t[onset:]
        self.model.simulator.t = [t - self.duration for t in self.model.simulator.t]

        for var, recs in self.model.recordings.items():
            for seg, rec in recs.items():
                recs[seg] = rec[onset:]

        self.model.simulator._duration -= self.duration