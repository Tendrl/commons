============
Installation
============

1. Clone latest dev version from the source code and install virtualenvwrapper_::

    $ git clone https://github.com/Tendrl/bridge_common.git
    $ cd bridge_common
    $ pip install virtualenv virtualenvwrapper

2. Modify $HOME/.bashrc::

    -------------------------------------
    export WORKON_HOME=$HOME/.virtualenvs
    source /usr/bin/virtualenvwrapper.sh
    -------------------------------------

3. Install bridge_common from source::

    $ mkvirtualenv bridge_common
    $ pip install .

4. Create config files::

    $ cp etc/tendrl/tendrl.conf.sample /etc/tendrl/tendrl.conf
    $ cp etc/sample/logging.yaml.timedrotation.sample /etc/tendrl/bridge_common_logging.conf

5. Edit config file ``/etc/tendrl/tendrl.conf`` as required

    ---------------------------------------------------------------
    # Central store etcd host/ip
    etcd_connection = <IP of the node where etcd server is running>
    ---------------------------------------------------------------

6. Create log dir::

    $ mkdir /var/log/tendrl
