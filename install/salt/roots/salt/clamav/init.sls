clamav-freshclam:
  pkg:
    - installed
  service:
    - running
    - enable: True

freshclam:
  cmd.wait:
    - watch:
      - pkg: clamav-freshclam

clamav-daemon:
  pkg:
    - installed
  service:
    - running
    - require:
      - cmd: freshclam

clamav-update:
  cmd:
    - name: /usr/bin/freshclam
    - onlyif: test -f /usr/bin/freshclam
    - run

clamav-daemon-restart:
  cmd:
    - name: service clamav-daemon restart
    - onlyif: test -f /usr/bin/freshclam
    - run
    - require:
      - cmd: clamav-update

clamav-updater-sudoers:
  file.managed:
    - name: /etc/sudoers.d/clamav_sudoers
    - source: salt://clamav/clamav_sudoers
    - mode: 0440

clamav-crontab:
  cron.present:
    - name: /usr/bin/freshclam --quiet --daemon-notify
    - user: 'root'
    - minute: random
    - hour: '1,7,13,19'
