import time

class TimeStruct:
   '''
   Class to encapsulate the time parameters year, month, day, hour, minute.
   Note that the state is individually held by these parameters, not by the 
   epochtime, although you can instantiate it using the epoch_time as an 
   optional parameter to the constructor
   '''
   def __init__(self, *args):
      self.year = ''
      self.month = ''
      self.day = ''
      self.hour = ''
      self.minute = ''
      self.seconds = '' 
      if len(args) > 0 :
         self._epoch_time = args[0]
         self.set_date_params_from_epoch_time()

   def set_date_params_from_epoch_time(self):
     self.year = time.strftime('%Y', time.localtime(self._epoch_time)) 
     self.month = time.strftime('%m', time.localtime(self._epoch_time)) 
     self.day = time.strftime('%d', time.localtime(self._epoch_time)) 
     self.hour = time.strftime('%H', time.localtime(self._epoch_time)) 
     self.minute = time.strftime('%M', time.localtime(self._epoch_time)) 

   def get_date_str(self):
      return '%s%s%s%s%s' %(self.year, self.month, self.day, self.hour, self.minute)

   def get_epochtime(self):
      elDay = '%s/%s/%s %s%s' %(self.month, self.day, self.year, self.hour, self.minute)
      return int( time.mktime( time.strptime(elDay, '%m/%d/%Y %H%M') ) )
   
   def get_yyyy_mm_dd_hh_mm(self):
      return get_yyyy_mm_dd_hh_mm(self.get_epochtime())

   def get_ymdhm(self):
      return self.get_date_str()

