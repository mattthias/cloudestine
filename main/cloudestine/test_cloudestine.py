#!/usr/bin/env python 

import unittest2
from cloudestine import Cloudestine
from signal import SIGKILL
from time import sleep
import logging

log=logging.getLogger(__name__)


'''
Created on 05.02.2013

@author: thomas
'''
import os
import shutil



class CloudestineTest(unittest2.TestCase):
    def unmount(self):
        os.system("fusermount -u %s" % self.fuse_dir)

    def __init__(self,test_name):
        super(CloudestineTest, self).__init__(test_name)
        self.basedir='/tmp/cloudestine'
        self.fuse_dir=self.basedir+'/mount'
        self.storage_dir=self.basedir+'/base_name' 
              
    def tearDown(self):
        if self.is_mounted() >0:
            self.unmount()
            if self.child >0 :
                os.kill(self.child, SIGKILL )
        if os.path.isdir(self.basedir):
            shutil.rmtree(self.basedir) 
        pass
    
    def setUp(self):
        self.child=-1
        os.makedirs(self.fuse_dir)
        pass
    
    def is_mounted(self):
        found=False
        
        proc_mount=file('/proc/mounts','r')
        for line in proc_mount.readlines():
            
            array=line.split(' ')

            if len(array)<3:
                continue 
            (fs, mount_point, fuse)=array[0:3]
            if fs != 'Cloudestine':
                continue
            working_directory = self.fuse_dir
            
            if mount_point != working_directory:
                continue
            
            if fuse != 'fuse':
                continue
           
            if mount_point != self.fuse_dir :
                continue
          
            log.debug("line=%s" % line)
            log.debug("array=%s" % array.__str__())

            found = True
            break
        
        proc_mount.close()
        
        return found
    
    def test_Cloudestine_file_system_start_and_stop(self):
        Cloudestine(True, 
                    mount   = self.fuse_dir,
                    base_name =self.storage_dir)
        
        self.assertFalse(self.is_mounted(), "should not run" )
   
        self.child=os.fork()
        
        if self.child == 0 :
            Cloudestine.main([self.fuse_dir, self.storage_dir])
            return
            
        sleep(2)
        self.assertTrue(self.is_mounted(), "should run" )
        
        self.unmount()       
        sleep(2)
        
        self.assertFalse(self.is_mounted(), "should not run" )
     
    def test_Cloudestine_write_read_file(self):
        cloudestine = Cloudestine(True,
                                  mount = self.fuse_dir,
                                  base_name = self.storage_dir) 

        fh=cloudestine.open("file", 0x644)
        log.debug(fh)
        
        
if __name__ == "__main__":
    unittest2.main()