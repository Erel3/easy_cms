from fabric.state import env
from fabric.api import sudo, run, execute, task, put, cd, settings
from fabric.decorators import task, parallel
import config


@parallel
def do(contest):
    counter = 0
    for i, host in enumerate(config.hosts):
        if env.host == host["ip"]:
            id = i
    with settings(warn_only=True):
        run("tmux kill-session -t cms")
    tmux_command = "tmux new-session -d -s cms -n ResourceService 'cmsResourceService {id} -a {contest}'\;".format(id=id, contest=contest)
    if config.hosts[id].get("lb", False):
        tmux_command += " neww -n Logs 'cmsLogService'\;"
    if config.hosts[id].get("rws", False):
        tmux_command += " neww -n RankingServer 'cmsRankingWebServer'\;"
    if config.hosts[id].get("aws", False):
        tmux_command += " neww -n AdminServer 'cmsAdminWebServer'\;"
    run(tmux_command)
