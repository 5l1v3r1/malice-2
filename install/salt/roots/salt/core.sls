# -*- mode: yaml -*-
# vi: set ft=yaml :
---
apt-update:
  cmd:
    - run
    - name: apt-get update

apt-upgrade:
  cmd:
    - run
    - name: apt-get --assume-yes upgrade
    - require:
      - cmd: apt-update

linux-utils:
  pkg:
    - latest
    - names:
      - git
      - mercurial
      - libapache2-svn
      - subversion
      - htop
      - zip
      - unzip
    - require:
      - cmd: apt-upgrade