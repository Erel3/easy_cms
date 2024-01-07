from fabric.state import env
from fabric.api import sudo, run, execute, task, put, cd, settings
from fabric.decorators import task, parallel
import config

from .deps import *
from .db import *
from .cms import *
from .nginx import *


@parallel
def do():
    put("./config/generated/hosts", "~/")
    sudo("cp hosts /etc/hosts")
    deps.install()
    cms.install()


@task
def initdb():
    db.configure()
    run("cmsInitDB")
    run("cmsAddAdmin -p {1} {0}".format(config.awslogin, config.awspass))

@task
def initnginx():
    nginx.configure()
