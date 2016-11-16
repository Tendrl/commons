===============================
common
===============================

Common code usable by all Tendrl sds side components

* Free software: LGPL2.1
* Documentation: https://github.com/Tendrl/common/tree/master/doc/source
* Source: https://github.com/Tendrl/common
* Bugs: https://github.com/Tendrl/common/issues

Features
--------

* Provide python object mapping for writing/reading  the central store (etcd)
* Provide validation mechanism for flows (operations on an sds cluster) and atoms (smallest task on an sds cluster) to be defined and validated as per the Tendrl Definitions (sds definitions) schema 0.3


Builds
------

.. image:: https://travis-ci.org/Tendrl/common.svg?branch=master
    :target: https://travis-ci.org/Tendrl/common

Code Coverage
-------------

.. image:: https://coveralls.io/repos/github/Tendrl/common/badge.svg
    :target: https://coveralls.io/github/Tendrl/common

Developer/Install documentation
-----------------------

We also have sphinx documentation in ``docs/source``.

*To build it, run:*

::

    $ python setup.py build_sphinx

