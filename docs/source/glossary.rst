Glossary
========

.. glossary::

    **Model**
        In DendroTweaks, a model is a representation of a neuron that contains the morphological data, the membrane mechanisms, stimuli and the means to run simulations.

    **Tree graph**
        A tree graph is a type of a network graph that is composed of nodes connected by edges. 
        In a tree graph, there is only one path between any two nodes.

    **Node**
        A node is a point in a tree graph that is connected to other nodes by edges.

    **Tree traversal**
        Tree traversal is the process of visiting each node in a tree graph exactly once.

    **Reconstruction**
        A reconstruction is a representation of a neuron morphology as a collection of points
        with coordinates and properties such as diameter, type, etc.

    **SWC file**
        An SWC file is a file format that is used to store neuron morphologies as a collection of points and connections between them.

    **Point**
        A point in 3D space that represents a part of a neuron 
        and is defined by its coordinates and properties such as diameter, type, etc. as well as connections to other points.

    **Section**
        A section is a part of a neuron between two bifurcation points.

    **Domain**
        A domain is a collection of sections that share the same properties and typically represents
        a part of a neuron such as soma, axon, dendrite, etc.

    **Segmentation**
        Segmentation is the process of dividing a neuron into segments.

    **Segment**
        A segment is a part of a section that is defined by a set of points.

    **Segment Group**
        A segment group is a collection of segments selected based on certain 
        criteria such as domain, diameter, distance, etc.

    **Membrane mechanism**
        A membrane mechanism is a set of equations that describe the behavior of the membrane of a neuron.

    **MOD file**
        A MOD file is a file that contains the equations, parameters, and other information
        that describe the behavior of a membrane mechanism.

    **Parameter**
        A parameter is a variable such as membrane capacitance, channel conductance, etc.
        that can have different values in different parts of a neuron. 
        Often, parameters are associated with membrane mechanisms, but they can also be independent.

    **Distribution**
        A distribution is a function that assigns values to parameters based on certain criteria, typically distance from the soma.

    **Synapse**
        A synapse is a connection between two neurons that allows them to communicate.

    **Population**
        A (presynaptic) population in DendroTweaks is a group of "virtual" neurons
        that form synapses on the postsynaptic neuron (the model). The synapses in a population
        share the same kinetic and activation properties.