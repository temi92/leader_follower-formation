from dronekit import connect

connection_string = "/dev/ttyS0"

vehicle = connect(connection_string, wait_ready=True,baud=57600)
#cmds = vehicle.commands
#cmds.download()
#cmds.wait_ready()
#home_position = vehicle.home_location
#print home_position

print vehicle.rangefinder.distance *100
