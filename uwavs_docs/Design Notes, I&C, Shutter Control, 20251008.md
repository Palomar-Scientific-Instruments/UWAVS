# I&C Design Note Shutter Control

# Questions / Comments / TODOs

TODOS: Search the document for "TODO"

1. Needs CODAC interface

2. Needs P&ID Diagram(s) and ideally a sequence diagram

## 55.C2 ETS Prototype of Pressure Intensifier for Shutter

### Assumptions / Questions / Assertions

There are proposed changes to the pneumatic shutter controls over the Japanese 55.C2 design. Lacking a BOM for the valve box and any interface details regarding the valves and other equipment in the valve box we are interfacing to, in order to make progress on the 55.GA UWAVS I&C interface to the valve box and implement shutter control, I am making the following assumptions:

1.	The valves will change from pneumatically piloted valves to solenoid valves.
2.	The “extension” of the non-SIC zone to include VG-0011 will be accepted, and this valve will be controlled by the 55.GA system.
3.	The proposed valve addition of a valve downstream of the High Pressure Tank TA-0004 will be accepted, and this valve will be controlled by the 55.GA system.
4.	Each valve will single solenoid, spring return, and normally-closed. A solenoid gets energized to open the  valve. When the solenoid is de-energized, the valve springs closed.

Other options would be normally open and/or double-solenoid. What each valve should do if control power is lost or unavailable should be considered. GA may have recommendations in the coming days as we progress with the design.

5.	Each solenoid control voltage will be 24 VDC, and each will be low enough current to be powered by a PLC Output card.
6.	Each valve shall have two limit switches. Each limit switch will be a normally open switch, and switch 24 VDC based on valve position. The corresponding PLC digital input module shall be a type to sink current. Thus the limit switch shall be a two wire current source type.
7.	The three pressure transducers MP-0001, MP-0002, MP-0004 shall have a 4-20 mA interface to the PLC and shall be two or three wire 24 VDC or loop powered devices.
8.	The motor controls for PU-0001 will consist of a 24 VDC PLC Digital output.  The slow-controller PLC will be able to start and stop the motor using this output. The power and circuit protection for the motor is outside the scope of 55.GA. 
9.	Control of and interfacing to VG-0021 and VG-0022, both SIC-1 valves, is outside the scope of 55.GA.
10.	Control of and interfacing to the Piezo Interlock indicated on the “New design proposal – summary” diagram is outside the scope of 55.GA.
11. PBS31 "Purging and Supply of N2 Gas for Shutter Control" provides 0.12 MPa/1.2 bar/17.4 psi N2 maximum pressure gas.
Assume the high pressure side of pump PU-0001 is at a sufficient pressure to overcome this pressure, and close the shutter. The PBS31 essentially sets the "low pressure" level of the system

**OLD: Should get customer verification: ** Assume there is a 3-position valve ahead of the valve box that is either 1) closed, 2) hooks the valve box to the exhaust side of the ITER Service Vacuum System, or 3) hooks the valve box to an N2 gas supply side of the ITER Service Vacuum System.

12. **Quesion:** What is the purpose of TA-0001? This is shown behind a hand valve VG-0008. Two functions I can see:
    1) Keep at high pressure (approx 0.35 MPa/3.5 bar/ 50.8 psi) to have a backup supply of N2. This could provide a means of filling the High Pressure Tank TA-0004 in the event of a need to keep the system closed loop, and pump PU-0001 failure.
    2) Keep at about 0.12 MPa/1.2 bar/17.4 psi, the pressure of PBS31. This would then be a way to keep VG-0011 closed (closed loop operation), and allow a number of shutter operations by giving a place for the Low Pressure Tank TA-0005 to exhaust to.
    3) Some other use case related to keeping the system closed loop due to Tritium/radiation/activation concerns.

13. **Proposal:** Propose adding a gauge MP-00N3 between the High Pressure Tank and the new valve VG-00N1, or moving exiting MP-0002 to this location (less desirable because the pressure at the shutter during low pressure operation (opening) is not known). This allows the system to know the pressure of the High Pressure Tank TA-0004.

14. **Question:** Does the shutter have travel limit indications of if it is open or closed?

15. As written the operation sequences below generally put the system into an idle state -- vavles closed, and pump off.
For example, when the shutter is opened, the pressure is exhausted into the low pressure tank, but then VG-0018 is closed, and the shutter should stay open -- but the system does not keep exhausting the shutter pressure. 
When the shutter is closed, pressure is applied by opening VG-00N1. The shutter opens, and then VG-00N1 is closed, and the shutter should stay closed -- but the system does not keep pressurizing the shutter. 

In both cases, the system goes to an idle/isolated state once the action is performed. **Is this what we want?** Maybe if there are not position indicator sensor(s).

# Introduction

## Purpose

This document outlines the Instrumentation and Controls ("I&C") design for the Pneumatic Shutter Control subsystem ("shutter control system"). The objective of the document is to define the system architecture, the main components related to I&C, the associated alarms and faults, the supervising Control Data Access and Communication ("CODAC") signal interface, and present important software functionality.

## Pneumatic Shutter Control Subsystem Overview


## Special Design Considerations


## System Architecture

The pneumatic shutter is controlled by the Valve Box. The valve box and the design of the valve box is not in the GA.55 UWAVs scope. The GA.55 UWAVs system does need to interface to the valve box. The Slow Controller Programmable Logic Controller ("PLC") in the Diagnostic Hall will control the Input / Output ("I/O") Modules that control and monitor the valve box.

### Key components

TODO: These designations are taken from a PPPL Proposed changed diagram. It is unclear if the 55.GA UWAVS system Valve Box will use the same designations.

| Designation | Description                                  | Notes                                             |
|-------------|----------------------------------------------|---------------------------------------------------|
| VG-0011     | Solenoid Valve, Valve Box Inlet              | PPPL proposed removing SIC-2 status               |
| MP-0001     | Pressure Transducer, Inlet Pressure          |                                                   |
| VG-0014     | Solenoid Valve, Compressor Inlet             |                                                   |
| PU-0001     | Compressor                                   |                                                   |
| TA-0004     | Tank, High Pressure                          |                                                   |
| VG-00N1     | Solenoid Valve, High Pressure Tank Outlet    | New PPPL Proposed valve. Placeholder designation. |
| MP-00N3     | Pressure Transducer, High Pressure Tank      | Proposed by GA. Placeholder designation.          |
| MP-0002     | Pressure Transducer, To Shutter              |                                                   |
| VG-0019     | Solenoid Valve, Low Pressure Tank Outlet     |                                                   |
| TA-0005     | Tank, Low Pressure                           |                                                   |
| MP-0004     | Pressure Transducer, Low Pressure Tank Inlet |                                                   |
| VG-0018     | Solenoid Valve, Low Pressure Tank Inlet      |                                                   |
| VG-0021     | SIC-1 Valve, Valve Box Outlet 1              | Control is outside scope of 55.GA UWAVS           |
| VG-0022     | SIC-1 Valve, Valve Box Outlet 2              | Control is outside scope of 55.GA UWAVS           |
| TA-0001     | Tank, ?                                      | Purpose/function unknown                          |
| PBS31       | Purging and Supply of N2 Gas                 | Feeds Valve Box via VG-0011                       |
|             | Slow Controller PLC                          |                                                   |
|             | Slow Controller PLC I/O Modules              |                                                   |

### Operation Sequence

TODO: Needs P&ID Diagram(s) and ideally a sequence diagram

#### Initial Conditions

1. Assume proper shutter operation is achieved using the two available pressures, 0.12 MPa and 0.35 MPa. When 0.12 MPa is applied, the shutter spring will open the shutter. When 0.35 MPa is applied, the spring is overcome by the pressure and the shutter closes.
2. PBS31 is capable of supplying and accepting 0.12 MPa N2 gas ("gas"). P&ID lists this pressure as a maximum, but assume for the purposes of this description, that the nominal pressure of PBS31 is this value.
3. All valves are closed, and pump PU-0001 is off.
4. High Pressure Tank TA-0004 is not over-pressurized.

#### Idle State
1. All valves are closed, and pump PU-0001 is off.
2. MP-00N3 (proposed pressure transducer) is within tolerance of 0.35 MPa.
3. MP-0004 is within tolerance of PBS31, 0.12 MPa.

**Exit Conditions**

If MP-00N3 (proposed pressure transducer) falls out of tolerance of 0.35 MPa, then go to Step 2.
If MP-0004 falls out of tolerance of PBS31, 0.12 MPa, then go to Step 1.

#### Step 1 -- Exhaust the Low Pressure Tank TA-0005

1. Introduce PBS31 into the system. Open VG-0011. Observe MP-0001 go the pressure of PBS31.
2. Exhaust Low Pressure Tank TA-0005. Open VG-0019. Observe MP-0004 go the pressure of PBS31.
3. Isolate Low Pressure Tank TA-0005. Close VG-0019. Observe steady pressure at MP-0004, which should remain steady and within tolerance of PBS31.
4. Isolate the valve box from PBS31. Close VG-0011.
5. Go to Idle State
 
#### Step 2 -- Pressurize High Pressure Tank TA-0004

1. Introduce PBS31 into the system. Open VG-0011. Observe MP-0001 go the pressure of PBS31.
2. Supply the pump PU-0001 with gas. Open VG-0014.
3. Pressurize High Pressure Tank TA-0004. Start pump PU-0001. Observe the pressure at MP-00N3 (proposed pressure transducer). Pressurize the tank to 0.35 MPa.
4. Isolate High Pressure Tank TA-0004. Close VG-0014. Observe the pressure at MP-00N3 (proposed pressure transducer) remain steady and within tolerance of 0.35 MPa.
5. Isolate the valve box from PBS31. Close VG-0011.
6. Go to Idle State

#### Step 3 -- Open the Shutter

In order to open the shutter, the pressure at the shutter must be exhausted to approximately the pressure of PBS31, or about 0.12 MPa, or lower. **What is the maximum? See Question below.**

1. Isolate the shutter from High Pressure. Close VG-00N1 (proposed valve). It will typically already be closed, unless shutter had just been commanded closed.
2. Exhaust the pressure into the Low Pressure Tank TA-0005. Open VG-0018. Observe the pressure at MP-0002 and MP-0004. Observe the shutter open.

**QUESTION:** This will raise the pressure of TA-0005. By approximately what amount, and what is the maximum pressure the spring can overcome? Approx (rough OOM) how may operations before this pressure is reached in TA-0005? One, a few, many?

3. Isolate the shutter. Close VG-0018. The shutter should stay open.
4. Go to the Idle State

#### Step 4 -- Close the Shutter

In order to close the shutter, pressure must be applied to the shutter, overcoming the spring and closing the shutter. **What is the minimu pressure needed to close the shutter? See Question below.**

1. Isolate the shutter from Low Pressure. Close VG-0018. It will typically already be closed, unless shutter had just been commanded open.
2. Apply pressure to the shutter. Open VG-00N1 (proposed valve). Observe the pressure at MP-0002 and MP-00N3 (proposed pressure transducer). Observe the shutter close.

**QUESTION:** This will lower the pressure of TA-0004. By approximately what amount, and what is the minimum pressure needed to overcome the spring? Approx (rough OOM) how may operations before this pressure is reached in TA-0004? One, a few, many?

3. Isolate the shutter. Close VG-00N1 (proposed valve). The shutter should stay closed.
4. Go to the Idle State

## Faults and Alarms

An *"Alarm"* is a condition that alerts an operator of an abnormal or deteriorated condition, and which limits operation, and generally requires intervention.
A *"Warning"* is a condition that alerts an operator of an abnormal or deteriorated condition, but which may not limit operation, or have only a minor impact on operation, and requires little or no intervention.

| Fault Type   | Description           | Possible Cause                      | System Response      | Error Recovery                              |
|--------------|-----------------------|-------------------------------------|----------------------|---------------------------------------------|
| Warning      | VG-0011 Not Closed    | * Limit switch sensor               | * Annunciate warning | * Fix sesor or wiring                       |
|              |                       | or wiring problem.                  |                      | * Configure or replace module               |
|              |                       | * PLC Input module config or error  |                      | * Fix or replace wiring or solenoid         |
|              |                       | * Solenoid or wiring problem        |                      | * Fix or replace valve                      |
|              |                       | * PLC Output module config or error |                      |                                             |
|              |                       | * Valve broken                      |                      |                                             |
|--------------|-----------------------|-------------------------------------|----------------------|---------------------------------------------|
| Warning      | VG-0011 Not Open      | * Limit switch sensor               | * Annunciate warning | * Fix sesor or wiring                       |
|              |                       | or wiring problem.                  |                      | * Configure or replace module               |
|              |                       | * PLC Input module config or error  |                      | * Fix or replace wiring or solenoid         |
|              |                       | * Solenoid or wiring problem        |                      | * Fix or replace valve                      |
|              |                       | * PLC Output module config or error |                      |                                             |
|              |                       | * Valve broken                      |                      |                                             |
|--------------|-----------------------|-------------------------------------|----------------------|---------------------------------------------|
| Warning      | VG-0014 Not Closed    | * Limit switch sensor               | * Annunciate warning | * Fix sesor or wiring                       |
|              |                       | or wiring problem.                  |                      | * Configure or replace module               |
|              |                       | * PLC Input module config or error  |                      | * Fix or replace wiring or solenoid         |
|              |                       | * Solenoid or wiring problem        |                      | * Fix or replace valve                      |
|              |                       | * PLC Output module config or error |                      |                                             |
|              |                       | * Valve broken                      |                      |                                             |
|--------------|-----------------------|-------------------------------------|----------------------|---------------------------------------------|
| Warning      | VG-0014 Not Open      | * Limit switch sensor               | * Annunciate warning | * Fix sesor or wiring                       |
|              |                       | or wiring problem.                  |                      | * Configure or replace module               |
|              |                       | * PLC Input module config or error  |                      | * Fix or replace wiring or solenoid         |
|              |                       | * Solenoid or wiring problem        |                      | * Fix or replace valve                      |
|              |                       | * PLC Output module config or error |                      |                                             |
|              |                       | * Valve broken                      |                      |                                             |
|--------------|-----------------------|-------------------------------------|----------------------|---------------------------------------------|
| Warning      | VG-00N1 Not Closed    | * Limit switch sensor               | * Annunciate warning | * Fix sesor or wiring                       |
|              |                       | or wiring problem.                  |                      | * Configure or replace module               |
|              |                       | * PLC Input module config or error  |                      | * Fix or replace wiring or solenoid         |
|              |                       | * Solenoid or wiring problem        |                      | * Fix or replace valve                      |
|              |                       | * PLC Output module config or error |                      |                                             |
|              |                       | * Valve broken                      |                      |                                             |
|--------------|-----------------------|-------------------------------------|----------------------|---------------------------------------------|
| Warning      | VG-00N1 Not Open      | * Limit switch sensor               | * Annunciate warning | * Fix sesor or wiring                       |
|              |                       | or wiring problem.                  |                      | * Configure or replace module               |
|              |                       | * PLC Input module config or error  |                      | * Fix or replace wiring or solenoid         |
|              |                       | * Solenoid or wiring problem        |                      | * Fix or replace valve                      |
|              |                       | * PLC Output module config or error |                      |                                             |
|              |                       | * Valve broken                      |                      |                                             |
|--------------|-----------------------|-------------------------------------|----------------------|---------------------------------------------|
| Warning      | VG-0018 Not Closed    | * Limit switch sensor               | * Annunciate warning | * Fix sesor or wiring                       |
|              |                       | or wiring problem.                  |                      | * Configure or replace module               |
|              |                       | * PLC Input module config or error  |                      | * Fix or replace wiring or solenoid         |
|              |                       | * Solenoid or wiring problem        |                      | * Fix or replace valve                      |
|              |                       | * PLC Output module config or error |                      |                                             |
|              |                       | * Valve broken                      |                      |                                             |
|--------------|-----------------------|-------------------------------------|----------------------|---------------------------------------------|
| Warning      | VG-0018 Not Open      | * Limit switch sensor               | * Annunciate warning | * Fix sesor or wiring                       |
|              |                       | or wiring problem.                  |                      | * Configure or replace module               |
|              |                       | * PLC Input module config or error  |                      | * Fix or replace wiring or solenoid         |
|              |                       | * Solenoid or wiring problem        |                      | * Fix or replace valve                      |
|              |                       | * PLC Output module config or error |                      |                                             |
|              |                       | * Valve broken                      |                      |                                             |
|--------------|-----------------------|-------------------------------------|----------------------|---------------------------------------------|
| Warning      | VG-0019 Not Closed    | * Limit switch sensor               | * Annunciate warning | * Fix sesor or wiring                       |
|              |                       | or wiring problem.                  |                      | * Configure or replace module               |
|              |                       | * PLC Input module config or error  |                      | * Fix or replace wiring or solenoid         |
|              |                       | * Solenoid or wiring problem        |                      | * Fix or replace valve                      |
|              |                       | * PLC Output module config or error |                      |                                             |
|              |                       | * Valve broken                      |                      |                                             |
|--------------|-----------------------|-------------------------------------|----------------------|---------------------------------------------|
| Warning      | VG-0019 Not Open      | * Limit switch sensor               | * Annunciate warning | * Fix sesor or wiring                       |
|              |                       | or wiring problem.                  |                      | * Configure or replace module               |
|              |                       | * PLC Input module config or error  |                      | * Fix or replace wiring or solenoid         |
|              |                       | * Solenoid or wiring problem        |                      | * Fix or replace valve                      |
|              |                       | * PLC Output module config or error |                      |                                             |
|              |                       | * Valve broken                      |                      |                                             |
|--------------|-----------------------|-------------------------------------|----------------------|---------------------------------------------|
| Warning      | MP-0001 Low Pressure  | * Sensor or wiring problem          | * Annunciate warning | * Fix sesor or wiring                       |
|              |                       | * PLC Input module config or error  |                      | * Configure or replace module               |
|              |                       | * PBS31 Pressure is low             |                      | * Fix PBS31 system                          |
|--------------|-----------------------|-------------------------------------|----------------------|---------------------------------------------|
| Alarm        | MP-0001 High Pressure | * Sensor or wiring problem          | * Annunciate alarm   | * Fix sesor or wiring                       |
|              |                       | * PLC Input module config or error  |                      | * Configure or replace module               |
|              |                       | * PBS31 Pressure is high            |                      | * Fix PBS31 system                          |
|--------------|-----------------------|-------------------------------------|----------------------|---------------------------------------------|
| Alarm        | MP-00N3 Low Pressure  | * Sensor or wiring problem          | * Annunciate alarm   | * Fix sesor or wiring                       |
|              |                       | * PLC Input module config or error  |                      | * Configure or replace module               |
|              |                       | * High pressure line problem        |                      | * Fix Pump PU-0001, Tank TA-0004 or related |
|--------------|-----------------------|-------------------------------------|----------------------|---------------------------------------------|
| Warning      | MP-00N3 High Pressure | * Sensor or wiring problem          | * Annunciate warning | * Fix sesor or wiring                       |
|              |                       | * PLC Input module config or error  |                      | * Configure or replace module               |
|              |                       | * High pressure line problem        |                      | * Fix Pump PU-0001, Tank TA-0004 or related |
|--------------|-----------------------|-------------------------------------|----------------------|---------------------------------------------|
| Warning      | MP-0002 Low Pressure  | * Sensor or wiring problem          | * Annunciate Warning | * Fix sesor or wiring                       |
| or           |                       | * PLC Input module config or error  | or Alarm             | * Configure or replace module               |
| Alarm        |                       | * Low pressure line problem         |                      | * Fix Tank TA-0005, PBS31 or related        |
| (oper. dep.) |                       | * High pressure line problem        |                      | * Fix Pump PU-0001, Tank TA-0004 or related |
|--------------|-----------------------|-------------------------------------|----------------------|---------------------------------------------|
| Warning      | MP-0002 High Pressure | * Sensor or wiring problem          | * Annunciate Warning | * Fix sesor or wiring                       |
| or           |                       | * PLC Input module config or error  | or Alarm             | * Configure or replace module               |
| Alarm        |                       | * Low pressure line problem         |                      | * Fix Tank TA-0005, PBS31 or related        |
| (oper. dep.) |                       | * High pressure line problem        |                      | * Fix Pump PU-0001, Tank TA-0004 or related |
|--------------|-----------------------|-------------------------------------|----------------------|---------------------------------------------|
| Warning      | MP-0004 Low Pressure  | * Sensor or wiring problem          | * Annunciate warning | * Fix sesor or wiring                       |
|              |                       | * PLC Input module config or error  |                      | * Configure or replace module               |
|              |                       | * Low pressure line problem         |                      | * Fix Tank TA-0005, PBS31 or related        |
|--------------|-----------------------|-------------------------------------|----------------------|---------------------------------------------|
| Alarm        | MP-0004 High Pressure | * Sensor or wiring problem          | * Annunciate alarm   | * Fix sesor or wiring                       |
|              |                       | * PLC Input module config or error  |                      | * Configure or replace module               |
|              |                       | * Low pressure line problem         |                      | * Fix Tank TA-0005, PBS31 or related        |
|--------------|-----------------------|-------------------------------------|----------------------|---------------------------------------------|
| Warning      | PU-0001 Fail To Start | * Power issue                       | * Annunciate warning | * Fix power problem                         |
|              |                       | * PLC output module config or error |                      | * Configure or replace module               |
|              |                       | * Contactor or motor control issue  |                      | * Fix contactor or control issue            |
|--------------|-----------------------|-------------------------------------|----------------------|---------------------------------------------|
| Warning      | PU-0001 Fault         | * Motor overcurrent issue           | * Annunciate warning | * Fix power problem                         |
|              |                       | * Motor mechanical issue            |                      | * Fix pump or motor problem                 |
|              |                       | * Contactor or motor control issue  |                      | * Fix contactor or control issue            |
|--------------|-----------------------|-------------------------------------|----------------------|---------------------------------------------|



## CODAC Interface

** TODO **
        
# Hardware

**TODO** I/O Modules reflected in the IO List.

