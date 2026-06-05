---
layout: default
title: Home
nav_order: 1
---

# The sscan module
{: .no_toc}

## Table of contents
{: .no_toc .text-delta }

- TOC
{:toc}

## Overview

The sscan module provides EPICS support for coordinated step-scanning of motors, detectors, and other process variables. It is part of [synApps](https://epics.anl.gov/bcda/synApps) and is developed by the Beamline Controls & Data Acquisition group at the Advanced Photon Source, Argonne National Laboratory.

The module consists of three main components:

- **[sscan record](sscanRecord.md)** -- A custom EPICS record type that moves positioners through a series of positions, triggers detectors at each position, and collects the resulting data into arrays. A single sscan record executes a one-dimensional scan; multiple sscan records can be chained together for multidimensional scans (up to 4D).
- **[scanparm record](scanparmRecord.md)** -- A convenience record that stores scan parameters (start, end, number of points, positioner PV, etc.) and can load them into an sscan record and start a scan with a single write.
- **[saveData](saveData.md)** -- A data-storage client that monitors sscan records via Channel Access and writes scan data to disk in the [MDA (Multi-Dimensional Archive)](MDAFormat.md) binary file format.

The module depends on [EPICS Base](https://epics-controls.org/) (3.15 or later) and optionally on the [sequencer](https://github.com/ISISComputingGroup/EPICS-seq) (for the scan-progress monitoring feature).

## Additional resources

- [saveData.req](saveData.req) -- Sample saveData configuration file.
- [XDR_RFC1014.txt](XDR_RFC1014.txt) -- XDR (External Data Representation) standard reference.
- [Scans.ppt](Scans.ppt) -- Presentation describing the sscan module, saveData, MDA file format, and EPICS putNotify/ca_put_callback() completion behavior.

## Installation and Building

After obtaining a copy of the distribution, it must be installed and built for use at your site. Usually, these steps only need to be performed once.

1. Clone or download the sscan module source, e.g.:
   ```
   git clone https://github.com/epics-modules/sscan.git
   ```
   Usually this is done in an EPICS 'support' directory.

2. Edit sscan's `configure/RELEASE` file and set the paths to your installation of EPICS base and to your versions of other dependent modules.

3. Run `make` in the top level directory and check for any compilation errors.

## Using sscan in an IOC

The sscan module is not intended to run an IOC application directly, but rather to contribute code libraries, databases, and display files to an IOC application. SynApps contains an example IOC application (the **xxx** module), which pulls software from the sscan module and deploys it in an IOC.

The essential steps in applying sscan-module code in an IOC application ("example") are the following:

1. Include the following line in `example/configure/RELEASE`:
   ```
   SSCAN=<full path to sscan module>
   ```

2. Include the following line in `example/exampleApp/src/Makefile`:
   ```
   example_dbd_file_DBD ++ $(SSCAN_IOC_DBDS)
   example_LIBS += $(SSCAN_IOC_LIBS)
   ```

3. Load the databases by including the following lines in `st.cmd`:
   ```
   dbLoadRecords("$(SSCAN)/sscanApp/Db/standardScans.db","P=xxx:,MAXPTS1=2000,MAXPTS2=1000,MAXPTS3=1000,MAXPTS4=10,MAXPTSH=2000")
   dbLoadRecords("$(SSCAN)/sscanApp/Db/saveData.db","P=xxx:")
   dbLoadRecords("$(SSCAN)/sscanApp/Db/scanProgress.db","P=xxx:scanProgress:")
   ```

   Alternatively, you can use the provided iocsh script:
   ```
   iocshLoad("$(SSCAN)/iocsh/sscan.iocsh", "PREFIX=xxx:,SSCAN=$(SSCAN)")
   ```

4. If you use autosave, include `standardScans_settings.req` and `saveData_settings.req` in your autosave request file:
   ```
   file standardScans_settings.req P=$(P)
   file saveData_settings.req P=$(P)
   ```

5. Configure and initialize saveData. See the [saveData documentation](saveData.md) for details on the configuration file format and initialization.

6. Before running any scans, specify where saveData is to write scan-data files. Bring up the medm display `scan_saveData.adl` and fill in the "File system" and "Subdirectory" fields (i.e., the PVs `$(P)saveData_fileSystem` and `$(P)saveData_subDir`).

Suggestions and Comments to:
[Keenan Lang](mailto:klang@anl.gov) : (klang@anl.gov)
