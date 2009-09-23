import numpy
from pyNN import recording
from pyNN.neuron import simulator

# --- For implementation of record_X()/get_X()/print_X() -----------------------

class Recorder(recording.Recorder):
    """Encapsulates data and functions related to recording model variables."""
        
    def _record(self, new_ids):
        """Add the cells in `new_ids` to the set of recorded cells."""
        if self.variable == 'spikes':
            for id in new_ids:
                id._cell.record(1)
        elif self.variable == 'v':
            for id in new_ids:
                id._cell.record_v(1)
        elif self.variable == 'gsyn':
            for id in new_ids:
                id._cell.record_gsyn("excitatory", 1)
                id._cell.record_gsyn("inhibitory", 1)
        else:
            raise Exception("Recording of %s not implemented." % self.variable)
        
    def get(self, gather=False, compatible_output=True):
        """Return the recorded data as a Numpy array."""
        # compatible_output is not used, but is needed for compatibility with the nest module.
        # Does nest really need it?                
        if self.variable == 'spikes':
            data = numpy.empty((0,2))
            for id in self.recorded:
                spikes = numpy.array(id._cell.spike_times)
                spikes = spikes[spikes<=simulator.state.t+1e-9]
                if len(spikes) > 0:    
                    new_data = numpy.array([numpy.ones(spikes.shape)*id, spikes]).T
                    data = numpy.concatenate((data, new_data))
        elif self.variable == 'v':
            data = numpy.empty((0,3))
            for id in self.recorded:
                v = numpy.array(id._cell.vtrace)  
                t = numpy.array(id._cell.record_times)               
                new_data = numpy.array([numpy.ones(v.shape)*id, t, v]).T
                data = numpy.concatenate((data, new_data))
        elif self.variable == 'gsyn':
            data = numpy.empty((0,4))
            for id in self.recorded:
                ge = numpy.array(id._cell.gsyn_trace['excitatory'])
                gi = numpy.array(id._cell.gsyn_trace['inhibitory'])
                t = numpy.array(id._cell.record_times)             
                new_data = numpy.array([numpy.ones(ge.shape)*id, t, ge, gi]).T
                data = numpy.concatenate((data, new_data))
        else:
            raise Exception("Recording of %s not implemented." % self.variable)
        if gather and simulator.state.num_processes > 1:
            data = recording.gather(data)
        return data
        
    def _local_count(self, gather=False):
        N = {}
        for id in self.recorded:
            N[id] = id._cell.spike_times.size()
        return N

simulator.Recorder = Recorder