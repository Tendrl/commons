============
Installation
============

Installation of latest dev version from the source code::

    $ git clone https://github.com/Tendrl/bridge_common.git
    $ cd bridge_common
    $ yum install http://dl.fedoraproject.org/pub/epel/7/x86_64/p/python-pip-7.1.0-1.el7.noarch.rpm
    $ pip install virtualenv virtualenvwrapper

Modify $HOME/.bashrc and add below content at the last

-------------------------------------
export WORKON_HOME=$HOME/.virtualenvs
source /usr/bin/virtualenvwrapper.sh
-------------------------------------

    $ mkvirtualenv bridge_common
    $ pip install .
    $ cp etc/tendrl/tendrl.conf.sample /etc/tendrl/tendrl.conf

Edit /etc/tendrl/tendrl.conf and update the correct IP of the etcd server node as below

---------------------------------------------------------------
# Central store etcd host/ip
etcd_connection = <IP of the node where etcd server is running>
---------------------------------------------------------------

Create the required log directory

    $ mkdir -p /var/log/tendrl
