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
    isalpha = env.host == config.hosts[0]["ip"]
    put("./config/generated/hosts", "~/")
    sudo("cp hosts /etc/hosts")
    deps.install()
    cms.install()
    if isalpha:
        db.configure()
    if isalpha:
        nginx.configure()


@task
def initdb():
    run("cmsInitDB")
    run("cmsAddAdmin -p {1} {0}".format(config.awslogin, config.awspass))
