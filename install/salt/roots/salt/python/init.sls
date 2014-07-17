# -*- mode: yaml -*-
# vi: set ft=yaml :
---
req_packages:
    pkg.installed:
        - names:
            - python
            - python-dev
            - python-pip
            - python-virtualenv
            - build-essential
            - python-software-properties
            # Needed for pydeep
            - libfuzzy2
            - libfuzzy-dev
            - ssdeep
            # Needed for Tracking module
            - libgeoip-dev
            - libxml2-dev
            - libxslt1-dev
            # Needed for LDAP
            - libldap2-dev
            - libsasl2-dev
            - libssl-dev

/home/vagrant/malice/venv:
    virtualenv.managed:
        - pip: True
        - no_site_packages: True
        - user: vagrant
        - require:
          - pkg: req_packages

update_pip_in_venv:
    pip.installed:
        - user: vagrant
        - name: pip
        - upgrade: True
        - bin_env: /home/vagrant/malice/venv/bin/pip
        - require:
          - virtualenv: /home/vagrant/malice/venv

install_requirements:
    pip.installed:
        - runas: vagrant
        - requirements: /vagrant/requirements.txt
        - bin_env: /home/vagrant/malice/venv/bin/pip
        - require:
          - virtualenv: /home/vagrant/malice/venv
          - pip: update_pip_in_venv

update_pefile_in_venv:
    pip.installed:
        - user: vagrant
        - name: pefile
        - source: svn+http://pefile.googlecode.com/svn/trunk/
        - upgrade: True
        - bin_env: /home/vagrant/malice/venv/bin/pip
        - require:
          - virtualenv: /home/vagrant/malice/venv