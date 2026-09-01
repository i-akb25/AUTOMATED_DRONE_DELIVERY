---
schemaVersion: 1
status: published
slug: automated-drone-delivery
title: Automated Drone Delivery
summary: A quadcopter prototype combining Pixhawk flight control, Raspberry Pi mission orchestration, onboard facial recognition, servo-actuated parcel release, and return-to-launch behaviour.
categoryLabel: Autonomous Systems · Computer Vision · Embedded Control
tier: flagship
lifecycle: completed
disciplines:
  - robotics
  - automation
  - ai
period: Repository published December 2024
role: Hardware integration and software development
publishedAt: "2024-12-28"
updatedAt: "2024-12-28"
homepageOrder: 1
technologies:
  - name: Raspberry Pi 4
    category: hardware
  - name: Pixhawk
    category: hardware
  - name: Python
    category: language
  - name: DroneKit
    category: framework
  - name: MAVLink
    category: protocol
  - name: face_recognition
    category: framework
  - name: Dlib
    category: framework
  - name: Pi Camera
    category: hardware
  - name: GNSS
    category: hardware
  - name: SG90 Servo
    category: hardware
metrics:
  - value: 2 m
    label: Programmed takeoff altitude
    context: The mission waits until the aircraft reaches at least 95% of the requested altitude.
    evidence: Implemented in arm_and_takeoff inside drone_automation.py.
  - value: 1 m/s
    label: Commanded ground speed
    context: The guided navigation command requests this speed while travelling to the destination.
    evidence: Implemented through vehicle.simple_goto inside drone_automation.py.
  - value: ≤ 2 m
    label: Destination threshold
    context: Navigation completes when the calculated geodesic distance enters this boundary.
    evidence: Implemented in the destination-monitoring loop inside drone_automation.py.
  - value: 640 × 480
    label: Recognition frame resolution
    context: Pi Camera frames are captured at this resolution for face detection and comparison.
    evidence: Configured directly in drone_automation.py.
---

## Problem

The project investigated whether a small quadcopter could combine autonomous navigation, recipient recognition, physical parcel release, and return-to-launch behaviour in one mission sequence.

Navigation alone is insufficient for a delivery system. Reaching a coordinate does not establish that the intended recipient is present, and releasing a parcel without an explicit condition creates an obvious control and security problem.

The prototype therefore treats delivery as a sequence of dependent states:

1. Establish communication with the aircraft.
2. Confirm that the flight controller is ready.
3. Arm and take off.
4. Navigate to the configured destination.
5. Detect and compare an observed face with an enrolled identity.
6. Release the parcel only after a match.
7. Return to the launch location.

The repository demonstrates this integration path. It does not claim production readiness or commercially reliable delivery performance.

## Architecture

The system separates flight-critical control from higher-level mission logic.

| Layer | Component | Responsibility |
| --- | --- | --- |
| Flight control | Pixhawk | Vehicle state, arming, stabilisation, guided navigation, servo command execution, and RTL mode |
| Mission control | Raspberry Pi 4 | Mission sequencing, navigation monitoring, camera processing, recognition decisions, and MAVLink communication |
| Positioning | GNSS module | Position data used during guided navigation and return-to-launch |
| Perception | Raspberry Pi Camera | RGB frame capture for face detection and encoding |
| Recipient matching | face_recognition and Dlib | Face-location detection, encoding generation, and comparison with the enrolled identity |
| Delivery actuation | SG90 micro servo | Mechanical parcel-release actuation |
| Communication | DroneKit and MAVLink | Companion-computer communication with the flight controller |

The Pixhawk remains responsible for aircraft control. The Raspberry Pi does not directly control individual motors. It sends higher-level commands and observes vehicle state through DroneKit.

This boundary matters because image processing and Python mission logic are appropriate for a companion computer, while stabilisation and flight-state control belong on a dedicated flight controller.

### Mission flow

The Raspberry Pi connects to the Pixhawk through the configured serial interface at 57,600 baud.

The mission then:

1. Waits until the aircraft reports that it is armable.
2. Selects `GUIDED` mode and arms the vehicle.
3. Commands a two-metre takeoff.
4. Waits until relative altitude reaches at least 95% of the target.
5. Sends a global-relative destination with a one-metre-per-second ground-speed request.
6. Calculates the remaining geodesic distance once per second.
7. Continues when the remaining distance is no greater than two metres.
8. Captures camera frames and compares detected face encodings.
9. Sends a `MAV_CMD_DO_SET_SERVO` command after a match.
10. Switches the aircraft to `RTL` mode.

The destination coordinate is intentionally excluded from this document. Precise operational locations should not be reproduced in public presentation content.

## Engineering decisions

### Separate the flight controller and companion computer

**Decision:** Keep vehicle control on Pixhawk and run vision and mission orchestration on Raspberry Pi.

**Reasoning:** Flight stabilisation and navigation require a controller designed for aircraft operation. The Raspberry Pi provides the processing environment required by Python, camera capture, Dlib, and face encoding.

**Tradeoff:** The architecture introduces serial communication, configuration, power, startup-order, and failure-handling dependencies between two computers.

### Gate parcel release with recipient recognition

**Decision:** Issue the servo command only after an observed face matches the enrolled encoding.

**Reasoning:** This creates an explicit delivery condition beyond simply reaching a coordinate.

**Tradeoff:** Facial recognition alone is not strong recipient authentication. Lighting, pose, camera quality, false matches, presentation attacks, and biometric privacy all remain unresolved.

### Use a navigation tolerance

**Decision:** Treat the destination as reached inside a two-metre geodesic boundary.

**Reasoning:** A GNSS-guided aircraft should not wait for an exact floating-point coordinate match.

**Tradeoff:** A fixed radius does not respond to reported GNSS accuracy, obstacles, local geometry, or the physical release area.

### Delegate the return flight to RTL

**Decision:** Switch the Pixhawk to return-to-launch mode after the release command.

**Reasoning:** Returning through an established autopilot mode is safer and simpler than duplicating the homeward-navigation sequence in the companion script.

**Tradeoff:** Correct behaviour depends on a valid home position, GNSS state, RTL altitude, battery condition, and flight-controller configuration.

## Implementation

### Vehicle connection

The Python script accepts the vehicle connection string through a command-line argument. DroneKit establishes the connection and waits for the vehicle to report readiness.

The reviewed implementation uses a baud rate of 57,600 for the companion-computer connection.

### Arming and takeoff

The mission waits for `vehicle.is_armable`, changes the vehicle mode to `GUIDED`, and requests arming.

After arming, `simple_takeoff` requests a two-metre target altitude. Relative altitude is checked once per second until it reaches at least 95% of that target.

### Guided navigation

The destination is represented with `LocationGlobalRelative`. The current relative altitude is preserved when constructing the target position.

`simple_goto` sends the destination with a requested ground speed of one metre per second.

The companion computer reads the current latitude and longitude, calculates geodesic distance with Geopy, and exits the loop inside the two-metre threshold.

### Recipient recognition

The implementation loads one enrolled image and calculates its face encoding before starting the mission.

For each captured frame:

1. The camera returns a 640 × 480 RGB array.
2. Face locations are detected.
3. Encodings are produced for detected faces.
4. Each encoding is compared with the enrolled encoding.
5. The recognition loop exits after a match.

This is a single-recipient prototype. It has no multi-recipient identity store, confidence policy, liveness detection, expiry mechanism, or secondary authentication factor.

### Parcel release

The release function constructs a MAVLink long command using `MAV_CMD_DO_SET_SERVO`.

The reviewed script targets servo channel nine with a PWM value of 1,000. The command is transmitted through the Pixhawk message factory.

The implementation sends the release command but does not verify servo movement or parcel separation.

### Return to launch

After sending the release command, the mission waits two seconds and changes the vehicle mode to `RTL`.

Return execution is delegated to the flight controller.

## Validation and evidence

The repository contains a readable implementation of the complete mission sequence:

- Pixhawk connection
- Readiness and arming checks
- Guided takeoff
- Destination navigation
- Distance monitoring
- Camera-frame capture
- Face detection and comparison
- MAVLink servo actuation
- Return-to-launch selection

The README documents the intended hardware stack and operating sequence.

However, the repository does not contain:

- Automated tests
- Simulation results
- Telemetry logs
- Flight logs
- Recognition evaluation data
- Payload weight records
- Endurance measurements
- Failure-case results
- Servo-position confirmation
- Video evidence linked to a repeatable test procedure

For that reason, this case study does not publish the previously discussed 95% recognition accuracy, 15-minute flight time, or one-kilogram payload figure. Those values require preserved measurement evidence before they can be presented as verified results.

## Limitations

### Hard-coded mission configuration

The reviewed script embeds its destination in source code.

This makes reuse difficult and exposes precise location information in repository history.

A production implementation should load destinations through validated, access-controlled runtime configuration. It should also enforce geofencing, altitude constraints, and mission authorisation.

### Enrolled-image path mismatch

The code expects `faces/anurag.jpeg`, while the reviewed repository stores `anurag.jpeg` at its root.

A clean repository checkout can therefore fail before the mission starts.

The path should be explicit configuration validated during startup, with a smoke test covering required files.

### Unbounded waiting loops

Vehicle readiness, arming, takeoff, navigation, and recognition loops have no timeout.

Hardware failure, poor GNSS reception, communication loss, or an absent recipient could leave the mission waiting indefinitely.

Each state needs:

- A maximum duration
- A structured failure reason
- Telemetry
- A safe transition
- Tested RTL or landing behaviour

### Incomplete preflight validation

The script checks whether the aircraft is armable, but it does not explicitly enforce thresholds for:

- Battery condition
- GNSS quality
- Home-position validity
- Camera availability
- Servo readiness
- Communication health
- RTL configuration

These checks must pass before an autonomous mission can begin.

### Single-factor biometric decision

One face comparison controls the delivery decision.

This is insufficient for strong recipient authentication and creates biometric privacy obligations.

A stronger design would combine liveness detection with a short-lived delivery credential or recipient confirmation channel.

### No release confirmation

The mission assumes that sending the servo command means the parcel was released.

There is no actuator-position, payload-presence, or separation feedback.

Release should become a confirmed mission state rather than a command with no observed outcome.

### No published performance evidence

The repository proves that the mission logic was implemented. It does not prove reliability, accuracy, payload capability, endurance, or operational safety.

Those claims require controlled tests and preserved evidence.

## Lessons

The most important lesson was that autonomous behaviour is not one algorithm. It is a chain of dependent states spanning flight control, navigation, perception, decision-making, physical actuation, and failure recovery.

Separating Pixhawk flight control from Raspberry Pi mission intelligence made the system easier to reason about. It also exposed the need for a stricter communication and failure contract between the two computers.

The prototype demonstrated that recipient recognition can gate a physical action, but it also showed why recognition cannot be treated as complete authentication.

Every hardware waiting loop needs a timeout and a safe exit. A mission that works only when every component behaves correctly is not yet robust.

Finally, implementation evidence and performance evidence are different. Source code can prove that a behaviour was programmed. It cannot, by itself, prove accuracy, endurance, payload capacity, or operational reliability.
