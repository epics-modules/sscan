---
layout: default
title: Scanparm Record
nav_order: 5
---

# Scanparm Record and Related Software

Original Author: Tim Mooney

## Contents

- [Overview](#overview)
- [Field Descriptions](#field-descriptions)
  - [Alphabetical listing of record-specific fields](#alphabetical-listing-of-record-specific-fields)
  - [Fields involved in sending information out](#fields-involved-in-sending-information-out)
  - [Fields involved in collecting information](#fields-involved-in-collecting-information)
  - [Fields involved in managing execution](#fields-involved-in-managing-execution)
  - [Miscellaneous fields](#miscellaneous-fields)
  - [Private fields](#private-fields)
- [Files](#files)
- [Restrictions](#restrictions)

## Overview

This documentation describes the EPICS scanparm record, and related EPICS software required to build and use it. This version of the record is compatible with EPICS 3.14.8.2 and onward, and is incompatible with any 3.13.x version of EPICS.

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

## Field Descriptions

In addition to fields common to all record types (see the EPICS Record Reference Manual for these) the scanparm record has the fields described below.

- [Alphabetical listing of record-specific fields](#alphabetical-listing-of-record-specific-fields)
- [Fields involved in sending information out](#fields-involved-in-sending-information-out)
- [Fields involved in collecting information](#fields-involved-in-collecting-information)
- [Fields involved in managing execution](#fields-involved-in-managing-execution)
- [Miscellaneous fields](#miscellaneous-fields)
- [Private fields](#private-fields)

### Alphabetical listing of record-specific fields

| Name | Type | DCT prompt | Access | DCT |
|---|---|---|---|---|
| [ACT](#fields-involved-in-collecting-information) | DBF\_SHORT | ScanActive | R | No |
| [AFT](#fields-involved-in-sending-information-out) | DBF\_MENU(sscanPASM) | After | R/W | Yes |
| [AR](#fields-involved-in-sending-information-out) | DBF\_MENU(sscanP1AR) | absRel | R/W | Yes |
| [AQT](#fields-involved-in-sending-information-out) | DBF\_DOUBLE | Acquire time | R/W\* | Yes |
| [DPV](#fields-involved-in-sending-information-out) | DBF\_STRING | DetPVName | R/W | Yes |
| [EP](#fields-involved-in-sending-information-out) | DBF\_DOUBLE | EndPos | R/W\* | Yes |
| [GO](#fields-involved-in-managing-execution) | DBF\_SHORT | Go | R/W\* | Yes |
| [IACT](#fields-involved-in-collecting-information) | DBF\_INLINK | InLink | R | Yes |
| [IMP](#fields-involved-in-collecting-information) | DBF\_INLINK | MP InLink | R | Yes |
| [LOAD](#fields-involved-in-managing-execution) | DBF\_SHORT | Load | R/W\* | Yes |
| [LSTP](#miscellaneous-fields) | DBF\_DOUBLE | Last stepSize | R | No |
| [MP](#fields-involved-in-collecting-information) | DBF\_LONG | MaxPts | R | No |
| [NP](#fields-involved-in-sending-information-out) | DBF\_LONG | nPts | R/W\* | Yes |
| [OAFT](#fields-involved-in-sending-information-out) | DBF\_OUTLINK | AFT OutLink | R | Yes |
| [OAQT](#fields-involved-in-sending-information-out) | DBF\_OUTLINK | AQT OutLink | R | Yes |
| [OAR](#fields-involved-in-sending-information-out) | DBF\_OUTLINK | AR OutLink | R | Yes |
| [ODPV](#fields-involved-in-sending-information-out) | DBF\_OUTLINK | D1PV OutLink | R | Yes |
| [OEP](#fields-involved-in-sending-information-out) | DBF\_OUTLINK | EP OutLink | R | Yes |
| [OGO](#fields-involved-in-managing-execution) | DBF\_OUTLINK | GO OutLink | R | Yes |
| [OLOAD](#fields-involved-in-managing-execution) | DBF\_OUTLINK | LOAD OutLink | R | Yes |
| [ONP](#fields-involved-in-sending-information-out) | DBF\_OUTLINK | NP OutLink | R | Yes |
| [OPPV](#fields-involved-in-sending-information-out) | DBF\_OUTLINK | P1PV OutLink | R | Yes |
| [OPRE](#fields-involved-in-sending-information-out) | DBF\_OUTLINK | PRE-write OutLink | R | Yes |
| [ORPV](#fields-involved-in-sending-information-out) | DBF\_OUTLINK | R1PV OutLink | R | Yes |
| [OSC](#fields-involved-in-sending-information-out) | DBF\_OUTLINK | SC OutLink | R | Yes |
| [OSM](#fields-involved-in-sending-information-out) | DBF\_OUTLINK | SM OutLink | R | Yes |
| [OSP](#fields-involved-in-sending-information-out) | DBF\_OUTLINK | SP OutLink | R | Yes |
| [OTPV](#fields-involved-in-sending-information-out) | DBF\_OUTLINK | T1PV OutLink | R | Yes |
| [PPV](#fields-involved-in-sending-information-out) | DBF\_STRING | PositionerPVName | R/W | Yes |
| [PRE](#fields-involved-in-sending-information-out) | DBF\_SHORT | PRE-write command | R/W\* | Yes |
| [PREC](#miscellaneous-fields) | DBF\_SHORT | Display Precision | R/W | Yes |
| [RPV](#fields-involved-in-sending-information-out) | DBF\_STRING | ReadbackPVName | R/W | Yes |
| [SC](#fields-involved-in-sending-information-out) | DBF\_SHORT | StartCmd | R/W | Yes |
| [SM](#fields-involved-in-sending-information-out) | DBF\_MENU(sscanP1SM) | StepMode | R/W | Yes |
| [SP](#fields-involved-in-sending-information-out) | DBF\_DOUBLE | StartPos | R/W\* | Yes |
| [STEP](#miscellaneous-fields) | DBF\_DOUBLE | StepSize | R | No |
| [TPV](#fields-involved-in-sending-information-out) | DBF\_STRING | TrigPVName | R/W | Yes |
| [VAL](#miscellaneous-fields) | DBF\_DOUBLE | Result | R | No |
| [VERS](#miscellaneous-fields) | DBF\_FLOAT | Code Version | R | No |

NOTE: Links in this table take you only to the *section* in which the linked item is described in detail. You may have to scroll down to find the actual item.

Note: In the __Access__ column above:

| Code | Meaning |
|---|---|
| R | Read only |
| R/W | Read and write are allowed |
| R/W\* | Read and write; a channel-access write triggers record processing if the record's SCAN field is set to "Passive." |
| N | No access allowed |

### Fields involved in sending information out

| Value Field | Type | Output Link | Typical Target Field | Purpose |
|---|---|---|---|---|
| PRE | DBF\_SHORT | OPRE | \<sscan\>.CMND | clear old positioner configuration |
| SM | DBF\_MENU(sscanP1SM) | OSM | \<sscan\>.P1SM | positioner scan mode (e.g., linear, table, fly) |
| AR | DBF\_MENU(sscanP1AR) | OAR | \<sscan\>.P1AR | positioner absolute/relative |
| AFT | DBF\_MENU(sscanPASM) | OAFT | \<sscan\>.PASM | positioner after-scan mode (e.g., stay, go to start pos,...) |
| PPV | DBF\_STRING | OPPV | \<sscan\>.P1PV | positioner drive PV name |
| RPV | DBF\_STRING | ORPV | \<sscan\>.R1PV | positioner readback PV name |
| TPV | DBF\_STRING | OTPV | \<sscan\>.T1PV | detector-trigger PV name |
| DPV | DBF\_STRING | ODPV | \<sscan\>.D01PV | detector PV name |
| SP | DBF\_DOUBLE | OSP | \<sscan\>.P1SP | positioner start point |
| EP | DBF\_DOUBLE | OEP | \<sscan\>.P1EP | positioner end point |
| NP | DBF\_LONG | ONP | \<sscan\>.NPTS | number of data points to acquire |
| SC | DBF\_SHORT | OSC | \<sscan\>.EXSC | start the scan |
| AQT | DBF\_DOUBLE | OAQT | \<scaler\>.TP | acquire time |

### Fields involved in collecting information

| Input Link | Value Field | Typical Target Field | Purpose |
|---|---|---|---|
| IMP | MP | \<sscan\>.MPTS | get the maximum permitted number of data points |
| IACT | ACT | \<sscan\>.BUSY | determine whether the target sscan record is active |

### Fields involved in managing execution

| Value field | Output Link | Typical Target Field | Purpose |
|---|---|---|---|
| LOAD | OLOAD | \<scanparm\>.LOAD | Cause the scanparm record to write parameters to the sscan record. If more than one scanparm record is needed to define a scan (e.g., for a multi-positioner scan, or a multi-dimensional scan), the OLOAD field should link to the next scanparm record. |
| GO | OGO | \<scanparm\>.GO | Cause the scanparm record to write parameters to the sscan record and also cause the sscan record to begin the scan. If more than one scanparm record is needed to define a scan (e.g., for a multi-positioner scan, or a multi-dimensional scan), the OGO field should link to the next scanparm record, and the last scanparm record to execute should use its OGO link to cause its sscan record to start scanning. |

### Miscellaneous fields

| Field | Type | Purpose |
|---|---|---|
| STEP | DBF\_DOUBLE | Step size, calculated from SP, EP, and NP |
| LSTP | DBF\_DOUBLE | Last step size (previous value of STEP) |
| PREC | DBF\_SHORT | Display precision |
| VAL | DBF\_DOUBLE | Result |
| VERS | DBF\_FLOAT | Code version |

### Private fields

| Field | Type | Purpose |
|---|---|---|
| RPVT | DBF\_NOACCESS | Record private |

## Files

The following table briefly describes the files required to implement and use the scanparm record.

### Source Code

| File | Description |
|---|---|
| scanparmRecord.c | Record support for the scanparm record |
| scanparmRecord.dbd | This file defines all of the fields menus, etc. for the scanparm record. |

### Database and Autosave-Request Files

| File | Description |
|---|---|
| scanParms.db | Database used for one-dimensional, one-positioner scans, when the sscan record and the scanparm record have the same prefix. |
| scanParmsRemote.db | Database used for one-dimensional, one-positioner scans, when the sscan record and the scanparm record have different prefixes. |
| scanParms2Pos.db | Database used for one-dimensional, two-positioner scans. |
| scanParms2D.db | Database used for two-dimensional scans. |

### MEDM Display Files

| File | Description |
|---|---|
| scanParms.adl | Single-positioner scan parameters |
| scanParmsRemote.adl | Remote single-positioner scan parameters |
| scanParmsCustom.adl | Custom scan parameters |
| scanParms2Pos.adl | Two-positioner scan parameters |
| scanParms2D.adl | Two-dimensional scan parameters |

These files build `medm` screens to access the scanparm record and related process variables. To use one of them from the command line, type, for example
```
medm -x -macro "P=xxx:,Q=m1,PV=m1" scanParms.adl
medm -x -macro "P=xxx:,Q=yyy:m1,PV=yyy:m1" scanParmsRemote.adl
medm -x -macro "P=xxx:,Q=m1,EGU=,NAME=,DESC=" scanParmsCustom.adl
medm -x -macro "P=xxx:,Q=device,PV1=xxx:m1,PV2=xxx:m2,SCAN=yyy:scan1" scanParms2Pos.adl
medm -x -macro "P=xxx:,Q=device,DESC=,EGU1=,NAME1=,EGU2=,NAME2=" scanParms2D.adl
```

### EPICS Startup File

This file is not included in the distribution. Here are annotated excerpts from a startup file that supports scanparms:
```
#######################################################################
# vxWorks startup script to load and execute system (iocCore) software.
# Tell EPICS all about the record types, device-support modules, drivers,
# etc. in the software we just loaded (xxxApp)
dbLoadDatabase("dbd/xxxApp.dbd")
dbLoadTemplate("scanParms.substitutions")
```

### Autosave Request File

| File | Description |
|---|---|
| scanParms\_Settings.req | Sample request file to be included in auto\_settings.req to save the user modifiable settings of one scanParms.db database. To use this, add a line of the following form in auto\_settings.req for each scanParms database: `file scanParms_settings.req P=xxx: M=m1` |
