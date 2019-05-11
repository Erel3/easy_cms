from fabric.state import env
from fabric.api import sudo, run, execute, task, put, cd, settings
from fabric.decorators import task, parallel
import config


@parallel
def do():
    put("./config/generated/hosts", "~/")
    sudo("cp hosts /etc/hosts")

    put("./config/generated/cms.conf", "~/cms/config/")
    put("./config/generated/cms.ranking.conf", "~/cms/config/")

    with cd("cms"):
        sudo("./prerequisites.py install -y")
