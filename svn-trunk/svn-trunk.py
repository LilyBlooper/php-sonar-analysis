#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import os
import subprocess
import time
import zutil

if sys.version_info < (2, 4):
    sys.stderr.write("错误: 需要 Python 2.4 或者更高版本\n")
    sys.stderr.flush()
    sys.exit(1)

# 定义svn命令常量
CONST_CMD_SVN = 'svn'
CONST_CMD_SVN_LOG = 'log'
CONST_DIR_ROOT = '/data/smartrepo'
CONST_DIR_ROOT_SCRIPTS = '/scripts/'
CONST_DIR_ROOT_DATA = '/data'


# 简单打印指定命令
def show_svn_log(svn_path, rev_from, rev_to):
    log_list = list_svn_log(svn_path, rev_from, rev_to)
    for one_line in log_list:
        print (one_line)


# svn log https://svn.team.bq.com/web/yuanchuang/trunk -r 185225:185494
# 查找指定revision从xx到yy的变动
def list_svn_log(svn_path, rev_from, rev_to):
    cmd = [CONST_CMD_SVN, CONST_CMD_SVN_LOG, svn_path, '-r', rev_from
           + ":" + rev_to]
    print(cmd)
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    proc.wait()
    try:
        cmd_log = []
        cmd_out = proc.stdout.read().splitlines()
        for one_line in cmd_out:
            cmd_log.append(one_line)
        return cmd_log
    except StandardError as e:
        print str(e)
        zutil.log_and_exit('debug::::' + "svn-trunk.py 执行 list_svn_log 异常")


def save_svn_log(proj_name, svn_path, rev_from, rev_to):
    svn_log_list = list_svn_log(svn_path, rev_from, rev_to)
    full_path = CONST_DIR_ROOT + CONST_DIR_ROOT_SCRIPTS + CONST_DIR_ROOT_DATA
    zutil.gracefully_append_file(full_path, proj_name + ".log", svn_log_list)


# 主函数
def main():
    trunk_path = sys.argv[1]
    revision_since_num = sys.argv[2]
    revision_to_num = sys.argv[3]
    zutil.jump_smoothly(CONST_DIR_ROOT)
    # show_svn_log(trunk_path, revision_since_num, revision_to_num)
    save_svn_log("yuanchang",trunk_path, revision_since_num, revision_to_num)


if __name__ == "__main__":
    main()
