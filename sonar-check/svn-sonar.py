#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import os
import subprocess
import time
import shutil
import zutil

if sys.version_info < (2, 4):
    sys.stderr.write("错误: 需要 Python 2.4 或者更高版本\n")
    sys.stderr.flush()
    sys.exit(1)

# 定义svn命令常量
CONST_CMD_SVNLOOK = 'svnlook'
CONST_CMD_SVNLOOK_INFO = 'info'
CONST_CMD_SVNLOOK_AUTHOR = 'author'
CONST_CMD_SVNLOOK_CHANGED = 'changed'
CONST_DIR_ROOT_SNAPSHOT = '/data/codereview/snapshot_sonar/'
CONST_DIR_ROOT_RAW = '/data/codereview/raw_copy/'
CONST_DIR_ROOT_SCRIPTS = '/data/codereview/scripts/'
CONST_AUTH_UNAME = 'root'
CONST_AUTH_PWD = 'root'


class SvnHandler:
    def __init__(self, repos_path, revision_num, svn_path, proj_name):
        self.proj_name = proj_name
        self.repos_path = repos_path
        self.revision_num = revision_num

    def list_author(self):
        cmd = [CONST_CMD_SVNLOOK, CONST_CMD_SVNLOOK_INFO, self.repos_path, '-r', self.revision_num]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        proc.wait()
        try:
            cmd_out = proc.stdout.read().splitlines()
            author = cmd_out[0]
            return author
        except StandardError as e:
            print str(e)
            zutil.log_and_exit('debug::::' + "svn-sonar.py 执行 list_author 异常")

    # svnlook changed /my/repo -r 88
    # 查找出本次revision影响的文件
    def list_files(self):
        cmd = [CONST_CMD_SVNLOOK, CONST_CMD_SVNLOOK_CHANGED, self.repos_path, '-r', self.revision_num]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        proc.wait()
        try:
            file_list = []
            cmd_out = proc.stdout.read().splitlines()
            for one_line in cmd_out:
                file_list.append(one_line)
            return file_list
        except StandardError as e:
            print str(e)
            zutil.log_and_exit('debug::::' + "svn-sonar.py 执行 list_files 异常")

    # 过滤并并备份到另外的位置
    def filter_backup_files(self, changed_lines):
        is_initialized = self._working_copy_exists()
        if is_initialized:
            self._working_copy_update()
        else:
            self._working_copy_checkout()
        # make copy to snapshot location
        src_location = CONST_DIR_ROOT_RAW + self.proj_name
        desc_location = CONST_DIR_ROOT_SNAPSHOT + self.proj_name + '/' + self.revision_num

        for each_line in changed_lines:
            if str(each_line).startswith("A") or str(each_line).startswith("M"):
                line_info = zutil.splice_svn_changed(each_line)
                zutil.log_debug('copy file:', line_info)
                zutil.gracefully_copy(line_info, src_location, desc_location)
                zutil.log_debug('copy file: .......', 'success')
        # FIXME 如何过滤CI框架本身的代码
        return desc_location

    # 判断当前目录是否已经是一个svn copy
    def _working_copy_exists(self):
        proj_location = CONST_DIR_ROOT_RAW + self.proj_name
        if os.path.exists(proj_location):
            os.chdir(proj_location)
            return os.path.isdir(proj_location + "/.svn")
        else:
            return False

    # 直接 svn up
    def _working_copy_update(self):
        proj_location = CONST_DIR_ROOT_RAW + self.proj_name
        os.chdir(proj_location)
        cmd = ['svn', 'up', '--revision', self.revision_num]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        proc.wait()
        try:
            cmd_out = proc.stdout.read().splitlines()
            at_ver = cmd_out[-1]
            if 'At revision' in at_ver:
                zutil.log_info('svn copy', '成功更新')
            else:
                raise StandardError()
        except StandardError as e:
            print str(e)
            zutil.log_and_exit('debug::::' + 'svn-sonar.py 执行 _working_copy_update 异常')

    # 首次进行 svn checkout
    def _working_copy_checkout(self):
        proj_location = CONST_DIR_ROOT_RAW + self.proj_name
        zutil.jump_smoothly(proj_location)

        cmd = ['svn', 'checkout', '--username', CONST_AUTH_UNAME, '--password', CONST_AUTH_PWD, 'svn://127.0.0.1']
        print cmd
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        proc.wait()
        try:
            cmd_out = proc.stdout.read().splitlines()
            checked_ver = cmd_out[-1]
            if 'Checked out revision' in checked_ver:
                zutil.log_info('svn copy', '成功检出')
            else:
                raise StandardError()
        except StandardError as e:
            print str(e)
            zutil.log_and_exit('debug::::' + 'svn-sonar.py 执行 _working_copy_checkout 异常')

    # 生成sonar使用的sonar-project.properties
    def generate_proj_info(self, author):
        if not os.path.exists("sonar-project.properties"):
            f = open("sonar-project.properties", "a+")
            lines = []
            project_keys = []
            project_keys.append(self.proj_name)
            project_keys.append(self.revision_num)
            project_keys.append(author)
            str_project_keys = '.'.join(project_keys)
            str_project_name = '-'.join(project_keys)
            lines.append('sonar.projectKey=' + str_project_keys + '\n')
            lines.append('sonar.projectName=' + str_project_name + '\n')
            lines.append('sonar.projectVersion=' + self.revision_num + '\n')
            lines.append('sonar.sources=.\n')
            f.writelines(lines)

    # 调用本地 sonar-scanner并上传结果
    def scan_by_sonar(self):
        cmd = ['/data/sonar-scanner/bin/sonar-scanner']
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        proc.wait()
        try:
            cmd_out = proc.stdout.read().splitlines()
            for cmd in cmd_out:
                zutil.log_debug('sonar-report', cmd)
        except StandardError as e:
            print str(e)
            zutil.log_and_exit('debug::::' + 'svn-sonar.py 执行 scan_by_sonar 异常')


# 简单打印下日志
def log_info(repo_path, rev_num):
    now_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    data = [{'timestamp': now_time_str, 'repos': repo_path, 'rev_num': rev_num}]
    log_json = json.dumps(data)
    f = open('/svn_log/svn2sonarHook.log', 'a+')
    f.write(log_json)


# 主函数
def main():
    repo_path = sys.argv[1]
    rev_num = sys.argv[2]
    svn_path = sys.argv[3]
    proj_name = sys.argv[4]  # 项目名称,用于标识目录

    log_info(repo_path, rev_num)
    svn_handler = SvnHandler(repo_path, rev_num, svn_path, proj_name)
    author = svn_handler.list_author()
    changed_lines = svn_handler.list_files()
    zutil.log_debug('author is', author)
    for oneline in changed_lines:
        print('debug::::' + 'changed files : ' + oneline)
    print('step1 : 检测文件变动成功!')
    desc_location = svn_handler.filter_backup_files(changed_lines)
    print('step2 : 更新并备份成功!')
    os.chdir(desc_location)
    svn_handler.generate_proj_info(author)
    print('step3 : 生成sonar project配置成功!')
    svn_handler.scan_by_sonar()
    print('step4 : sonar检测成功!')


if __name__ == "__main__":
    main()
