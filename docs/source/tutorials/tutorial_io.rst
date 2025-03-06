Importing and Exporting Models
=======================================================

This tutorial will guide you through the process of creating, manipulating, and sharing computational neuron models using DendroTweaks. 
You will learn how different components work together to simulate realistic neuronal behavior.

Understanding the model architecture
------------------------------------------

At its core, a computational neuron model requires several key components that mirror the biological structure and function of real neurons:

1. **Morphology**: The physical structure of the neuron (dendrites, soma, axon)
2. **Membrane Properties**: Ion channels and other biophysical mechanisms
3. **Stimulation Protocols**: How we activate or inhibit the neuron

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

- **membrane/**: JSON files defining the distribution and properties of ion channels and other membrane mechanisms
- **mod/**: NEURON mechanism files (MOD) that implement specific ion channel kinetics and other biophysical processes
- **python/**: Python classes automatically generated from MOD files
- **morphology/**: SWC files describing the morphological structure of the neuron
- **stimuli/**: the temporal patterns (JSON) and spatial distribution (CSV) of inputs to the model

Assembling a model
------------------------------------------

Let's walk through the process of loading an existing model.
Assuming we have cratead a :code:`UserModel` directory with the necessary components, we can
start by creating a :code:`Model` 
examining the available morphologies:

.. code-block:: python

    >>> from dendrotweaks.model import Model
    >>> model = Model(name='UserModel', path_to_data='data/')
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

Finally, we will set up the stimulation protocol:

.. code-block:: python

    >>> model.list_stimuli()
    ['stim1', 'stim2']

.. code-block:: python

    >>> model.load_stimuli('stim1')



Switching between configurations
------------------------------------------

One of the key advantages of computational modeling is the ability to rapidly test different scenarios. 
For instance, we can apply the same membrane configuration and stimulation pattern to a different morphological structure:

.. code-block:: python

    >>> model.load_morphology('cell2')

Or we can change the stimulation pattern while keeping the same morphology and membrane properties:

.. code-block:: python

    >>> model.load_stimuli('stim2')

This flexibility allows you to investigate how cellular properties and input patterns interact to produce different responses.


Sharing and reproducibility
------------------------------------------

After developing your model, you can export components for sharing or future use:

.. code-block:: python

    >>> model.export_stimuli(version='stim3')
    >>> model.export_membrane(version='config3')
    >>> model.export_morphology(version='cell3')




