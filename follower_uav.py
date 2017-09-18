from dronekit import connect,VehicleMode,LocationGlobalRelative,LocationGlobal
from position_vector import PositionVector
from vehicle_params import Params,Vehicle_params
from broadcast import ReceiverThread,Task_handler
from handler_functions import *
from haversine import haversine
import Queue,threading,time,logging
import argparse
queue = Queue.Queue()

class Task_handler(threading.Thread):
   def __init__(self,q,recv_thread,vehicle,distance):
       threading.Thread.__init__(self)
       self.daemon = True
       self.vehicle = vehicle
       self.msg_queue = q
       self.recv_thread = recv_thread
       self.count = 0
       self.distance = distance
       self.called = False

   def haversine_distance(self,master_position,slave_position):
       distance = haversine(master_position,slave_position) *1000
       logging.debug("distance between 2 vehicles based on haversine is %.3f" %distance)

   def run(self):
       
       while True:
           if self.vehicle.mode.name !="GUIDED": #if we are no longer in guided mode stop receving messages
              logging.info("follower vehicle aborted GUIDED mode")
              self.recv_thread.stop()
              break
           try:
              (message,address) = self.msg_queue.get()
              self.haversine_distance((message.lat,message.lon),(self.vehicle.location.global_relative_frame.lat,self.vehicle.location.global_relative_frame.lon))
              if not self.called:
                  #set home location to home location of master vehicle
                  
                  PositionVector.set_home_location(LocationGlobal(message.home_location.lat,message.home_location.lon,message.home_location.alt))
                  logging.debug("master home location is...")
                  logging.debug(message.home_location)
                  self.called = True
              logging.debug("message received %s %s %s" %(message.lat, message.lon,message.alt))
               
              #altitude = 5 #in metres
              separation = self.distance #distance between drones
             
              original_pos = PositionVector.get_from_location(message)
              logging.debug("position for leader vehicle -> %s heading -> %s" %(original_pos,message.heading))
              logging.debug("leader vehicle groundspeed is %.3f" %message.groundspeed)
              logging.debug("leader vehicle lidar altitude is %.4f m"%message.rangefinder)
              new_pos = selection_coding(original_pos,message.heading,separation)
              
              new_pos = PositionVector(new_pos[0],new_pos[1],new_pos[2])
              logging.debug("position for follower vehicle is %s" %(new_pos))
              
              
              lat = new_pos.get_location().lat
              lon = new_pos.get_location().lon
              alt = new_pos.get_location().alt - message.home_location.alt
              dest = LocationGlobalRelative(lat,lon,alt)
              logging.debug("gps locationglobal data for follower vehicle to procced to is %s" %new_pos.get_location())
              logging.debug("gps locationglobalrelative data for follower vehicle to procced to is %s" %dest)

              self.vehicle.simple_goto(dest)
              set_yaw(self.vehicle,message.heading)
              logging.debug("vehicle groundspeed is %.3f" %self.vehicle.groundspeed)
              logging.debug("vehicle heading is %.3f" %self.vehicle.heading)
              logging.debug("vehicle lidar altitude is %.4f m "%self.vehicle.rangefinder.distance)
              actualpath = PositionVector.get_from_location(self.vehicle.location.global_frame)
              logging.debug("vehicle actual path in X direction is %.5f m" %actualpath.x)
              logging.debug("vehicle actual path in Y direction is %.5f m" %actualpath.y)

              time.sleep(0.1)
             
              logging.debug("**************")
              self.count+=1
              self.msg_queue.task_done()
           except Queue.Empty:
              print ("all messages processed")

def main():

   parser = argparse.ArgumentParser(description="follower formation flight..")
   parser.add_argument("follower_address",help="vehicle address of the follower UAV")
   parser.add_argument("log_file",help="log file to log vehicle information")
   parser.add_argument("distance",help = "distance between follower and leader",type=int)
   args = parser.parse_args()
   
   logging.basicConfig(filename=args.log_file,level=logging.DEBUG,format='(%(threadName)-6s) %(relativeCreated)d  %(message)s',)

   #connection_string = 'tcp:127.0.0.1:5762'
   connection_string = args.follower_address
   distance = args.distance

   #vehicle1 = connect(connection_string,wait_ready=True,baud=115200)
   vehicle1 = connect(connection_string,wait_ready=True,baud=57600)
   v = Vehicle_params()
   param = Params(vehicle1,v)
   #get home_location
   home_position = v.home_location
   #home_position.alt = 0 #set altitude of home_location to zero .
   logging.debug("follower home_position is %s" %home_position)
 
   arm_and_takeoff(vehicle1,5) #sets vehicle to GUDIED mode

   #wait for vehicle to finish taken off before spawning thread..
   logging.debug("vehicle taken off to 5 metres")

   address = ("192.168.137.83",8001)
   t = ReceiverThread(address,queue)
   task_handler = Task_handler(queue,t,vehicle1,distance)
   t.start()
   task_handler.start()

   t.join() #waits for thread spawned to finish before joining main thread
   logging.debug("all done")
   
main()
