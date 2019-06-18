#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
  222
"""
from __future__ import print_function
import sys
import os
import optparse
import time
import shutil
import docker
import belonesox_tools.MiscUtils as ut   
import platform

#import MiscUtils as ut

import socket
from contextlib import closing

def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

class DocstructBuilder(object):
    """
    Main class for all commands
    """
    version__ = "01.01"

    def __init__(self):
        """Set up and parse command line options"""
        usage = "Usage: %prog [options] <source directory>"
        #
        #self.parser = optparse.OptionParser(usage)
        #
        #self.parser.add_option('-d', '--directory',
        #                       dest='build_directory',
        #                       action='store_true',
        #                       default=False,
        #                       metavar="",
        #                       help="Build Time Directory for files")
        #
        #
        #self.options, self.args = self.parser.parse_args()
        self.homedir = os.getcwd()

        self.uid = 0 #os.getuid()
        self.gid = 0 #os.getgid()

        if platform.system() != 'Windows':
            self.uid = os.getuid()
            self.gid = os.getgid()
        # print("self.uid=",  self.uid)

        self.port = find_free_port()
        self.target = '/home/stas/projects/lectures-cs/algorithms/simple/intro-and-samples.beam.pdf'
        if len(sys.argv) > 1:
            self.target = sys.argv[1]
        self.target = os.path.realpath(self.target)
        parts = self.target.split(os.path.sep)
        self.target = self.target.replace('\\', '/')
        
        self.basedir = None 
        for k in range(1, len(parts)):
            path_to_test = os.path.sep.join(parts[:-k])
            if os.path.exists(os.path.join(path_to_test, 'SConstruct')):
                self.basedir = path_to_test
                break
                
        self.basedir = self.basedir.replace('\\', '/')
        self.target_filename = ut.relpath(self.basedir, self.target)
        print(self.target_filename)
        self.basedir = self.basedir.replace('C:/', '/c/')        
        self.mount_point = self.basedir #.replace('/c/', '/')
        self.container_name = 'docstruct-build-' + ut.hash4string(self.basedir)
        pass

    def process(self):
        """
        Main entry point.
        Process command line options, call appropriate logic.
        """
        client = docker.from_env()
        need_creation = True
        try:
            container = client.containers.get(self.container_name)
            if container.status != 'exited':
                need_creation = False
            else:
                container.remove()
            pass
        except docker.errors.APIError as ex_:
            pass

        print("***", self.mount_point, "---")
        if need_creation:
            #exec docker run -d --rm --name latex_daemon -i --user="$(id -u):$(id -g)" --net=none -t -v $PWD:/data "$IMAGE" /bin/sh -c "sleep infinity"
            port_mapping = {'22/tcp': self.port}
            volume_mapping = {self.basedir: {'bind': self.mount_point, 'mode': 'rw'}}
            print(volume_mapping)
            container = client.containers.run('belonesox/docstruct-centos',
                                              'sleep infinity',
                                              name=self.container_name,
                                              remove=True,
                                              ports=port_mapping,
                                              volumes=volume_mapping,
                                              user=self.uid, #!!! для винды.
                                              entrypoint=None,
                                              detach=True
                                              )
            pass
        # scmd = 'scons -D "%s"' % self.target
        scmd = 'bash -c "pwd; cd %s; scons -D %s "' % (self.mount_point, self.target_filename)
        # scmd = 'bash -c "pwd; cd %s; ls -la . "' % (self.mount_point, )
        (res, output) = container.exec_run(scmd,
                           stdout=True,
                           stderr=True,
                           stdin=False,
                           tty=False,
                           privileged=False,
                           user=str(self.uid),
                           detach=False,
                           stream=False,
                           environment=None,
                           workdir=self.mount_point
                           )

        out = str(output).replace('\\n', '\n')
        out = out.replace('--->!!--->', '')
        print(out)
        pass


def main():
    """
     Start procedure
    """
    processor = DocstructBuilder()
    processor.process()

if __name__ == '__main__':
    main()
