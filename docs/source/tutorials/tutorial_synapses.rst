Adding Synapses
==========================================

In this tutorial, we will learn how to create and configure synaptic inputs 
in a neuronal model. 
We will create a population of "virtual" presynaptic neurons that will form
synapses on our postsynaptic explicitely simulated neuron.
Synapses within a population share the same kinetic properties but 
can have different activation times.

Creating a Population
------------------------------------------

First, let's create a population of presynaptic neurons that will form 50 AMPA 
synapses on the apical dendrite of the postsynaptic neuron. We create the synapses and allocate them to the sections of the postsynaptic neuron.
Each synapse in the population is assigned 
a random segment.

.. code-block:: python

    >>> segments = model.get_segments(group_names=['apical'])
    >>> model.add_population(
    ...    segments, 
    ...    N=50, 
    ...    syn_type='AMPA'
    ... )


We can now access the populations through the :code:`populations` attribute.

.. code-block:: python

    >>> model.populations
    {'AMPA': {'AMPA_0': <Population(AMPA_0, N=50)>},
     'NMDA': {},
     'AMPA_NMDA': {},
     'GABAa': {}
    }

We can access the population properties for a given population though :code:`kinetic_params` and :code:`input_params`.

.. code-block:: python

    >>> model.poulations['AMPA']['AMPA_0'].kinetic_params
    {'gmax': 0.001, 'tau_rise': 0.1, 'tau_decay': 2.5, 'e': 0}


.. code-block:: python

    >>> model.poulations['AMPA']['AMPA_0'].input_params
    {'rate': 1, 'noise': 1, 'start': 100, 'end': 200, 'weight': 1, 'delay': 0}


We can access individual synapses through the :code:`synapses` attribute.

.. code-block:: python

    >>> model.populations['AMPA']['AMPA_0'].synapses
    {
        (Section(idx=50), 0.853): [<Synapse(Section(idx=50)(0.853))>],
        (Section(idx=10), 0.03): [<Synapse(Section(idx=10)(0.030))>],
        (Section(idx=17), 0.819): [<Synapse(Section(idx=17)(0.819))>],
        (Section(idx=23), 0.455): [<Synapse(Section(idx=23)(0.455))>],
        (Section(idx=21), 0.444): [<Synapse(Section(idx=21)(0.444))>],
        (Section(idx=45), 0.986): [<Synapse(Section(idx=45)(0.986))>],
        ...
    }

We allocate the synapses to the sections of the postsynaptic neuron uniformly.
A synapse is assigned a random section (:code:`syn.sec`) and location (:code:`syn.loc`) within the section.

Each synapse has the following references to the NEURON objects:

* :code:`_ref_syn` - Reference to the synapse object
* :code:`_ref_stim` - Reference to the stimulus object (NetStim)
* :code:`_ref_con` - Reference to the connection object (NetCon)


Setting Activation Properties
------------------------------------------

We can now update the activation properties of the synapses of our choice, 
such as the rate, noise, start time, and end time.
    
.. code-block:: python

    >>> model.update_population_input_params(
    ...        pop_name='AMPA_0',
    ...        rate=30, # Hz
    ...        noise=1, # ms between 0 and 1
    ...        start=100, # ms
    ...        end=900 # ms
    ...        weight=1 # (1)
    ...    )

Setting Kinetic Properties
------------------------------------------

Finally, we can update the kinetic properties of the synapses, 
such as the maximum conductance, rise time, decay time, and reversal potential.


.. code-block:: python

    >>> model.update_population_kinetic_params(
    ...        pop_name='AMPA_0', 
    ...        gmax=0.1, # uS
    ...        tau_rise=0.1, # ms
    ...        tau_decay=2, # ms
    ...        e=0 # mV
    ...    )


