from dronekit import VehicleMode
from math import radians,cos,sin,asin,sqrt,pi,tan
from pymavlink import mavutil
from position_vector import PositionVector
import time

def selection_coding(vehicle_pos,heading,s):
   #heading = 90 - heading
   if heading ==0:
      heading = 1
      heading = 90 -heading
   
   elif heading ==180:
     heading = 181
     heading = 360+(90-heading)
   
   elif heading ==270:
     heading = 269
     heading = 360+(90-heading)

   elif heading <= 90:
      heading = 90 - heading
   elif heading >90:
      heading = 360+(90-heading) 
   
   """
   if heading == 90:
      heading = 89
   elif heading==270:
      heading = 269
   elif heading ==180:
      heading = 179
   """
   beta = 1 + tan(heading*pi/180)**2
   a = beta
   b = -2 * vehicle_pos.y *beta #vehicle_pos.y is longitude
   c = vehicle_pos.y**2*beta-s**2
   
   if heading <90 or heading > 270:
          #print "heading is %s " %heading
          x2 = (-b+sqrt(b**2-4*a*c))/(2*a)

   elif heading > 90 or heading <180:
          #print "heading is %s" %heading

          x2 = (-b-sqrt(b**2-4*a*c))/(2*a)
               

   y2 = (x2-vehicle_pos.y)*tan(heading*pi/180)+vehicle_pos.x
   z2 = vehicle_pos.z
   return y2,x2,z2 #latitude,longitude,alt


def set_yaw(vehicle,heading, relative=False):
    if relative:
        is_relative=1 #yaw relative to direction of travel
    else:
        is_relative=0 #yaw is an absolute angle
    # create the CONDITION_YAW command using command_long_encode()
    msg = vehicle.message_factory.command_long_encode(
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_CMD_CONDITION_YAW, #command
        0, #confirmation
        heading,    # param 1, yaw in degrees
        0,          # param 2, yaw speed deg/s
        1,          # param 3, direction -1 ccw, 1 cw
        is_relative, # param 4, relative offset 1, absolute angle 0
        0, 0, 0)    # param 5 ~ 7 not used
    # send command to vehicle
    vehicle.send_mavlink(msg)

# sleep so we can see the change in map
def print_all(vehicle,duration=30):
    start = time.time()

    while time.time() - start < duration:
               print("(%s) Lat=%f Lon=%f alt=%f Heading=%f" % (vehicle.mode, vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon,vehicle.location.global_relative_frame.alt,vehicle.heading))
               #print (PositionVector.get_from_location(vehicle.location.global_frame).x)
               #print (PositionVector.get_from_location(vehicle.location.global_frame).y)
               #print (PositionVector.get_from_location(vehicle.location.global_frame).z)
               #print (PositionVector.get_distance_xy(PositionVector.get_from_location(vehicle.location.global_frame),pos1))
               time.sleep(1)

def arm_and_takeoff(vehicle,aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    """

    print "Basic pre-arm checks"
    # Don't try to arm until autopilot is ready
    while not vehicle.is_armable:
     print " Waiting for vehicle to initialise..."
     time.sleep(1)


    print "Arming motors"
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    # Confirm vehicle armed before attempting to take off
    while not vehicle.armed:
        print " Waiting for arming..."
        time.sleep(1)

    print "Taking off!"
    vehicle.simple_takeoff(aTargetAltitude) # Take off to target altitude

    # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command 
    #  after Vehicle.simple_takeoff will execute immediately).
    while True:
        print " Altitude: ", vehicle.location.global_relative_frame.alt
        #Break and return from function just below target altitude.        
        if vehicle.location.global_relative_frame.alt>=aTargetAltitude*0.95:
            print "Reached target altitude"
            break
        time.sleep(1)

if __name__=="__main__":
  
   pos1 = PositionVector(-5,-8,10)
   pos_test = selection_coding(pos1,270,10) #last argument is distance
   pos2 = PositionVector(pos_test[0],pos_test[1],10)
   #print "y-axis is %f" %pos2.x #y-axis
   #print "x-axis is %f" %pos2.y #x axis
   print "y-axis"
   print pos2.x
   print "x-axis"
   print pos2.y

   print "********"
   print PositionVector.get_distance_xy(pos1,pos2)
   
