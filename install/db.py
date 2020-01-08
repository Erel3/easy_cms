from fabric.state import env
from fabric.api import sudo, run, execute, task, put, cd, settings
from fabric.decorators import task, parallel
import config


def configure():
    run("sudo -u postgres psql -c \"CREATE USER {0} WITH PASSWORD '{1}'\"".format(config.dblogin, config.dbpass))
    run("sudo -u postgres createdb --username=postgres --owner={} cmsdb".format(config.dblogin))
    run("sudo -u postgres psql --username=postgres --dbname=cmsdb --command='ALTER SCHEMA public OWNER TO {}'".format(config.dblogin))
    run("sudo -u postgres psql --username=postgres --dbname=cmsdb --command='GRANT SELECT ON pg_largeobject TO {}'".format(config.dblogin))
    run("echo 'host    all             all             {}            md5' | sudo tee -a /etc/postgresql/10/main/pg_hba.conf".format(config.localipmask))
    run("echo \"listen_addresses = '*'\" | sudo tee -a /etc/postgresql/10/main/postgresql.conf")
    run("sudo service postgresql restart")
