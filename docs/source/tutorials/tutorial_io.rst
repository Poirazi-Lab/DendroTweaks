Importing and Exporting Models
=======================================================

This tutorial explains how to load, export, and organize model components for reproducible workflows.


Understanding the model structure
------------------------------------------

At its core, a computational neuron model requires three key components:

1. **Morphology**: The physical structure of the neuron (dendrites, soma, axon).
2. **Biophysical Properties**: Ion channels and other membrane mechanisms.
3. **Stimulation Protocols**: The external stimuli applied to the model (e.g., current injections or synaptic inputs) and the measurements (e.g., voltage recordings) taken.

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
            ├── biophys/  
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

Each model folder inside the :code:`data` directory contains the following components:

- :code:`morphology/`: SWC files describing the morphological structure of the neuron
- :code:`biophys/`: JSON files defining the distribution and properties of ion channels and other membrane mechanisms
- :code:`mod/`: NMODL mechanism files (MOD) that implement specific ion channel kinetics and other biophysical processes
- :code:`python/`: Python classes automatically generated from MOD files
- :code:`stimuli/`: the parameters (JSON) and spatial distribution (CSV) of inputs to the model and the corresponding recordings

In addition to widely used SWC and MOD files, 
DendroTweaks employs a custom data format to specify biophysical configurations and stimulation protocols using JSON and CSV files.
For a comprehensive description of this data format, refer to the :doc:`Data Format Specification </tutorials/data_format>`.

Downloading example data
------------------------------------------

You can download the example `data <https://github.com/Poirazi-Lab/DendroTweaks/tree/main/examples>`_ from the DendroTweaks repository.

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

Next, we will add biophysical properties to the model.

.. code-block:: python

    >>> model.list_biophys()
    ['config1', 'config2']

.. code-block:: python

    >>> model.load_biophys('config1')

Finally, we will set up the stimulation and recording protocols:

.. code-block:: python

    >>> model.list_stimuli()
    ['stim1', 'stim2']

.. code-block:: python

    >>> model.load_stimuli('stim1')



Switching between configurations
------------------------------------------

One of the key advantages of computational modeling is the ability to rapidly test different scenarios. 
For instance, we can change the stimulation pattern while keeping the same morphology and biophysical properties:

.. code-block:: python

    >>> model.load_stimuli('stim2')

We can switch to a different biophysical configuration while keeping the same morphology and stimulation pattern:

.. code-block:: python

    >>> model.load_biophys('config2')

It is also possible to apply the same biophysical configuration to a different morphology.
This is possible because the biophysical properties are defined on the domain level, independent of the specific morphological structure.
Therefore, as long as the morphologies come from the same cell type and have the same domains, the biophysical configuration can be applied to any of them.

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
    >>> model.export_biophys(file_name='config3')
    >>> model.export_morphology(file_name='cell3')