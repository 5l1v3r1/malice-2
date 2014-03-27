from uuid import uuid4
from datetime import datetime, timedelta

from flask.sessions import SessionInterface, SessionMixin
from werkzeug.datastructures import CallbackDict
import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError, RqlDriverError


class RethinkSession(CallbackDict, SessionMixin):
    def __init__(self, initial=None, sid=None):
        CallbackDict.__init__(self, initial)
        self.db = ""
        self.sid = sid
        self.modified = False


class RethinkSessionInterface(SessionInterface):
    def __init__(self, host='localhost', port=28015, db='', collection='sessions'):
        self.db = db
        connection = r.connect(host=host, port=port)
        try:
            r.db_create(db).run(connection)
            r.db(db).table_create(collection).run(connection)
            print 'Database setup completed'
        except RqlRuntimeError:
            print 'Database already exists.'
        finally:
            connection.close()

        self.store = r.connect(host=host, port=port, db=db)

    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)
        if sid:
            stored_session = r.db(self.db).table('sessions').filter({'sid': sid}).run(self.store)
            sess = list(r.db(self.db).table('sessions').run(self.store))
            if sess:
                if stored_session.get('expiration') > datetime.utcnow():
                    return RethinkSession(initial=stored_session['data'],
                                          sid=stored_session['sid'])
        sid = str(uuid4())
        return RethinkSession(sid=sid)

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        if not session:
            response.delete_cookie(app.session_cookie_name, domain=domain)
            return
        if self.get_expiration_time(app, session):
            expiration = self.get_expiration_time(app, session)
        else:
            expiration = datetime.utcnow() + timedelta(hours=1)
        self.store.get({'sid': session.sid}).update({'sid': session.sid,
                                                     'data': session,
                                                     'expiration': expiration})
        response.set_cookie(app.session_cookie_name, session.sid,
                            expires=self.get_expiration_time(app, session),
                            httponly=True, domain=domain)
