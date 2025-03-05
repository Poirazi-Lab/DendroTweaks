.. _importing_exporting_models:

Importing and Exporting Models
==========================================

This tutorial provides an overview of DendroTweaks model structure and demonstrates how to import and export model components.

Understanding Model Structure
------------------------------------------

DendroTweaks models are composed of multiple modular components, such as morphologies, membrane configurations, and stimulation protocols. These components are stored in a structured directory as follows:

.. code-block:: bash

    .
    └── data/
        └── UserModel/  
            ├── membrane/  
            │   ├── config1.json
            │   └── config2.json
            ├── mod/
            │   ├── Kv.mod
            │   └── Nav.mod
            ├── morphology/
            │   ├── cell1.swc
            │   └── cell2.swc
            └── stimuli/ 
                ├── stim1.csv 
                ├── stim1.json
                ├── stim2.csv
                └── stim2.json

Each subdirectory serves a specific function:

- **membrane/**: Defines biophysical configurations in JSON format.
- **mod/**: Contains MOD files specifying ion channel mechanisms.
- **morphology/**: Stores SWC files representing neuron morphologies.
- **stimuli/**: Holds JSON and CSV files defining stimulation properties and spatial locations.

This modular structure enables flexibility in combining different components to create customized models.

Loading Model Components
------------------------------------------

To work with a model, we first inspect its available components.

Listing the available morphologies:

.. code-block:: python

    >>> model.list_morphologies()
    ['cell1', 'cell2']

Loading a specific morphology:

.. code-block:: python

    >>> model.load_morphology('cell1')

Checking the available membrane configurations:

.. code-block:: python

    >>> model.list_membrane_configurations()
    ['config1', 'config2']

Loading a specific membrane configuration:

.. code-block:: python

    >>> model.load_membrane('config1')

Listing available stimulation protocols:

.. code-block:: python

    >>> model.list_stimuli()
    ['stim1', 'stim2']

Loading a specific stimulation protocol:

.. code-block:: python

    >>> model.load_stimuli('stim1')

This applies the stimulation protocol as defined in `stim1.json` and `stim1.csv`.

Switching Components Dynamically
------------------------------------------

DendroTweaks models allow dynamic switching between components, facilitating flexible experimentation. For instance, we can apply the same membrane configuration to a different morphology:

.. code-block:: python

    >>> model.load_morphology('cell2')

Similarly, we can change the stimulation protocol:

.. code-block:: python

    >>> model.load_stimuli('stim2')

This approach enables us to study how different stimuli affect the same neuronal model.

Exporting Model Components
------------------------------------------

When exporting a model, we follow the same modular structure.

Exporting the current stimulation (and recording) protocol:

.. code-block:: python

    >>> model.export_stimuli(version='stim3')

This generates `stim3.json` and `stim3.csv` in the `stimuli/` directory.

Exporting the current membrane configuration:

.. code-block:: python

    >>> model.export_membrane(version='config3')

Exporting the current morphology:

.. code-block:: python

    >>> model.export_morphology(version='cell3')

By exporting components separately, we can efficiently share and reuse them in different models, enhancing modularity and reproducibility.
