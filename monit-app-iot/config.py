import os
basedir= os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI='sqlite:///'+os.path.join(
    basedir, '//home/ockifals/Projects/PycharmProjects/console/galeh/monit-app-iot/monitor.db'
)
SQLALCHEMY_MIGRATE_REPO=os.path.join(basedir,'db_repo')
