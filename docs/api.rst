Alchemize API Documentation
=====================================

Transmuters
------------------

.. autoclass:: alchemize.JsonTransmuter
    :members:

.. autoclass:: alchemize.AbstractBaseTransmuter
    :members:


Mapped Models
----------------

.. autoclass:: alchemize.Attr
    :members:

.. autoclass:: alchemize.JsonMappedModel
    :members:

.. autofunction:: alchemize.mapping.get_key_paths

.. autofunction:: alchemize.mapping.get_normalized_map

Helpers
----------------

.. autoclass:: alchemize.JsonModel
    :members:

.. autoclass:: alchemize.JsonListModel
    :members:
    :inherited-members:


Exceptions
------------

.. autoclass:: alchemize.AlchemizeError

.. autoclass:: alchemize.transmute.RequiredAttributeError

.. autoclass:: alchemize.transmute.UnsupportedMappedModelError


Custom Types
------------

.. autoclass:: alchemize.ExpandedType
    :members:
