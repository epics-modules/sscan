---
layout: default
title: Overview
nav_order: 2
---



The sscan module
================

Documentation
-------------

The following documentation is available:

[sscanRecord](sscanRecord.md)

The sscan record documentation. This also includes some information on saveData, the synApps client program that writes scan data to disk.

[scanparmRecord](scanparmRecord.md)

The scanparm record documentation.

[saveData\_fileFormat.txt](saveData_fileFormat.txt)

description of the 'MDA' (multidimensional archive) file format written by saveData. This file format uses the XDR standard for cross-platform compatibility.

[saveData](saveData.req)

Sample copy of the file that tells saveData what to do.

[XDR\_RFC1014.txt](XDR_RFC1014.txt)

A description of the XDR (External Data Representation) standard

[Scans.ppt](Scans.ppt)

Powerpoint presentation that describes the sscan module; shows how to use the sscan record; describes saveData's MDA file format; and explains how EPICS putNotify/ca\_put\_callback() completion behaves, and how to handle processing chains that don't satisfy EPICS' execution-tracing requirements.

Installation and use of the sscan module
----------------------------------------

### Installation and Building

After obtaining a copy of the distribution, it must be installed and built for use at your site. Usually, these steps only need to be performed once.

1.  Unzip and untar the distribution, e.g. on Unix:  
    
    gunzip sscan\_R2-3.tar.gz  
    tar xf sscan\_R2-3.tar
    
    Usually this is done in an EPICS 'support' directory. It will produce the subdirectory
    
    sscan/2-3
    
    > _in synApps 5.5 and higher, it will produce `sscan-2-6-6` -- i.e., no subdirectory._
    
2.  Edit **sscan**'s configure/RELEASE file and set the paths to your installation of EPICS base and to your versions of other dependent modules.
3.  Run gnumake in the top level directory and check for any compilation errors.

### Use of the sscan module in an EPICS IOC

The **sscan** module is not intended to run an IOC application directly, but rather to contribute code libraries, databases, MEDM displays, etc., to an IOC application. SynApps contains an example IOC application (the **xxx** module), which pulls software from the **sscan** module and deploys it in an IOC.

The essential steps in applying **sscan**\-module code in an IOC application ("example") are the following:

1.  Include the following line in example/configure/RELEASE.
    ```
    SSCAN=<full path to **sscan** module>
    ```
    
2.  Include the following line in example/exampleApp/src/iocexampleInclude.dbd.
    ```
    include "sscanSupport.dbd"
    include "scanProgressSupport.dbd"
    ```
    
3.  Include the following line in example/exampleApp/src/Makefile.
    ```
    example\_LIBS += sscan scanProgress
    ```
    
4.  Load the databases standardScans, and saveData, by including the following lines in st.cmd:
    ```    
    dbLoadRecords("$(SSCAN)/sscanApp/Db/standardScans.db","P=xxx:,MAXPTS1=2000,MAXPTS2=1000,MAXPTS3=1000,MAXPTS4=10,MAXPTSH=2000")
    dbLoadRecords("$(SSCAN)/sscanApp/Db/saveData.db","P=xxx:")
    dbLoadRecords("$(SSCAN)/sscanApp/Db/scanProgress.db","P=xxx:scanProgress:")
    ```
    
5.  If you use autosave, include standardScans\_settings.req, and saveData\_settings.req in your autosave request file:
    ```
    file standardScans\_settings.req P=$(P)
    file saveData\_settings.req P=$(P)
    ```
    
6.  Tell saveData how to initialize by editing the file `saveData.req`, and placing it in the ioc's startup directory. Usually, the only part of this file that you modify is the section marked `[extraPV]`. In this section, enter the names of the PV's you want saveData to include in every scan-data file. If a PV is not well described by it's record's `.DESC` field, you can append your own description.
    
7.  Initialize saveData by including the following line in st.cmd, after iocInit:
    ```
    saveData\_Init("saveData.req", "P=xxx:")
    ```
    
8.  Before running any scans, specify where saveData is to write scan-data files. Bring up the medm display, `scan_saveData.adl` and fill in the "File system" and "Subdirectory" fields (i.e., the PV's `$(P)saveData_fileSystem` and `$(P)saveData_subDir`).

Suggestions and Comments to:  
[Tim Mooney](mailto:mooney@aps.anl.gov) : (mooney@aps.anl.gov)
