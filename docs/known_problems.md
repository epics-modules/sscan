---
layout: default
title: Known Issues
nav_order: 6
---


sscan\_known\_problems
======================

R2-10-2 and earlier
-------------------

*   On Windows, built with Visual Studio 2010, scanProg.st crashes because it uses a strftime() format character that is not implemented by Visual Studio 2010.

sscan 2-7
---------

*   saveData is not ready for 64-bit architectures. It writes 1D files correctly, but not 2D or higher.

sscan 2-6-6
-----------

*   On Linux, Solaris, and probably other non-real-time operating systems, saveData can write corrupted data files for 2D and higher scans, because monitored DATA fields from sscan records can be received out of order. This bug affects 2.6.6 and all earlier releases of the sscan module.
*   scans with any fly-mode positioners and no detector triggers fail to launch fly-mode positioners to the end point.
*   saveData is not ready for 64-bit architectures

sscan 2-6-4
-----------

*   saveData did not check all chids before using them, leading to the task crashing when PV's did not connect.

sscan 2-6-3
-----------

*   saveData crashed under tornado 2.2.*

sscan 2-6-2
-----------

*   saveData occassionally writes garbage to the file-version number (the first four bytes of an .mda file).

sscan 2-6-1
-----------

*   Callback counters are susceptible to a race condition that leads the sscan record to think detector values have been received over channel access when they might not have been received, and to hang waiting for values that have, in fact, been received.
*   The sscan record renews positioner links unnecessarily during multidimensional scans.

sscan 2-6
---------

*   Callback counters are susceptible to a race condition that leads the sscan record to think detector values have been received over channel access when they might not have been received, and to hang waiting for values that have, in fact, been received.
*   The sscan record renews positioner links unnecessarily during multidimensional scans.

sscan 2-5-7
-----------

*   Callback counters are susceptible to a race condition that leads the sscan record to think detector values have been received over channel access when they might not have been received, and to hang waiting for values that have, in fact, been received.
*   The sscan record renews positioner links unnecessarily during multidimensional scans.
*   The sscan record doesn't correctly handle writes to PnPA (the arrays used for table scans).
*   saveData aborts its initialization when its initialization file lacks a \[basename\] section, and fails to connect to sscan records.

sscan 2-5-6
-----------

*   Callback counters are susceptible to a race condition that leads the sscan record to think detector values have been received over channel access when they might not have been received, and to hang waiting for values that have, in fact, been received.
*   The sscan record renews positioner links unnecessarily during multidimensional scans.
*   saveData's init file cannot usefully specify PV names containing several characters that are legal for a PV name.

sscan 2-5-5
-----------

*   saveData was writing scan dimensions to the wrong offset in the data file header, under some circumstances, corrupting the header so that some readers could not understand the file.
*   Prefix length was inconsistently enforced, with the result that the maximum number of characters (exclusing the trailing null) was actually eight, instead of nine.

sscan 2-5-5
-----------

*   saveData was writing scan dimensions to the wrong offset in the data file header, under some circumstances, corrupting the header so that some readers could not understand the file.
*   Prefix length was inconsistently enforced, with the result that the maximum number of characters (exclusing the trailing null) was actually eight, instead of nine.

sscan 2-5-4
-----------

*   scanSee (a display program not included in the sscan module) gets confused because saveData's messages to users have been reformatted.
*   the sscan record does not behave correctly if autosave restores an illegal value for NPTS.

sscan 2-5-3
-----------

*   Scans hang if the data-file fails.

sscan 2-5-2
-----------

*   Scans can hang because of a race condition in doPuts() and a call to recDynLinkPutCallback() that failed for a reason other than notifyInProgress.

sscan 2-4
---------

*   The before-scan link (.BSPV, .BSCD) is broken.
*   If a PV link is changed while the previous value is still connecting, the software will hang.
