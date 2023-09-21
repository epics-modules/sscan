---
layout: default
title: Release Notes
nav_order: 3
---


sscan Release Notes
===================

Release 2-11-6 - Sep 21, 2023
-----------------------------

*  Fixed subdirectory detection issue for saveData on Windows
*  scan_settings.req changed to pull required PV's for scan.db,
   previous uses of scan_settings.req should instead use sscanRecord_settings.req


Release 2-11-5 - Oct 19, 2021
-----------------------------

*   Fixed build issues with newer versions of base

Release 2-11-4 - Oct 5, 2020
----------------------------

*   Fixed an issue where vxWorks was failing to save to netApps appliances
*   Added bob files, updated ui and edl files.

Release 2-11-3 - Jun 14, 2019
-----------------------------

*   Req files now installed to top level db folder.

Release 2-11-2 - Feb 28, 2019
-----------------------------

*   Fixes to build with EPICS base 3.16 and 7.0

Release 2-11-1 - Dec 8, 2017
----------------------------

*   Check return code from fclose(), and retry if it failed.

Release 2-11 - Nov 30, 2017
---------------------------

*   Introduce end-of-line normalization
*   fix -Wformat
*   Added sscan iocsh script
*   EPICS-base-version dependent definition of dbNameToAddr
*   display each HTML file (on github main page)
*   progressBar: Included Jon Tischler's new hangWait stuff.
*   Kevin Peterson's fixes for compatibility with Visual Studio 2010
*   Modified .adl files to better convert for caQtDM
*   New version of \*Main.cpp file from base 3.15.5; contains epicsExit() after iocsh(NULL) which is needed for epicsAtExit() to work on Windows
*   Enable Travis CI
*   Converted CRLF to LF

Release 2-10-2 - Nov 6, 2015
----------------------------

*   documented PnPP field

Release 2-10-1 - Mar 27, 2015
-----------------------------

*   saveData: minor bug fix
*   saveData\_writeXDR.c, writeXDR.c: small changes to support minGW compilation
*   If a detector was connected to a remote array, the sscanRecord did not wait for retrace motion to finish before declaring itself done.

Release 2-10 - Oct 22, 2014
---------------------------

*   Changed DBD\_INSTALLS to DBD for sscanSupport and sscanProgressSupport
*   Previously, a scan driven by a scanparm record from a different ioc was occasionally failing to get the new positioner's current value before starting the scan.
*   sscanRecord: More thorough mutex lock around PV-status checks and updates, including essentially all of lookupPV() and the "psscan->faze == sscanFAZE\_SCAN\_PENDING" sections of posMonCallback() and pvSearchCallback(). Initialize p\_pp when positioner PV changes, so we can detect a value that hasn't been updated from the new PV. More thorough PV-status check in checkConnections (also check dbAddrNv or recDynLinkConnectionStatus()). checkConnections() was failing to check the recDynLinkConnectionStatus of the positioner-output link.
*   For positioner-input links, check waitingForPosMon along with connectInProgress. Wait until links disconnect before calling lookupPV. Previously, was setting badOutPutPv before changing positioner-input links, and badInputPv before changing positioner-output links. No longer init p\_cv to -HUGE\_VAL (replaced by waitingForPosMon)
*   When changing positioner links, and waiting for the first monitor callback after the change (to get current position for, e.g., relative scan about that position), do a recDynLinkGetCallback from posMonCallback() to defend against old monitors from the previous positioner PV.
*   scanAux.db: Make record name $(P)$(S), add macro for MPTS
*   sscanRecord.c: check access-security permissions for links  
    scan\*.adl: show write links that are read-only because of access security
*   recDynLink.c: added recDynLinkCheckReadWriteAccess() to check access-security permissions.
*   scan\_full.adl: TnNV were implemented wrong: showed red with no PV name.
*   sscanRecord.c had "#include epicsExport.h" in the wrong place, and this broke cygwin builds.
*   Modified scanParms\_settings.req so it uses the same macro as scanParms.db (M instead of Q). Added scanAux\_settings.req, alignParms\_settings.req, scanParms2D\_settings.req, scanParmsRemote\_settings.re.
*   saveData was failing to read its .req file correctly in some cases on Windows. Fixed by opening the file with fopen(file, "rb"), instead of as fopen(file, "r").

Release 2-9 - Apr. 17, 2013
---------------------------

*   Added Jon Tischler's scanProgress support. To use, include scanProgressSupport.dbd, link with libscanProgress, load scanProgress.db, start the scanProgress seq program, and view with scanProgress.adl. (The support is packaged separately from the rest of the sscan module, and built only if SNCSEQ is defined (typically, in configure/RELEASE), to avoid requiring existing users of the sscan module to build and run the sequencer.)
*   Deleted the PV $(P)saveData\_config from saveData.db and scan\_saveData.adl. The PV was never used.
*   Included new version of mdautils-src.tar
*   New versions of op/python/\* (from utils/mdaPythonUtils).
*   Added CSS-BOY and caQtDM display files.
*   on vxWorks, use open(), rather than creat(), to check that we can open a new file.

Release 2-8-1 - Sept. 1, 2012
-----------------------------

*   Fixed minor problems in writeXDR.h and writeXDR.c that prevented it from compiling on Windows with Visual Studio compiler.
*   Previously, saveData crashed with versions of vxWorks that have a 10-function xdr\_ops table. Now xdr\_stdio.c checks for 8-, 10-, and 12-function tables.

Release 2-8 - Feb 8, 2012
-------------------------

*   Previously, saveData could not be buit on WIN32 because Windows has no XDR library. The file saveData\_writeXDR.c uses a local implementation (writeXDR) of XDR's file-writing specification that doesn't require any help from the OS. This support runs on any OS, but it's likely to be slower than system implementations, and so should probably be used only for WIN32.
*   Previously, aborting a sscan record that was already idle was treated as an error (special returned -1, which could be confusing to clients, and served no useful purpose). Thanks to Sergey Stepanov for noticing this very long-standing problem.
*   Previously, saveData did not flush the channel access output buffer after doing cagets for extra PVs. This resulted in some PVs having stale values in the data file - particularly PVs repeated by a PV gateway. Thanks to Wang Xiaoqiang (PSI) for this fix.
*   Previously, on 64-bit architectures, saveData wrote 2D and higher files with NPTS\*4 extra bytes immediately preceding the name of outer-loop sscan-record names, because it calculated file offsets using sizeof(long) instead of sizeof(epicsInt32). Thanks to Eric Berryman for reporting the problem.
*   Previously, writing an array of DBF\_LONG or DBF\_USHORT failed on 64-bit OS. This happened when such an array was specified in the "extraPV" section of saveData.req

Release 2-7 - August 26, 2011
-----------------------------

*   Previously, on Linux, Solaris, and probably other non-real-time operating systems, saveData could write corrupted data files for 2D and higher scans, because monitored DATA fields from sscan records could be received out of order.
*   Previously, scans with any fly-mode positioners and no detector triggers failed to launch fly-mode positioners to the end point.
*   The detailed order of operations has changed slightly for one type of fly scan. Previously, in soft fly scans (scans with ACQT="SCALAR", and one or more fly-mode positioners) detector triggers were executed and awaited after fly-mode positioners had arrived at the start point, and before they were launched toward the end point. This error caused the first point in such a fly scan to be different from all other data points, in that it was a static measurement, rather than an average over position. Now, fly mode positioners are launched toward their endpoints before detector triggers are executed for the first time. _Note that this change does not affect hardware-assisted fly scans (scans with ACQT="1D ARRAY"), which have always behaved in this way._
*   Increased the maximum size of the PV-name prefix specified to saveData\_Init() from 10 to 30 (PVNAME\_STRINGSZ/2).
*   The sscan record's CMND field is now a DBF\_MENU, instead of a DBF\_ENUM.
*   Makefile was modified to build saveData on cygwin 1.7.x.
*   Added python programs for MDA files in sscanApp/op/python.
*   In the scan\_more.adl and scan\_triggers.adl display files, t\*nv (the red numbers) were displaying error when assoc trigger link was not defined, instead of only when it was defined but not connected
*   fixes for 64-bit architectures.
*   sscanRecord.html: better discussion of fly scans and examples of loading PnPA for table mode.
*   Modified RELEASE; deleted RELEASE.arch
*   Added .opi display files for CSS-BOY
*   standardScans.db: scanResumeSEQ was not defending against a change in the command value during the resume delay. As a result, resuming and then pausing during the resume delay did not leave the scan paused.
*   Previously, when an inner scan was paused while it was idle waiting for the next poke from the outer scan, the scan would not resume when the pause was rescinded. This problem was caused by my change that treated an attempt to execute a paused scan as an error. The sscan record no longer treats this as an error.

Release 2-6-6 - March 30, 2010
------------------------------

*   Previously, a monitor on the file\_subdir PV could leave savaData in the STATUS\_ACTIVE\_FS\_ERROR state, if the PV hadn't actually changed. As a result, saveData booted up into the error state when the file\_subdir PV was blank.
*   scan\_settings.req - added ATIME and COPYTO; deleted AAWAIT
*   sscanRecord.c - fixes for 64-bit arch
*   saveData.c - defend against saveData\_init() being called more than once.

Release 2-6-5
-------------

*   Check all chid's before using them.
*   Modified saveData so that, when it finds the filename it would like to use (e.g., base\_0001.mda) already in use, it writes, e.g., base\_0001\_01.mda, instead of base\_0001.mda\_01, as it used to do.

Release 2-6-4
-------------

*   In 2.6.3, saveData crashed under tornado 2.2, because a vxWorks XDR structure changed. Now we define an old and a new structure, and identify the correct structure by its size.

Release 2-6-3
-------------

*   scanDetPlot.adl - added count
*   don't build busy record (split out into separate module) but retain a copy here for a while, since the busy module has new different version
*   saveData.c - don't include nfsDrv.h (which is renamed in tornado 2.2.2); instead, define nfsMount, nfsUnmount by hand.
*   sscanRecord.c - handle DBRprecision definition in EPICS 3.14.10; scanOnce() arg cast

Release 2-6-2
-------------

*   Removed race conditions affecting callback counters, and added mutex to protect them. Changed timing of when to renew positioner links from now-last\_scan\_start to now-last\_scan\_end.
*   display\_fields.adl uses new link-help displays from std R2.6

Release 2-6-1
-------------

*   The sscan record didn't correctly handle reads or writes to PnPA, for n>1. As a result, table scans did not work with positioners 2-4.
*   saveData didn't fail correctly when it could not find the \[basename\] section in its initialization file, and when it failed to connect to the basename PV. Instead, it aborted its initialization, and failed to connect to sscan records.

Release 2-6
-----------

*   The sscan record can now post current-data arrays during a scan. While ATIME >= 0.1, ALL arrays will be posted when a new data point has been acquired and ATIME seconds have elapsed since the last array posting. New sets of array PV's have been added for this purpose, since the old array PV's must contain the previous scan's data to avoid breaking data-storage clients. The new PV's are PnCA (positioners, e.g., P1CA), and DnnCA (detectors, e.g., D01CA). During a scan, arrays are posted with the attribute DBE\_VALUE; at end of scan, they are posted with DBE\_LOG as well.
    
    Unfortunately, posting current-data arrays during a scan results unavoidably in the posting of the previous-data arrays, PnRA and DnnDA. Clients that monitor these PV's can regain their old behavior by specifying the mask DBE\_LOG in their ca\_add\_event() or ca\_create\_subscription() call.
    
*   The MEDM display scanDetPlot.adl now uses the new current-data PV's to display data. (These PV's also get end-of-scan data.) The MEDM display scanDetPlotRT.adl has been renamed scanDetPlotFromScalars.adl.
*   Previously, the sscan record repeated final data values out to the ends of arrays, when a scan was finished, to aid display clients that don't know how to plot only a PV-specified number of data points. Now this treatment can be done also during a scan, as controlled by the PV COPYTO.

Release 2-5-7
-------------

*   Allow end user to specify the base name of data files written by saveData. Previously, the ioc prefix (modified to avoid characters illegal in file names on the supported operating systems) was used as the base file name. Now, if saveData.req contains the section \[basename\], and the PV named in that section exists, and the string value of that PV is not the empty string, then saveData will use the string value, instead of the ioc prefix, as the base file name (onto which the scan number and the string ".mda" will be appended).
*   Previously, saveData's init file could not usefully specify PV names containing the characters '-', '\[', '\]', '<', '>', or ';', even though these are legal characters for a PV name.
*   New documentation files: saveData.req and scanParmRecord.html
*   Busy record now pays attention to it's UDF and alarm fields, executes its its DOL link only if that link is not CONSTANT.
*   If recDynLink encounters a link structure that thinks it has an instance on queue, but the queue is in fact empty, then the link structure is corrected.
*   saveData's stack size increased.to epicsThreadStackBig.

Release 2-5-6
-------------

*   scan.db database separated into standardScans.db and saveData.db.
*   Added standardScans\_settings.req and sscanRecord\_settings.req. This allows a script to more easily write a new auto\_settings.req file, since the request file has the same name as the database it supports. Also, this makes it easy to load more than one copy of standardScans.db.
*   Win32-specific .dbd file is no longer needed, since Mark Rivers added saveDataWin32.c, which contains stub functions for commands that could not be built for Win32.
*   saveData now checks all data-file writes for errors, and retries until file is successfully written, or user-specified number of retries has been done. User also specifies the time between retries. The new PV's were added to scan\_saveData.adl
*   In sscan module 2.5.3, saveData was writing scan-dimensions to the wrong file offset, under certain circumstances. This is fixed.
*   recDynLink now calls epicsAtExit, so it can avoid making CA calls after CA has been shut down.
*   recDynLink handles null and empty PV names more gracefully.
*   sscan record now has a CMND-field value for clearing positioner drive and readback PV's, and the default medm display file uses this value for it's "CLEAR" button.

Release 2-5-3
-------------

*   Added sscanApp/op/python directory, with the following programs:
    
    addMDA.py
    
    Front end for adding MDA files, uses readMDA, opMDA, and writeMDA from mda.py
    
    mda.py
    
    Python API for MDA files. Supports reading, writing, and arithmetic operations for up to 4-dimensional MDA files
    
    mdaAsc.py
    
    Uses mda.py to render a 1-dimensional MDA file as ascii text.
    
    opMDA.py
    
    Front end for operating on MDA files, uses readMDA, opMDA, and writeMDA from mda.py
    
*   Fixed problems in the communication between the sscan record and saveData that caused corrupted data files to be written:
    *   The basic problem was that saveData was getting bufferred data arrays, but an unbuffered copy of the sscan record's CPT field. The sscan record now maintains the field BCPT (bufferred CPT) which is posted when data array buffers are switched.
    *   A second problem was that saveData was not able to put AWAIT=1 quickly enough to stop a very fast scan in time to ensure integrity of the data file. saveData now writes '1' to the sscan record's AAWAIT field on init, and writes '0' if it ever exits (not a supported operation at this time). As a consequence, AAWAIT no longer occurs in the autosave-request file scan\_settings.req.
    *   A remaining problem, thus far seen only on cygwin, is that multidimensional scans can get saveData into trouble because CA monitors sometimes are received by saveData in a different order than they were posted by the sscan records. Currently, neither the sscan record nor saveData defend against this.
*   Added Dohn Arms' 'mdautils' software in the sscanApp/src directory. This software can convert an MDA file to ascii, print info about an MDA file, and read an MDA file into C data structures.
*   Fixed a race condition in the sscan record that was responsible for hanging scans at the last point (and maybe other things as well).
*   the sscan record no longer renews PV links when a scan starts if the new scan follows the previous scan by less than sscanRecordLookupTime.
*   If retrace or after-scan fails because recDynLinkPutCallback returns an error, skip the action rather than hang.
*   If the sscan record attempts to connect to a PV while an earlier connection attempt is still in progress, it now waits and retries.
*   recDynLinkQsize is now exported for use by the ioc shell.
*   recDynLink used to crash if one of its callback functions received an event\_handler\_args structure with a status element whose value was not == ECA\_NORMAL. Now it declines to process the event or to pass it on to the client.
*   saveData used to check directory permissions by attempting to create a file whose name was illegal (contained ':') on some operating systems.
*   rewrote sscanRecord.html

Release 2-5-2
-------------

*   sscanRecord checks parameters more closely, allows before-scan and after-scan links to write to selected PV's of their own sscan record.
*   New after-scan action: Move to center of mass of peak (this choice has problems with multiple positioners, since they won't, in general, have the same peak position).
*   In previous versions, recDynLink would deadlock if asked to clear the link to a PV while an action for that PV was still on queue. This is fixed.
*   saveData zeros unused points in its XDR buffer, because XDR doesn't manage this well.

Release 2-4
-----------

This version is intended to build with EPICS base 3.14.7.

*   The sscan record and saveData now take advantage of the sscan record's double buffered data arrays, and allow a scan to proceed while the previous scan's data is being written to disk. (AWAIT, AAWAIT fields)
*   saveData now runs on Solaris and Linux ioc's.
*   Array valued detectors are now supported in all scan modes. Arrays are read at the end of the scan. If processing is required to get array PV's ready, the sscan record can trigger that processing with the A1PV, A1CD fields (just like detector triggers, but executed after the scan is done, and just before array PV's are acquired).
*   The new field DSTATE shows the state of the sscan record's data arrays. When DSTATE==POSTED, the sscan record can begin a new scan.
*   Previously, the before-scan and after-scan links always waited for completion. Now the user decides, by setting BSWAIT and ASWAIT.
*   If scan fails limit checks, the scan hangs until user aborts. Previously, the scan would appear to complete.
*   new medm displays for scans are simpler, less cluttered, and have documentation callups.
*   In saveData.req (the file in the ioc directory that tells saveData what scans to monitor, etc), the handshake PV is now ignored. saveData now uses scanX.AWAIT to handshake with scanX.
*   saveData no longer allocates local storage for unused sscan-record detectors. Once a sscan-detector PV is specified, storage is allocated and never released.
*   Modified the scanparm record to support multi-dimensional, multiple- positioner scans: Added two output links to the scanparmRecord: OLOAD, and OGO. If LOAD is nonzero, it's written to OLOAD; if GO is nonzero, it's written to OGO.
*   Added scanParms2Pos.db, scanParms2Pos.adl -- scan parameters for a 1D scan with two positioners.
*   The scanparm record now uses long int, rather than short int, for the number of data points (fields MP and NP).
*   sscanRecord.dbd and scanparmRecord.dbd now include sscanMenu.dbd, to ensure that menus are consistent. Sometime in the past, the scanparm record wasn't updated when sscanRecord menu fields were modified. In particular, scanParm\*.db and alignParms.db used to specify "Relative" positioning, while the sscan record accepted only "RELATIVE" or "ABSOLUTE".
*   The sscan record now issues recDynLinkGetCallback() for each positioner and detector PV, and waits for the callback before using the PV value that was cached by recDynLink.
*   Added recDynLinkGetCallback() to recDynLink library. Also fixed some bugs.
*   [cvs log](cvsLog.txt)

Release 2-3
-----------

This is the first release of the synApps sscan module. Version numbering for this module begins with 2.3 because this module was split from version 2.2 of the std module, and I wanted to retain the CVS histories of module contents.

This version is intended to build with EPICS base 3.14.5. Differences from software as previously released in std 2.2:

*   Converted to EPICS 3.14. Currently saveData runs on vxWorks only.
    
*   Docs updated and moved to sscan/documentation
    
*   saveData - added iocsh support; changed number of data points from short to long int, to support very large scans. The data file format is unchanged, however, because the number of points was already being written as a four-byte quantity.
    
*   sscanRecord - Number of points in a scan is essentially limited only by available memory. save-restored value of NPTS is now checked against MPTS. Array mode (ACQT="1D ARRAY") was broken. (The change from ACQM="ARRAYS" to ACQT="1D ARRAY" wasn't done correctly.)
    
    Previously, the sscan record's response to an abort request (.EXSC=0) while no scan was in progress (.BUSY==0) was to return nonzero from special(), and EPICS tolerated this without comment. Now it signals an error to the client. But we don't (always?) want this action to be regarded as an error. For now, the scan database just declines to abort a sscan record that isn't busy, but clients writing directly to the sscan record directly can still get this error message.
    
*   recDynLink - Fixed memory leak (epicsMutex created but not destroyed). Switched communication with link tasks from ring buffer to message queue. recDynOut was calling ca\_pend\_event, which used to flush the ca buffer, but evidently no longer does; replaced with ca\_flush\_io.
    
*   saveData\_settings.req - new file.
    
*   scan\_settings.req - added fields ACQT and ACQM.
    

Suggestions and Comments to:  
[Tim Mooney](mailto:mooney@aps.anl.gov) : (mooney@aps.anl.gov)  
Last modified: May 26, 2008
