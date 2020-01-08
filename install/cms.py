from fabric.state import env
from fabric.api import sudo, run, execute, task, put, cd, settings
from fabric.decorators import task, parallel
import config


def install():
    run("wget https://github.com/cms-dev/cms/releases/download/v1.4.rc1/v1.4.rc1.tar.gz")
    run("tar -xvf v1.4.rc1.tar.gz")
    put("./config/generated/cms.conf", "~/cms/config/")
    put("./config/generated/cms.ranking.conf", "~/cms/config/")
    with cd("cms"):
        sudo("python3 prerequisites.py -y install")
        sudo("pip3 install -r requirements.txt")
        sudo("python3 setup.py install")
