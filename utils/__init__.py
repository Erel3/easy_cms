from fabric.state import env
from fabric.api import sudo, run, execute, task, put, cd, settings
from fabric.decorators import task, parallel
import config
import random
import string

def validate():
    has_db = False
    has_lb = False
    has_cws = False
    has_aws = False
    has_rws = False
    has_worker = False
    for host in config.hosts:
        if host.get("workers", 0) > 0:
            has_worker = True
        if host.get("db", False):
            if has_db:
                return False
            has_db = True
        if host.get("lb", False):
            if has_lb:
                return False
            has_lb = True
        if host.get("cws", False):
            has_cws = True
        if host.get("aws", False):
            if has_aws:
                return False
            has_aws = True
        if host.get("rws", False):
            if has_rws:
                return False
            has_rws = True
    if not has_db or not has_lb or not has_cws or not has_aws or not has_rws or not has_worker:
        return False
    return True

@parallel
def getlocalip():
    return run(config.getlocalip_command)

def instname(id):
    return "instance{:02}".format(id)

def genhosts():
    f = open("config/generated/hosts", "w")
    f.write("127.0.0.1 localhost\n")
    localips = execute(getlocalip, hosts=[host["ip"] for host in config.hosts])
    for id, host in enumerate(config.hosts):
        if host.get("db", False):
            f.write("{local} {name}\n".format(local=localips[host["ip"]],
                                          name="database"))
        if host.get("lb", False):
            f.write("{local} {name}\n".format(local=localips[host["ip"]],
                                          name="loadbalancer"))
        if host.get("aws", False):
            f.write("{local} {name}\n".format(local=localips[host["ip"]],
                                          name="aws"))
        if host.get("rws", False):
            f.write("{local} {name}\n".format(local=localips[host["ip"]],
                                          name="rws"))
        f.write("{local} {name}\n".format(local=localips[host["ip"]],
                                          name=instname(id)))


def genconfigs():
    with open("config/templates/cms.conf", "r") as f:
        cmsconf = ''.join(f.readlines())
    resources = ", ".join(["[\"{}\", 28000]".format(instname(id)) for id, host in enumerate(config.hosts)])
    cws_cnt = 0
    cws_list = []
    for id, host in enumerate(config.hosts):
        if host["cws"]:
            cws_list.append("[\"{host}\", {port}]".format(host=instname(id), port=21000))
            cws_cnt += 1
    cws = ", ".join(cws_list)
    workers_list = []
    for id, host in enumerate(config.hosts):
        if host["workers"] > 0:
            workers_list.append(", ".join(["[\"{host}\", {port}]".format(host=instname(id), port=26000+i) for i in range(host["workers"])]))
    workers = ", ".join(workers_list)
    loadbalancer_name = instname([id for id, host in enumerate(config.hosts) if host.get("lb", False)][0])
    aws_name = instname([id for id, host in enumerate(config.hosts) if host.get("aws", False)][0])
    with open("config/generated/cms.conf", "w") as f:
        f.write(cmsconf.format(aws_name=aws_name,
                               loadbalancer_name=loadbalancer_name,
                               resources=resources,
                               workers=workers,
                               cws=cws,
                               cws_listen_addr=", ".join("\"\"" for i in range(cws_cnt)),
                               cws_listen_port=", ".join("8888" for i in range(cws_cnt)),
                               dblogin=config.dblogin,
                               dbpass=config.dbpass,
                               rwstalklogin=config.rwstalklogin,
                               rwstalkpass=config.rwstalkpass))

    with open("config/templates/cms.ranking.conf", "r") as f:
        cmsrankingconf = ''.join(f.readlines())
    with open("config/generated/cms.ranking.conf", "w") as f:
        f.write(cmsrankingconf.format(rwstalklogin=config.rwstalklogin,
                                      rwstalkpass=config.rwstalkpass))
    with open("config/templates/nginx.conf", "r") as f:
        nginxconf = ''.join(f.readlines())
    cws_list = []
    for id, host in enumerate(config.hosts):
        if host["cws"]:
            cws_list.append("server {host}:8888;".format(host=instname(id)))
    cws = "".join(cws_list)
    with open("config/generated/nginx.conf", "w") as f:
        f.write(nginxconf.format(cws=cws))

def random_string(size=6, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
