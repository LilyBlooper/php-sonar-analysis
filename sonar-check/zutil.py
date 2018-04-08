#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import os

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

