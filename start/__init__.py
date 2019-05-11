from fabric.state import env
from fabric.api import sudo, run, execute, task, put, cd, settings
from fabric.decorators import task, parallel
import config


@parallel
def do(contest):
    isalpha = env.host == config.hosts[0]["ip"]
    for i, host in enumerate(config.hosts):
        if env.host == host["ip"]:
            id = i
    with settings(warn_only=True):
        run("tmux kill-session -t cms")
    if isalpha:
        run("tmux new-session -d -s cms -n AdminServer 'cmsAdminWebServer'\; neww -n Logs 'cmsLogService'\; neww -n RankingServer 'cmsRankingWebServer'\; neww -n ResourceService 'cmsResourceService 0 -a {}'".format(contest))
    else:
        run("tmux new-session -d -s cms -n ResourceService 'cmsResourceService {} -a {}'".format(id, contest))
