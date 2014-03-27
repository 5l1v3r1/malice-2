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
  pip.installed:
    - require:
      - pkg: pip-depends