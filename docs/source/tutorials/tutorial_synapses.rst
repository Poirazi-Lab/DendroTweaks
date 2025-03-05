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
synapses on the apical dendrite of the postsynaptic neuron.

.. code-block:: python

    >>> from dendrotweaks.stimuli.synapses import Population
    >>> pop = Population(name='apic_AMPA', 
    ...                  sections=model.groups['apic'].sections,
    ...                  N=50, syn_type='AMPA')

We can now access the population properties though :code:`kinetic_params` and :code:`input_params`.

Assigning Sections and Locations to Synapses
---------------------------------------------

Next, we can create the synapses and allocate them to the sections of the postsynaptic neuron.
This can be done using the :code:`allocate_synapses` method.
Each synapse in the population needs to be assigned 
a random section and location within that section. 

.. code-block:: python
    
    >>> pop.allocate_synapses()

Creating Synapses in the Simulator
------------------------------------------



.. code-block:: python
    
    >>> pop.create_inputs() # Create the NetStim and NetCon objects
    >>> pop.synapses[10]
    [<Synapse(sec[10](0.66))>, <Synapse(sec[10](0.22))>]

Each synapse will have the following references:

* :code:`_ref_syn` - Reference to the synapse object
* :code:`_ref_stim` - Reference to the stimulus object (NetStim)
* :code:`_ref_con` - Reference to the connection object (NetCon)

Setting Activation Properties
------------------------------------------

We can now update the activation properties of the synapses of our choice, 
such as the rate, noise, start time, and end time.

.. code-block:: python
    
    >>> pop.update_input_params(params={'rate': 0.1, 'noise': 1})

Setting Kinetic Properties
------------------------------------------

Finally, we can update the kinetic properties of the synapses, 
such as the maximum conductance, rise time, decay time, and reversal potential.

.. code-block:: python

    >>> pop.update_kinetic_params(params={'gmax': 0.1, 'e': 0})