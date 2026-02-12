Choosing a Simulator
====================

.. warning::

    Full compatibility with simulators other than NEURON is currently under development.

DendroTweaks provides a high-level, simulator-agnostic model representation 
and performs all model construction steps (e.g., building morphologies from SWC files), 
whereas the actual numerical simulation is delegated to an external simulator.
To achieve this, DendroTweaks automatically instantiates corresponding sections and segments within the selected simulator.

The following simulators are currently supported:

- `NEURON <https://neuron.yale.edu/neuron/>`_

Planned support for the following simulators:

- `Jaxley <https://jaxley.readthedocs.io/en/latest/>`_

.. tip::

    While support for Jaxley is an ongoing effort, you can already automatically create Jaxley-compatible ion channel classes from MOD files using DendroTweaks.
    For more information about the Jaxley-compatible classes, refer to the corresponding :doc:`tutorial</tutorials/convert_to_jaxley>`.

Creating and Referencing Sections in a Simulator
------------------------------------------------

Once we have created an instance of a :code:`SectionTree`, we can reference the sections in the simulator. 

.. code-block:: python

    >>> for sec in sec_tree.sections:
            sec.create_and_reference()

This step is normally performed automatically when using a :code:`Model` instance inside 
the :code:`load_morphology` method. You would need to do it manually only if you are working directly with a :code:`SectionTree`.

Now each DendroTweaks :term:`Section` is associated with a simulator-specific section. The user can access the simulator-specific section using the :code:`_ref` attribute.

.. code-block:: python

    >>> soma = model.get_sections(lambda sec: sec.domain_name == 'soma')[0]
    >>> soma._ref
    <nrn.Section at 0x7f8b3b3b3b50>

.. image:: ../_static/ref.png
    :width: 50%
    :align: center
