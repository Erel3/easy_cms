from fabric.state import env
from fabric.api import sudo, run, execute, task, put, cd, settings
from fabric.decorators import task, parallel
import config
import random
import string



@parallel
def getlocalip():
    return run(config.getlocalip_command)


def instname(id):
    return "alpha" if id == 0 else "beta{:02}".format(id)


def genhosts():
    f = open("config/generated/hosts", "w")
    f.write("127.0.0.1 localhost\n")
    localips = execute(getlocalip, hosts=[host["ip"] for host in config.hosts])
    for id, host in enumerate(config.hosts):
        f.write("{local} {name}\n".format(local=localips[host["ip"]],
                                          name=instname(id)))


def genconfigs():
    with open("config/templates/cms.conf", "r") as f:
        cmsconf = ''.join(f.readlines())
    resources = ", ".join(["[\"{}\", 28000]".format(instname(id)) for id, host in enumerate(config.hosts)])
    workers_list = []
    for id, host in enumerate(config.hosts):
        if host["workers"] > 0:
            workers_list.append(", ".join(["[\"{host}\", {port}]".format(host=instname(id), port=26000+i) for i in range(host["workers"])]))
    workers = ", ".join(workers_list)
    with open("config/generated/cms.conf", "w") as f:
        f.write(cmsconf.format(resources=resources,
                               workers=workers,
                               dblogin=config.dblogin,
                               dbpass=config.dbpass,
                               rwstalklogin=config.rwstalklogin,
                               rwstalkpass=config.rwstalkpass))

    with open("config/templates/cms.ranking.conf", "r") as f:
        cmsrankingconf = ''.join(f.readlines())
    with open("config/generated/cms.ranking.conf", "w") as f:
        f.write(cmsrankingconf.format(rwstalklogin=config.rwstalklogin,
                                      rwstalkpass=config.rwstalkpass))

def random_string(size=6, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
