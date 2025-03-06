Segmentation
==========================

Before running simulations, we need to set the spatial discretization of the model. The spatial discretization determines the number of segments in a section. The number of segments is calculated based on the frequency-dependent length constant and the spatial discretization coefficient.
Spatial discretization also depends on the membrane capacitance and axial resistance of the model.
We can do this by setting the values globally for the entire cell.

.. code-block:: python

    >>> model.set_parameter('cm', value=1.0)
    >>> model.set_parameter('Ra', value=100.0)

Alternatively, we can set the values for specific groups of sections. For example, to set the membrane capacitance and axial resistance for all sections in the model
as it was done in the previous :doc:`tutorial</tutorials/tutorial_distributions>`.



The :code:`set_segmentation` method is used to set the spatial discretization coefficient. The spatial discretization coefficient determines the number of segments in a section. The number of segments is calculated based on the frequency-dependent length constant and the spatial discretization coefficient.

.. code-block:: python
    
    >>> model.set_segmentation(d_lambda=0.1, f=100)
    

We can access the segmentation graph using the :code:`seg_tree` attribute.

.. code-block:: python

    >>> len(model.seg_tree) # number of segments
    256


How does it work?
-------------------------------------------------------------
The segmentation process is based on the frequency-dependent length constant and the spatial discretization coefficient. The frequency-dependent length constant is calculated as follows:

.. math::

    \lambda_f = \frac{1}{2} \cdot \sqrt{\dfrac{d}{\pi f R_a c_m}}

where

- :math:`\lambda_f` - frequency-dependent length constant
- :math:`d` - diameter of the segment
- :math:`f` - frequency
- :math:`R_a` - axial resistance
- :math:`c_m` - membrane capacitance

.. math::

    \text{nseg} = \left\lfloor \dfrac{L}{d\_\lambda \cdot \lambda_f} + 0.9 \right\rfloor / 2 \cdot 2 + 1

where

- :math:`\text{nseg}` - number of segments
- :math:`L` - length of the section
- :math:`d\_\lambda` - coefficient that determines the spatial discretization
