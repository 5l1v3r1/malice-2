avg-reqts:
  pkg.installed:
    - names:
      - libc6-i386

/tmp/avg2013flx-r3118-a6926.i386.deb:
  file.managed:
    - source: http://download.avgfree.com/filedir/inst/avg2013flx-r3118-a6926.i386.deb
    - source_hash: md5=e27ce887fb583c19deffb03e15e55225
    - require:
      - pkg: avg-reqts

avg-installation:
  cmd.run:
    - name: dpkg -i /tmp/avg2013flx-r3118-a6926.i386.deb
    # - user: root
    - require:
      - file: /tmp/avg2013flx-r3118-a6926.i386.deb

avgd:
  service:
    - running
    - enable: True
    - reload: True

/etc/sudoers.d/avg_sudoers:
  file.managed:
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
