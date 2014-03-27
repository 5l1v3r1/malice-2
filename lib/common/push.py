__author__ = 'Josh Maine'

import flask, redis

app = flask.Flask(__name__)
red = redis.StrictRedis(host='localhost', port=6379, db=0)

def event_stream():
    pubsub = red.pubsub()
    pubsub.subscribe('notifications')
    for message in pubsub.listen():
        print message
        yield 'data: %snn' % message['data']

@app.route('/post', methods=['POST'])
def post():
    red.publish('notifications', 'Hello!')
    return flask.redirect('/')

@app.route('/stream')
def stream():
    return flask.Response(event_stream(),
        mimetype="text/event-stream")

@app.route('/')
def index():
    return '''
<html>
<head>
    <script>
        var source = new EventSource('/stream');
        source.onmessage = function (event) {
             console.log(event.data);
        };
    </script>
</head>
<body>
    <form method="POST" action="/post">
        <input type="submit"/>
    </form>
</body>
</html>

'''

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', threaded=True)