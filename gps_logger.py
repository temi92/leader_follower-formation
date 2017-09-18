"""
This script logs GPS data for a certain amount of time in a csv file
"""

from dronekit import connect,Vehicle
import time
import argparse 
import csv


seconds = 300.0 # Number of seconds to log gps data
filename = "follower_gpsposition10_08_17_3m.csv"
flag =  True

def csv_writer(path,fieldnames,data):
   'allows writing of csv data to a file'
   global flag
   with open(path,"a") as csvfile:
       writer = csv.DictWriter(csvfile,fieldnames=fieldnames)
       if flag:
           writer.writeheader()
       for row in data:
           writer.writerow(row)
       flag = False

def timer(seconds):
   'timer function to allow gps data to be logged in for certain amount of seconds'
   start_time = time.time()
   while time.time() < start_time + seconds:
       pass
   return True
   
class GpsStatus(object):
   def __init__(self,time_usec=None,fix_type=None,lat=None,lon=None,alt=None,eph=None,epv=None,satellites_visible=None):
       self.time_usec = time_usec
       self.fix_type = fix_type
       self.lat = lat
       self.lon = lon
       self.alt = alt
       self.eph = eph
       self.epv = epv
       self.satellites_visible = satellites_visible
   
   def __str__(self):
        return "GPSInfo:time_usec=%s,fix_type=%s,eph=%s,satellites_visible=%s" % (self.time_usec, self.fix_type,self.eph,self.satellites_visible)

class MyVehicle(Vehicle):
   def __init__(self, *args):
       super(MyVehicle,self).__init__(*args)
       self._gps_status = GpsStatus()
       @self.on_message('GPS_RAW_INT')
       def listener(self,name,message):
           self._gps_status.time_usec = message.time_usec
           self._gps_status.fix_type = message.fix_type
           self._gps_status.lat = message.lat / 1.0e7
           self._gps_status.lon = message.lon / 1.0e7
           self._gps_status.alt = message.alt / 1000
           self._gps_status.eph = message.eph
           self._gps_status.epv = message.epv
           self._gps_status.satellites_visible = message.satellites_visible

           #notfiy observers of new messsage 
           self.notify_attribute_listeners('gps_info',self._gps_status)
   
   @property
   def gps_info(self):
       return self._gps_status

if __name__ == "__main__":
   parser = argparse.ArgumentParser(description='dumping gps data for analysis. ')
   parser.add_argument('--connect', 
                   help="Vehicle connection target string. If not specified, SITL automatically started and used.")
   args = parser.parse_args()
   connection_string = args.connect
   # Connect to the Vehicle
   print 'Connecting to vehicle on: %s' % connection_string
   vehicle = connect(connection_string, wait_ready=True,baud=57600,vehicle_class=MyVehicle)
   gps_data=[]
   fieldnames=["time_usec","fix_type","eph","epv","lat","lon","satellites_visible"]
   def gps_callback(self,attr_name,value):
       #attr_name = gps_info
       #value is an object of type GpsStatus
       data=[{"time_usec":value.time_usec,"fix_type":value.fix_type,"eph":value.eph,"epv":value.epv,"lat":value.lat,"lon":value.lon,"satellites_visible":value.satellites_visible}]
       csv_writer(filename,fieldnames,data) 
                                 
   vehicle.add_attribute_listener('gps_info',gps_callback)
   print "logging gps data for %s seconds and exit" %(seconds)
   try:
       timer(seconds)
   except KeyboardInterrupt:
       print "interrupted gps logging"
   finally:
       print "close vehicle object"
       vehicle.close()
     




