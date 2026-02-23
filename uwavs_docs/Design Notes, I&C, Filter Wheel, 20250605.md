# I&C Design Notes BEOC Filter Wheel

# Questions / Comments / TODOs

1. I found two COTS laser sensors (mfg: IFM, sensor: OMH550) and (mfg: Sick, sensor: OD2-P50W1012) with a visible light ~0.5 mm dot, that senses features as small as ~0.5-0.75 mm objects from a distance of between 30 mm - 80 mm, and 40 mm - 60 mm respectively and a resolution of 0.01 mm. This could point radially towards the center of the filter wheel, and count the hills and valleys of the teeth of the external gear as they go by. It would need to be positioned at least 30 mm/40 mm from the features to be sensed.

Colby prefers the IFM OMH550 sensor because it has a shorter minimum sensing distance (30mm) and that makes it easier to integrate.

In discussing the application with Colby, he raised concerns/questions about orientation (sensor housing parallel or perpendicular to FW for example or some other orientation needed), cross-talk of adjacent sensors, and beam 'walking' across the detector as the FW rotates and the beam incidence angle changes due to the sloped sides of the teeth for example.

Colby and Jeff had a discussion with an application specialist at IFM, Nuno Martins on 6/3/2025 (info.us@ifm.com 800-441-8246). He confirmed the sensor seems appropriate for the application. The concerns Colby raised seem like they should not be a problem. In the end, we all three agreed the sensor seemed like a good fit, and *should* work, but testing would be prudent.

The OMH550 sensor has a switching frequency of 200 Hz so this is the fastest the teeth can go by and have the sensor switch from low-high-low for example. At 280 teeth per revolution, the maximum speed possible without mis-counting = 200 pulses/second * 1 rev/280 pulses = 200/280 = ~.7 rev/sec. With a filter wheel position every 60 degrees or 0.16 revolutions, the time it takes to rotate to the next position at max speed would be 0.16 rev / 0.7 rev/sec = ~0.23 seconds. Rounding this to 0.25 seconds.

I would propose we run at about half the max speed for reliability if that is acceptable. ~0.35 rev /sec with a filter to filter movement time of ~0.5 seconds.

1. I would propose we stick with the proposed rad hardened stepper motors unless there is a compelling reason to change, even if the requirement for rad hardness is relaxed due to shielding.

1. ? When in some sort of maintenance/calibration/engineering operation (i.e. not shot operation) that allows easy assessment of if/when a filter is in the correct position? I.e., the filter wheel did not under/over rotate?

? How do we calibrate / position a filter position for homing for example? Should there be a mechanical index mark showing when Filter 1 is in the optimal ("center") position?

In some sort of "calibration" operations which is an off-normal operation, can the diagnostic see when the aperture is eclipsing the "field of view". If so, there would be a procedure to drive to one side, note this effect. Drive to the other side, note this effect, and then go to a middle position, and call this the "Filter Position".

1. The Design Description R00028 talks about "Alternate Filters". This brings up a point about how the system is told about what filters are what. A lookup table is talked about for looking up filter positions based on plant needs, but how is the information entered that is used to build the lookup table, for example. Are the possible types of filters (choices) known in advance -- i.e 10 filter types possible, and 6 are chosen to be fitted.

1. **TODO**: Flow chart for homing procedure
1. **TODO**: Network diagram and/or architecture diagram

1. ? CODAC: How do we specify what info we get from CODAC. I attempted this below, but may need attention, or to fall into some standard.
? Can we send stuff back to CODAC, like confirmaiton of what diagnostic measurement the filter wheels are positioned to measure?

# Introduction

## Purpose

This document outlines the Instrumentation and Controls ("I&C") design of the Filter Wheel subsystem of the Back End Optics and Cameras ("BEOC"). The objective of the document is to define the system architecture, the main components related to I&C, the associated alarms and faults, the supervising Control Data Access and Communication ("CODAC") signal interface, and present important software functionality.

## Filter Wheel Subsystem Overview

A subsystem of the UWAVS 55.GA ("UWAVS System") is the BEOC. The BEOC subsystem is located in the Port Cell, and encloses beam splitting, shaping, and correcting optics for camera imaging. There are two visible and two infrared cameras and optical paths. As part of each visible optical path, there are actuated filter wheel assemblies mounted, two assemblies in total. The filter wheel assembly contains the necessary filters to isolate 10 frequency bands for the observation of specific elements, as well as a set of neutral density filters.

Each filter wheel assembly contains a stack of three 280 mm external gear tooth filter wheels, 6 filter wheels in total. Each filter wheel has six positions (denoted *"Filter Position 1-6"*) for 85 mm diameter wavelength or neutral density filters.

The I&C system for the filter wheels ("the filter wheel control system") comprises the hardware and software necessary to control and monitor the position of each filter wheel, and allow the system operators and CODAC the necessary interface, control, and feedback necessary to operate and monitor the filter wheel system. The hardware and software that comprises the I&C system for the filter wheels is a subsystem of the UWAVS Slow Controller I&C system. The 55.GA Slow Controller Programmable Logic Controller ("the PLC") in the Diagnostic Hall has the ownership of the filter wheel control system hardware and software. The interface between the PLC and the filter wheel components is via a remote input/output ("remote I/O") rack in the BEOC.

The primary components of the filter wheel control system are:
* The Slow Controller PLC in the Diagnostic Hall
* A stepper motor for each filter wheel
* A position sensor for each filter wheel
* A remote I/O rack in the BEOC
* A stepper motor control module for each filter wheel (in the remote I/O rack)
* A signal counting module for each position sensor (in the remote I/O rack)
* A power supply, cabling, connectors, terminal blocks and other support hardware

## Special Design Considerations

Being in the Port Cell, the BEOC is in an area that is exposed to neutron, gamma, and electromagnetic radiation. The BEOC is surrounded with protective shielding layers to absorb this radiation. The position sensor is mounted near the filter wheel, and the BEOC shielding must be sufficient to protect these sensors. (**TODO:** Review this last sentence -- how or does the need to be quantified, is there more or less to say here?) In addition, enclosures with additional shielding will be used to house the remote I/O rack and other components that contain electronics (**TODO:** Is this correct? Is there an additional enclosure and shielding for electronics?). 

The shielding of the BEOC gives rise to the use of non-radiation hardened commercial-off-the-shelf ("COTS") components. The use of COTS components and minimizing the need to qualify non-qualified components to operate in a radiation exposed environments leads to an improved design, and greatly reduces the cost and shortens the schedule.

The distance between the PLC in the Diagnostic Hall and the BEOC, when taking cable routing into account, can be approximated at 200 meters. This distance is excessive for a cable run going from a motor control module to a stepper motor. For this reason, an I&C remote I/O rack is mounted in the BEOC. While shielding and space constrains in the BEOC need to be considered carefully, moving the I&C interfaces closer to the filter wheel assemblies will increase system performance and reliability.

Placing a remote I/O rack in the BEOC shortens the cable distances for the motor interfaces and position sensor interfaces. This remote I/O rack, however, gives rise to the need for a cable run between the PLC in the Diagnostic Hall and the remote I/O rack in the BEOC, also approximated at 200 meters. This distance is excessive for a copper Ethernet/Profinet network cable run. Common best-practice is to keep cable runs to 100 meters or less, and this is especially true in challenging electromagnetic conditions. For this reason, the network cable between the PLC in the Diagnostic Hall and the remote I/O rack in the BEOC will use a fiber optic cable.

By using appropriate network switches, connectors, cable and associated accessories, other network segments can use fiber optic cable as needed.

## Design Rationalization

The I&C design rationalization considers that successful operation of the UWAVS, and ultimately the reactor itself, relies on many complex systems and subsystems working as expected. All of the systems and subsystems need to work in concert with each other in order to achieve successful operation. The design of the UWAVS should minimize the chances of a failed diagnostic measurement. At the same time, operation of UWAVS should be reliable, intuitive, and simple for an operator who may be simultaneously overseeing the operation of many systems and subsystems. 

Stepper motors without encoders and without brakes are used to drive the filter wheels. This allows open-loop positioning control and eliminates failure modes related to encoders or brakes.

An earlier conceptual design used a radiation hardened mechanical switch and a cam located at a specific location on the filter wheel to sense a home position. When the cam engaged the switch, it was defined to be at the home position. This allowed a filter wheel to be position referenced to a known position, but limited the ability for the system to detect position errors.

An alternative to the mechanical switch and cam design is a laser based distance sensing sensor used to count filter wheel teeth. This is made possible by the relaxation of the radiation hardness requirement for electronics in the BEOC. This allows real-time feedback of the filter wheel rotational position. This coupled with the open-loop position control means that the system can detect position discrepancies as they occur, but also operate without position feedback. See the Fault Tolerance section below.

# System Architecture

The electrical interface between the filter wheel I&C components and the PLC is via the remote I/O rack in the BEOC. 

The PLC will have a local PROFINET ("Process Field Network", denoted "Profinet") communication card dedicated to UWAVS I/O communication. This network is controlled by the PLC and isolated from other networks. Due to cable distance, routing, the potential for electrical interference and performance considerations, the connection between the PLC and the remote I/O rack uses a fiber optic cable. This cable will be duplex, use "LC" type fiber optic connectors, and Multimode cable with core/cladding diameters of either 50/125 um or 62.5/125 um. Such cable is common for these applications and typically readily available.

The remote I/O rack houses a stepper motor controller for each stepper motor, 6 in total. It also houses a signal counting module for each position sensor, 6 in total. 

**TODO**: Network diagram


## Position Sensor

A laser based distance sensor would be fitted in such a way that it would count the teeth by detecting the presence/absence of a filter wheel tooth, or more specifically the distance between the sensor and the gear top land versus bottom land. The system will treat the pulse train generated by the teeth passing by the sensor in a similar way it would treat an incremental encoder. This sensor and associated pulse counting input module gives the system real-time feedback of the filter wheel rotational position ("the filter wheel position"). This arrangement allows the system to keep track of filter wheel position to a reasonable degree of certainty and precision, even if the motor misses steps, stalls, or if the spur gear becomes disengaged or slips for example. The sensor position can always be compared to the theoretical position derived from motor commands. Thus, there would be a high degree of confidence that the actual filter wheel position matches the believed filter wheel position. See the Fault Tolerance section below.

In addition to tracking the position of the filter wheel, the position sensor is also used to detect a "Home Feature", such as a blind hold in the bottom land. This feature denotes a specific location on the filter wheel, and the filter wheel is defined to be at the "Home Position" when the Home Feature is detected by the sensor. An important characteristic of the Home Feature is that the distance from the sensor of this feature shall be different than the typical top land or bottom land distance. Having a defined home position means that the system can always locate a particular Filter Position, and thus calibration is made easier and can be automated or semi-automated with a software routine or sequence.

## Motor Control System

Each filter wheel is driven by an encoderless stepper motor fitted with a 30mm diameter spur gear.

The control each stepper motor shall be via the PLC. The PLC will control remote I/O located in a shielded portion of the BEOC. The remote I/O will contain motor drive modules that are the electrical and control interface to the stepper motors. The remote I/O will contain signal pulse counting modules that will be the electrical and control interface to the position sensors.

Velocity, relative, and absolute move types are supported. A velocity move type will take specified velocity (deg/sec), acceleration (deg/sec²), and deceleration (deg/sec²), and move until a stop is issued. A relative move type will take the same parameters as a velocity move plus an additional distance (bipolar value in degrees denoting distance and direction), or a distance (postive value in degrees) and direction (forward/backward, cw/ccw). An absolute move type will take the same parameters as a velocity move, plus an additional position value (degrees), and an optional direction.  If a move is expressed in distance, a relative move is typically used. If a move is expressed as going to a position, then a absolute move is typically used. 

Note that this rotary application is configured as a periodic "limitless" axis.  An absolute move can always take the shortest distance to a specified position without regard to position rollover or exceeding position limits. For this reason, the direction is optional for absolute moves. If no direction is specified, an absolute move will go to the desired position using the shortest distance.

Note that velocity and relative moves can be used before an axis is position reference or "homed", but absolute moves require the axis to be homed. Furthermore, once homed, the application shall support moving to a specific filter position. This capability is based on absolute moves, but allows the operator to specify a filter position rather than degrees.

The motor driving the filter wheel will be a radiation hardened stepper motor without an encoder, and without a brake.

## Fault Tolerance

The stepper motors are encoderless, and the position control will be open-loop. This is for fault tolerance -- the system can be operated without the need for an encoder and can be operated without functioning position sensors. The PLC motor control hardware and software will keep track of a theoretical motor position ("the motor position"), and assume the motor achieves the moves that are issued.

The filter wheel position will be tracked using the filter wheel position sensor and the PLC. This value will be compared to the motor position. In normal operation, these should always agree within a tolerance. If the difference in these two positions is outside a tolerance, a position discrepancy warning shall be issued, indicating the filter wheel may be out of position or in need of homing. This arrangement of open-loop position control and a position sensor are important features for fault tolerance. It allows the system to operate if the position sensor is not working, but also allows early position warnings to be issued to the operator if discrepancies are detected.

If a position discrepancy arises, the operator can be made aware of this situation as it develops. The operator can then make decisions about what to do about the discrepancy based on the situation. If the position error is small, the size of the filter aperture may mean that diagnostic performance may not be affected. If the position error is large, it mean the filter wheel needs a position adjustment before operation resumes or additional investigation may be needed.


## Faults and Alarms

Alarm is a condition that alerts an operator of an abnormal or deteriorated condition, and which limits operation, and generally requires intervention.
Warning is a condition that alerts an operator of an abnormal or deteriorated condition, but which may not or only minory limit operation, and may require little or no intervention.

| Fault Type | Description                  | Possible Cause                             | System Response                  | Error Recovery              |
|------------|------------------------------|--------------------------------------------|----------------------------------|-----------------------------|
| Alarm      | Remote I/O rack              | * Communicatin link broken                 | Annunciate alarm                 | * Fix communication link    |
|            |                              | * Communication module broken, missing     | Filter wheel motion not possible | * Fix or install the module |
|            |                              | or misconfigured                           |                                  | * Fix the configuration     |
|            |                              | * PLC misconfigured                        |                                  |                             |
|------------|------------------------------|--------------------------------------------|----------------------------------|-----------------------------|
| Alarm      | Motor control module fault   | * Module broken, missing or misconfigured  | Annunciate alarm                 | * Fix or install the module |
|            |                              | * PLC misconfigured                        | Filter wheel motion not possible | * Fix the configuration     |
|------------|------------------------------|--------------------------------------------|----------------------------------|-----------------------------|
| Alarm      | Counter module fault         | * Module broken, missing, or misconfigured | Annunciate alarm                 | * Fix or install the module |
|            |                              | * PLC misconfigured                        |                                  | * Fix the configuration     |
|            |                              |                                            |                                  | * Operate in dead-reckoning |
|------------|------------------------------|--------------------------------------------|----------------------------------|-----------------------------|
| Warning    | Position Disrepancy Small    | * Filter wheel position <> Motor Position  | Annunciate warning               | * Run the home sequence     |
|            | Diagnostic measurement       | Difference is small                        |                                  | * Set reference position    |
|            | may not be affected          |                                            |                                  | * Operate in dead-reckoning |
|------------|------------------------------|--------------------------------------------|----------------------------------|-----------------------------|
| Alarm      | Position Disrepancy Large    | * Filter wheel position <> Motor Position  | Annunciate alarm                 | * Run the home sequence     |
|            | Diagnostic measurement       | Difference is large                        |                                  | * Set reference position    |
|            | probably affected            |                                            |                                  | * Operate in dead-reckoning |
|------------|------------------------------|--------------------------------------------|----------------------------------|-----------------------------|
| Alarm      | Position sensor not detected | * Sensor broken, not aligned, or miswired  | Annunciate alarm                 | * Service the sensor and    |
|            |                              | * Pulses not detected while moving         |                                  | home the system.            |
|            |                              |                                            |                                  | * Operate in dead-reckoning |
|------------|------------------------------|--------------------------------------------|----------------------------------|-----------------------------|
| Alarm      | Home Unsuccessful            | * Home feature not detected where expected | Annunciate alarm                 | * Repeat home request       |
|            |                              | * Sensor broken, not aligned, or miswired  | Clear referenced status          | * Service the sensor        |
|            |                              |                                            |                                  | * Operate in dead-Reckoning |
|------------|------------------------------|--------------------------------------------|----------------------------------|-----------------------------|

# Filter Wheel Process / Measurement Position

## Filter Selection

The filter set for each filter wheel is be operator specified. The operator can specify the filter wavelength or function for each filter wheel position, based on what filter element is fitted to a filter position. Typically each filter wheel position will contain a "notch" filter which allows a specific wavelength to pass, a neutral density filter which reduces the amount of light that passes, or is "open" or "neutral" in which case the beam passes unaltered.

The possible filter selections are as follows:

* H-Alpha
* Be
* W
* C
* Cu
* Ne
* Ar
* Kr
* He
* ND Neutral Density
* Open / Neutral

For measurement flexibility, it is anticipated that each wheel will contain a Neutral Density filter in a position, and an open/neutral filter in a position. 

If a change is made to the fitted filters, the operator needs to update the filter wheel configuration.

## Process / Measurement Position

Based on the filter wheel selection and the position of each filter wheel, the system will determine a *"Process Position"* or *"Measurement Position"* (herein referred to as the *"Measurement Position"*). The Measurement Position is the combined effect of the positioning of the three filter wheels. If one or more filter wheels is not in a filter position, the Measurement Position is "Unknown". If all the filter wheels are in a filter position, but the resulting combination would not produce a valid measurement, then the Measurement Position is "Unknown". Otherwise, the Measurement Position will indicate the selected measurement. 

Typically a measurement would be made with one wheel having an element filter in place, a second wheel having a neutral density or open filter in place, and the third wheel having a neutral density or open filter in place. Thus, the anticipated Measurement Positions are as follows:

| Measurement Postion | Notes                                                                    |
|---------------------|--------------------------------------------------------------------------|
| H-Alpha             | Element filter selected and two open positions selected                  |
| H-Alpha ND 1        | Element filter selected, one open position, and one ND position selected |
| H-Alpha ND 2        | Element filter selected and two neutral density positions selected       |
|---------------------|--------------------------------------------------------------------------|
| Be                  | Element filter selected and two open positions selected                  |
| Be ND 1             | Element filter selected, one open position, and one ND position selected |
| Be ND 2             | Element filter selected and two neutral density positions selected       |
|---------------------|--------------------------------------------------------------------------|
| W                   | Element filter selected and two open positions selected                  |
| W ND 1              | Element filter selected, one open position, and one ND position selected |
| W ND 2              | Element filter selected and two neutral density positions selected       |
|---------------------|--------------------------------------------------------------------------|
| C                   | Element filter selected and two open positions selected                  |
| C ND 1              | Element filter selected, one open position, and one ND position selected |
| C ND 2              | Element filter selected and two neutral density positions selected       |
|---------------------|--------------------------------------------------------------------------|
| Cu                  | Element filter selected and two open positions selected                  |
| Cu ND 1             | Element filter selected, one open position, and one ND position selected |
| Cu ND 2             | Element filter selected and two neutral density positions selected       |
|---------------------|--------------------------------------------------------------------------|
| Ne                  | Element filter selected and two open positions selected                  |
| Ne ND 1             | Element filter selected, one open position, and one ND position selected |
| Ne ND 2             | Element filter selected and two neutral density positions selected       |
|---------------------|--------------------------------------------------------------------------|
| Ar                  | Element filter selected and two open positions selected                  |
| Ar ND 1             | Element filter selected, one open position, and one ND position selected |
| Ar ND 2             | Element filter selected and two neutral density positions selected       |
|---------------------|--------------------------------------------------------------------------|
| Kr                  | Element filter selected and two open positions selected                  |
| Kr ND 1             | Element filter selected, one open position, and one ND position selected |
| Kr ND 2             | Element filter selected and two neutral density positions selected       |
|---------------------|--------------------------------------------------------------------------|
| He                  | Element filter selected and two open positions selected                  |
| He ND 1             | Element filter selected, one open position, and one ND position selected |
| He ND 2             | Element filter selected and two neutral density positions selected       |
|---------------------|--------------------------------------------------------------------------|
| Open                | All open positions selected                                              |
| Open ND 1           | Two open positions selected and one ND positon selected                  |
| Open ND 2           | One open position selected, and two ND position selected                 |
| Open ND 3           | All ND positions selected                                                |
|---------------------|--------------------------------------------------------------------------|

## CODAC Interface

At the start of normal operations, the 55.GA system will import a configuration from CODAC. This will include the *"Desired Measurement"*. Based on the position mode, the system or the operator will position the filter wheels such that the Measurement Position matches the Desired Measurement.

The system will send back to the CODAC system the Desired Measurement, as a confirmation of receipt, and the Measurement Position, as a confirmation that the filter wheels are in the correct position. **Do we information to CODAC??**

# Software Functionality

## Filter wheel positioning

The filter wheel control system will support moving the filter wheels in either *"Supervisory Control Auto"*, *"Supervisory Control Manual"*, or *"Manual Control"*. It is envisioned that "normal" operation will be in *Supervisory Control Auto*, where the system will position the filter wheels based on configuration information received from the supervising CODAC system without operator intervention. The other control modes give the operator control of the filter wheel positions in order to accommodate other operations or off-normal events.

**? Does CODAC receive back what diagnostic measurement the system is set to deliver?**

Assuming normal operation, if after every move, the theoretical motor position and the process position derived from the positioning sensor are within tolerance of each other, no operator intervention is needed for position adjustment. If, however, the theoretical motor position and the process position derived from the positioning sensor differ by more than a tolerance, an warning or alarm is raised annunciating the possibility of a position problem.

Note that all moves except Manual Relative Moves require the system be position referenced/homed before the move is available.

### Supervisory Control
Typically at the start of operations, the UWAVS system wold import a configuration from the supervising CODAC system. This configuration will identify which diagnostic measurements are wanted from the UWAVS system. The system would then translate the desired measurement need received from CODAC into a set of filter wheel positions.

Assuming the filter wheels have been position referenced, then the repositioning of the filter wheels in response to a change in CODAC configuration can be done automatically or manually.
* In *Supervisory Control Auto*, the system will determine and display the proper position of each filter wheel, and will move the filter wheels to the necessary positions at a predetermined point in a operational sequence without operator intervention.
* In *Supervisory Control Manual*, the system will determine and display the proper position of each filter wheel, but the operator will need to issue a command to move the filter wheels.

### Manual Control
In Manual Control, it is the operators responsibility to move the filter wheels. There are several ways this can be done.
* In *Manual Control Measurement Parameter* the operator selects a desired measurement parameter, and after a command is issued, all three wheels in the assembly go the positions necessary to support the selected measurement parameter. Note that this mode requires the system to be position referenced, and that the resulting positions are the same as if the same measurement parameter had been sent by the CODAC system, and the system was in *Supervisory Control*.
* In *Manual Control Filter Position* the operator selects a filter wheel and desired filter position (1-6), and after a command is issued, the selected filter wheel goes to the position necessary for the selected filter position. Note that this mode requires the system to be position referenced.
* In *Manual Control Manual Position* the operator selects a filter wheel, a move type, and a desired distance or position. The supported move types are *Relative* and *Absolute*. A Relative move allows the operator to specify a direction and distance in degrees from the current position. An Absolute move allows the operator to specify a position, in degrees. Direction options for an Absolute Move are *Shortest Distance*, *Clockwise (CW)*, or *Counter-Clockwise (CCW)*. Note that an absolute move requires the system to be position referenced, but a relative move is the only move that can be issued if the system is not position referenced.

### Sensorless/Dead-Reckoning Mode
If homing cannot be achieved, because the sensor is broken, not calibrated, or not aligned for example, it shall be possible to run without a position sensor.

Dead-reckoning has to be specified as an operational mode, and requires the system to have been referenced using the Referencing Process, *"Set Zero Position"* or *"Set Position Reference"*. From that point on, the system would behave similar to if it was using the position sensor. Moves would be done by as described above, but would be done "blindly" in the sense that the system would assume a motor movement of the correct distance gets the filter wheel in the correct location. Thus, a motor stalling or missing steps, or the filter wheel not being in the correct position would not be accounted for and would not be anunciated 

## Position Referencing Process / Homing Process

Position referencing or "homing" refers to setting a control system logical position. 
A homing process is used to calibrate a filter wheel physical position to a control system logical location. In addition to the homing process, the logical position can simply be set to zero, using a *"Set Zero"* command, or the logical position can be set to any operator entered value using a *"Set Reference Position"* command.

In normal operation, a homing process would be performed to set the position reference. A filter wheel only needs to be *"homed"* or *"position referenced"* after a mechanical change, if calibration is needed, a fault occurs, or possibly after a power interruption or some sort of systemic change. In normal operation, once position referencing is performed, the system should stay position referenced. The position referencing process can be repeated any time operations permit, but if a particular filter wheel is homed already, repeating the process is generally not necessary.

With a cam switch, it is recommended final home position be approached always from the same direction (sensor switch hysteresis, cam location vs switch vs symmetry, etc.)    
I would not assume the switch operates at exactly the same wheel position when approached from two different directions. In fact it is very likely to be different without a design change.  If this error is on the order of the tolerance of a filter being in position, then homing direction will likely be important.
Refer to this direction as *"Home Direction"*. Choice of direction may be somewhat arbitrary, but should be constant without a calibration or configuration change. 

With a laser sensor, the Home Direction is less important.

This process assumes the filter wheel can always be rotated a full rotation in either direction. I.e there are not stops that prevent the wheel from going all the way around, and the it is okay to approach and run past the cam switch, for example.

**TODO:** This should probably be a flowchart or other diagram

### Request to Set Zero Position

This command is used to set the position reference to the zero position. The logical Filter Position will also be set to 1, as by definition, the optimum position for Filter 1 is when the position is zero.

A request to Set Zero would be performed, for example, if the operator knows the filter wheel in already in the optimum position for Filter 1, and a homing sequence is not needed. Note it can be performed with or without a functioning position sensor. 

### Request to Set Reference Position

This command is used to set the position reference to a known value. It could be any value from 0-360. If the set position is within tolerance of a Filter Position (a 60 degree division), the Filter Position will be set.

This would be performed, for example, if the operator knows the filter wheel in already in a specific position, and a homing sequence is not needed. Note it can be performed with or without a functioning position sensor. 

### Request to Home is Made While Position Referenced

If a request to home is made, and the system has been previously homed or position reference, and there has not been a power interruption, major fault, etc. and the system at least thinks the home position is valid, then it is said to be *"Position Referenced"* or *"Homed"*. In this case there is good reason to believe that at least the approximate current home position can be believed.

#### Find Home
Go towards the home position in the direction of shortest travel, and a configured *Transit Speed*. Note the direction of travel vs the *Home Direction*.

##### Home Found
If the home switch is found approximately (current Raw Home Position +/- *"Home Tolerance"*) where it is expected:

###### Traveling in the Home Direction
1. Stop
1. Reverse direction of travel, and move to clear the home switch, plus a configured (small) distance the *"Home Over Travel Distance"*, and Stop.
1. Reverse direction again, and travel at the configured *Home Speed*, now in the *Home Direction* until the home switch is made. The *"Home Speed"* is deliberately very slow so the effects of system latency when the home switch is detected become negligible.  
Set a *"Home Search Distance"* to 2x the *Home Over Travel Distance*.

####### Home Found
Once the home switch is found within the *Home Search Distance*:
1. Stop immediately

This is the *"Raw Home Position*".

There shall be a configurable *"Home Offset"* distance (+/- degrees) added to the *Raw Home Position* such that the resulting position is the position which results in the *Filter 1* being in the optimum position.

1. Knowing the *Raw Home Position* and the *Home Offset*, perform a set-zero function such that the 0-degree position is when *Filter 1* is in the optimum position. The other filter positions are assumed to be at 60 degree intervals from this position.

1. Set the *"Position Referenced"* flag.

####### Home Not Found
If the home switch is not found within the *Home Search Distance*:
1. Stop
1. Clear the Position Referenced flag.
1. Trigger a *"Home Unsuccessful Alarm"*
1. Repeating the home request with a now non-Position Referenced system should find a home switch that was not where it was expected to be. 

###### Traveling Opposite the Home Direction
1. Continue for at least the configured (small) distance the *"Home Over Travel Distance"*, and Stop.
1. Reverse direction, and travel at the configured *Home Speed*, now in the *Home Direction* until the home switch is made. The *"Home Speed"* is deliberately very slow so the effects of system latency when the home switch is detected become negligible.

####### Home Found
Once the home switch is found within the *Home Search Distance*:
1. Stop immediately

	This is the *"Raw Home Position*". (Same details as above.)
1. Set the *"Position Referenced"* flag.

####### Home Not Found
If the home switch is not found within the *Home Search Distance*:
1. Stop
1. Clear the Position Reference flag.
1. Trigger a *"Home Unsuccessful Alarm"*
1. Repeating the home request with a now non-Position Referenced system may find a home switch that was not where it was expected to be. 

### Request to Home is Made While Not Position Referenced
If a request to home is made, and the system has not been homed, if there has been a power interruption, major fault, etc. and for whatever reason the does not have a valid home position, then it is not *"Position Referenced"*. In this case, assume the system has no idea where the home switch is.

#### Find Home

1. Run in the opposite direction as the Home Direction at a configured *"Transit Speed"*, while looking for the Home Switch. The direction choice is simply because starting in the direction opposite the Home Direction slightly simplifies the sequence (eliminates a direction change) once the home switch is found. 

##### Home Found
If the home switch is found before an entire rotation of the filter wheel is made:
1. Continue moving until the home switch is cleared, and continue for at least the configured (small) distance *"Home Over Travel Distance"*, and Stop.  
Set a *"Home Search Distance"* to 2x the Home Over Travel Distance.

1. Reverse direction, and travel, now in the Home Direction, to the home switch slowly, at a configured *"Home Speed"*. (Same details as above)

###### Home Found
Once the home switch is found within the Home Search Distance, stop immediately.
This is the *"Raw Home Position*". (Same details as above)

###### Home Not Found
1. If the home switch is not found within the Home Search Distance, then  
1. Stop
1. Clear the Position Reference flag.
1. Trigger a *"Home Unsuccessful Alarm"*
    
##### Home Not Found
If the home switch is not found before an entire rotation of the filter wheel is made:
1. Stop
1. Clear the Position Reference flag.
1. Trigger a *"Home Unsuccessful Alarm"*
        
# Hardware

In summary the Slow Controller PLC in the Diagnostic Hall controls a remote I/O rack in the BEOC. The connection between the two is a fiber optic cable with LC connectors. The remote I/O rack contains a communication module for connection back to the PLC, motor controllers for the stepper motors, a pulse counting modules for counting sensor pulses, a digital input module to sense the home position output of the sensor. A position sensor part of the filter wheel assembly, and is listed here for completeness.

IFM OMH550 is the preferred sensor between two identified sensors because it has a shorter minimum sensing distance (30mm) and that makes it easier to integrate.


| Description                  | Location              | Mfr     | Part Number        | Qty | Notes                              |
|------------------------------|-----------------------|---------|--------------------|-----|------------------------------------|
| Slow Controller PLC          | Diagnostic Hall       | Siemens | 6ES7516-3AP03-0AB0 | 1   | Supervising controller             |
|------------------------------|-----------------------|---------|--------------------|-----|------------------------------------|
| Mounting Rail                | BEOC                  | Siemens | 6ES5710-8MA11      | 1   | Cut to length                      |
|------------------------------|-----------------------|---------|--------------------|-----|------------------------------------|
| Remote I/O Comm Module       | BEOC Remote IO        | Siemens | 6ES7155-6AU01-0CN0 | 1   | Accpets bus adapters               |
|------------------------------|-----------------------|---------|--------------------|-----|------------------------------------|
| Bus Adapter                  | BEOC Remote IO        | Siemens | 6ES7193-6AC00-0AA0 | 1   | 2x LC fiber optic                  |
|------------------------------|-----------------------|---------|--------------------|-----|------------------------------------|
| Stepper Motor Drive Module   | BEOC Remote IO        | Phytron | TM StepDrive       | 6   | 1x24..48V/5A                       |
|------------------------------|-----------------------|---------|--------------------|-----|------------------------------------|
| Base Unit and terminal block | BEOC Remote IO        | Siemens | 6ES7193-6BP20-0BB1 | 6   | Base unit for motor drives         |
|------------------------------|-----------------------|---------|--------------------|-----|------------------------------------|
| Counter Module               | BEOC Remote IO        | Siemens | 6ES7138-6AA01-0BA0 | 6   | 1x HS Counter. For position pulses |
|------------------------------|-----------------------|---------|--------------------|-----|------------------------------------|
| Base Unit and terminal block | BEOC Remote IO        | Siemens | 6ES7193-6BP00-0DA0 | 6   | Base unit for counter modules      |
|------------------------------|-----------------------|---------|--------------------|-----|------------------------------------|
| Digital Input                | BEOC Remote IO        | Siemens | 6ES7131-6BF00-0DA0 | 1   | 8x HS DI. For home pulses          |
|------------------------------|-----------------------|---------|--------------------|-----|------------------------------------|
| Base Unit and terminal block | BEOC Remote IO        | Siemens | 6ES7193-6BP00-0BA0 | 1   | Base unit for DI module            |
|------------------------------|-----------------------|---------|--------------------|-----|------------------------------------|
| Position Sensor              | Filter Wheel Assembly | IFM     | OMH550             | 6   | Dual Digital outpus for counting   |
|------------------------------|-----------------------|---------|--------------------|-----|------------------------------------|
| LC MM Fiber Optic Cable      | DH to BEOC Remote IO  | various | various            | 1   | Duplex, 50/125 um or 62.5/125 um   |



