#!/bin/bash

tox -epep8
retval1=$?
tox -ecover
retval2=$?
exit $retval1 && $retval2
