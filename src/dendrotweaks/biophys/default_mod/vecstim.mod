:  Vector stream of events

NEURON {
	THREADSAFE
	ARTIFICIAL_CELL VecStim
	RANGE delay
}

ASSIGNED {
	index
	etime (ms)
	space
	delay
}

INITIAL {
	index = 0
	element()
	if (index > 0) {
		net_send(delay + etime - t, 1)
	}
}

NET_RECEIVE (w) {
	if (flag == 1) {
		net_event(t)
		element()
		if (index > 0) {
			net_send(delay + etime -t, 1)
		} 
	}
}

PROCEDURE element() {
VERBATIM	
  { void* vv; int i, size; double* px;
	i = (int)index;
	if (i >= 0) {
		vv = *((void**)(&space));
		if (vv) {
			size = vector_capacity(vv);
			px = vector_vec(vv);
			if (i < size) {
				etime = px[i];
				index += 1.;
			}else{
				index = -1.;
			}
		}else{
			index = -1.;
		}
	}
  }
ENDVERBATIM
}

PROCEDURE play() {
VERBATIM
	void** vv;
	vv = (void**)(&space);
	*vv = (void*)0;
	if (ifarg(1)) {
		*vv = vector_arg(1);
	}
ENDVERBATIM
}
