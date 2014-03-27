nginx:
  pkg:
    - installed
  service:
    - running
    - require:
      - pkg: nginx
    - watch:
      - file: /etc/nginx/nginx.conf
      {% for build in pillar.get('builds', []) %}
      {% with build_name = [build, pillar['project'], pillar['client']]|join("-") %}
      - file: /etc/nginx/sites-available/{{ build_name }}.conf
      {% endwith %}
      {% endfor %}

/etc/nginx/nginx.conf:
  file.managed:
    - source: salt://nginx/nginx.conf

/etc/nginx/sites-available/default:
  file.absent

/etc/nginx/sites-enabled/default:
  file.absent

{% for build in pillar.get('builds', []) -%}
{% with build_name = [build, pillar['project'], pillar['client']]|join("-") %}

/etc/nginx/sites-available/{{ build_name }}.conf:
  file.managed:
    - source:
      - salt://nginx/{{ build_Name }}.tmpl?env={{ pillar['project'] }}-{{ pillar['client'] }}
      - salt://nginx/build-specific.conf.tmpl
    - template: jinja
    - context:
      build: {{ build }}
      client: {{ pillar['client'] }}
      project: {{ pillar['project'] }}
      build_name: {{ build_name }}
      project_dir: /var/www/{{ pillar['client'] }}/{{ pillar['project'] }}
      nginx_config: {{ pillar['nginx'][build] }}
      locale: en_AU.UTF-8

/etc/nginx/sites-enabled/{{ build_name }}.conf:
  file.symlink:
    - target: /etc/nginx/sites-available/{{ build_name }}.conf
    - require:
      - file: /etc/nginx/sites-available/{{ build_name }}.conf

/var/www/{{ pillar['client'] }}/{{ pillar['project'] }}/{{ build_name }}_htpasswd:
  file.managed:
    - source: salt://nginx/htpasswd.tmpl
    - template: jinja
    - user: www-data
    - group: www-data
    - mode: 0600
    - context:
      passwd: {{ pillar['nginx'][build]['basic_auth'] }}

{% endwith -%}
{% endfor -%}