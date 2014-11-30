.. Malice documentation master file, created by
   sphinx-quickstart on Sat Nov 29 18:48:54 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: ../app/static/img/logo/malice_logo.png

======
malice
======

VirusTotal Wanna Be

Requirements
------------
1. `VirtualBox`_ or `VMWare`_
2. `Vagrant`_

Installing Requirements on OSX
------------------------------
 - Install `Homebrew <http://brew.sh>`_
.. code-block:: bash

    $ brew install cask
    $ brew cask install virtualbox
    $ brew cask install vagrant


Installation
------------
.. code-block:: bash

    $ git clone https://github.com/blacktop/malice.git
    $ cd malice
    $ vagrant up

    wait...

    $ vagrant ssh
    $ source ~/malice/venv/bin/activate
    (venv)$ python /vagrant/manage.py createdb

Note: for additional notes please see the Malice `wiki <https://github.com/blacktop/malice/wiki>`_

Usage
-----
(While ssh'd into the VM via ```vagrant ssh```)
.. code-block:: bash

    $ source ~/malice/venv/bin/activate
    (venv)$ python /vagrant/manage.py runserver


Then browse to http://127.0.0.1:5000

.. _VirtualBox: https://www.virtualbox.org/wiki/Downloads
.. _VMWare: https://www.vmware.com/products/fusion/
.. _Vagrant: http://www.vagrantup.com/downloads.html