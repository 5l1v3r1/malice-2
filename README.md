![malice logo](https://raw.githubusercontent.com/black-top/malice/master/app/static/img/logo/malice_logo.png)

malice
======
[![Build Status](https://drone.io/github.com/blacktop/malice/status.png)](https://drone.io/github.com/blacktop/malice/latest)
[![Build Status](https://travis-ci.org/blacktop/malice.svg?branch=master)](https://travis-ci.org/blacktop/malice)
[![Support blacktop via Gittip](http://img.shields.io/gittip/blacktop.svg)](https://www.gittip.com/blacktop/)

VirusTotal Wanna Be

Requirements
------------
1. [VirtualBox](https://www.virtualbox.org/wiki/Downloads) or [VMWare](https://www.vmware.com/products/fusion/)
2. [Vagrant](http://www.vagrantup.com/downloads.html)

Installation
-----------
```bash
$ git clone https://github.com/blacktop/malice.git
$ cd malice
$ vagrant up
...wait...
```
##### NOTE - During recent testing salt states were failing for:
- trid
- exif
- clamav
- avg

Usage
-----
```bash
$ vagrant ssh
$ source malice/venv/bin/activate
$ python /vagrant/manage.py runserver
```

Then browse to http://127.0.0.1:5000

### Home
![malice logo](https://raw.githubusercontent.com/blacktop/malice/master/docs/images/index.png)
### Samples
![malice logo](https://raw.githubusercontent.com/blacktop/malice/master/docs/images/samples.png)
### Analysis
![malice logo](https://raw.githubusercontent.com/blacktop/malice/master/docs/images/analysis.png)

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
2. Create a branch (`git checkout -b my_virus_total_api`)
3. Commit your changes (`git commit -am "Added Something Cool"`)
4. Push to the branch (`git push origin my_virus_total_api`)
5. Open a [Pull Request](https://github.com/blacktop/virustotal-api/pulls)
6. Wait for me to figure out what the heck a pull request is...
