import uuid,random,time,logging

class Params(object):
   def __init__(self,vehicle,q):
       self.vehicle = vehicle
       q.mode = vehicle.mode
       q.lost_heartbeat = False
       q.heading = vehicle.heading
       q.groundspeed = vehicle.groundspeed
       q.rangefinder = vehicle.rangefinder.distance
       q.lat = vehicle.location.global_relative_frame.lat
       q.lon = vehicle.location.global_relative_frame.lon
       q.alt = vehicle.location.global_relative_frame.alt
       q.home_location = self.get_home_position()
       self.ID = uuid.uuid4().int       
       self.add_listeners(vehicle,q)
  

   def get_home_position(self):
       #returns latitude and longitude of home positon
       print "getting home position"
       cmds = self.vehicle.commands
       cmds.download()
       cmds.wait_ready()
       home = self.vehicle.home_location
       return home
   

   

   def add_listeners(self,vehicle,q):
       @vehicle.on_attribute('mode')
       def decorated_mode_callback(self,attr_name,value):
           print "vehicle mode changed to %s" %value.name
           q.mode = value
            

       @vehicle.on_attribute('groundspeed')
       def decorated_velocity_callback(self,attr_name,value):
           if not q.groundspeed == round(value,2):
               q.groundspeed =round(value,2)
      
       @vehicle.on_attribute('rangefinder') 
       def decorated_rangefinder_callback(self,attr_name,value):
            if q.rangefinder == round(value.distance,4):
                 return
            q.rangefinder = round(value.distance,4)

       @vehicle.on_attribute('location.global_relative_frame')
       def decorated_global_relative_frame_callback(self,attr_name,value):
           if q.lat == round(value.lat,7) and q.lon ==round(value.lon,7) and q.alt ==round(value.alt,2):
               pass
              
           else:
               q.lat = round(value.lat,7)
               q.lon = round(value.lon,7)
               q.alt = round(value.alt,2)

       @vehicle.on_attribute('heading')
       def decorated_heading_callback(self,attr_name,value):
           if q.heading == value or q.heading == (value +1) or q.heading ==(value-1):
              pass
           else:
              q.heading = value
           
      
       @vehicle.on_attribute('last_heartbeat')
       def decorated_last_heartbeat(self,attr_name,value):
           if value > 5: #if no heartbeat recieved in 5 seconds
              q.lost_heartbeat = True
              logging.debug("lost communication with vehicle!!!")
           else:
              q.lost_heartbeat = False
              
               
              
class Vehicle_params(object):
   def __init__(self):
       self.mode = None
       self.lat = None
       self.lon = None
       self.alt = None
       self.lost_hearbeat = None
       self.groundspeed = 0.0
       self.heading = 0
       self.home_location = None
       self.rangefinder = 0.0




