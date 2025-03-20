Changelog
=============

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

