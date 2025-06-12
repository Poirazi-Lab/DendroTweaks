Changelog
=============

Version 0.4.4
--------------
  This release addresses a bug introduced in version 0.4.3, where vectorized inputs to some
  distribution functions caused errors during parameter distribution using the :code:`model.distribute` method.
  The issue has been addressed by reverting to the non-vectorized implementation, as the performance impact 
  is minimal.

Version 0.4.3
--------------
  This release improves performance and resolves several bugs.

  Updates:

  - Fixed a bug where population loading ignored synapse types.
  - Enhanced parameter distribution performance by introducing cached properties for path distances:
    :code:`section.path_distance_to_root` and :code:`section.path_distance_within_domain`.
  - Resolved issues with re-segmentation involving stimuli and recordings. The :code:`model.set_segmentation` method now correctly updates segments, preserving existing stimuli and recordings by temporarily exporting and reloading their configurations.
  - Renamed "Test" model to "Toy" model and refined its morphologies.

Version 0.4.2
--------------
  This release fixes a bug introduced in version 0.4.1 where segments were not properly updated
  in the :code:`set_segmentation` method.

Version 0.4.1
--------------
  This release addresses minor bugs and improves the separation of NEURON-specific code from core classes.

  Key Updates:

  - New :code:`NeuronSection` and :code:`NeuronSegment` subclasses encapsulating NEURON-specific functionality and separating it from the base :code:`Section` and :code:`Segment` classes.
  - Proper :code:`CVode` handling and :code:`dt` updates during simulation initialization.

  Minor Updates:

  - Enhanced the :code:`PythonCodeGenerator` class to handle MOD file procedures with no parameters, defaulting to 'v'.


Version 0.4.0
--------------
    This release enhances cross-platform compatibility and introduces a redesigned
    data structure for recording multiple variables, such as voltage and ion channel currents.

    Key Updates:

    - Redesigned data structure for recordings with support for multiple variables. 
      The :code:`model.recordings` attribute now uses a nested dictionary to store variable names 
      (e.g., 'v', 'i_Na') and their corresponding segment values.
      To record a variable, use the :code:`model.add_recording` method, which now accepts :code:`var` argument.
    - Improved cross-platform compatibility with resolved installation and MOD file 
      compilation issues on Windows.

    Minor Updates:

    - Renamed the 'membrane' subpackage and folder to 'biophys', along with updated methods for exporting 
      and importing biophysical properties, such as :code:`model.export_biophys` and
      :code:`model.load_biophys`.
    - Renamed the :code:`model.export_stimuli_config` method to :code:`model.export_stimuli`.
    - Added a :code:`current_available` attribute to each Mechanism to indicate whether the current 
      through the channel can be recorded.


Version 0.3.1
--------------
    This release includes a minor update to resolve issues encountered during the distribution upload process to PyPI.


Version 0.3.0
--------------

    This release focuses on extending and reorganizing examples, and addressing minor bugs.

    Key Updates:

    - Reorganized example notebooks and a new example model (Hay 2011).
    - Utility function for downloading examples from the repository.
    - Default MOD files and templates included in the distribution.

    Minor Updates:

    - Replaced the prefix for standard channels.
    - Fixed the issue with parsing MOD files without TITLE.
    - Updated the standard CaDyn MOD file.
    - Improved SWC-to-domain mapping, resolving domains mismatched during export to NEURON.
    - Refined the template for exporting models to plain NEURON code.
    - Removed Jupyter from the dependencies.


Version 0.2.0
--------------
    This release reintroduces morphology reduction functionality and provides the capability to export models in plain Python NEURON code.

    Key Updates:

    - Morphology reduction subpackage for simplifying dendritic trees (based on :code:`neuron_reduce`, Amsalem et al., 2020).
    - New functionality for fitting resultant distributions in reduced models with a polynomial (for easy I/O and post-reduction modifications).
    - New :code:`model_io` module for exporting models in plain NEURON code using a Jinja2 template.

    Minor Updates:

    - Updated the :code:`lambda_f` function to align with NEURON's implementation.
    - Added :code:`domain_idx` to sections when adding a section to a domain.
    - Changed sorting algorithm to maintain SWC order by default when building morphological graphs, with an option to sort each node's children by subtree size (smallest first).
    - Fixed a bug that caused failures in selecting synaptic locations.
    - Added an option to modify :code:`nseg` per section.
    - Added :code:`node._tree` reference to each node in the tree graph.


Version 0.1.0
-------------
    This release marks a step forward in modularizing DendroTweaks, separating the core functionalities into a standalone Python library that integrates with the web-based app. The codebase is now more coherent and robust, with improved handling of neuronal morphology, ion channel kinetics, and model validation.

    Key Updates:

    - New morphology subpackage for SWC file processing and model representation.
    - Improved MOD-to-Python converter
    - Improved modular I/O for morphologies, membrane mechanisms, and stimuli

