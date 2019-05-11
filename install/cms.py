from fabric.state import env
from fabric.api import sudo, run, execute, task, put, cd, settings
from fabric.decorators import task, parallel
import config


def install():
    run("wget https://github.com/cms-dev/cms/releases/download/v1.3.rc0/v1.3.rc0.tar.gz")
    run("tar -xvf v1.3.rc0.tar.gz")
    put("./config/generated/cms.conf", "~/cms/config/")
    put("./config/generated/cms.ranking.conf", "~/cms/config/")
    with cd("cms"):
        sudo("./prerequisites.py install -y")
        sudo("pip2 install -r requirements.txt")
        sudo("python2 setup.py install")
