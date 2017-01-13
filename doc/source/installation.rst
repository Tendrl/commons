============
Installation
============

1. Clone latest dev version from the source code and install virtualenvwrapper_::

    $ git clone https://github.com/Tendrl/commons.git
    $ cd commons
    $ pip install virtualenv virtualenvwrapper

2. Modify $HOME/.bashrc::

    -------------------------------------
    export WORKON_HOME=$HOME/.virtualenvs
    source /usr/bin/virtualenvwrapper.sh
    -------------------------------------

3. Install commons from source::

    $ mkvirtualenv commons
    $ pip install .
