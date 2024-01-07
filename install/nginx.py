from fabric.state import env
from fabric.api import sudo, run, execute, task, put, cd, settings
from fabric.decorators import task, parallel
import config


def configure():
    put("./config/generated/nginx.conf", "~/cms/config/")
    sudo("cp cms/config/nginx.conf /etc/nginx/nginx.conf")
    sudo("htpasswd -b -c /etc/nginx/htpasswd_AWS {0} {1}".format(config.awsaclogin, config.awsacpass))
    sudo("htpasswd -b -c /etc/nginx/htpasswd_RWS {0} {1}".format(config.rwsaclogin, config.rwsacpass))
    sudo("service nginx restart")
