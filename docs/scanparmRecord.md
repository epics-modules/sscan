---
layout: default
title: Scanparm Record
nav_order: 5
---


Scanparm Record and Related Software
====================================

Tim Mooney

- - - - - -

Contents
--------

- [Overview](#Overview)
- [Field Descriptions](#Fields)
- [Files](#Files)
- [Restrictions](#Restrictions)

Overview
--------

This documentation describes the EPICS scanparm record, and related EPICS software required to build and use it. This version of the record is compatible with EPICS 3.14.8.2, and is incompatible with any 3.13.x version of EPICS.

The scanparm record stores parameters intended to be written to the EPICS sscan record, and provides the EPICS end user with a convenient way to load those parameters into the sscan record and cause the sscan record to perform a scan. The idea is to allow the user to configure and execute a predefined scan with a single mouse click.

> By the way, the word *scan*, in EPICS, normally refers to the execution of a record, and particularly to the method by which a record is selected for execution. In this documentation, *scan* will never have that meaning. Here, a *scan* is what the sscan record does:
> 
> - send a positioner to some position, and wait for it to arrive
> - trigger a detector, and wait for it to finish acquiring
> - read and store data from the positioner and detector
> - repeat
> 
> For more about scans, see the sscan record documentation.

In the simplest and most common use, a scanparm record is associated at boot time with a particular positioner (e.g., a motor) and targeted to configure and run a particular sscan record. At run time, the user typically will write start and end positions, and the number of data points to be acquired, to a scanparm record, and from then on can run that scan with a single write to the scanparm record. It is possible to have more than one scanparm record associated with a positioner, and it is possible to gang scanparm records together into a database that stores parameters for scans involving more than one positioner, and more than one sscan record.

The scanparm record contains sets of paired fields for parameters it writes, for parameters it reads, and for commands it receives from the user and may forward to another record. 



Field Descriptions
------------------

In addition to fields common to all record types (see the EPICS Record Reference Manual for these) the scanparm record has the fields described below.

- [Alphabetical listing of record-specific fields](#Fields_alphabetical)
- [Fields involved in sending information out](#Fields_write)
- [Fields involved in collecting information](#Fields_read)
- [Fields involved in managing execution](#Fields_command)
- [Miscellaneous fields](#Fields_misc)
- [Private fields](#Fields_private)

- - - - - -

<a name="Fields_alphabetical"></a>

| Name | Type | DCT prompt | Access | DCT |
|---|---|---|---|---|
| [ ACT ](#Fields_read) | DBF\_SHORT | ScanActive | R | No |
| [ AFT ](#Fields_write) | DBF\_MENU(sscanPASM) | After | R/W | Yes |
| [ AR ](#Fields_write) | DBF\_MENU(sscanP1AR) | absRel | R/W | Yes |
| [ AQT ](#Fields_write) | DBF\_DOUBLE | Acquire time | R/W\* | Yes |
| [ DPV ](#Fields_write) | DBF\_STRING | DetPVName | R/W | Yes |
| [ EP ](#Fields_write) | DBF\_DOUBLE | EndPos | R/W\* | Yes |
| [ GO ](#Fields_command) | DBF\_SHORT | Go | R/W\* | Yes |
| [ IACT ](#Fields_read) | DBF\_INLINK | InLink | R | Yes |
| [ IMP ](#Fields_read) | DBF\_INLINK | MP InLink | R | Yes |
| [ LOAD ](#Fields_command) | DBF\_SHORT | Load | R/W\* | Yes |
| [ LSTP ](#Fields_misc) | DBF\_DOUBLE | Last stepSize | R | No |
| [ MP ](#Fields_read) | DBF\_LONG | MaxPts | R | No |
| [ NP ](#Fields_write) | DBF\_LONG | nPts | R/W\* | Yes |
| [ OAFT ](#Fields_write) | DBF\_OUTLINK | AFT OutLink | R | Yes |
| [ OAQT ](#Fields_write) | DBF\_OUTLINK | AQT OutLink | R | Yes |
| [ OAR ](#Fields_write) | DBF\_OUTLINK | AR OutLink | R | Yes |
| [ ODPV ](#Fields_write) | DBF\_OUTLINK | D1PV OutLink | R | Yes |
| [ OEP ](#Fields_write) | DBF\_OUTLINK | EP OutLink | R | Yes |
| [ OGO ](#Fields_command) | DBF\_OUTLINK | GO OutLink | R | Yes |
| [ OLOAD ](#Fields_command) | DBF\_OUTLINK | LOAD OutLink | R | Yes |
| [ ONP ](#Fields_write) | DBF\_OUTLINK | NP OutLink | R | Yes |
| [ OPPV ](#Fields_write) | DBF\_OUTLINK | P1PV OutLink | R | Yes |
| [ OPRE ](#Fields_write) | DBF\_OUTLINK | PRE-write OutLink | R | Yes |
| [ ORPV ](#Fields_write) | DBF\_OUTLINK | R1PV OutLink | R | Yes |
| [ OSC ](#Fields_write) | DBF\_OUTLINK | SC OutLink | R | Yes |
| [ OSM ](#Fields_write) | DBF\_OUTLINK | SM OutLink | R | Yes |
| [ OSP ](#Fields_write) | DBF\_OUTLINK | SP OutLink | R | Yes |
| [ OTPV ](#Fields_write) | DBF\_OUTLINK | T1PV OutLink | R | Yes |
| [ PPV ](#Fields_write) | DBF\_STRING | PositionerPVName | R/W | Yes |
| [ PRE ](#Fields_write) | DBF\_SHORT | PRE-write command | R/W\* | Yes |
| [ PREC ](#Fields_misc) | DBF\_SHORT | Display Precision | R/W | Yes |
| [ RPV ](#Fields_write) | DBF\_STRING | ReadbackPVName | R/W | Yes |
| [ SC ](#Fields_write) | DBF\_SHORT | StartCmd | R/W | Yes |
| [ SM ](#Fields_write) | DBF\_MENU(sscanP1SM) | StepMode | R/W | Yes |
| [ SP ](#Fields_write) | DBF\_DOUBLE | StartPos | R/W\* | Yes |
| [ STEP ](#Fields_misc) | DBF\_DOUBLE | StepSize | R | No |
| [ TPV ](#Fields_write) | DBF\_STRING | TrigPVName | R/W | Yes |
| [ VAL ](#Fields_misc) | DBF\_DOUBLE | Result | R | No |
| [ VERS ](#Fields_misc) | DBF\_FLOAT | Code Version | R | No |

NOTE: Hot links in this table take you only to the *section* in which the linked item is described in detail. You'll probably have to scroll down to find the actual item.  

Note: In the __Access__ column above:
* R \| Read only \|  
* R/W \| Read and write are allowed \| 
* N \| No access allowed \|

a channel-access write triggers record processing if the record's SCAN field is set to "Passive." 


- - - - - -

<a name="Fields_write"></a>

### Fields involved in sending information out

| Value Field | Type | Output Link | Typical Target Field | Purpose |
|---|---|---|---|---|
| PRE | DBF\_SHORT | OPRE | <sscan>.CMND | clear old positioner configuration |
| SM | DBF\_MENU(sscanP1SM) | OSM | <sscan>.P1SM | positioner scan mode (e.g., linear, table, fly) |
| AR | DBF\_MENU(sscanP1AR) | OAR | <sscan>.P1AR | positioner absolute/relative |
| AFT | DBF\_MENU(sscanPASM) | OAFT | <sscan>.PASM | positioner after-scan mode (e.g., stay, go to start pos,...) |
| PPV | DBF\_STRING | OPPV | <sscan>.P1PV | positioner drive PV name |
| RPV | DBF\_STRING | ORPV | <sscan>.R1PV | positioner readback PV name |
| TPV | DBF\_STRING | OTPV | <sscan>.T1PV | detector-trigger PV name |
| DPV | DBF\_STRING | ODPV | <sscan>.D01PV | detector PV name |
| SP | DBF\_DOUBLE | OSP | <sscan>.P1SP | positioner start point |
| EP | DBF\_DOUBLE | OEP | <sscan>.P1EP | positioner end point |
| NP | DBF\_LONG | ONP | <sscan>.NPTS | number of data points to acquire |
| SC | DBF\_SHORT | OSC | <sscan>.EXSC | start the scan |
| AQT | DBF\_DOUBLE | OAQT | <scaler>.TP | acquire time |

- - - - - -

<a name="Fields_read"></a>

### Fields involved in collecting information

| Input Link | Value Field | Typical Target Field | Purpose |
|---|---|---|---|
| IMP | MP | <sscan>.MPTS | get the maximum permitted number of data points |
| IACT | ACT | <sscan>.BUSY | determine whether the target sscan record is active |

- - - - - -

<a name="Fields_command"></a>

### Fields involved in managing execution.

| Value field | Output Link | Typical Target Field | Purpose |
| LOAD | OLOAD | <scanparm>.LOAD | cause the scanparm record to write parameters to the sscan record. If more than one scanparm record is needed to define a scan (e.g., for a multi-positioner scan, or a multi-dimensional scan), the OLOAD field should link to the next scanparm record. |
| GO | OGO | <scanparm>.GO | Cause the scanparm record to write parameters to the sscan record and also cause the sscan record to begin the scan. If more than one scanparm record is needed to define a scan (e.g., for a multi-positioner scan, or a multi-dimensional scan), the OGO field should link to the next scanparm record, and the last scanparm record to execute should use its OGO link to cause its sscan record to start scanning. |

- - - - - -

Files
-----

The following table briefly describes the files required to implement and use the scanparm record.

### SOURCE CODE 

| scanparmRecord.c | Record support for the scanparm record |
| scanparmRecord.dbd | This file defines all of the fields menus, etc. for the scanparm record. |

### DATABASE and AUTOSAVE-REQUEST FILES

| scanParms.db | database used for one-dimensional, one-positioner scans, when the sscan record and the scanparm record have the same prefix. |
| scanParmsRemote.db | database used for one-dimensional, one-positioner scans, when the sscan record and the scanparm record have different prefixes. |
| scanParms2Pos.db | database used for one-dimensional, two-positioner scans. |
| scanParms2D.db | database used for two-dimensional scans. |

### MEDM DISPLAY FILES

| scanParms.adl |  |
| scanParmsRemote.adl |  |
| scanParmsCustom.adl |  |
| scanParms2Pos.adl |  |
| scanParms2D.adl |  |

These files build `medm` screens to access the scanparm record and related process variables. To use one of them from the command line, type, for example 
```  
medm -x -macro "P=xxx:,Q=m1,PV=m1" scanParms.adl 
medm -x -macro "P=xxx:,Q=yyy:m1,PV=yyy:m1" scanParmsRemote.adl 
medm -x -macro "P=xxx:,Q=m1,EGU=,NAME=,DESC=" scanParmsCustom.adl 
medm -x -macro "P=xxx:,Q=device,PV1=xxx:m1,PV2=xxx:m2,SCAN=yyy:scan1" scanParms2Pos.adl 
medm -x -macro "P=xxx:,Q=device,DESC=,EGU1=,NAME1=,EGU2=,NAME2=" scanParms2D.adl 
```

### EPICS STARTUP FILE

| st.cmd | Startup script |

This file is not included in the distribution. Here are annotated excerpts from a startup file that supports scanparms: 
```
####################################################################### 
# vxWorks startup script to load and execute system (iocCore) software. 
# Tell EPICS all about the record types, device-support modules, drivers, 
# etc. in the software we just loaded (xxxApp) 
dbLoadDatabase("dbd/xxxApp.dbd")  
dbLoadTemplate("scanParms.substitutions")    
```

### AUTOSAVE REQUEST FILE

| scanParms\_Settings.req | sample request file to be included in auto\_settings.req to save the user modifiable settings of one scanParms.db database. To use this, add a line of the following form in auto\_settings.req for each scanParms database: `file scanParms_settings.req P=xxx: M=m1` |

- - - - - -

Restrictions
------------

Suggestions and comments to:   
[Tim Mooney](mailto:mooney@aps.anl.gov) : (mooney@aps.anl.gov)   
Last modified: December 11, 2007
