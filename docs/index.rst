Welcome to Alchemize's documentation!
=====================================

|travis|  |codecov|

Alchemize is designed to be a simple serialization and deserialization
library. The primary use-case for Alchemize is to allow for users to
quickly build ReST clients using simple model mappings to transform
data from Python objects to a serializable form and vice-versa.

The power of Alchemize is that you can use it to augment existing
model structures from other libraries. For example, you can use Alchemize
to easily serialize your ORM models.

Installation
--------------

Alchemize is available on PyPI

.. code-block:: shell

    pip install alchemize


.. toctree::
   :maxdepth: 2

   using
   api


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. |travis| image:: https://travis-ci.org/jmvrbanac/alchemize.svg
    :target: https://travis-ci.org/jmvrbanac/alchemize

.. |codecov| image:: https://codecov.io/gh/jmvrbanac/alchemize/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/jmvrbanac/alchemize
