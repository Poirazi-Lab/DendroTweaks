Importing and Exporting Models
=======================================================

This tutorial will guide you through the process of creating, manipulating, and sharing computational neuron models using DendroTweaks. 
You will learn how different components work together to simulate realistic neuronal behavior.

Understanding the model architecture
------------------------------------------

At its core, a computational neuron model requires several key components:

1. **Morphology**: The physical structure of the neuron (dendrites, soma, axon)
2. **Membrane Properties**: Ion channels and other biophysical mechanisms
3. **Stimulation Protocols**: How we activate or inhibit the neuron via current injection or synaptic input

DendroTweaks organizes these components in a structured directory:

.. code-block:: bash

    .
    └── data/
        .
        .
        .
        └── UserModel/  
            ├── morphology/
            │   ├── cell1.swc
            │   └── cell2.swc
            ├── membrane/  
            │   ├── config1.json
            │   ├── config2.json
            |   ├── mod/
            |   |   ├── Kv.mod
            |   |   └── Nav.mod
            |   └── python/
            |       ├── Kv.py
            |       └── Nav.py
            └── stimuli/ 
                ├── stim1.csv 
                ├── stim1.json
                ├── stim2.csv
                └── stim2.json

Each folder contains specific components of the model:

- :code:`membrane/`: JSON files defining the distribution and properties of ion channels and other membrane mechanisms
- :code:`mod/`: NEURON mechanism files (MOD) that implement specific ion channel kinetics and other biophysical processes
- :code:`python/`: Python classes automatically generated from MOD files
- :code:`morphology/`: SWC files describing the morphological structure of the neuron
- :code:`stimuli/`: the temporal patterns (JSON) and spatial distribution (CSV) of inputs to the model and the corresponding recordings

Downloading example data
------------------------------------------

To follow along with this tutorial, you can download the example data from the DendroTweaks repository:

.. code-block:: python

    >>> import dendrotweaks as dd
    >>> dd.download_example_data('path/to/local/directory')

    

Assembling a model
------------------------------------------

Assuming we have cratead a :code:`UserModel` directory with the necessary components, we can
start by creating a :code:`Model` 
examining the available morphologies:

.. code-block:: python

    >>> model = dd.Model(path_to_model='data/UserModel')
    >>> model.list_morphologies()
    ['cell1', 'cell2']

We can load a specific morphology using the :code:`load_morphology` method:

.. code-block:: python

    >>> model.load_morphology('cell1')

Next, we will add membrane properties to the model.

.. code-block:: python

    >>> model.list_membrane_configurations()
    ['config1', 'config2']

.. code-block:: python

    >>> model.load_membrane('config1')

Finally, we will set up the stimulation and recording protocols:

.. code-block:: python

    >>> model.list_stimuli()
    ['stim1', 'stim2']

.. code-block:: python

    >>> model.load_stimuli('stim1')



Switching between configurations
------------------------------------------

One of the key advantages of computational modeling is the ability to rapidly test different scenarios. 
For instance, we can change the stimulation pattern while keeping the same morphology and membrane properties:

.. code-block:: python

    >>> model.load_stimuli('stim2')

We can switch to a different membrane configuration while keeping the same morphology and stimulation pattern:

.. code-block:: python

    >>> model.load_membrane('config2')

It is also possible to apply the same membrane configuration to a different morphology.
This is possible because the membrane properties are defined on the domain level, independent of the specific morphological structure.
Therefore, as long as the morphologies come from the same cell type and have the same domains, the membrane configuration can be applied to any of them.

.. warning::

    Recordings and stimuli cannot be transferred between models with different morphologies because they are defined on the section level.
    Make sure to remove all recordings and stimuli before loading a new morphology.

.. code-block:: python

    >>> model.remove_all_recordings()
    >>> model.remove_all_stimuli()
    >>> model.load_morphology('cell2')




Sharing and reproducibility
------------------------------------------

After developing your model, you can export components for sharing or future use:

.. code-block:: python

    >>> model.export_stimuli(file_name='stim3')
    >>> model.export_membrane(file_name='config3')
    >>> model.export_morphology(file_name='cell3')




