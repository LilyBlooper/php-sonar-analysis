#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import os
import subprocess
import time
import zutil
import xml.etree.ElementTree as ET
from datetime import datetime
import json

if sys.version_info < (2, 4):
    sys.stderr.write("错误: 需要 Python 2.4 或者更高版本\n")
    sys.stderr.flush()
    sys.exit(1)

# @author : lilyblooper | blooper@163.com
# 定义svn命令常量
CONST_CMD_SVN = 'svn'
CONST_CMD_SVN_LOG = 'log'
CONST_DIR_ROOT = '/data/smartrepo'
CONST_DIR_ROOT_SCRIPTS = '/scripts'
CONST_DIR_ROOT_DATA = '/data'
CONST_FTYPE_IDX = ".idx"
CONST_FTYPE_DAT = ".log"


# 简单打印指定命令
def show_svn_log(svn_path, rev_from, rev_to):
    log_list = list_svn_log(svn_path, rev_from, rev_to)
    for one_line in log_list:
        print (one_line)


# svn log https://svn.team.bq.com/web/user/trunk --xml -r 185225:185494
# 查找指定revision从xx到yy的变动
def list_svn_log(svn_path, rev_from, rev_to):
    cmd = [CONST_CMD_SVN, CONST_CMD_SVN_LOG, svn_path, '--xml', '-r', rev_from
           + ":" + rev_to]
    # print(cmd)
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
        zutil.log_and_exit('debug::::' + "svn-reader.py 执行 list_svn_log 异常")


# 保存svn log 到指定文件 (无处理)
def save_svn_log(proj_name, svn_path, rev_from, rev_to):
    svn_log_list = list_svn_log(svn_path, rev_from, rev_to)
    zutil.gracefully_write_file(CONST_DIR_ROOT + "/temp", proj_name + "-temp.xml", svn_log_list)
    formatted_list = prettify(CONST_DIR_ROOT + "/temp" + "/" + proj_name + "-temp.xml")
    # 1. save file
    full_path = CONST_DIR_ROOT + CONST_DIR_ROOT_DATA
    zutil.gracefully_append_file(full_path, proj_name + CONST_FTYPE_DAT, formatted_list)
    # 2. save index
    full_path = CONST_DIR_ROOT + CONST_DIR_ROOT_DATA
    zutil.gracefully_write_file_oneline(full_path, proj_name + CONST_FTYPE_IDX, rev_to)


# 解析出xml中的log对象,返回多行,每行为一个csv(类似)的文本
def prettify(xml_location):
    pretty_log_list = []
    tree = ET.parse(xml_location)
    root = tree.getroot()
    for logentry in root.findall('logentry'):
        oneLine = buildOneLine(logentry)
        pretty_log_list.append(oneLine)
    print pretty_log_list
    return pretty_log_list


# 解析svn的时间戳
def parseSvnDate(raw_str):
    format_date = datetime.strptime(raw_str, '%Y-%m-%dT%H:%M:%S.%fZ')
    return format_date


# 构造一行
def buildOneLine(logentry):
    revId = logentry.attrib['revision']
    author = logentry.find('author').text
    cDate = parseSvnDate(logentry.find('date').text)
    msg = logentry.find('msg').text
    # print revId, author, cDate, msg
    oneLine = {"revId": revId, "author": author, "cDate": cDate, "msg": msg}
    return zutil.encodeJsonStringOneline(oneLine)


# 主函数
def main():
    trunk_path = sys.argv[1]
    revision_since_num = sys.argv[2]
    revision_to_num = sys.argv[3]
    proj_name = sys.argv[4]
    zutil.jump_smoothly(CONST_DIR_ROOT)
    # show_svn_log(trunk_path, revision_since_num, revision_to_num)
    save_svn_log(proj_name, trunk_path, revision_since_num, revision_to_num)


if __name__ == "__main__":
    main()
