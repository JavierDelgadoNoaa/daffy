import shutil
from time import sleep
import os
import sys
import random 
import xml.etree.ElementTree as ET
from optparse import OptionParser
import subprocess
import time
import xml.dom.minidom
from daffy_log import DaffyLog
import uuid

EXPERIMENT_ID = '234'

class Config:
  def __init__(self):
    self.global_experiment_database = '/home/javi/global.xml'

def commit_to_global_database(local_xml_file):
  localRoot = ET.parse(local_xml_file).getroot()
  
  for exptNode in ET.parse(cfg.global_experiment_database).findall(".//experiment"):
    if 'uuid' in exptNode.attrib:
      if exptNode.attrib['uuid'] == EXPERIMENT_ID:
	print 'Experiment ID already exists in database!'
	sys.exit(13)
    else:
      print 'WARN :: ID field not found for an entry in the global database'
      
  globalRoot = ET.parse(cfg.global_experiment_database).getroot()
  
  globalRoot.append(localRoot)
  
  out = ET.tostring(globalRoot)
  xmlOut = xml.dom.minidom.parseString(out)
  xmlText = xmlOut.toprettyxml()
  
  #with open('output.xml', 'w') as xmlFile:
  with open(cfg.global_experiment_database, 'w') as xmlFile:
    out = ET.tostring(globalRoot)
    xmlOut = xml.dom.minidom.parseString(out)
    xmlText = xmlOut.toprettyxml()
    for line in xmlText.splitlines():
	if not line.isspace():  xmlFile.write(line + '\n')

cfg = Config()
commit_to_global_database('/home/javi/local.xml')
  #with globalDatabase = open(cfg.global_experiment_database, 'r'):
  