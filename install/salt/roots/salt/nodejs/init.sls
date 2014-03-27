# -*- mode: yaml -*-
# vi: set ft=yaml :
---
nodejs:
    pkgrepo:
    - managed
    - ppa: chris-lea/node.js
    - require_in:
        - pkg: nodejs
    pkg:
        - installed

npm-pkgs:
  npm.installed:
    - names:
      - bower
      - grunt-cli

bower_install:
  cmd.run:
    - name: bower install
    - cwd: /vagrant/app/static/
    - user: vagrant