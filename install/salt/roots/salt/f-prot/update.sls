f-prot-update-sigs:
  cmd:
    - name: /opt/f-prot/fpupdate
    - onlyif: test -f /opt/f-prot/fpupdate
    - run