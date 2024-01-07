#!/usr/bin/env python

import argparse
from fabric.state import env
from fabric.api import sudo, run, execute, task, put, cd, settings
from multiprocessing import Process, Queue

import config
import install
import task
import start
import start_admin
import stop
import update
import utils
import tgbot

import argparse
import sys


class Parser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


env.user = config.user
env.key_filename = config.key_filename
env.skip_bad_hosts = True
env.disable_known_hosts = True


if __name__ == "__main__":

    parser = Parser(prog="easy_cms.py",
                    description="easily install, configure, "\
                    "control [cms](http://cms-dev.github.io/)"\
                    "(contest management system v1.3rc0) on "\
                    "remote ubuntu 16.04 machines.",
                    epilog="for better understanding see README.md")
    parser.add_argument('ids', action='store', type=int, nargs='*', help='machines id\'s numbered from zero in config file')
    parser.add_argument('-i', '--install', action='store_true', default=False, dest='install', help='installs cms on some machines. do not forget to update configs for other machines if it exists.')
    parser.add_argument('-u', '--update', action='store_true', default=False, dest='update', help='updates configs on some machines.')
    parser.add_argument('-s', '--start', action='store', default=None, type=int, dest='start_contest_id', help='starts cms on some machines. takes id of contest as argument.')
    parser.add_argument('--stop', action='store_true', default=False, dest='stop', help='stops cms on some machines.')
    parser.add_argument('--start_admin', action='store_true', default=False, dest='start_admin', help='starts only admin web server.')
    parser.add_argument('-ti', '--task_import', action='store', default=None, dest='imp_task', help='import task from polygon.')
    parser.add_argument('-tu', '--task_update', action='store', default=None, dest='upd_task', help='update task from polygon.')
    parser.add_argument('--bot', action='store', default=None, type=int, dest='tgbot_contest_id', help='start telegram bot for cid.')
    parser.add_argument('--version', action='version', version='%(prog)s 3.2')
    parse_results = parser.parse_args()
    

    if not utils.validate():
        print("Please check configs")
        exit(1)

    if parse_results.ids and parse_results.ids[0] == -1:
        parse_results.ids = list(range(len(config.hosts)))

    if parse_results.install or parse_results.update:
        utils.genhosts()
        utils.genconfigs()
    
    if parse_results.install and parse_results.ids:
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Installing cms")
        execute(install.do, hosts=[config.hosts[id]["ip"] for id in parse_results.ids])
        execute(install.initdb, hosts=[config.hosts[id]["ip"] for id in parse_results.ids if config.hosts[id].get("db", True)])
        execute(install.initnginx, hosts=[config.hosts[id]["ip"] for id in parse_results.ids if config.hosts[id].get("lb", True)])
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Done")

    if parse_results.update and parse_results.ids:
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Updating configs")
        execute(update.do, hosts=[config.hosts[id]["ip"] for id in parse_results.ids])
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Done")

    if parse_results.stop and parse_results.ids:
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Stopping cms")
        execute(stop.do, hosts=[config.hosts[id]["ip"] for id in parse_results.ids if config.hosts[id].get("aws", True)])
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Done")

    if parse_results.start_admin:
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Starting admin")
        execute(start_admin.do, hosts=[config.hosts[id]["ip"] for id in range(len(config.hosts)) if config.hosts[id].get("aws", True)])
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Done")

    if parse_results.imp_task:
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Importing task")
        execute(task.imp.do, parse_results.imp_task, hosts=[config.hosts[id]["ip"] for id in range(len(config.hosts)) if config.hosts[id].get("db", True)])
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Done")

    if parse_results.upd_task:
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Updating task")
        execute(task.upd.do, parse_results.upd_task, hosts=[config.hosts[id]["ip"] for id in range(len(config.hosts)) if config.hosts[id].get("db", True)])
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Done")

    if not (parse_results.start_contest_id is None) and parse_results.ids:
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Starting contest")
        execute(start.do, parse_results.start_contest_id, hosts=[config.hosts[id]["ip"] for id in parse_results.ids])
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Done")

    if not (parse_results.tgbot_contest_id is None):
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Starting bot")
        tgbot.start(parse_results.tgbot_contest_id)
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Done")
