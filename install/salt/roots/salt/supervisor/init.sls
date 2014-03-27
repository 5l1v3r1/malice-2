supervisor:
  pkg:
    - installed
  service.running:
    - require:
      - pkg: supervisor
    - watch:
      - file: /etc/supervisor/supervisord.conf

/etc/supervisor/supervisord.conf:
  file.managed:
    - template: jinja
    - require:
      - pkg: supervisor