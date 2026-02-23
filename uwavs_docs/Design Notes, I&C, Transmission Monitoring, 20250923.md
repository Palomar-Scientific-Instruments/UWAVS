# I&C Design Notes Transmission Monitoring

# Questions / Comments / TODOs

TODOS: Search the document for "TODO"
1. Needs CODAC interface

# Introduction

## Purpose

This document outlines the Instrumentation and Controls ("I&C") design for the Transmission Monitoring subsystem ("transmission monitoring system"). The objective of the document is to define the system architecture, the main components related to I&C, the associated alarms and faults, the supervising Control Data Access and Communication ("CODAC") signal interface, and present important software functionality.

## Transmission Monitoring Subsystem Overview

Part of the calibration strategy for the UWAVS 55.GA ("UWAVS System") is a Transmission Monitoring subsystem. The transmission monitoring system provides periodic measurements of the UWAVS system's optical and infrared transmission measurement to account for any degradation of the optical system (in particular the first mirrors). This is accomplished with a hot filament source, mounted on the back of the shutter, within the bullnose. This filament creates a known radiation source for both visible and infrared channels. 

The I&C aspects of the transmission monitoring system relate to controlling the temperature of the filament by controlling the electrical power delivered to the filament. The filament temperature is not measured directly. The filament will be characterized, and a relationship between temperature and resistance and/or power will be established. This characterization can be used to determine target power given a target temperature. By measuring the voltage across the filament and the current going through the filament, the resistance of the filament and the power being dissipated by the filament can be calculated. These values can be used to infer a temperature of the filament.

The primary components related to the I&C design of the transmission monitoring system are:
* The filament assembly mounted on the back of the shutter, in the bullnose. 
* A variable transformer
* A stepper motor driving (moving) the variable transformer
* A step-down transformer
* A source voltage signal transducer
* A filament voltage signal transducer
* A current signal transducer
* A power contactor used to isolate the filament from the power source
* Circuit protection circuit breakers

The stepper motor controlled variable transformer provides a means of delivering variable power to the filament. The stepdown transformer is used to decrease the voltage but increase the current for a given power setting. The source voltage transducer and contactor provide a means of isolating the filament and ensuring a slow and controlled application of voltage and current when the filament is being energized. The current signal transducer and filament voltage transducer provide a means of calculating filament power, and thereby determining filament temperature. Additionally, these devices can be used to ensure voltage and current maximums are never exceeded.

## Special Design Considerations

Being on the back of the back of the shutter, the filament is in an area that is exposed to neutron, gamma, and electromagnetic radiation. To prevent the associated electronics and I&C components from being subjected to this radiation, the I&C components are located in cubicles in the Diagnostics Hall.

The original target temperature range for the filament was between approximately 800-1500 ºC, and power was expected to be approximately 200 watts or under. To extend the operational life of the filament, the maximum target temperature was reduced to 1200 ºC. Testing and characterization of prototype and first article filament units shows that resistance at 1200 ºC is approximately 0.4 Ω. Furthermore, the recommended maximum current is approximately 20 amps, and maximum voltage is approximately 10 volts or less.

With most of the transmission monitoring components in the Diagnostic Hall, the distance between these components and the filament must be taken into account when sizing electrical components. Cable distances to the filaments vary with the port location and routing. For the purposes of estimating line ohmic losses of the power leads and connections, a range of cable distances between 50-200 meters was assumed, using 12 AWG cable. This is likely a worst case calculation, as the majority of installed cable is expected to be 10 AWG, with short lengths of smaller 12-16 AWG diameter cable used. 

Variable power control is achieved using a variable transformer and a stepper motor to control the transformer voltage output. This design choice was made over using solid-state relays ("SSR") or silicon controlled rectifiers ("SCR") for power control. The decision to use a variable transformer is based on a desire to minimize electrical noise, harmonics, and possibly non-sinusoidal wave-forms associated with solid-state controllers, and to maximize the chance of clean power with slow controlled changes in power.

If a variable transformer is problematic for some reason, a zero-cross time-proportioning SCR may be a suitable alternate. Such a device reduces much of the noise and harmonics associated with other types of solid-state control. Investigation would be needed, as these sometimes are not meant for inductive loads, so placing it before the step-down transformer may not be ideal. Furthermore, they may require higher voltages than present after the step-down transformer, so after the step-down transformer may not be an option.

# System Architecture

## Power Circuit Component Selection

TODO: Need a circuit Drawing

Facility power supplied for this sub-system is 240 VAC, Single phase, 50 Hz. 

The first component is a 10 amp circuit breaker with a "D" trip curve which is feeding the primary size of the variable transformer. The trip curve is rated to handle the inrush tha may occur when energizing the transformer without a nuisance trip. This circuit breaker acts as a protection device and a disconnection means. Our expected current is nominally 4 amps max, and for small inductive loads like this, it is not uncommon to size a primary breaker to 150% - 200% nominal. 10 amps is rounded up to a common size, but any size between about 6 amps - 10 amps would be suitable.

The variable transformer is designed for a 240 VAC 50/60 Hz primary voltage, and a variable 0-240 VAC secondary voltage, with a rated current of 9.5 Amps. The variable transformer has a efficiency of 95% - 98%, at full voltage. At lower voltages, the it becomes less efficient, but the current is lower, so this tends to offset the lower efficiency. For the purposes of calculating power given off into the environment from the transformer, assuming 5% loss, at our full operational current of 4 amps, loss to the environment would be about 48 watts.

The secondary of the variable transformer feeds the primary side of a step-down transformer that is designed with a 120/240 VAC 50/60 Hz primary, and a 48 VAC secondary rated at 20A continuous. Once again, efficiency is expected to be about 95%, so loss to the environment under full load is expected to be about 48 watts.

On the secondary side of the step-down transformer is a 25 amp circuit breaker with a "C" trip curve. This breaker will see a smaller inductive load than the main breaker, and be subject to less inrush current, and thus has a "lower" trip curve. It is sized at 125% of the expected load, which is typical for this application. 

After the circuit breaker is the point at which a voltage transducer for the filament supply voltage ("Vs") is fitted. This transducer will provide an RMS DC output signal to the slow-controller PLC. This transducer is deliberately on the filament side of the step-down transformer, and after the breaker such that any upstream interruption can be detected. Its use in the control scheme will be described below.

After the Vs voltage transducer, a contactor is fitted. This contactor is rated to make or break full load current, and is controlled by the PLC with a 24 VDC control voltage. Its purpose is to ensure the filament is isolated until voltage control is established and help ensure the filament is never subject to a large initial current.

After the contactor, a current transducer is fitted in series with one of the power leads to going to the filament. It will measure the supply current ("Cs"). It is a shunt based current sensor to minimize the effects of magnetic field interference that be an issue with a hall-effect based sensor for example. The shut based sensor provides an small AC voltage output signal that is proportional to the current flowing through the sensor. This AC signal is fed into signal converter which will provide an RMS DC output signal to the slow-controller PLC. Its use in the control scheme will be described below.

Lastly, there is an additional voltage transducer wired to measure the voltage at the filament ("Vf"). The transducer has long leads that leave the Diagnostic Hall and connect as close to the filament as is practical. The transducer has a high input impedance, so current flow through these voltage sensing wires is very low, and the wires can be small gauge, and run long distances with very little loss. One thing to note about the run, however, is that the cable should be shielded, and steps to minimize interference need to be taken. The transducer will provide an RMS DC output signal to the slow-controller PLC. Its use in the control scheme will be described below.

Vs and Cs allow calculation of the power being supplied by the power system. The power lead resistance is significant, and in fact larger than the filament resistance, so relying on Vs to calculate filament power and resistance would be inaccurate. The existence of Vf and its use with Cs allow filament power ("Pf") and resistance ("Rf") to be calculated. This gives a much better measurement of filament power and resistance and therefore temperature.
 
The equipment above is all situated in cubicles in the Diagnostic Hall. Leaving the diagnostic hall are the power leads and voltage sense leads for Vf. These wires are routed and go through a series of connections leading to and terminating at the filament. 

## Electrical Characteristics

TODO: Could benefit for more precise lengths and gauge calculations. 

### Filament Resistance

Testing of a single filament generally indicates that filament resistance varies between approximately 0.3 Ω at 900 ºC and approximately 0.4 Ω at 1200 ºC. ** TODO: Reference Walt's testing or a particular test?** The test results show the approximate current and power needed to achieve the range of temperatures needed, and the resulting resistance.

| Temp | Power | Current | Filament |
| ºC   | (W)   | (A)     | Res. (Ω) |
| ---- | ----- | ------- | -------- |
| 900  | 51    | 12.9    | 0.31     |
| 1000 | 71    | 14.4    | 0.34     |
| 1100 | 96    | 16.1    | 0.37     |
| 1200 | 126   | 17.9    | 0.39     |

### Initial Estimate Power Line Loss Calculations

This will show how the secondary voltage of the step-down transformer was selected. The below are initial calculations used to size the above components, with the primary goal of figuring out the minimum value for the step-down transformer secondary voltage when driving maximum current, while adhering to the filament maximum operational voltage and current. To get the highest expected value needed for Vs, the calculations use 20 A to represent full current, and a filament resistance of 0.4 Ω.

For the purposes of sizing the step-down transformer, the maximum value below of ~32 volts was rounded up to 48 volts, as this secondary voltage is available as a standard option for some step-down transformers. 48 volts and 20 amps also gives a 960 VA, informing us that a 240 volt primary, 48 volt secondary, 1000 VA transformer is what is needed for a step-down transformer. 

** Assumptions **
1. Assume 20 A full current.
2. Assume 12 AWG power cables throughout. Assume a nominal resistance of 1.6 Ω / 1000 feet or 0.525 Ω / 100 meters.
3. Assume a total connection resistance of 0.25 Ω. This value is a rough estimate represents an aggregation of all the connection resistances.
4. Assume cable run distances for the different ports as shown below. **TODO: Source of estimated lengths. Can we call out a doc or source?**
5. Assume 5 meters to account for the distance between the EFT and the filament.
6. Assume filament resistance varies between approximately 0.3 Ω at 900 ºC and approximately 0.4 Ω at 1200 ºC. For the below calculations, use 0.4 Ω, as this will help illustrate a minimum Vs value.

| Port | Cable    | Connection | Cable    | Total    | Vcable | Vf (V)   | Vs (V)        |
|      | Dist (m) | Res. (Ω)   | Res. (Ω) | Res. (Ω) | (V)    | (0.40 Ω) | (Vcable + Vf) |
| ---- | -------- | ---------- | -------- | -------- | ------ | -------- | ------------- |
| AO   | 117      | 0.25       | 0.614    | 0.864    | 17.28  | 8.0      | 25.28         |
| BO   | 173      | 0.25       | 0.908    | 1.158    | 23.16  | 8.0      | 31.16         |
| CO   | 137      | 0.25       | 0.719    | 0.969    | 19.38  | 8.0      | 27.38         |
| DO   | 181      | 0.25       | 0.950    | 1.200    | 24.00  | 8.0      | 32.0          |


# Filament Temperature Control Scheme

The temperature of the filament is not measured directly. The temperature of the filament is controlled by controlling the amount of power dissipated by the filament. The power will be controlled by controlling (varying) the voltage across the filament. For a given temperature, the resistance is fixed, and thus the temperature can be inferred by knowing the voltage and current, which are both measured.

The power to the filament will be handed in two "phases": 1) Establising current, and 2) Temeperature control. These are detailed below.

**
TODO: How do we handle changes in resistance v temperature characterization of the filament over time?
Is it expected to change as the filament ages?
Are there periodic opportunities to calibrate with a calibrated IR gun for example?
Are there values that are early warning signs of failure, end-of-life?
**

## Soft Start -- Establishing Current

The filament power circuit has a contactor installed in the Diagnostic Hall, after the transducer measuring Vs. The initial position of this contactor is open, and this contactor shall be open whenever power is not being called for. When power is needed, the following soft-start sequence is run, closing the contactor, and initiating current flow through the filament. A cold filament will have low resistance, and if power is applied suddenly, the filament initially sees a high current flow, before filament heating establishes a higher than initial filament resistance. This sudden application of power (current) shortens the life of the filament, and is typically a reason for "burn-out". The soft-start sequence eliminates the sudden application of power.

The contactor allows the system to ensure the filament is not being connected while a voltage is being applied, and it also allows the system to verify voltage control before connecting the contactor.

Note a full (stop-to-stop) traversal of the variable transformer is dependent on how quickly we run the stepper motor, but it may only take a few seconds. It is expected that Steps 1-4 will be performed quickly, and should only take a few seconds to complete.

**TODO: Any problem with getting limit switches on the variable transformer?**

When initiating operation of the filament, the following sequence is used to establish an initial current:

1. Open the contactor if needed. Should already be open.
2. Adjust variable transformer to minimum voltage.
3. Confirm Vs and variable transformer operation:
	3a. Measure minimum voltage at variable transformer minimum voltage position.
	3b. Go to 20 volt position and verify expected Vs measurement. 20 volts is chosen here as it is approximately what will be needed for a minimum operational temperature.
	3c. Go to 35 volt position and verify expected Vs measurement. 35 volts is chosen here as it is approximately what will be needed for a maximum operational temperature.
	3d. Once the above is confirmed, go to a minimum voltage, and confirm Vs measurement. 
4. Close the contactor.
5. Establish initial current flow:
	5a. Ramp variable transformer to the initial voltage "Vinitial". The ramp rate is chosen to slowly increase current going through the module, and Vinitial is chosen to be low enough to limit current, but high enough to provide filament heating and measurement of meaningful voltages and currents from Vs, Vf, and Cs.
	5b. While ramping voltage to Vinitial, measure Vs, Vf, and Cs. Calculate Filament Resistance Rf and Supply Power Ps, and make sure values are within tolerance.
	5c. While at Vinitial, calculate Filament Resistance Rf, wait for it to stabilize, and make sure it is within tolerance.
	5d. Once filament resistance is stable at an initial value, a current has safely been established in the filaments, and temperature control can begin.

## Temperature Control

The temperature of the filament is controlled by controlling the amount of power applied to the filament. The filament is characterized, as shown in the table above, and the relationship between filament power and temperature is known. 

When a filament temperature is called for, the above sequence is used to establish an initial current. After that sequence in complete, then temperature control can begin. The following implementation is planned for temperature control:

1. Given a target temperature, use a lookup table to determine the corresponding power level. This lookup will interpolate between known points so that control to intermediate temperatures can be achieved.

2. Supply current "Cs" and Filament voltage "Vf" are constantly being measured. Use these values to calculate measured filament power,"Pf".

3. Use a Proportional-Integral-Derivitive ("PID") feedback control loop to indirectly control temperature by controlling power. The target power is the set-point ("SP"), the calculated power is the process-variable ("PV"), and the variable transformer position or voltage is the controlled-variable ("CV"). Modulate the variable transformer position to achieve the desired power and therefore temperature. 

The PID loop should be tuned using relatively low motor speeds to avoid rapid changes in power, and should dampened to avoid overshooting. A deadband on the error and/or integral term may be desirable to avoid constant fluctuations around the SP when errors are small.

In theory resistance could be used for the lookup and the calculated PV value, but it is more prone to inaccuracy. Like power, it is a calculated value from Vf and Cs, but because resistance does not change as much as power does across the operating temperature range, a small measurement error in either measurement would translate into a larger error in the corresponding temperature.

4. While running above a threshold current, the line resistance ("Rline") can be calculated by comparing the supply voltage ("Vs") and Vf. Similarly, the filament resistance can be calculated using Vf and Cs. Both these values can be trigger warnings or alarms if they are not as expected.

5. Changes to the target temperature trigger a new power to be looked up, and thus a new SP. 

6. When filament power is to be shutoff, the current is ramped down by reducing the variable voltage. Once current is near zero, the contactor is opened. 
**TODO: Any reason not to ramp down? I.e. Any reason to step change to off for current?**

## Faults and Alarms

An *"Alarm"* is a condition that alerts an operator of an abnormal or deteriorated condition, and which limits operation, and generally requires intervention.
A *"Warning"* is a condition that alerts an operator of an abnormal or deteriorated condition, but which may not limit operation, or have only a minor impact on operation, and requires little or no intervention.

| Fault Type | Description                  | Possible Cause                   | System Response                | Error Recovery                     |
|------------|------------------------------|----------------------------------|--------------------------------|------------------------------------|
| Alarm      | Vs Not as expected, Vmin     | * Sensor or wiring problem       | * Annunciate alarm             | * Fix sesor or wiring              |
|            |                              | * Supply voltage problem or      | * Hold/Pause current init seq. | * Fix channel configuration        |
|            |                              | CB open                          |                                | * Inspect/test variable            |
|            |                              | * Variable transformer           |                                | transformer voltage control        |
|            |                              | positon control                  |                                |                                    |
|------------|------------------------------|----------------------------------|--------------------------------|------------------------------------|
| Alarm      | Vs Not as expected, 20 volts | * Sensor or wiring problem       | * Annunciate alarm             | * Fix sesor or wiring              |
|            |                              | * Supply voltage problem or      | * Hold/Pause current init seq. | * Fix channel configuration        |
|            |                              | CB open                          |                                | * Inspect/test variable            |
|            |                              | * Variable transformer           |                                | transformer voltage control        |
|            |                              | positon control                  |                                |                                    |
|------------|------------------------------|----------------------------------|--------------------------------|------------------------------------|
| Alarm      | Vs Not as expected, 35 volts | * Sensor or wiring problem       | * Annunciate alarm             | * Fix sesor or wiring              |
|            |                              | * Supply voltage problem or      | * Hold/Pause current init seq. | * Fix channel configuration        |
|            |                              | CB open                          |                                | * Test variable transformer        |
|            |                              | * Variable transformer           |                                | voltage control                    |
|            |                              | positon control                  |                                |                                    |
|------------|------------------------------|----------------------------------|--------------------------------|------------------------------------|
| Alarm      | Cs low, Vinitial             | * Sensor or wiring problem       | * Annunciate alarm             | * Fix sensor or wiring             |
|            |                              | * Open/nearly open power circuit | * Hold/Pause current init seq. | * Fix power circuit connections    |
|            |                              | or filament                      |                                | * Fix filament high impedance      |
|            |                              | * Supply voltage problem or      |                                | * Test variable transformer        |
|            |                              | CB open                          |                                | voltage control                    |
|            |                              | * Variable transfomer            |                                | * Observe Vs and Vf to assist      |
|            |                              | position control                 |                                | with isolating the issue.          |
|------------|------------------------------|----------------------------------|--------------------------------|------------------------------------|
| Alarm      | Cs high, Vinitial            | * Sensor or wiring problem       | * Annunciate alarm             | * Fix sensor or wiring             |
|            |                              | * Low impedance power circuit    | * Hold/Pause current init seq. | * Fix power circuit connections    |
|            |                              | or filament                      |                                | * Fix filament low impedance       |
|            |                              | * Variable transfomer            |                                | * Test variable transformer        |
|            |                              | position control                 |                                | voltage control                    |
|            |                              |                                  |                                | * Observe Vs and Vf to assist      |
|            |                              |                                  |                                | with isolating the issue.          |
|------------|------------------------------|----------------------------------|--------------------------------|------------------------------------|
| Alarm      | Vs high, Vinitial            | * Sensor or wiring problem       | * Annunciate alarm             | * Fix sensor or wiring             |
|            |                              | * Supply voltage problem         | * Hold/Pause current init seq. | * Test variable transformer        |
|            |                              | * Variable transfomer            |                                | voltage control                    |
|            |                              | position control                 |                                | * Observe Cs and Vf to assist      |
|            |                              |                                  |                                | with isolating the issue.          |
|------------|------------------------------|----------------------------------|--------------------------------|------------------------------------|
| Alarm      | Vs low, Vinitial             | * Sensor or wiring problem       | * Annunciate alarm             | * Fix sensor or wiring             |
|            |                              | * Supply voltage problem         | * Hold/Pause current init seq. | * Test variable transformer        |
|            |                              | * Variable transfomer            |                                | voltage control                    |
|            |                              | position control                 |                                | * Observe Cs and Vf to assist      |
|            |                              |                                  |                                | with isolating the issue.          |
|------------|------------------------------|----------------------------------|--------------------------------|------------------------------------|
| Warning    | Rf high, Vinitial            | * Sensor or wiring problem       | * Annunciate warning           | * Fix sensor or wiring             |
|            | (disabled if Vs in alarm)    | * Filament may be out of cal.    |                                | * Test or calibrate/recharacterize |
|            |                              | or near end-of-life              |                                | filament                           |
|            |                              | * Less severe than alarm         |                                | * Observe Cs and Vs to assist      |
|            |                              |                                  |                                | with isolating the issue.          |
|------------|------------------------------|----------------------------------|--------------------------------|------------------------------------|
| Alarm      | Rf high, Vinitial            | * Sensor or wiring problem       | * Annunciate alarm             | * Fix sensor or wiring             |
|            | (disabled if Vs in alarm)    | * Filament may be out of cal.    | * Hold/Pause current init seq. | * Test or calibrate/recharacterize |
|            |                              | or near end-of-life              |                                | filament                           |
|            |                              |                                  |                                | * Observe Cs and Vs to assist      |
|            |                              |                                  |                                | with isolating the issue.          |
|------------|------------------------------|----------------------------------|--------------------------------|------------------------------------|
| Warning    | Rf low, Vinitial             | * Sensor or wiring problem       | * Annunciate warning           | * Fix sensor or wiring             |
|            | (disabled if Vs in alarm)    | * Filament may be out of cal.    |                                | * Test or calibrate/recharacterize |
|            |                              | or near end-of-life              |                                | filament                           |
|            |                              | * Less severe than alarm         |                                | * Observe Cs and Vs to assist      |
|            |                              |                                  |                                | with isolating the issue.          |
|------------|------------------------------|----------------------------------|--------------------------------|------------------------------------|
| Alarm      | Rf low, Vinitial             | * Sensor or wiring problem       | * Annunciate alarm             | * Fix sensor or wiring             |
|            | (disabled if Vs in alarm)    | * Filament may be out of cal.    | * Hold/Pause current init seq. | * Test or calibrate/recharacterize |
|            |                              | or near end-of-life              |                                | filament                           |
|            |                              |                                  |                                | * Observe Cs and Vs to assist      |
|            |                              |                                  |                                | with isolating the issue.          |
|------------|------------------------------|----------------------------------|--------------------------------|------------------------------------|
| Warning    | Vs not as expected           | * Sensor or wiring problem       | * Annunciate warning           | * Fix sensor or wiring             |
|            |                              | * Supply voltage problem         |                                | * Test variable transformer        |
|            | Vs mismatch with transformer | * Variable transfomer            |                                | voltage control                    |
|            | position                     | position control                 |                                | * Observe Cs and Vf to assist      |
|            |                              | * Less severe than alarm         |                                | with isolating the issue.          |
|------------|------------------------------|----------------------------------|--------------------------------|------------------------------------|
| Alarm      | Vs not as expected           | * Sensor or wiring problem       | * Annunciate alarm             | * Fix sensor or wiring             |
|            |                              | * Supply voltage problem         | ** TODO: Go to Vinitial??**    | * Test variable transformer        |
|            | Vs mismatch with transformer | * Variable transfomer            |                                | voltage control                    |
|            | position                     | position control                 |                                | * Observe Cs and Vf to assist      |
|            |                              |                                  |                                | with isolating the issue.          |
|------------|------------------------------|----------------------------------|--------------------------------|------------------------------------|
| Warning    | Rline not as expected        | * Sensor or wiring problem       | * Annunciate warning           | * Fix sensor or wiring             |
|            | (disabled if Vs in           | * Less severe than alarm         |                                | * Check connections                |
|            | warning or alarm)            |                                  |                                | * Observe Cs, Vs, and Vf to        |
|            |                              |                                  |                                | assist with isolating the issue.   |
|------------|------------------------------|----------------------------------|--------------------------------|------------------------------------|
| Alarm      | Rline not as expected        | * Sensor or wiring problem       | * Annunciate alarm             | * Fix sensor or wiring             |
|            | (disabled if Vs in           |                                  | ** TODO: Go to Vinitial??**    | * Check connections                |
|            | warning or alarm)            |                                  |                                | * Observe Cs, Vs, and Vf to        |
|            |                              |                                  |                                | assist with isolating the issue.   |
|------------|------------------------------|----------------------------------|--------------------------------|------------------------------------|
| Warning    | Rf not as expected           | * Sensor or wiring problem       | * Annunciate warning           | * Fix sensor or wiring             |
|            | (disabled if Vs in           | * Filament may be out of cal.    |                                | * Check connections                |
|            | warning or alarm)            | or near end-of-life              |                                | * Observe Cs, Vs, and Vf to        |
|            |                              | * Less severe than alarm         |                                | assist with isolating the issue.   |
|------------|------------------------------|----------------------------------|--------------------------------|------------------------------------|
| Alarm      | Rf not as expected           | * Sensor or wiring problem       | * Annunciate alarm             | * Fix sensor or wiring             |
|            | (disabled if Vs in           | * Filament may be out of cal.    | ** TODO: Go to Vinitial??**    | * Check connections                |
|            | warning or alarm)            | or near end-of-life              |                                | * Observe Cs, Vs, and Vf to        |
|            |                              |                                  |                                | assist with isolating the issue.   |
|------------|------------------------------|----------------------------------|--------------------------------|------------------------------------|
| Warning    | Cs high                      | * Cs near maximum value          | * Annunciate warning           | * High power or temperature target |
|            |                              | * Sensor or wiring problem       |                                | * Fix sensor or wiring             |
|            |                              | * Filament may be out of cal.    |                                | * Check connections                |
|            |                              | or near end-of-life              |                                | * Observe Cs, Vs, and Vf to        |
|            |                              | * Some margin to maximum current |                                | assist with isolating the issue.   |
|------------|------------------------------|----------------------------------|--------------------------------|------------------------------------|
| Alarm      | Cs high                      | * Cs at maximum value            | * Annunciate alarm             | * High power or temperature target |
|            |                              | * Sensor or wiring problem       | * Limit current to maximum     | * Fix sensor or wiring             |
|            |                              | * Filament may be out of cal.    |                                | * Check connections                |
|            |                              | or near end-of-life              |                                | * Observe Cs, Vs, and Vf to        |
|            |                              |                                  |                                | assist with isolating the issue.   |
|------------|------------------------------|----------------------------------|--------------------------------|------------------------------------|

## CODAC Interface

** TODO **
        
# Hardware

** TODO: More specific location than "Diagnostic Hall"? **

** TODO: Fill in missing Siemens p/ns. **

| Description                  | Location        | Mfr                 | Part Number              | Qty | Notes                                       |
|------------------------------|-----------------|---------------------|--------------------------|-----|---------------------------------------------|
| Circuit Breaker, Main        | Diagnostic Hall | Allen-Bradley       | 1489-M2D100              | 1   |                                             |
| 10A, Trip Curve D            |                 |                     |                          |     |                                             |
|------------------------------|-----------------|---------------------|--------------------------|-----|---------------------------------------------|
| Transformer, Variable        | Diagnostic Hall | Staco               | Variac 30M1520           | 1   | Mfg motor to be replaced with stepper motor |
| 240 VAC 50/60 Hz Primary     |                 |                     |                          |     |                                             |
| 0-240 VAC secondary 2280 VA  |                 |                     |                          |     |                                             |
|                              |                 |                     |                          |     |                                             |
|------------------------------|-----------------|---------------------|--------------------------|-----|---------------------------------------------|
| Transformer, Step Down       | Diagnostic Hall | Pacific Transformer | 46797                    | 1   |                                             |
| 110/240 VAC 50/60 Hz Primary |                 |                     |                          |     |                                             |
| 48 VAC secondary 1000 VA     |                 |                     |                          |     |                                             |
|------------------------------|-----------------|---------------------|--------------------------|-----|---------------------------------------------|
| Transducer, Voltage          | Diagnostic Hall | Verivolt            | ISOFLEX-V(LR)            | 1   | AC Input, DC RMS Output                     |
| Supply Votage "Vs"           |                 |                     | 50V Input, 4-20ma Output |     | to DC RMS value for PLC.                    |
| 0-50 VAC In, 4-20mA Output   |                 |                     |                          |     |                                             |
|------------------------------|-----------------|---------------------|--------------------------|-----|---------------------------------------------|
| Circuit Breaker, Load        | Diagnostic Hall | Allen-Bradley       | 1489-M2C250              | 1   |                                             |
| 25A, Trip Curve C            |                 |                     |                          |     |                                             |
|------------------------------|-----------------|---------------------|--------------------------|-----|---------------------------------------------|
| Contactor, Load              | Diagnostic Hall | Allen-Bradley       | 100-E26KJ00              | 1   |                                             |
| 26A, 24 VDC electronic coil  |                 |                     |                          |     |                                             |
|------------------------------|-----------------|---------------------|--------------------------|-----|---------------------------------------------|
| Transducer, Current          | Diagnostic Hall | Verivolt            | ISOBLOCK I-ST-C          | 1   | Shunt based current sensor                  |
| Supply Current "Cs"          |                 |                     | (30A, 10V, 0.1%)         |     | AC Current Input, AC Voltage Output         |
| 0-30A AC In, 0-10V AC Out    |                 |                     |                          | 1   |                                             |
|------------------------------|-----------------|---------------------|--------------------------|-----|---------------------------------------------|
| Transducer, Voltage          | Diagnostic Hall | Verivolt            | ISOFLEX-V(LR)            | 1   | AC Input, DC RMS Output                     |
| Supply Current "Cs"          |                 |                     | 10V Input, 4-20ma Output |     | Converts current sensor AC output           |
| 0-10 VAC In, 4-20mA Output   |                 |                     |                          |     | to DC RMS value for PLC.                    |
|------------------------------|-----------------|---------------------|--------------------------|-----|---------------------------------------------|
| Transducer, Voltage          | Diagnostic Hall | Verivolt            | ISOFLEX-V(LR)            | 1   | AC Input, DC RMS Output                     |
| Filament Votage "Vf"         |                 |                     | 10V Input, 4-20ma Output |     | to DC RMS value for PLC.                    |
| 0-10 VAC In, 4-20mA Output   |                 |                     |                          |     |                                             |
|------------------------------|-----------------|---------------------|--------------------------|-----|---------------------------------------------|
| Stepper Motor Drive Module   | Diagnostic Hall | Phytron             | TM StepDrive             | 1   | 1x24..48V/5A                                |
|------------------------------|-----------------|---------------------|--------------------------|-----|---------------------------------------------|
| Base Unit and terminal block | Diagnostic Hall | Siemens             | 6ES7193-6BP20-0BB1       | 1   | Base unit for motor drive                   |
|------------------------------|-----------------|---------------------|--------------------------|-----|---------------------------------------------|
| Module, PLC, Analog Input    | Diagnostic Hall | Siemens             | ?                        | 1   | Need 3 channels for Vs, Cs, and Vf          |
|------------------------------|-----------------|---------------------|--------------------------|-----|---------------------------------------------|
| Module, PLC, Digital Input   | Diagnostic Hall | Siemens             | 6ES7131-6BF00-0DA0       | 1   | Need 2 channels for varialbe                |
|                              |                 |                     |                          | 1   | Need 2 channels for varialbe                |
|------------------------------|-----------------|---------------------|--------------------------|-----|---------------------------------------------|
| Module, PLC, Digital Output  | Diagnostic Hall | Siemens             | ?                        | 1   | Need 1 channel for contactor control        |
|------------------------------|-----------------|---------------------|--------------------------|-----|---------------------------------------------|

