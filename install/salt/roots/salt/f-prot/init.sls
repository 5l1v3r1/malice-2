f-prot-reqts:
  pkg.installed:
    - names:
      - libc6-i386

f-prot-tarball:
  file.managed:
    - name: /opt/fp-Linux.x86.32-ws.tar.gz
    - source: salt://f-prot/install_media/fp-Linux.x86.32-ws.tar.gz
    - require:
      - pkg: f-prot-reqts

f-prot-extract:
  cmd:
    - cwd: /opt/
    - names:
      - tar zxvf fp-Linux.x86.32-ws.tar.gz
    - run
    - require:
      - file: f-prot-tarball

/opt/fp-Linux.x86.32-ws.tar.gz:
  file.absent:
    - require:
      - file: f-prot-tarball

#f-prot-untar:
#  archive:
#    - extracted
#    - name: /opt/f-prot/
#    - source: salt://f-prot/install_media/fp-Linux.x86.32-ws.tar.gz
#    - source_hash: md5=fca330070f62953caf1c52cb71d6203c
#    - archive_format: tar
#    - tar_options: zxvf
#    - if_missing: /opt/f-prot/

#f-prot-installation:
#  cmd.run:
#    - name: ./install-f-prot.pl
#    - cwd: /opt/f-prot/
#    - unless: test -f /opt/f-prot/install-f-prot.pl
#    - user: root
#    - require:
#      - cmd: f-prot-extract

install_step_1:
  cmd.run:
    - user: root
    - unless: test -f /opt/f-prot/fpscan
    - name: ln -fs /opt/f-prot/fpscan /usr/local/bin/fpscan

install_step_2:
  cmd.run:
    - user: root
    - unless: test -f /opt/f-prot/doc/man/fpscan.1
    - name: ln -fs /opt/f-prot/doc/man/fpscan.1 /usr/local/man/man1/

install_step_3:
  cmd.run:
    - user: root
    - unless: test -f /opt/f-prot/doc/man/fprot-conf.5
    - name: ln -fs /opt/f-prot/doc/man/fprot-conf.5 /usr/local/man/man5/

install_step_4:
  cmd.run:
    - user: root
    - unless: test -f /opt/f-prot/doc/man/fpupdate.8
    - name: ln -fs /opt/f-prot/doc/man/fpupdate.8 /usr/local/man/man8/

install_step_5:
  cmd.run:
    - user: root
    - unless: test -f /opt/f-prot/fpscand
    - name: ln -fs /opt/f-prot/fpscand /usr/local/sbin/fpscand

install_step_6:
  cmd.run:
    - user: root
    - unless: test -f /opt/f-prot/fpmon
    - name: ln -fs /opt/f-prot/fpmon /usr/local/sbin/fpmon

install_step_7:
  cmd.run:
    - user: root
    - unless: test -f /opt/f-prot/doc/man/fpscand.8
    - name: ln -fs /opt/f-prot/doc/man/fpscand.8 /usr/local/man/man8/

install_step_8:
  cmd.run:
    - user: root
    - unless: test -f /opt/f-prot/doc/man/fp-milter.8
    - name: ln -fs /opt/f-prot/doc/man/fp-milter.8 /usr/local/man/man8/

install_step_9:
  cmd.run:
    - user: root
    - unless: test -f /opt/f-prot/doc/man/fp-qmail.8
    - name: ln -fs /opt/f-prot/doc/man/fp-qmail.8 /usr/local/man/man8/

install_step_10:
  cmd.run:
    - user: root
    - unless: test -f /opt/f-prot/doc/man/fpmon.8
    - name: ln -fs /opt/f-prot/doc/man/fpmon.8 /usr/local/man/man8/

install_step_11:
  cmd.run:
    - user: root
    - unless: test -f /opt/f-prot/doc/man/fp.so.8
    - name: ln -fs /opt/f-prot/doc/man/fp.so.8 /usr/local/man/man8/

install_step_12:
  cmd.run:
    - user: root
    - unless: test -f /opt/f-prot/f-prot.conf.default
    - name: cp /opt/f-prot/f-prot.conf.default /opt/f-prot/f-prot.conf

install_step_13:
  cmd.run:
    - user: root
    - unless: test -f /opt/f-prot/f-prot.conf
    - name: ln -fs /opt/f-prot/f-prot.conf /etc/f-prot.conf

install_step_14:
  cmd.run:
    - user: root
    - unless: test -f /opt/f-prot/fpscan
    - name: chmod a+x /opt/f-prot/fpscan

install_step_15:
  cmd.run:
    - user: root
    - unless: test -f /opt/f-prot/fpupdate
    - name: chmod u+x /opt/f-prot/fpupdate

install_step_16:
  cmd.run:
    - user: root
    - unless: test -f /opt/f-prot/man_pages/scan-mail.pl.8
    - name: ln -fs /opt/f-prot/man_pages/scan-mail.pl.8 /usr/share/man/man8/

install_step_17:
  cmd.run:
   - user: root
   - unless: test -f /opt/f-prot/mailtools/scan-mail.pl
   - name: chmod +x /opt/f-prot/mailtools/scan-mail.pl

f-prot-updater-sudoers:
  file.managed:
    - name: /etc/sudoers.d/f_prot_sudoers
    - source: salt://f-prot/f_prot_sudoers
    - mode: 0440
    - require:
      - cmd: install_step_15

f-prot-update-sigs:
  cmd:
    - name: /opt/f-prot/fpupdate
    - onlyif: test -f /opt/f-prot/fpupdate
    - run
    - require:
      - cmd: install_step_15