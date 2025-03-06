Glossary
========

.. glossary::

    **Model**
         In DendroTweaks, a computational representation of a neuron that includes its morphological structure, membrane properties, 
         and simulation parameters necessary for numerical simulation.


    **Tree graph**
         A hierarchical graph structure where nodes are connected by edges, with no cycles and a single path between any two nodes.

    **Node**
        The fundamental unit of which graphs are formed.

    **Edge**
        A connection between two nodes in a graph.

    **Tree traversal**
        An algorithmic process of visiting each node in a tree graph exactly once.

    **Reconstruction**
        A digital representation of a neuron's three-dimensional morphology, composed of interconnected points with spatial coordinates.

    **SWC file**
        A standard text-based file format for storing neuronal morphology data, where each line represents a point with its type, 
        coordinates, radius, and parent point index.

    **Point**
        A discrete location in 3D space representing a specific position in a neuronal reconstruction, 
        defined by x, y, z coordinates and associated properties.

    **Section**
        A continuous unbranched segment of a neuron between points of topological change (bifurcations).

    **Domain**
        A collection of sections sharing common morphological or physiological characteristics, 
        typically corresponding to parts of a neuron such as soma, dendrites, axon, etc.

    **Segmentation**
        The process of dividing a section into smaller segments to discretize the spatial domain for numerical simulation.

    **Segment**
        A small subunit of a section resulting from the segmentation process, used to approximate the spatial properties of a neuron.

    **Segment Group**
        A collection of segments selected based on specific criteria such as domain, diameter, or distance.

    **Membrane mechanism**
        A mathematical model describing the electrical properties of a neuronal membrane, such as ion channels and pumps.

    **MOD file**
        A NEURON-specific file containing the implementation of membrane mechanisms, defining their mathematical equations and computational behavior.

    **Parameter**
        A quantitative variable describing specific neuronal properties, such as membrane capacitance, ion channel conductance, 
        or other physiological characteristics.

    **Distribution**
        A mathematical function that assigns parameter values across neuronal structures based on spatial or morphological relationships.

    **Synapse**
        A specialized junction enabling signal transmission between neurons, represented computationally as a point of conductance and kinetic changes.

    **Population**
        In DendroTweaks, a group of "virtual" neurons
        that form synapses on the postsynaptic neuron (the model). The synapses in a population
        share the same kinetic and activation properties.