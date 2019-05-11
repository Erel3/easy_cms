from fabric.state import env
from fabric.api import sudo, run, execute, task, put, cd, settings
from fabric.decorators import task, parallel
import config


@parallel
def do():
    with settings(warn_only=True):
        run("tmux kill-session -t cms")
