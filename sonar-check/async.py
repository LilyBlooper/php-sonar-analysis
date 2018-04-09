#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess


# 异步调用本地 sonar-scanner
def scan_by_sonar_async(self, dest_location):
    subprocess.Popen(['nohup', '/data/sonar-scanner/bin/sonar-scanner'],
                     stdout=open('/dev/null', 'w'),
                     stderr=open('logfile.log', 'a')
                     )
