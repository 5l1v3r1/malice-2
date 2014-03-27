# -*- mode: yaml -*-
# vi: set ft=yaml :
---
req_trid:
  pkg:
    - latest
    - names:
      - libncurses5:i386

/opt/trid/tridupdate.py:
  file.managed:
    - source: salt://trid/tridupdate.py
    - user: root
    - group: root
    - mode: 644

/opt/trid/trid:
  file.managed:
    - source: salt://trid/trid
    - user: vagrant
    - mode: 755

#unzip_trid:
#  module.run:
#    - name: archive.unzip
#    - zipfile: /opt/trid/trid_linux.zip
#    - dest: /opt/trid/
#    - mode: 755

update_trid:
  cmd.run:
    - name: "python tridupdate.py"
    - cwd: /opt/trid/
    - user: root