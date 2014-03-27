Malice Flask Web App
==================

## To Run
    python run.py runserver

### API
    localhost:5000/api/v1/search?md5=60b7c0fead45f2066e5b805a91f4f0fc

    localhost:5000/api/v1/searches?md5=60b7c0fead45f2066e5b805a91f4f0fc&md5=5e28284f9b5f9097640d58a73d38ad4c

### supervisord
    [program:Malice]
    command=uwsgi --plugin python /home/ubuntu/malice/web/uwsgi.ini
    directory=/home/ubuntu/malice/web/
    autostart=true
    autorestart=true
    stdout_logfile=/home/ubuntu/malice/web/logs/uwsgi.log
    redirect_stderr=true
    stopsignal=QUIT

### nginx.conf
    server {
            listen   80; ## listen for ipv4; this line is default and implied

            # Make site accessible from http://localhost/
            server_name malice.com;

            location / {
                    try_files $uri @app;
            }

            location @app {
                include uwsgi_params;
                uwsgi_pass unix:/tmp/uwsgi.sock;
            }
    }
