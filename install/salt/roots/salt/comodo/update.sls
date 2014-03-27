avg-update-sigs:
  cmd:
    - name: /usr/bin/avgupdate
    - onlyif: test -f /usr/bin/avgupdate
    - run