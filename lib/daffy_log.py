#!/usr/bin/env python
##
# Basic logger for the DAFFY framework
# In addition to the standard debug, info, warn, error, methods, there are the
# warn_once and info_once methods, which only report messages if they have not 
# already been reported.
##

import sys

class DaffyLog:
   
   # Static Variables # 
   
   # Level name <-> severity mappings 
   DEBUG = 2
   INFO = 4
   WARN = 6
   ERROR = 7
   # Prefixes for messages
   DEBUG_PREFIX = '(DBG)  '
   INFO_PREFIX = '(INFO) '
   WARN_PREFIX = '*WARN* '
   ERROR_PREFIX = '***ERROR***  '

   def __init__(self, level):
      ''' Initialize logger. The <level> argument should be numerical or one of 'INFO', 'DEBUG', 'WARN', 'ERROR' '''
      self.set_level(level)
      # list of messages that have already been reported
      self.reported_messages = []

   def set_level(self, level):
      ''' The <level> argument should be numerical or one of 'INFO', 'DEBUG', 'WARN', 'ERROR' '''
      self.level = level
      if level == 'INFO': self.level = self.INFO
      elif level == 'DEBUG' : self.level = self.DEBUG
      elif level == 'WARN' : self.level = self.WARN
      elif level == 'ERROR' : self.level = self.ERROR
      else:
         try: 
            int(level)
         except:
            sys.stderr.write("level argument to DaffyLog() should be an integer or one of 'INFO', 'DEBUG', 'WARN', 'ERROR'")
            raise Error("level argument to DaffyLog() should be an integer or one of 'INFO', 'DEBUG', 'WARN', 'ERROR'")
         self.level = level

   def debug(self, msg):
      if self.level <= self.DEBUG:
         sys.stdout.write('%s %s\n' %(self.DEBUG_PREFIX, msg) )

   def info(self, msg):
      if self.level <= self.INFO:
         sys.stdout.write('%s %s\n' %(self.INFO_PREFIX, msg) )

   def warn(self, msg):
      if self.level <= self.WARN:
         sys.stdout.write('%s %s\n' %(self.WARN_PREFIX, msg) )

   def error(self, msg):
      if self.level <= self.ERROR:
         sys.stdout.write('%s %s\n' %(self.ERROR_PREFIX, msg) )

   def warn_once(self, msg):
      ''' See comments in the beginning for info about the *_once methods '''
      if self.level <= self.WARN:
         if not msg in self.reported_messages :
            self.warn(msg)
            self.reported_messages.append(msg)

   def info_once(self, msg):
      ''' See comments in the beginning for info about the *_once methods '''
      if self.level <= self.INFO:
         if not msg in self.reported_messages:
            self.info(msg)
            self.reported_messages.append(msg)
