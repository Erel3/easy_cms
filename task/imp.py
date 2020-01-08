from fabric.state import env
from fabric.api import sudo, run, execute, task, put, cd, settings
from fabric.decorators import task, parallel
import config
import utils


@parallel
def do(link):
    work_folder = utils.random_string(15)
    name = link.split("/")[-1]
    run("mkdir -p tasks")
    run("mkdir -p tasks/{}/{}".format(work_folder, name))
    with cd("tasks/{}/{}".format(work_folder, name)):
        run("wget -O task.zip --post-data=login={}\&password={} {}".format(config.pollogin, config.polpassword, link))
        run("unzip task.zip")
        run("find . -name \"*.sh\" -exec chmod +x {} \;")
        run("./doall.sh")
        run("cmsImportTask ./ -n {}".format(name))
