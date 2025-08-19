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

Each folder contains specific components of the model:

- :code:`biophys/`: JSON files defining the distribution and properties of ion channels and other membrane mechanisms
- :code:`mod/`: NEURON mechanism files (MOD) that implement specific ion channel kinetics and other biophysical processes
- :code:`python/`: Python classes automatically generated from MOD files
- :code:`morphology/`: SWC files describing the morphological structure of the neuron
- :code:`stimuli/`: the temporal patterns (JSON) and spatial distribution (CSV) of inputs to the model and the corresponding recordings

Data Format Specifications
------------------------------------------

Biophysical Configuration Format
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The biophysical configuration files use a comprehensive JSON format inspired by the Allen Cell Types Data Base `specification <https://github.com/AllenInstitute/sonata/blob/master/docs/SONATA_DEVELOPER_GUIDE.md#ion_channels>`_, 
extended to handle complex ion channel distributions in detailed biophysical models. 
The format captures three key aspects of neuronal biophysics:

- **Domain-to-Mechanism Mapping**: Defines which ion channels and mechanisms are present in each morphological domain.
- **Segment Groups Definition**: Defines collections of morphological segments that should share similar biophysical properties.
- **Parameter-wise Group-to-Distribution Mapping**: For each parameter, specifies how its value is distributed across different segment groups using mathematical functions.

**1. Domain-to-Mechanism Mapping**

This section defines which ion channels and mechanisms are present in each morphological domain. 
For example, to specify that the soma contains sodium (Na) and potassium (Kv) channels, while the apical dendrite contains in addition calcium (CaHVA, CaLVA) channels, one would use:



.. code-block:: json

    "domains": {
        "apic": [
            "CaHVA",
            "CaLVA", 
            "Kv",
            "Na"
        ],
        "soma": [
            "Kv",
            "Na"
        ]
    }



Available domains (and their corresponding SWC file IDs) are:

- :code:`soma` (1): Soma region
- :code:`perisomatic` (11): Perisomatic region (e.g., proximal dendrites)
- :code:`axon` (2): Axon
- :code:`dend` (3): Dendritic regions (both basal and apical)
- :code:`basal` (31): Basal dendrites
- :code:`apic` (4): Apical dendrites
- :code:`trunk` (41): The apical trunk
- :code:`tuft` (42): The apical tuft
- :code:`oblique` (43): Oblique dendrites
- :code:`custom` (5): Custom domain defined by the user
- :code:`neurite` (6): Generic neurite
- :code:`glia` (7): Glial cell region
- :code:`reduced` (8): Domain obtained during morphology reduction
- :code:`undefined` (0): Undefined region

Numerical indices can be added to :code:`custom` and :code:`reduced` domains, 
resulting in names like :code:`custom_0` (50), :code:`custom_1` (51), etc.

The channel names (e.g., :code:`CaHVA`, :code:`Kv`, :code:`Na`) correspond to the 
MOD file names, which implement the biophysical properties of these channels.

.. warning::

    For consistency, DendroTweaks automatically ensures that the SUFFIX 
    in each MOD file matches its filename. If there is a mismatch, the SUFFIX will be replaced with the MOD file name during import.


**2. Segment Groups**

Groups define collections of morphological segments that share similar biophysical properties. Here are examples of different group types:

*Domain-matching group:*

.. code-block:: json

    {
        "name": "apical",
        "domains": ["apic"]
    }

*A group spanning multiple domains:*

.. code-block:: json

    {
        "name": "dendritic",
        "domains": ["dend", "apic"]
    }


To define a segment group, we can specify not only the domains where we will search for matching segments, 
but also a criterion to filter segments based on their properties.

The criterion can be one of four types:

- :code:`diam` - diameter of the segment (in micrometers)
- :code:`section_diam` - diameter at the center of the section to which the segment belongs
- :code:`distance` - distance of the segment center from the soma center (in micrometers)
- :code:`domain_distance` - distance of the segment center to the closest parent segment in a different domain


*Diameter-based filtering (thin dendrites only):*

.. code-block:: json

    {
        "name": "dendritic_thin",
        "domains": ["dend", "apic"],
        "select_by": "section_diam",
        "max_value": 0.8
    }

*Distance-based filtering (distal dendrites):*

.. code-block:: json

    {
        "name": "distal_apical",
        "domains": ["dend", "apic"],
        "select_by": "distance",
        "min_value": 100
    }

*Distance-based filtering (apical Ca2+ "hot spot"):*

.. code-block:: json

    {
        "name": "apical_hot_spot",
        "domains": ["apic"],
        "select_by": "distance",
        "min_value": 260,
        "max_value": 300
    }



This allows you to target specific morphological regions with distinct biophysical properties, such as different channel densities in proximal vs. distal dendrites.

**3. Parameter Distributions**

To define how biophysical parameters are distributed across different groups, we can use mathematical functions.
For each of the parameters, we associate a mapping from segment groups to functions that describe how the parameter varies across the segments in that group.

*Constant value across a group:*

.. code-block:: json

    "cm": {
        "all": {
            "function": "constant",
            "parameters": {
                "value": 2
            }
        }
    }

*Linear gradient with distance:*

.. code-block:: json

    "gbar_CaHVA": {
        "basal": {
            "function": "linear",
            "parameters": {
                "slope": 1e-08,
                "intercept": 5e-06
            }
        }
    }

The following distribution functions are available, along with their expected parameters:

- :code:`constant`: Requires a :code:`value` parameter.
- :code:`linear`: Requires :code:`slope` and :code:`intercept` parameters.
- :code:`exponential`: Requires :code:`vertical_shift`, :code:`scale_factor`, :code:`growth_rate`, and :code:`horizontal_shift` parameters.
- :code:`sigmoid`: Requires :code:`vertical_shift`, :code:`scale_factor`, :code:`growth_rate`, and :code:`horizontal_shift` parameters.
- :code:`sinusoidal`: Requires :code:`amplitude`, :code:`frequency`, and :code:`phase` parameters.
- :code:`gaussian`: Requires :code:`amplitude`, :code:`mean`, and :code:`std` parameters.
- :code:`step`: Requires :code:`start`, :code:`end`, :code:`min_value`, and :code:`max_value` parameters.
- :code:`polynomial`: Requires :code:`coeffs` parameter, which is a list of coefficients for the polynomial function.

To learn more about segment groups and parameter distributions, refer to the
:doc:`tutorial</tutorials/tutorial_distributions>` on distributing parameters.



Stimulation and Recording Format
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The stimulation protocol consists of two complementary files: a CSV file defining spatial locations and a JSON file defining temporal patterns and simulation parameters.

**CSV Format - Spatial Distribution**

The CSV file specifies the exact locations of stimuli and recordings on the neuronal morphology. 

It contains the following columns:

- **type**: Type of stimulus or recording (e.g., iclamp, AMPA, NMDA, GABAa, rec)
- **idx**: Index identifier for grouping multiple instances of the same type
- **sec_idx**: Section index in the morphology
- **loc**: Location along the section (0.0 = start, 1.0 = end)

Here is an example of a CSV file:

.. table:: Example Data
    :widths: 25 25 25 25

    ========== ========== ========== ==========================================================
    type       idx        sec_idx    loc
    ========== ========== ========== ==========================================================
    rec        0          0          0.5
    rec        1          20         0.5
    iclamp     0          0          0.5
    AMPA       0          13         0.863
    AMPA       0          17         0.732
    ========== ========== ========== ==========================================================

The first two rows define two recordings, one at the soma center and another at a dendritic location.
The third row defines a current clamp at the soma center.
The last two rows define two AMPA synapses from the same population of "virtual" presynaptic neurons at specific dendritic locations.

**JSON Format - Temporal Patterns and Parameters**

The JSON file defines simulation parameters, temporal patterns, and synaptic properties:

*Simulation parameters:*

.. code-block:: json

    "simulation": {
        "temperature": 37,
        "v_init": -79,
        "dt": 0.025,
        "duration": 1000
    }

*Recording specification:*

.. code-block:: json

    "recordings": [
        {
            "name": "rec_0",
            "var": "v"
        }
    ]

*Synaptic population definition:*

.. code-block:: json

    "populations": {
        "AMPA": [
            {
                "name": "AMPA_0",
                "syn_type": "AMPA", 
                "N": 50,
                "input_params": {
                    "rate": 30,
                    "start": 100,
                    "end": 800,
                    "weight": 1
                },
                "kinetic_params": {
                    "gmax": 0.001,
                    "tau_rise": 0.1,
                    "tau_decay": 2.5,
                    "e": 0
                }
            }
        ]
    }

This example defines a population of 50 AMPA synapses firing at 30 Hz between 100-800 ms, 
with specific kinetic properties for synaptic transmission.

**Key Components of the JSON Structure:**

- :code:`metadata`: General information about the stimulus protocol
- :code:`simulation`: Global simulation parameters (temperature, timestep, duration)
- :code:`recordings`: Voltage and current recordings from specific locations
- :code:`iclamps`: Current clamp stimulations
- :code:`populations`: Synaptic input populations organized by neurotransmitter type

Each population contains:

- :code:`input_params`: Temporal pattern parameters (rate, timing, noise)
- :code:`kinetic_params`: Synaptic kinetics (conductance, time constants, reversal potential)

.. warning::

    This representation focuses on defining the statistical properties of synaptic inputs, such as firing rate and timing, rather than specifying exact spike times. 
    

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