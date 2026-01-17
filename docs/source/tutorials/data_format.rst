
Data Format Specification
===========================

This specification will guide you through the custom data format for biophysical configurations and stimulation protocols, used 
in DendroTweaks to describe single-cell neuronal models with complex morphological and biophysical properties.


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
                ├── protocol1/
                │   ├── config.json
                │   ├── recordings.csv
                │   ├── iclamps.csv
                │   └── synapses.csv
                └── protocol2/
                    ├── config.json
                    ├── recordings.csv
                    ├── iclamps.csv
                    └── synapses.csv

Each model folder inside the :code:`data` directory contains the following components:

- :code:`morphology/`: SWC files describing the morphological structure of the neuron
- :code:`biophys/`: JSON files defining the distribution and properties of ion channels and other membrane mechanisms
- :code:`mod/`: NMODL mechanism files (MOD) that implement specific ion channel kinetics and other biophysical processes
- :code:`python/`: Python classes automatically generated from MOD files
- :code:`stimuli/`: the stimulation protocols, each in its own subfolder with JSON and CSV files defining stimuli and recordings

Biophysical Configuration Format
----------------------------------

The biophysical configuration files use a comprehensive JSON format inspired by the Allen Cell Types Data Base `specification <https://github.com/AllenInstitute/sonata/blob/master/docs/SONATA_DEVELOPER_GUIDE.md#ion_channels>`_, 
extended to handle complex ion channel distributions in detailed biophysical models. 
The format captures three key aspects of neuronal biophysics:

- **Domain-to-Mechanism Mapping**: Defines which ion channels and mechanisms are present in each morphological domain.
- **Segment Groups Definition**: Defines collections of morphological segments that should share similar biophysical properties.
- **Parameter-wise Group-to-Distribution Mapping**: For each parameter, specifies how its value is distributed across different segment groups using mathematical functions.

1. Domain-to-Mechanism Mapping
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This section defines which ion channels and mechanisms are present in each morphological domain.
For example, to specify that the soma contains sodium (Na) and potassium (Kv) channels, 
while the apical dendrite contains in addition calcium (CaHVA, CaLVA) channels, one would use:


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



Available domains (and their corresponding `SWC specification <https://swc-specification.readthedocs.io/en/latest/swc.html>`_ IDs) are:

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


2. Segment Groups
~~~~~~~~~~~~~~~~~~

Groups define collections of morphological segments that share similar biophysical properties. 

In the JSON file, segment groups are defined in the :code:`groups` section, which contains a list of group definitions.

.. code-block:: markdown

    "groups": [
        {
          ...
        },
        {
          ...
        },
    ],

Here are examples of different group types:

*Domain-matching group:*

.. code-block:: json

    {
        "name": "apical",
        "domains": ["apic"]
    }

*Groups spanning multiple domains:*

.. code-block:: json

    {
        "name": "dendritic",
        "domains": ["dend", "apic"]
    }

.. code-block:: json

    {
        "name": "all",
        "domains": ["soma", "axon", "dend", "apic"]
    }

To define a segment group, we can specify not only the domains where we will search for matching segments, 
but also a criterion to filter segments based on their properties.

The criterion can be one of the following types:

- :code:`diam` - diameter of the segment (in :math:`\mu m`)
- :code:`section_diam` - diameter at the center of the section to which the segment belongs
- :code:`distance` - distance of the segment center from the soma center (in :math:`\mu m`)
- :code:`domain_distance` - distance of the segment center to the closest parent segment in a different domain

When using a criterion, we must specify the minimum and/or maximum value for the segments to be included in the group.

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


3. Parameter Distributions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To define how biophysical parameters are distributed across different groups, we can use distribution functions.
For each of the parameters, we associate a mapping from segment groups to functions that describe how the parameter varies across the segments in that group.

This mapping is defined in the :code:`params` section of the JSON file, where each parameter can have a different distribution function for each group.

.. code-block:: markdown

    "params": {
            "cm": {
                   ...
            },
            "gbar_Kv": {
                   ...
            },
            ...
    }

The mapping includes all parameters, such as channel conductances (e.g., :code:`gbar_Kv`, :code:`gbar_Na`), kinetic properties (e.g., :code:`vhalf_n_Kv`), and
passive parameters (e.g., :code:`cm`, :code:`Ra`). 

.. note::

    Note that the leak mechanism is implemented as a :code:`Leak` channel with a conductance :code:`gbar_Leak`
    and an equilibrium potential :code:`e_Leak`. 
    Calcium dynamics are defined by the :code:`CaDyn` mechanism, which includes parameters such 
    as :code:`depth` (calcium shell depth), :code:`taur` (removal time constant), 
    :code:`cainf` (steady-state calcium concentration), 
    :code:`gamma` (fraction of non-buffered calcium), as well as the optional parameters :code:`kt` (Michaelis-Menten rate) and :code:`kd` (dissociation constant).

Here are some examples of how to define parameter distributions:

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

In this example, the membrane capacitance (:code:`cm`) is set to a constant value of 2 :math:`\mu F/cm^2` for the group named :code:`all`, which includes all segments in the model.
Note that we don't need to assign functions to every group available in the model.

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

The following distribution functions (along with their expected parameters) are available:

- :code:`constant`: Requires a :code:`value` parameter.
- :code:`linear`: Requires :code:`slope` and :code:`intercept` parameters.
- :code:`power`: Requires :code:`vertical_shift`, :code:`scale_factor`, :code:`exponent` and :code:`horizontal_shift` parameters.
- :code:`exponential`: Requires :code:`vertical_shift`, :code:`scale_factor`, :code:`growth_rate`, and :code:`horizontal_shift` parameters.
- :code:`sigmoid`: Requires :code:`vertical_shift`, :code:`scale_factor`, :code:`growth_rate`, and :code:`horizontal_shift` parameters.
- :code:`sinusoidal`: Requires :code:`amplitude`, :code:`frequency`, and :code:`phase` parameters.
- :code:`gaussian`: Requires :code:`amplitude`, :code:`mean`, and :code:`std` parameters.
- :code:`step`: Requires :code:`start`, :code:`end`, :code:`min_value`, and :code:`max_value` parameters.
- :code:`polynomial`: Requires :code:`coeffs` parameter, which is a list of coefficients for the polynomial function.

In addition to these functions, we can also use the following special values:

- :code:`inherit`: Each segment in the group inherits the value of the parameter from its parent segment. 

This is particularly useful for oblique dendrites, allowing them to inherit parameter values from their parent segments in the apical trunk, where the parameter may vary non-uniformly.

*Inheritance from parent segments:*

.. code-block:: json
    
    "gbar_Kv": {
        "oblique": "inherit"
    }

To learn more about segment groups and parameter distributions, refer to the
:doc:`tutorial</tutorials/tutorial_distributions>` on distributing parameters.



Stimulation and Recording Format
----------------------------------

Each stimulation protocol has its own subfolder with a :code:`config.json` file and three CSV files 
(:code:`recordings.csv`, :code:`iclamps.csv`, and :code:`synapses.csv`).

CSV Format - Locations and Properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The CSV file specifies the exact locations of stimuli and recordings on the neuronal morphology
and their properties.

All three CSV files share the same format for specifying locations on the morphology.

The :code:`recordings.csv` file contains the following columns:

- **sec_idx**: Section index in the morphology
- **loc**: Location along the section (0.0 = start, 1.0 = end)
- **var**: Variable to record (e.g., v for voltage, cai for intracellular calcium concentration)

The :code:`iclamps.csv` file contains the following columns:

- **sec_idx**: Section index in the morphology
- **loc**: Location along the section (0.0 = start, 1.0 = end)
- **amp**: Amplitude of the current clamp (in nA)
- **delay**: Delay before the current clamp starts (in ms)
- **dur**: Duration of the current clamp (in ms)

The :code:`synapses.csv` file contains the following columns:

- **sec_idx**: Section index in the morphology
- **loc**: Location along the section (0.0 = start, 1.0 = end)
- **pop_idx**: Index of the presynaptic population (this links to the population defined in the JSON file)


JSON Format - Simulation Parameters and Populations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The JSON file defines simulation parameters and properties of the virtual presynaptic populations.

*Simulation parameters:*

.. code-block:: json

    "simulation": {
        "d_lambda": 0.1,
        "temperature": 37,
        "v_init": -79,
        "dt": 0.025,
        "duration": 1000
    }


*Synaptic population definition:*

.. code-block:: json

    "populations": {
        "excitatory": {
            "idx": 0,
            "name": "excitatory",
            "syn_type": "AMPA", 
            "N": 50,
            "input_params": {
                "rate": 10,
                "noise": 1,
                "start": 100,
                "end": 800,
                "weight": 1,
                "delay": 0,
                "seed": 42
            },
            "kinetic_params": {
                "gmax": 0.001,
                "tau_rise": 0.1,
                "tau_decay": 2.5,
                "e": 0
            }
        }
    }

This example defines a population of 50 AMPA synapses firing at 10 Hz between 100-800 ms, 
with specific kinetic properties for synaptic transmission.

**Key Components of the JSON Structure:**

- :code:`metadata`: General information about the stimulus protocol
- :code:`simulation`: Global simulation parameters (temperature, timestep, duration)
- :code:`populations`: Synaptic input populations organized by neurotransmitter type

Each population contains:

- :code:`input_params`: Temporal pattern parameters (rate, timing, noise)
- :code:`kinetic_params`: Synaptic kinetics (conductance, time constants, reversal potential)

.. warning::

    This representation focuses on defining the statistical properties of synaptic inputs, such as firing rate and timing, rather than specifying exact spike times. 
   