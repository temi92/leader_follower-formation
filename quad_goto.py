#Set up option parsing to get connection string
from dronekit import connect, VehicleMode,LocationGlobal,LocationGlobalRelative
from position_vector import PositionVector
from vehicle_params import Params,Vehicle_params
from handler_functions import *
from broadcast import Senderthread
import argparse
import time 
import logging
import sys

logging.basicConfig(filename='quad100817.log',level=logging.DEBUG)

parser = argparse.ArgumentParser(description='Print out vehicle state information. Connects to SITL on local PC by default.')
parser.add_argument('--connect',
                   help="vehicle connection target string. If not specified, SITL automatically started and used.")
parser.add_argument('--baudrate',type=int,
                   help="Vehicle baudrate settings specify 57600 when connecting with 3dr telemetry radio.",default=115200)

args = parser.parse_args()

connection_string = args.connect
pos1 = PositionVector(10,0,5)
pos2 = PositionVector(10,-10,5)
dist_tol = 1.0 #used to determine if uav has reached allocated position


if not args.connect:
    print "vehicle path not specified"
    sys.exit(1) #abort cause of error..


# Connect to the Vehicle. 
#   Set `wait_ready=True` to ensure default attributes are populated before `connect()` return
print "\nConnecting to vehicle on: %s" % connection_string
vehicle = connect(connection_string, wait_ready=True,baud=args.baudrate)
v = Vehicle_params()
param = Params(vehicle,v)
#get home position ...
home_position = v.home_location

logging.info("home position is %s",home_position)

PositionVector.set_home_location(LocationGlobal(home_position.lat,home_position.lon,home_position.alt))

arm_and_takeoff(vehicle,5)

vehicle.simple_goto(pos1.get_location())
#set_yaw(vehicle,0) #set yaw

while True:
    pos = PositionVector.get_from_location(vehicle.location.global_frame)
    logging.debug("vehicle_pos in N-S direction from home is  %f" %pos.x) 
    logging.debug("vehicle_pos in W-E direction from home is  %f" %pos.y) 
    print "distance from vehicle to pos1 is %s" %PositionVector.get_distance_xy(PositionVector.get_from_location(vehicle.location.global_frame),pos1)
    logging.debug("distance from vehicle to pos1 is %s" %PositionVector.get_distance_xy(PositionVector.get_from_location(vehicle.location.global_frame),pos1))
    time.sleep(0.5)
    if PositionVector.get_distance_xy(PositionVector.get_from_location(vehicle.location.global_frame),pos1) <=dist_tol:
       print vehicle.location.global_relative_frame
       print ("reached........hurrrayyyyyyy")
       logging.debug("vehicle reached position1")
       break

#set_yaw(vehicle,45)
vehicle.simple_goto(pos2.get_location())
while True:
    pos = PositionVector.get_from_location(vehicle.location.global_frame)
    logging.debug("vehicle_pos in N-S direction from home is  %f" %pos.x)
    logging.debug("vehicle_pos in W-E direction from home is  %f" %pos.y)
    print "distance from vehicle to pos2 is %s" %PositionVector.get_distance_xy(PositionVector.get_from_location(vehicle.location.global_frame),pos2)
    logging.debug("distance from vehicle to pos2 is %s" %PositionVector.get_distance_xy(PositionVector.get_from_location(vehicle.location.global_frame),pos2))
    time.sleep(0.5)
    if PositionVector.get_distance_xy(PositionVector.get_from_location(vehicle.location.global_frame),pos2) <=dist_tol:
       print vehicle.location.global_relative_frame
       print ("reached........hurrrayyyyyyy")
       logging.debug("vehicle reached position2")
       break

print "vehicle returning back to launch..."
vehicle.mode = VehicleMode("RTL")

print "close vehicle object.."
vehicle.close()

logging.debug("mission finished...")                                                               
