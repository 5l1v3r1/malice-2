avg-reqts:
  pkg.installed:
    - names:
      - libc6-i386

avg-installer:
  file.managed:
    - name: /root/avg/avg2013flx-r3118-a6926.i386.deb
    - source: salt://avg/install_media/avg2013flx-r3118-a6926.i386.deb
    - require:
      - pkg: avg-reqts

avg-installation:
  cmd.run:
    - name: dpkg -i /root/avg/avg2013flx-r3118-a6926.i386.deb
    - unless: test -f /root/avg/avg2013flx-r3118-a6926.i386.deb
    - user: root
    - require:
      - file: avg-installer

avgd:
  service:
    - running
    - enable: True
    - reload: True

avast-updater-sudoers:
  file.managed:
    - name: /etc/sudoers.d/avg_sudoers
    - source: salt://avg/avg_sudoers
    - mode: 0440
    - require:
      - cmd: avg-installation

avg-update-sigs:
  cmd:
    - name: /usr/bin/avgupdate
    - onlyif: test -f /usr/bin/avgupdate
    - run
    - require:
      - cmd: avg-installation