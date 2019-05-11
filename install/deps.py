from fabric.state import env
from fabric.api import sudo, run, execute, task, put, cd, settings
from fabric.decorators import task, parallel
import config


def install():
    sudo("dpkg --add-architecture i386")
    sudo("apt-get update")
    sudo("DEBIAN_FRONTEND=noninteractive apt-get -y upgrade")
    sudo("DEBIAN_FRONTEND=noninteractive apt-get -y install wine build-essential "\
         "openjdk-8-jre openjdk-8-jdk fpc postgresql postgresql-client gettext "\
         "python2.7 iso-codes shared-mime-info stl-manual cgroup-lite dos2unix "\
         "nginx-full php7.0-cli php7.0-fpm texlive-latex-base a2ps gcj-jdk "\
         "haskell-platform htop tmux python-pip postgresql-server-dev-9.5 "\
         "libcups2-dev apache2-utils")
