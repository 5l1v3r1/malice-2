![malice logo][malice-logo]

malice
======

VirusTotal Wanna Be

Requirements
------------
1. [VirtualBox](https://www.virtualbox.org/wiki/Downloads) or [VMWare](https://www.vmware.com/products/fusion/)
2. [Vagrant](http://www.vagrantup.com/downloads.html)

##### Installing Requirements on OSX
 - Install [Homebrew](http://brew.sh)
```bash
$ brew install cask
$ brew cask install virtualbox
$ brew cask install vagrant
```

Installation
------------
```bash
$ git clone https://github.com/blacktop/malice.git
$ cd malice
$ vagrant up

wait...

$ vagrant ssh
$ source ~/malice/venv/bin/activate
(venv)$ python /vagrant/manage.py createdb
```
#### Note: for additional notes please see the Malice [wiki](https://github.com/blacktop/malice/wiki)
Usage
-----
(While ssh'd into the VM via ```vagrant ssh```)
```bash
$ source ~/malice/venv/bin/activate
(venv)$ python /vagrant/manage.py runserver
```

Then browse to http://127.0.0.1:5000

<!-- Links -->
[malice-logo]: https://raw.githubusercontent.com/black-top/malice/master/app/static/img/logo/malice_logo.png