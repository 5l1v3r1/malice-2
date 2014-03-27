from flask.ext.script import Manager
from app import app, db
from lib.core.database import destroy_db, db_setup

manager = Manager(app)

@manager.command
def deletedb():
    destroy_db()
    db.drop_all()
    db_setup()
    app.run(host='0.0.0.0', port=5000, debug=True)

@manager.command
def runserver():
    db_setup()
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)

if __name__ == '__main__':
    manager.run()
