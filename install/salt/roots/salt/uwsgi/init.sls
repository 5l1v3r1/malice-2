# -*- mode: yaml -*-
# vi: set ft=yaml :
---
pip-depends:
  pkg.installed:
    - names:
      - build-essential
      - python-dev
      - python-pip
      - libxml2-dev

uwsgi:
  pkg.installed:
    - require:
      - pkg: pip-depends

uwsgi-plugin-python:
  pkg.installed:
    - require:
      - pkg: pip-depends
