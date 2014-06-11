comodo-reqts:
  pkg.installed:
    - names:
      - libc6-i386
      - gdebi

/tmp/cav-linux_1.1.268025-1_amd64.deb:
  file.managed:
    - source: http://download.comodo.com/cavmgl/download/installs/1000/standalone/cav-linux_1.1.268025-1_amd64.deb
    - source_hash: md5=73feaa175c9d3f0d098dd416441dd740
    - require:
      - pkg: comodo-reqts

comodo-installation:
  cmd.run:
    - name: gdebi -n /tmp/cav-linux_1.1.268025-1_amd64.deb
    # - user: root
    - require:
      - file: /tmp/cav-linux_1.1.268025-1_amd64.deb

comment_1:
  file.comment:
    - name: /opt/COMODO/post_setup.sh
    - regex: ^read DISPLIC
    # - char: '#'

comment_2:
  file.blockreplace:
    - name: /opt/COMODO/post_setup.sh
    - show_changes: False
    - marker_start: 'if [ "$ACCEPT" = "NO" ]; then'
    - marker_end: "fi"
    - content: '  echo 1'

comment_3:
  file.blockreplace:
    - name: /opt/COMODO/post_setup.sh
    - show_changes: False
    - marker_start: "while true; do"
    - marker_end: "done"
    - content: "    break"

post_setup.sh:
  cmd.run:
    - name: /opt/COMODO/post_setup.sh
    - timeout: 10
    - require:
      - file: comment_3

# comodo-updater-sudoers:
#   file.managed:
#     - name: /etc/sudoers.d/comodo_sudoers
#     - source: salt://comodo/comodo_sudoers
#     - mode: 0440
#     - require:
#       - cmd: comodo-installation

update-comodo-step-1:
  cmd:
    - name: wget http://download.comodo.com/av/updates58/sigs/bases/bases.cav
    - cwd: /opt/COMODO/scanners/
    - run
    - require:
      - cmd: post_setup.sh

update-comodo-step-2:
  cmd:
    - name: mv bases.cav.1 bases.cav
    - cwd: /opt/COMODO/scanners/
    - run
    - require:
      - cmd: update-comodo-step-1
