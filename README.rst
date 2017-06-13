===============================
commons
===============================

Common code usable by all Tendrl sds side components

* Free software: LGPL2.1
* Documentation: https://github.com/Tendrl/commons/tree/master/doc/source
* Source: https://github.com/Tendrl/commons
* Bugs: https://github.com/Tendrl/commons/issues

Features
--------

* Provide python object mapping for writing/reading  the central store (etcd)
* Provide validation mechanism for flows (operations on an sds cluster) and atoms (smallest task on an sds cluster) to be defined and validated as per the Tendrl Definitions (sds definitions) schema 0.3


Builds
------

.. image:: https://travis-ci.org/Tendrl/commons.svg?branch=master
  :target: https://travis-ci.org/Tendrl/commons

Code Coverage
-------------

.. image:: https://codecov.io/gh/Tendrl/commons/branch/develop/graph/badge.svg
  :target: https://codecov.io/gh/Tendrl/commons

Release process
---------------

When you are ready to cut a new version:

#. Bump the version number in ``tendrl/commons/__init__.py`` and commit your
   changes.
   ::

      python setup.py bumpversion

#. Tag and push to GitHub.
   ::

      python setup.py release

#. Make an SRPM.
   ::

      make srpm



Developer/Install documentation
-------------------------------

We also have sphinx documentation in ``docs/source``.

*To build it, run:*

::

    $ python setup.py build_sphinx

