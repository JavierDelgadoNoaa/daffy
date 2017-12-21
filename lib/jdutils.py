import time

def zeropad(number, num_digits):
   ''' Pad <number> so that it is a string of length <num_digits> '''
   try:
     number = int(number)
   except:
     print '<number> must be an integer or convertible to an integer'
     sys.exit(1)
   if number > pow(10, num_digits): raise Exception
   currLen = len( str(number) )
   num_zeros = num_digits - currLen
   padding = ''
   for i in range(num_zeros): padding += '0'
   return padding + str(number)

def get_yyyy_mm_dd_hh_mm(rundate):
   # UPDATE : Changed from gmtime to localtime for portability on systems that use different TZs
   return time.strftime('%Y_%m_%d_%H_%M', time.localtime(rundate))

