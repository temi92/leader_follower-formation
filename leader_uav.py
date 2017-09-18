from dronekit import connect,VehicleMode,LocationGlobalRelative,LocationGlobal
from broadcast import Senderthread
from vehicle_params import Params,Vehicle_params
import time,logging
from handler_functions import *

logging.basicConfig(filename='leader100817_7m_square.log',level=logging.DEBUG,format='(%(threadName)-6s) %(relativeCreated)d %(message)s',)
#connection_string = 'tcp:127.0.0.1:5762'
connection_string = '/dev/ttyS0'
address = ("192.168.137.83",8001)

#vehicle1 = connect(connection_string,wait_ready=True,baud=115200)
vehicle1 = connect(connection_string,wait_ready=True,baud=57600)

v = Vehicle_params()
param = Params(vehicle1,v)

#get home_location...
home_position = v.home_location
print home_position
PositionVector.set_home_location(LocationGlobal(home_position.lat,home_position.lon,home_position.alt))

thread1 = Senderthread(address,v)
thread1.start()#start sending information to the reciever(server)

while True:
   if not vehicle1.mode.name == 'LOITER':
       logging.debug("not in loiter mode....")
       print vehicle1.mode
       thread1.stop()   
       break
   else:
       pos = PositionVector.get_from_location(vehicle1.location.global_relative_frame)
       logging.debug("position is %s" % pos)
       logging.debug("Lat=%f Lon=%f alt=%f heading =%f" %(vehicle1.location.global_relative_frame.lat,vehicle1.location.global_relative_frame.lon,vehicle1.location.global_relative_frame.alt,vehicle1.heading))
       print "vehicle airspeed is %.3f" %vehicle1.airspeed
       logging.debug("vehicle airspeed is %.3f" %vehicle1.airspeed)
       print "vehicle groundspeed is %.3f" %vehicle1.groundspeed
       logging.debug("vehicle groundspeed is %.3f" %vehicle1.groundspeed)
       print "vehicle lidar altitude is %.4f m" %vehicle1.rangefinder.distance
       logging.debug("vehicle lidar altitude is %.4f m" %vehicle1.rangefinder.distance)
       time.sleep(0.1)
   

logging.debug("end of mission.")

