![malice logo][malice-logo]

malice
======
[![Build Status][travis-badge]](https://travis-ci.org/blacktop/malice)
[![Code Health][health-badge]](https://landscape.io/github/blacktop/malice/mongo)
[![Coverage Status][cov-badge]](https://coveralls.io/r/blacktop/malice)
[![Support blacktop via Gittip][gittip-badge]](https://www.gittip.com/blacktop/)
[![Gitter Chat][gitter-badge]](https://gitter.im/blacktop/malice)

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

### Home
![malice logo][index]
### Samples
![malice logo][samples]
### Analysis
![malice logo][analysis]

Documentation
-------------
Documentation is comming soon.

Testing
-------
To run the tests (in the project directory):
```bash
$ pip install nose coverage
$ nosetests --with-coverage --cover-html -s
```

Todo
----
- [x] Get Initial Alpha Release Ready
- [ ] Create Salt states for uwsgi and nginx and supervisor so Malice auto starts on **vagrant up**
- [ ] Transition to MongoDB
- [ ] Re-implement async distribute worker task framework ([python-rq](http://python-rq.org) or [celery](http://www.celeryproject.org)/[RabbitMQ](http://www.rabbitmq.com))
- [ ] Create Plug-in framework
- [ ] Transition to [Docker](), [CoreOS]() and [serf]()
- [ ] Deploy Demo server

Contributing
------------
1. Fork it.
2. Create a branch (`git checkout -b my_malice`)
3. Commit your changes (`git commit -am "Added Something Cool"`)
4. Push to the branch (`git push origin my_malice`)
5. Open a [Pull Request](https://github.com/blacktop/malice/pulls)
6. Wait for me to figure out what the heck a pull request is...

<!-- Links -->
[malice-logo]: https://raw.githubusercontent.com/black-top/malice/master/app/static/img/logo/malice_logo.png
[travis-badge]: https://travis-ci.org/blacktop/malice.svg?branch=mongo
[health-badge]: https://landscape.io/github/blacktop/malice/mongo/landscape.png
[cov-badge]: https://coveralls.io/repos/blacktop/malice/badge.png
[gittip-badge]: http://img.shields.io/gittip/blacktop.svg
[gitter-badge]: https://badges.gitter.im/blacktop/malice.png
[index]: https://raw.githubusercontent.com/blacktop/malice/master/docs/images/index.png
[samples]: https://raw.githubusercontent.com/blacktop/malice/master/docs/images/samples.png
[analysis]: https://raw.githubusercontent.com/blacktop/malice/master/docs/images/analysis.png