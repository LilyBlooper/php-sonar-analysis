#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import shutil

'''\
@author : lilyblooper | blooper@163.com
@date :  2018-04-08 16:45:00
@description : 常用工具类

'''


# 校验一个目录,如果不存在,那么创建它
def check_or_create(proj_location):
    if not os.path.exists(proj_location):
        os.makedirs(proj_location)


# 直接进入某目录
def jump_smoothly(proj_location):
    check_or_create(proj_location)
    os.chdir(proj_location)


# 记录异常并退出
def log_and_exit(errmsg=None):
    if errmsg is None:
        stream = sys.stdout
    else:
        stream = sys.stderr
    stream.write("%s\n" % __doc__)
    stream.flush()
    if errmsg:
        stream.write("\nError: %s\n" % errmsg)
        stream.flush()
        sys.exit(2)
    sys.exit(0)


# 记录debug日志(自定义规则)
def log_debug(key, value):
    print ('debug::::' + key + 'is : ' + value)


# 记录info日志(自定义规则)
def log_info(key, value):
    print ('info::::' + key + 'is : ' + value)


# 截取有用的目录信息
def splice_svn_changed(log):
    log_str = log[4:len(log)]
    return log_str


# 找到对应的父目录
def get_parent_dir(file_to_copy):
    r_pos = file_to_copy.rindex('/')
    file_dir = file_to_copy[:r_pos + 1]
    return file_dir


# 获取文件名称
def get_file_name(file_to_copy):
    r_pos = file_to_copy.rindex('/')
    file_name = file_to_copy[r_pos + 1:]
    return file_name


# copy 文件到指定目录
def gracefully_copy(file_to_copy, src_root, dest_root):
    dest_dir = get_parent_dir(file_to_copy)
    dest_file = get_file_name(file_to_copy)
    dest_path = dest_root + '/' + dest_dir
    check_or_create(dest_path)
    shutil.copy2(src_root + '/' + file_to_copy, dest_path + '/' + dest_file)


# 主函数
def main():
    spliced = splice_svn_changed('A   service/application_zdm/libraries/zmop/request/ZhimaOpenLogFeedbackRequest.php')
    print spliced
    print get_parent_dir(spliced)
    print get_file_name(spliced)


if __name__ == "__main__":
    main()
