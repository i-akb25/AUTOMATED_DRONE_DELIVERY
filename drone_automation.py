from dronekit import connect, VehicleMode, LocationGlobal, LocationGlobalRelative
from pymavlink import mavutil 
import time
import math
import socket
import argparse
import geopy.distance

import face_recognition
import picamera
import numpy as np

# Connect to the drone
def connectMyCopter():
    parser = argparse.ArgumentParser(description='commands')
    parser.add_argument('--connect')
    args = parser.parse_args()

    connection_string = args.connect
    baud_rate = 57600
    print("\nConnecting to vehicle on: %s" % connection_string)
    vehicle = connect(connection_string, baud=baud_rate, wait_ready=True)
    return vehicle

# Arm and take off to meters
def arm_and_takeoff(aTargetAltitude):
    """
    Arms vehicle and flies to aTargetAltitude.
    """
    print("Basic pre-arm checks")
    # Don't let the user try to arm until autopilot is ready
    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialise...")
        time.sleep(1)

    print("Arming motors")
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    while not vehicle.armed:      
        print(" Waiting for arming...")
        time.sleep(1)

    print("Taking off!")
    vehicle.simple_takeoff(aTargetAltitude)  # Take off to target altitude

    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)      
        if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:  # Trigger just below target alt.
            print("Reached target altitude")
            break
        time.sleep(1)

# Drop the parcel
def drop_parcel():
    msg = vehicle.message_factory.command_long_encode(
        0, 0,  # target_system, target_component
        mavutil.mavlink.MAV_CMD_DO_SET_SERVO,  # Command
        0,  # Confirmation
        9,  # Servo number
        1000,  # Servo position between 1000 and 2000
        0, 0, 0, 0, 0)  # Param 3 ~ 7 not used
    print("Dropping parcel...")
    vehicle.send_mavlink(msg)
    print("Parcel dropped.")

# Calculate distance
def get_distance(cord1, cord2):
    # Return distance in meters
    return (geopy.distance.geodesic(cord1, cord2).km) * 1000

# Get a reference to the Raspberry Pi camera
camera = picamera.PiCamera()
camera.resolution = (640, 480)
output = np.empty((480, 640, 3), dtype=np.uint8)

# Load a sample picture and learn how to recognize it
print("Loading known face image(s)")
anurag_image = face_recognition.load_image_file("faces/anurag.jpeg")
anurag_face_encoding = face_recognition.face_encodings(anurag_image)[0]

# Initialize some variables
face_locations = []
face_encodings = []

# Connect to the drone
vehicle = connectMyCopter()

# Go to a specific location
def goto_location(to_lat, to_long):    
    print(" Global Location (relative altitude): %s" % vehicle.location.global_relative_frame)
    curr_lat = vehicle.location.global_relative_frame.lat
    curr_lon = vehicle.location.global_relative_frame.lon
    curr_alt = vehicle.location.global_relative_frame.alt

    # Set to location (lat, lon, alt)
    to_pont = LocationGlobalRelative(to_lat, to_long, curr_alt)
    vehicle.simple_goto(to_pont, groundspeed=1)
    
    to_cord = (to_lat, to_long)
    while True:
        curr_lat = vehicle.location.global_relative_frame.lat
        curr_lon = vehicle.location.global_relative_frame.lon
        curr_cord = (curr_lat, curr_lon)
        print("Current location: {}".format(curr_cord))
        distance = get_distance(curr_cord, to_cord)
        print("Distance remaining: {}".format(distance))
        if distance <= 2:
            print("Reached within 2 meters of target location.")
            break
        time.sleep(1)

# Identify the person
def identify_person():
    found = False
    while True:
        print("\nCapturing image.")
        # Grab a single frame of video from the RPi camera as a numpy array
        camera.capture(output, format="rgb")
        
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(output)
        print("Found {} faces in image.".format(len(face_locations)))
        face_encodings = face_recognition.face_encodings(output, face_locations)

        # Loop over each face found in the frame to see if it's someone we know
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            match = face_recognition.compare_faces([anurag_face_encoding], face_encoding)
            name = "<Unknown Person>"

            if match[0]:
                name = "Anurag"
                found = True
                print("Found {}.".format(name))

            print("I see someone named {}!".format(name))
            
        if found:
            # Found customer
            break

# Execute the mission
def my_mission():
    arm_and_takeoff(2)
    goto_location(25.6198818, 85.1724020)
    identify_person()
    drop_parcel()
    time.sleep(2)
    print("Returning to Launch")
    vehicle.mode = VehicleMode("RTL")

# Invoke the mission    
my_mission()