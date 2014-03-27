# -*- mode: yaml -*-
# vi: set ft=yaml :
---
req_packages:
    pkg.installed:
        - names:
            - python-dev
            - python-virtualenv
            - libfuzzy2
            - libfuzzy-dev
            - ssdeep
            - libgeoip-dev
            - libxml2-dev
            - libxslt1-dev

/home/vagrant/malice/venv:
    virtualenv.managed:
        - no_site_packages: True
        - runas: vagrant
        - requirements: salt://requirements/requirements.txt
        - require:
            - pkg: libfuzzy2
            - pkg: libfuzzy-dev
            - pkg: ssdeep

#update_pip:
#  pip.installed:
#    - name: pip
#    - bin_env: /home/vagrant/malice/venv
#    - upgrade: True
#    - require:
#      - pkg: python-pip
#      - pkg: python-virtualenv
#
#update_setuptools:
#  pip.installed:
#    - name: setuptools
#    - bin_env: /home/vagrant/malice/venv
#    - upgrade: True
#    - require:
#      - pkg: python-pip
#      - pkg: python-virtualenv