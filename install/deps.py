from fabric.state import env
from fabric.api import sudo, run, execute, task, put, cd, settings
from fabric.decorators import task, parallel
import config


def install():
    sudo("dpkg --add-architecture i386")
    sudo("apt-get update")
    sudo("DEBIAN_FRONTEND=noninteractive apt-get -y upgrade")
    sudo("DEBIAN_FRONTEND=noninteractive \
        apt-get -yq install wine-stable build-essential openjdk-8-jdk-headless fp-compiler \
        postgresql postgresql-client python3.6 cppreference-doc-en-html \
        cgroup-lite dos2unix libcap-dev zip python3.6-dev libpq-dev libcups2-dev \
        libyaml-dev libffi-dev python3-pip nginx-full python2.7 php7.2-cli \
        php7.2-fpm a2ps texlive-latex-base haskell-platform rustc \
        mono-mcs apache2-utils")
