---
layout: default
title: sscan Record
nav_order: 4
---


The sscan record
================

Author: Tim M. Mooney  
Based on the scan record, written by Ned D. Arnold.  
 Advanced Photon Source   
 Argonne National Laboratory

Contents:   
[__1.__  Introduction](#HEADING_1)  
[__1.1.__ A Simple One Dimensional Scan](#HEADING_1-1)  
[__1.2.__ Multidimensional Scans](#HEADING_1-2)  
[__1.3.__ Interaction with clients](#HEADING_1-3)  
[__1.3.1__ Starting a scan](#HEADING_1-3-1)  
[__1.3.2__ Stopping a scan](#HEADING_1-3-2)  
[__1.3.3__ Pausing a scan](#HEADING_1-3-3)  
[__1.3.4__ Displaying scan data](#HEADING_1-3-4)  
[__1.3.5__ Handshaking with data-storage clients](#HEADING_1-3-5)  
[__1.3.6__ Handshaking with CA clients that implement positioners or detectors](#HEADING_1-3-6)  
[__1.4.__ Completion of positioner and detector-trigger operations](#HEADING_1-4)  
[__1.5.__ Fly scans](#HEADING_1-5)  
[__1.5.1.__ Scalar-mode fly scans](#HEADING_1-5-1)  
[__1.5.2.__ Array-mode fly scans](#HEADING_1-5-2)  
[__2.__  sscan-Record Fields](#HEADING_2)  
[__2.1.__ Control Fields](#HEADING_2-1)  
[__2.2.__ Positioner Fields](#HEADING_2-2)  
[__2.2.1__ LINEAR Mode](#HEADING_2-2-1)  
[__2.2.2.__ TABLE Mode](#HEADING_2-2-2)  
[__2.2.3.__ FLY Mode](#HEADING_2-2-3)  
[__2.3.__ Detector-Trigger Fields](#HEADING_2-3)  
[__2.4.__ Delay Fields](#HEADING_2-4)  
[__2.5.__ Client Handshaking Fields](#HEADING_2-5)  
[__2.6.__ Detector Fields](#HEADING_2-6)  
[__2.7.__ Execution Fields](#HEADING_2-7)  
[__2.8.__ Status/Progress Fields](#HEADING_2-8)  
[__2.10.__ Miscellaneous Fields](#HEADING_2-10)

- - - - - -

<a name="HEADING_1"></a>

1. Introduction
===============

- - - - - -

The purpose of the sscan record is to move *positioners* through a series of positions and record *detector* data at each of the positions. This series of operations is commonly referred to as a *scan*, or as one loop of a multi-dimensional scan. After parameters defining the scan have been initialized and the scan has been launched, the sscan record begins a possibly long and involved sequence of operations normally without further input, and notifies any interested clients as the scan progresses. The data are collected into arrays within the record so that clients needn't handle them point by point. A separate piece of software ("saveData", which is included with the sscan record in the synApps sscan module) can coordinate with the sscan record to write scan data to disk. 

> Note that the word "scan" is used frequently in other EPICS documentation to mean something quite different from what is meant here. In the *EPICS Application Developers Guide*, "scan" connotes record processing or execution, as in "Database scanning is the mechanism for deciding when to process a record." Also, periodic record processing is performed by "scan tasks", and the field that controls when a record will be processed is named "SCAN". None of these uses of "scan" have anything to do with the sscan record, and the word will not have the EPICS meaning in the rest of this documentation.

A single sscan record supports a one dimensional scan. Several sscan records can be linked together to perform a multi-dimensional scan. Each sscan record can control up to four positioners, trigger up to four detectors, and acquire data from up to 74 process variables (70 detector values of type floatand four positioner readbacks of type double).

In the most common use, the sscan record moves motors and acquires scaler (pulse counter) data at each motor position, but obviously it can also be used for other purposes. Any writable EPICS PV (process variable) can be scanned through a set of values while data are recorded from any other PVs. For example, one of the positioner PVs could be used to vary the gain or dwell time of a detector during a scan. Therefore, throughout this document the term *positioner* should be taken to mean "any PV to which you can write a number". Similarly, the term *detector trigger* will typically refer to a PV that will cause data acquisition to begin when it is written to, but it could be taken to mean "any PV to which you can write a number". Finally, the term *detector* refers to any readable numeric PV. ("Signal" might be a better word for this.)

The sscan record normally acquires sets of scalar data values and assembles them into arrays, but it can also acquire arrays directly from array-valued PVs. The end results can only be one-dimensional arrays, however; a single sscan record cannot acquire multi-dimensional data.

All of the process variable names used to identify positioners, detectors, and detector triggers are specified using *reassignable links*. This allows a scan to be configured at run time, immediately before it is executed. Currently, these links are implemented with the recDynLink library, which is distributed along with the __sscan__ module.

Before a scan can start, all of the links that aren't blank must connect with the named PVs. Links that will write must, in addition, have write permission granted by EPICS' access security. The sscan record doesn't check continuously for link connection and write permission; it checks when a link is defined, and at the beginning of every scan.

<a name="HEADING_1-1"></a>

1.1. A Simple One Dimensional Scan
----------------------------------

In the simplest reasonably complete configuration for a one-dimensional scan, the following fields are used: P1PV the name of a positioner (e.g., "myMotor.VAL") P1SP start position -- the first position at which data will be acquired P1EP end position -- the last position at which data will be acquired NPTS the total number of positions to visit T1PV the name of a detector-trigger PV. This PV will be written to after the positioner has arrived at each position, and it is expected to initiate some data-acquisition operation. D01PV the name of a detector (signal) PV. The value of this PV will be recorded after the detector trigger has finished acquiring data. When a scan is started (by writing a 1 to the EXSC field) the sscan record commands the positioner to move to its starting position. The sscan record uses recDynLinkPutCallback() to tell the positioner to move, and waits for the resulting callback, indicating that the positioner is finished, before moving on to the next phase of the scan, which is to trigger the detector. The detector is also triggered using recDynLinkPutCallback(), and the sscan record waits for it to finish before reading detectors and going on to perform another (move, trigger, read) sequence to acquire the next data point. This algorithm continues until the sscan record has completed NPTS steps, or the scan is aborted (by a client writing 0 to the EXSC field). At the end of the scan, the sscan record has filled in an array of the positions visited (P1RA), and an array of detector values acquired (D01DA). Let's run through that again, this time more generally, with more detail, and including more of the available options.

Positioners You can specify zero to four positioners. Positioners are expected to tell the sscan record when they're done moving (more about this later). After all positioners have declared themselves done, the sscan record waits for a user-specified settling time (PDLY, normally zero) before writing to detector triggers. (If no positioners, then no positioner settling time.) Positions to visit There are lots of possibilities here. You can specify any combination of the set \[*start, end, center, width, step-size*\] for each positioner; you can load a table of positions for each positioner; or you can specify that positioners are to be moved continuously during a scan. You can specify that positions be regarded as absolute, or as relative to the pre-scan position. Detector triggers Detector triggers act much like positioners, in that they write a value and wait for any ensuing processing to finish, but they send the same value at every data point (T*n*CD). After all triggered detectors have declared themselves done, the sscan record waits for a user-specified settling time (DDLY, normally zero) before reading data from detector-signal PVs. (If no detector triggers, then no detector settling time.) Detector signals Typically, detector signals are scalar PVs, but they can be array-valued PVs. If so, the sscan record will read NPTS values from them at the end of the scan. If array-valued PVs require processing to acquire their values, the sscan record can write to a special array trigger (A1PVA1CD, exactly analogous to detector triggers), and wait for any ensuing processing to finish before reading the arrays. If all detector signals are array valued, it's probably better to use the array acquisition type. (See ACQT.) Detector-signal values can be accumulated from scan to scan, so you can sweep over a set of positions, building up statistical precision and averaging over any positioning errors or variable external conditions. (See ACQM.)

After the scan You can tell positioners what to do after the scan is finished, using the PASM field. The default behavior is simply to remain where the scan left them, but you could tell them to return to their pre-scan positions, go to their start positions, or go to positions calculated from acquired data (e.g., the position at which a specified detector signal REFD reached its peak value during the scan). <a name="HEADING_1-2"></a>

1.2. Multidimensional Scans
---------------------------

Multidimensional scans are easy: an outer-loop sscan record (which we'll call "scan2") regards an inner-loop sscan record ("scan1") as a detector to be triggered, and each sscan record acquires its own data. Thus, scan2.T1PV, is set to scan1.EXSC, and scan2.T1CD is set to 1. In words, scan2 writes a 1 to the "execute scan" field (EXSC) of scan1. To initiate the scan, the scan2 record is commanded to begin (scan2.EXSC is set to 1). scan2 sends its *positioners* to their starting points, and waits for their callbacks. Then scan2 writes to its *detector trigger*(s), (one of) which in this case causes scan1 to begin its own scan. The scan1 record will now go through its entire programmed scan, acquiring data from its detectors at each point.

When scan1 is finished, and its data have been written (or at least secured), its completion callback causes scan2 to continue in its scan procedure -- reading detector values, moving positioners to new positions, and causing scan1 to execute again.

This approach to configuring multidimensional scans is very flexible and permits scans of any dimension. Note that scan1 can be executed independently of scan2, so a complex multidimensional scan can be built and tested one dimension at a time. (In principle, it's possible to run several inner-loop scans in parallel from a single outer-loop scan, but in practice, the capability is of limited use, because there is no coordination between the inner-loop scans, and no data-storage client exists that would correctly understand the acquired data.)

An outer sscan record involved in a multidimensional scan doesn't know or care that the detector trigger it's writing to is actually another sscan record, which is going to do an entire inner scan; the outer sscan record simply triggers what it regards as a detector, and waits for that detector to complete. Nor do the inner sscan records know that they are parts of something larger than themselves. The only piece of code that has to know a multidimensional scan is occurring is the client that stores the data. This client must collect all of the data from each inner scan before those data are overwritten by the next execution of that inner scan, because sscan records hold only one-dimensional arrays of data.

Clearly, this calls for some handshaking between the client and the sscan records involved in a multidimensional scan. The next section describes the handshake mechanisms implemented by the sscan record.

<a name="HEADING_1-3"></a>

1.3. Interaction with clients
-----------------------------

Clients of the sscan record include the software that starts, stops, or pauses a scan; software that displays data acquired by a scan; software that writes scan data to disk; and software that participates in the a scan by implementing positioner or detector operation. A single client may do any or all of these things, of course, but it seems best to discuss them separately.

<a name="HEADING_1-3-1"></a>

### 1.3.1 Starting a scan

The client writes the number 1 to the sscan record's EXSC field to start a scan. If the sscan record is able to start a new scan, it sets its BUSY field to 1 while the new scan is in progress, and it sets BUSY to 0 when the scan is done. If the sscan record is not able to start a new scan, the client will receive an error indication, and the command may be ignored. The sscan record will set its SMSG field to a string describing the reason why it cannot start a new scan. Possible reasons include the following:

 "Waiting for PV's to connect"One or more of the PVs specified as positioners, triggers, readbacks, etc. has not yet connected. If the offending PV must be written to, it's possible that the PV has connected but the ioc doesn't have permission to write to it, because of an EPICS access-security setting or condition. "Scan is paused ..."The sscan-record field PAUS has a nonzero value, indicating that some client has told the sscan record to stand by until PAUS is set back to 0. In this case, the sscan record will set FAZE to "SCAN\_PENDING", and wait until PAUS is rescinded before setting BUSY to 1 and starting the scan. "waiting for client ..."The sscan-record field WTNG has a nonzero value, indicating that some client has told the sscan record to wait. (See "Handshaking with data-storage clients", below, for details.) In this case the command will be ignored. "Already scanning"A scan is already in progress. Setting EXSC to 1 while scan is in progress has no effect on that scan. In this case, the command will be ignored. "Waiting for saveData"A new scan cannot be started because the data-storage client, "saveData", is still using one of the two sets of data arrays, and the other set is full of scan data also waiting for service by saveData. In this case, the sscan record will wait until saveData has finished using the arrays (which saveData indicates by writing 0 to the sscan record's AWAIT field) before setting BUSY to 1 and starting the scan. "Waiting for callback"The previous scan is essentially complete, but one of the commands the sscan record issued has not yet completed. In this case, the command to start a new scan will be ignored. In all but the "Waiting for PV's to connect" and "Scan is paused" cases, the start command will be ignored, and the scan will not automatically start when the condition that prevented it from starting is removed. A new start command must be issued.

<a name="HEADING_1-3-2"></a>

### 1.3.2 Stopping a scan

A client tells the sscan record to stop scanning by writing 0 to the EXSC field. But stopping a scan is sometimes a complicated process, because, while a scan is in progress, the sscan record issues commands to other software, and waits for the *callbacks* that will come when those commands complete. Also, the sscan record handshakes with the data-storage client (if present) to ensure that data arrays are not overwritten before their content has been written to disk. When a sscan record receives a "stop" command, it can stop itself easily, but it cannot unsend or abort the commands it already sent, and it's not permitted to assume that commands already sent, or data not yet written, may simply be abandoned. If it's waiting for either of these, it will continue to wait until the user tells it to stop by writing 0 again to the EXSC field. If it's waiting for data storage, two writes of 0 to EXSC are required. When a sscan record is told to stop while it has outstanding callbacks, it sets its SMSG field to the string "Abort: waiting for callback". When the callback arrives, SMSG will change to "Scan aborted by operator", and the BUSY field will be set to 0.

When a sscan record is told to stop while it is waiting for service by the data-storage client, "saveData", it sets its SMSG field to the string "Killing scan (kill=*n*/3)", where *n* is 1, 2, or 3.. When saveData has serviced the sscan record, SMSG will change to "Scan aborted by operator", and the BUSY field will be set to 0. If saveData does not service the sscan record, writing 0 to EXSC a total of three times will cause the scan to complete with the message "Abandoning unsaved scan data".

If the sscan record is waiting for both outstanding callbacks and the data-storage client, the messages it writes to SMSG may overwrite each other, and not clearly indicate what is happening. The user's course of action, however, is always the same:

- A single write of 0 to the EXSC field requests a polite scan abort, waiting for callbacks and data storage.
- Two successive writes of 0 to EXSC request a scan abort with no wait for outstanding callbacks. However, the sscan record will still wait for the data-storage client.
- Three successive writes of 0 to EXSC demand an immediate scan abort with no regard for consequences. Scan data will be lost in this case.

When a scan is aborted, and more than one write to EXSC was required, the *next* scan may inherit the problem. If the problem was an outstanding callback, and that callback *still* has not come in by the next time the sscan record is told to start, the scan will not be permitted to write to the PV whose callback is still outstanding. This may indicate that a PV is imperfectly implemented, and cannot be scanned; or that some error prevented the operation from completing; or that the sscan record missed the completion message; or simply that the operation is taking a long time to finish. If the operation cannot be manually stopped, the only recourse is to erase the PV name and rewrite it. This closes and reopens the channel-access connection to that PV, and frequently will resolve the immediate problem.

<a name="HEADING_1-3-3"></a>

### 1.3.3 Pausing a scan

A scan can be paused by writing "PAUSE", or the number 1, to the PAUS field. While a sscan record is paused, it will do nothing to further the progress of the scan, but it will remain receptive to outstanding callbacks. A paused scan is continued by writing "GO", or the number 0, to the PAUS field. A multidimensional scan can be paused by writing "PAUSE" to the PAUS fields of all involved sscan records. (The database standardScans.db does this by implementing a single "PAUSE" pv, and writing its value to all of the sscan records in the database.)

<a name="HEADING_1-3-4"></a>

### 1.3.4 Displaying scan data

Scan data is published by the sscan record using EPICS Channel Access, just as any other EPICS record would publish the values of its fields. The act of publishing data via Channel Access is referred to here as *posting*, because the EPICS function that performs this function is db\_post\_events(). After a field has been posted, a client can get the new value by issuing the Channel Access call ca\_get(). A client can also arrange, in advance, to receive posted data from a particular field, whenever it is posted, by *monitoring* -- also called *subscribing to*-- the field. See the Channel Access Reference Manual (specifically, ca\_add\_event() or ca\_create\_subscription()) for the details of how this is done. The purpose here is simply to introduce the terms *post*and *monitor*, so that I can use them in this documentation. The sscan record maintains two sets of array PV's for scan data: data from a completed scan are posted as P*n*RA and D*nn*DA (e.g., P1RA, D01DA); data from a scan in progress are posted as P*n*CA and D*nn*CA. During a scan, arrays are posted only if the user requests this by setting the array-posting period, ATIME, to a value greater than or equal to 0.1 (seconds). After a scan has completed, all data arrays are posted, marked with the mask DBE\_LOG, and the completed-scan postings (P*n*RA and D*nn*DA) remain available to clients until the next scan completes.

> Because the sscan record implements double-buffered data arrays, and because of the way in which posting is accomplished in EPICS, the posting of scan-in-progress data arrays results unavoidably in useless reposting of completed-scan data arrays. If this presents a problem for a data-display or data-storage client, there are two ways to avoid the problem: 1) Tell the sscan record not to post arrays during scans by leaving the array-post period, ATIME, at its default value of zero; 2) modify the client so that it monitors only postings flagged with the DBE\_LOG mask.

A more efficient, but more difficult, way for a client to get data from a scan in progress is to monitor the scalar current-value PVs, such as R1CV, D01CV, etc., and collect their values into arrays. Positioners actually have two fields that might be suitable for display while a scan is in progress: the positioner's desired value (P*n*DV) and the readback's current value (R*n*CV). (If there is no readback PV, the posted readback value will be a copy of the desired value.)

Not all data points of a scan are guaranteed to be posted as scalar values, because the sscan record *throttles* it's posting, so that it doesn't exceed 20 data points per second. ("data point" means "all positioners and detectors".) This throttling is intended to limit the network activity caused by a scan, and it's necessary because displaying scan data is not more important that acquiring it, and because the sscan record also uses the network to acquire data.

The task of accumulating posted scalar values into data arrays is complicated by the standard EPICS behavior of declining to post a field whose value has not changed since the last time the field was posted. If a client were simply to append each new posting to the data arrays it is accumulating, it would not be including those repeated values. The following algorithm will accumulate data correctly:

1. Create local variables to hold cached values of the fields to be monitored, and a local variable (which I'll call "numPoints") to hold the number of data points accumulated.
2. Monitor D*nn*CV, R*m*CV and VAL (*scalar data and control fields*).
3. Monitor D*nn*DA, P*m*RA, DATA, and CPT (*array data and control fields*).
4. Whenever D*nn*CV, R*m*CV, or CPT are received, cache the received scalar value in a local variable.
5. Whenever D*nn*DA or P*m*RA are received, cache the received array value in a local variable.
6. When DATA==0 is received, clear all data arrays, and reset numPoints to zero.
7. When VAL is received, append to all data arrays from cached scalar values, and increment numPoints.
8. When DATA==1 is received, clear all data arrays and replace with cached array values; set numPoints to the cached value received from CPT.

<a name="HEADING_1-3-5"></a>

### 1.3.5 Handshaking with data-storage clients

1\) __The new way, using the AWAIT and AAWAIT fields:__

The data-storage client waits for DATA==1, which indicates that the scan is over and the sscan record has finished posting all array fields; writes 1 to the AWAIT field to prevent the sscan record from overwriting array fields before the client has read them; and writes 0 to AWAIT when it is finished reading. One advantage of this handshake is that it allows the sscan record to proceed with the next scan (the sscan record's data arrays are double buffered) until it's time to post data. In this way, the data-storage client can be writing one set of scan data while the sscan record is acquiring the next set.

For *very* fast scans, or a very slow data-storage client, there might not be sufficient time, between the posting of one data set and the acquisition of the next, for the client to write 1 to AWAIT (array wait) field. In this case, you can cause the sscan record automatically to set AWAIT==1, whenever it posts data, by setting the AAWAIT (auto array wait) field to 1. (It's OK if the client also sets AWAIT==1.) __saveData__, the data-storage client included in the synApps __sscan__ module, sets AAWAIT for each of the sscan records it monitors.

NOTE: Because saveData sets AAWAIT for the sscan records it monitors, a scan cannot execute to completion until saveData has written the previous scan's data to disk (or has tried and failed a preset number of times to do this). The __sscan__ module currently does not provide a mechanism by which the end user can turn data storage off and on. Data storage is turned on at boot time, for each sscan record, by telling saveData to monitor that sscan record. The only way to turn data storage off is to edit the startup file and reboot.

 Only one data-storage client can use AWAIT. If you have more than one data-storage client, you must arrange for them to pool their use of the AWAITfield, so that it gets reset to zero only when all have finished. (It's OK if AWAIT gets set to one more than once. Only the first AWAIT==1 write has any effect.)

Note that this AWAIT handshake protects scan data no matter how the sscan record gets executed, unlike the old method described next.

2\) __The old way, using the WAIT, WCNT, and AWCTfields:__

Before the AWAIT field was introduced, the only means of handshaking was an extension of the mechanism by which the sscan record waits for detector triggers to signal completion. In this extension, the sscan record waits until all detector triggers have signalled completion, *and* the field WAIT is equal to zero. This extension's intended purpose is to support detectors that can't signal completion with a callback, but that can write to a PV -- for example, a detector that's implemented as a channel-access client -- and it can still be used for that purpose, while a data-storage client is using it to protect data acquired from an inner-loop scan.

Here's how the handshake works in a data-storage application: The data-storage client notices that an inner sscan record has started a scan (typically, it monitors the DATA field, which is set to zero at the beginning of a scan), and writes a 1 to the outer sscan record's WAIT field. This prevents the outer sscan record from continuing until the client has read the inner scan's data. The client waits for DATA==1, which indicates that new data are available. When the client has finished reading the inner scan's data, it writes a 0 to the outer sscan record's WAIT field, allowing the scan to continue.

If there are several clients that want the scan to WAIT for them, they can all write to the WAIT field. Each 1 increments the scan's wait-count field, WCNT; each 0 decrements it. When WCNT reaches zero, the scan continues.

In fast scans, there might not be time for a client to notice that an inner scan has started and write that 1 to the outer scan's WAIT field before the inner scan completes and is triggered again. In this case, the outer scan can be made automatically to write a 1 to it's own WAIT field whenever it triggers detectors. It will do this if its AutoWaitCounT (AWCT) field is set to 1. In this case, the client must NOT write another 1 to the outer scan's WAIT field (that would increment the wait count to 2), but must only write 0 to the WAIT field to indicate that it is ready for the scan to continue.

If there are N clients, the autoWaitCount can be set to N, and the scan will continue only after N 0's have been written to the WAIT field.

The advantage of the autoWaitCount==0 method is that scans can be performed whether or not a client is available to write to the WAIT field. The disadvantage is that the is not reliable for very fast scans.

Note that this form of handshaking doesn't do a very thorough job of data protection, because it does not directly prevent a sscan record from overwriting its own arrays; it only prevents an outer-loop sscan record from *telling* an inner-loop record to start a new scan line. If the sscan record is executed by some other agent, the WAIT handshake doesn't protect data at all.

<a name="HEADING_1-3-6"></a>

### 1.3.6 Handshaking with CA clients that implement positioners or detectors

A channel-access client can participate in scans driven by the sscan record if two criteria are met:  
1. The client is driven by a PV to which one of the sscan record's positioner or detector-trigger links writes.
2. The client can signal completion in a way that the sscan record understands.

There are two mechanisms the client can use to signal completion that will work with the sscan record:

*putNotify-based completion signalling* - This is the method the sscan record expects everything it drives to use for signalling completion, and it is the method the sscan record itself uses to signal completion. Clients can't signal completion directly using putNotify, because their execution is not managed by EPICS. But they can do it indirectly, by writing to a *busy* record.

A *busy* record is a custom EPICS record, supplied as part of the synApps package, that looks and operates almost exactly like the binary-output ("bo") record, except that it executes its forward link, FLNK, only when its VAL field has the value zero. As it happens, EPICS' putNotify completion mechanism is implemented as part of the processing of forward links, so the fact that the *busy* record allows a CA client to control the execution of its forward link means that the client can control the timing of a putNotify callback.

Here's how it works in practice:

- A developer loads a *busy* record (let's call it xxx:detBusy) into the IOC.
- The sscan record writes a 1 to xxx:detBusy.VAL, causing the record to process.
- The client monitors xxx:detBusy.VAL, and begins some operation when it goes to 1.
- When the client's done, it writes 0 to xxx:detBusy.VAL. This causes the record to process. Because its VAL field is 0, it executes its forward link.
- EPICS understands that a record is finished processing when it executes its forward link, so it sends a completion callback to the sscan record.

Thus, the *busy* record appears to be executing all the time the client actually *is* executing, so the sscan record can know when the client is done.

Very simple, but it does require that a dedicated record be loaded in some IOC. Here's a database that loads a *busy* record:

```
record(busy, "xxx:CCD_Busy")
{
}
```

Many of the databases in synApps contain *busy* records for this purpose, particularly those that act as front ends for State Notation Language (SNL) code. Though motivated by the needs of the sscan record, this completion-signalling capability can be used by any CA client participating in any EPICS application. __WAIT-field handshake with the sscan record__This handshake is intended for CA clients that implement detectors, and that do *not* signal completion using a *busy* record. Here's how it works:

- The client monitors a PV to find out when someone wants it to acquire data.
- The sscan record writes some value to the PV to start acquisition.
- The client writes 1 to &lt;scanrecord&gt;.WAIT, indicating that it wants the sscan record to wait.
- The client performs its data-acquisition task.
- The client writes 0 to &lt;scanrecord&gt;.WAIT, indicating that it's done.

Several clients can use the WAIT field, each write of 1increments a wait count WCNT; each write of 0 decrements WCNT; the sscan record stops waiting when WCNT is decremented to zero. The sscan record doesn't care, by the way, who writes what to WAIT; it simply waits until the number of WAIT==0writes equals the number of WAIT==1 writes.

But what if clients are a little slow to react, and the sscan record checks its wait-count WCNT before the clients have had time to write 1's to it? If this is a problem, you can cause the sscan record to set WCNT at the appropriate time, by setting &lt;scanrecord&gt;.AWCT to the number of slow clients. (But now those slow clients must NOT write 1 to WAIT.)

 <a name="HEADING_1-4"></a>

 1.4. Completion of positioner and detector-trigger operations
--------------------------------------------------------------

As was mentioned previously, all of the process variable names used to identify positioners, detectors, and detector triggers are specified using *reassignable links*. These links are implemented differently than standard EPICS links. Reassignable links are channel-access links implemented with the recDynLink library (originally written by Marty Kraimer and Ned Arnold; modified to use callbacks and currently maintained by Tim Mooney). These links perform writes with the channel-access function, ca\_put\_callback(), and the sscan record expects the resulting callback function to be called only after all processing caused by the write operation has completed. (I'll call this expectation the *completion-callback criterion*, in this documentation, and I'll describe the conditions under which it is met.)

For simple positioners and detectors, this is never a problem. Individual records (using either *synchronous* or *asynchronous* completion strategies, as these terms are defined in the *EPICS Application Developer's Guide*) always satisfy the completion-callback criterion. Special records (motor, scaler, mca, and sscan records) which do not use either synchronous or asynchronous strategies, have been engineered to satisfy the completion-callback criterion simply by having them refrain from calling recGblFwdLink()(i.e., from executing their Forward Links) until the operation they started has finished.

If a positioner or detector is implemented with a collection of linked records all of which individually satisfy the completion-callback criterion, the whole series of records will also satisfy the criterion if all links in the processing chain started by the sscan record's write have the attribute PP, and all of the records that process are scan-passive (i.e., their SCAN fields are set to "Passive"). Databases that do not satisfy this criterion can still satisfy the completion-callback criterion very simply: at least one record in the database must refrain from executing its Forward Link until the operation is finished, and that record must be either be the record written to, or it must be driven by that record via an unbroken series of PP links.

If a positioner or detector is implemented with the help of a CA client, such as an SNL program, see the subsection on "putNotify-based completion signalling" in section [__1.3.6__ Handshaking with CA clients that implement positioners or detectors](#HEADING_1-3-6).

Database developers should note that a PP link from a record in one IOC to a record in another IOC will silently be converted to a CA link, which will not satisfy the completion-callback criterion. In this case, there are two options: the *busy*-record solution, detailed above, and the use of a buffer record that can do a ca\_put\_callback() to make the link between IOCs. I know of six record types that can do a ca\_put\_callback(): the sscan, swait, and sseq records; an ai record with soft asynchronous device support; and the sCalcout and aCalcout records. (The sscan, swait, sseq, sCalcout, and aCalcout records are distributed with synApps. swait, sCalcout, and aCalcout are variants of the calcout record in EPICS base; sseq is a variant of the seq record in EPICS base.)

<a name="HEADING_1-5"></a>

 1.5. Fly scans
---------------

The term "fly scan" is generic for several types of scans that behave and are configured differently, though all involve one or more positioners moving while data are being acquired. Such positioners are said to be in "fly mode". Currently, the sscan record treats fly-mode positioners in essentially the same way for all types of fly scans: they are sent to their start positions (along with any non-fly-mode positioners), and the sscan record waits for all to complete; then, fly-mode positioners are launched toward their end points when detectors are triggered for the first (or only) time, and the sscan record does not wait for them to complete.

Clearly, the speed at which a fly-mode positioner moves is an important consideration for a fly scan, because one wants to know at what position data points are acquired. But the sscan record does not provide any support for reconciling positioner speed with other scan conditions, such as the start and end points, the number of data points to be acquired, and the detector dwell time. This must be done by external software, either before the scan starts, or as part of processing triggered by one of the sscan record's links, such as the before-scan link.

From the viewpoint of the sscan record, there are two types of fly scans: *scalar-mode* fly scans, in which the sscan record directs the scan point by point; and *array-mode* fly scans, in which the scan record hands off the point-by-point direction to some other entity, such as a multichannel scaler. These types are distinguished by the value of ACQT (ACQuisition Type).

<a name="HEADING_1-5-1"></a>

###  1.5.1 Scalar-mode fly scans

If ACQT==SCALAR ("scalar mode", the default), the sscan record will direct the acquisition of NPTS data points individually, as we've been assuming thus far. That is, it will execute NPTS iterations of (move, trigger, read). A scalar-mode scan is a fly scan if one or more positioners have their step mode PVs (P*n*SM) set to FLY. The only difference between this type of scan and the scans we've considered up to now is the motion of those fly-mode positioners.

In scalar mode, the sscan record executes fly scans as follows:

1. Execute the before-scan link. Wait for completion if BSWAIT==Wait.
2. Send all positioners to their start points, and wait for completion.
3. Send fly-mode positioners to their end points. Do not wait for completion.
4. Trigger detectors and wait for completion.
5. Read positioners and detectors.
6. Send non-fly-mode positioners to their next positions and wait for completion.
7. Trigger detectors and wait for completion.
8. Read positioners and detectors.
9. Repeat (6,7,8) until NPTS data points have been acquired, or the scan is aborted.
10. Execute the array-trigger link, and wait for completion.
11. Read the first NPTS elements of any array-valued detectors.
12. If PASM!=STAY, send all positioners to specified positions, and wait for completion. (It is assumed that these commands will redirect any fly-mode positioners that are still moving toward their end points.)
13. Execute the after-scan link. Wait for completion if ASWAIT==Wait.

Scalar-mode fly scans are relatively easy to configure, because the only external conditions that must be set are the positioner speed and the detector dwell time. However, the association between positioner and detector values is typically not as precise or as repeatable as in a step scan. This is because fly-mode positioners are read while they are moving, and because the timing of those reads is not tightly synchronized with the positioner's motion. In the simplest case (no non-fly-mode positioners) the time between positioner reads is the detector dwell time plus the sscan record's per-point overhead time, which varies because the IOC processor is doing other things in addition to scanning.

<a name="HEADING_1-5-2"></a>

###  1.5.2 Array-mode fly scans

If ACQT==1D ARRAY ("array mode"), the sscan record will direct the acquisition of only a single "data point", and that data point will be a set of one-dimensional arrays of length NPTS. In an array-mode scan, all positioners are treated as being in fly mode, whatever the values of their step-mode PVs, because the sscan record writes to them only twice. After moving positioners to their start positions, the sscan record will execute only one (move, trigger, read) sequence.

> Array mode was originally intended merely to read a collection of array-valued detectors (multichannel analyzer spectra), and not to involve positioners at all. However, the sscan record does not erase any existing positioner PVs when array mode is selected, and if any exist then *something* must be done with them, so this documentation must describe it.

In array mode, the sscan record executes fly scans as follows:

1. Execute the before-scan link. Wait for completion if BSWAIT==Wait.
2. Send all positioners to their start points, and wait for completion.
3. Send all positioners to their end points. Do not wait for completion.
4. Trigger detectors and wait for completion.
5. Execute the array-trigger link, and wait for completion.
6. Read the first NPTS elements of any array-valued detectors.
7. If PASM!=STAY, send all positioners to specified positions, and wait for completion. (It is assumed that these commands will redirect any fly-mode positioners that are still moving toward their end points.)
8. Execute the after-scan link. Wait for completion if ASWAIT==Wait.

Because the sscan record doesn't do any point-by-point writes to (or reads from) positioners during an array-mode scan, the data it acquires will represent an average over position, unless some external agent enforces a coordination between positioner values and the acquisition of detector-array elements. The advantage of array-mode fly scans over scalar-mode fly scans is that this coordination can be done externally by hardware that's capable of doing it well; the disavantage is that hardware positioner/detector coordination must be arranged.

In one common implementation of an array-mode scan, detector data are acquired by a multichannel scaler, which is advanced from channel to channel either by a periodic signal, or by pulses from a motor. In contrast to the scalar-mode fly scans discussed above, this type of fly scan can have a very precise and reproducible association between positioner and detector values.

> In releases of the sscan module lower than 2.7, fly mode was implemented slightly differently, as follows (differences are in *italics*) If the sscan record was in scalar mode (ACQT==SCALAR), and a positioner's step mode had the value FLY, the sscan record sent it to the start position at the beginning of a scan, waited for it to get there, *acquired one data point (trigger, read),* sent the positioner to the end position, and began acquiring the remaining data points while the positioner was travelling to the end position. *If the record was in array mode (ACQT==1D ARRAY), positioners that were not explicitly in fly mode (PnSM!=FLY) were not sent to the end position at all.*

  
  
  
- - - - - -

<a name="HEADING_2"></a>

sscan-Record Fields
===================

- - - - - -

Many options are available to control the execution of a scan. All parameters for a particular sscan record must be configured prior to initiating the scan, as the sscan record will not allow most fields to be written to while a scan is in progress. However, in a multidimensional scan, outer scans can modify the parameters of inner scans, because at the time an outer sscan record is writing to positioners, all inner sscan records are idle. You should use caution in programming such self modifying scans, because clients displaying or analyzing multidimensional scan data may have trouble dealing with parameters changing during a scan. In this documentation, many of the sscan-record fields will be listed in tables containing the following informational headings:

__Field__The name of the sscan-record field__Summary__Basic purpose of the field__Type__Data type of the field. If the field is a menu, the menu choices (text strings) are listed in quotes. (Don't include the quotes when you write to the field.) Note that if you write a numeric value to a menu field, the number will be interpreted as an index into the list of menu choices. The first item in the list has the index 0.__DCT__Can this field be modified by database-configuration tools?__Initial/Default__Value if the field is not specified in the .db file. If the field is a menu, the text string will be shown, followed by the corresponding index. __Read__Can user read this field?__Modify__Is user ever allowed to write to this field? (Note that the sscan record will reject writes to certain otherwise writable fields while a scan is underway.)__Posted__If the record should modify the field, will the new value be posted?__PP__Does a channel-access write to this field cause the record to process?<a name="HEADING_2-1"></a>

2.1. Control Fields
-------------------

| Field | Summary | Type | DCT | Initial/Default | Read | Modify | Posted | PP |
|---|---|---|---|---|---|---|---|---|
| NPTS | Number of Points | LONG | Yes | 100 | Yes | Yes | Yes | No |
| MPTS | Maximum Number of Points | LONG | Yes | 100 | Yes | No | No | No |
| PASM | Positioner After-Scan Mode | Menu ("STAY", "START POS", "PRIOR POS", "PEAK POS", "VALLEY POS", "+EDGE POS", "-EDGE POS", CNTR OF MASS) | Yes | "STAY" (0) | Yes | Yes | No | No |

> PASM allows the user to control where positioners are left after a scan is finished. Here are the possibilities:  "STAY"Do nothing. Leave positioners where they were when the last data point was acquired. "START POS"Go the the position of the first data point acquired. "PRIOR POS"Go to the position they occupied prior to the scan. "PEAK POS"Attempt to find the highest point in the data from the detector specified by the REFD field. If a highest point is found, go to its position, else "STAY". "VALLEY POS"Attempt to find the lowest point in the data from the detector specified by the REFD field. If a lowest point is found, go to its position, else "STAY". "+EDGE POS"Take the derivative of the REFD data, then do "PEAK POS". "-EDGE POS"Take the derivative of the REFD data, then do "VALLEY POS". "CNTR OF MASS"Like "PEAK POS", but sends positioner(s) the position of the center of mass of the data, as calculated with reference to positioner 1. Note that the calculated center of mass depends on the distribution of positioner data. If multiple positioners are involved in a scan, they will not, in general, have the same center of mass.

| Field | Summary | Type | DCT | Initial/Default | Read | Modify | Posted | PP |
|---|---|---|---|---|---|---|---|---|
| REFD | Reference detector for After-Scan mode | SHORT | Yes | 1 | Yes | Yes | No | No |
| BSPV | Before-Scan Process Variable link | STRING \[40\] | Yes | Null | Yes | Yes | No | No |
| BSNV | BSPV Name Valid | MENU("PV OK","No PV", "PV NoRead", "PV illegal1", "PV NoWrite", "PV illegal2", "PV BAD")   "PV OK" and "No PV" are good states; all others will prevent a scan from starting | No | 0 | Yes | No | Yes | No |
| BSCD | Before-Scan Command Data | FLOAT | Yes | 1 | Yes | Yes | No | No |
| BSWAIT | Wait for completion? | MENU ("YES", "NO") | Yes | "YES" (0) | Yes | Yes | Yes | No |

> BSPV, BSNV, BSCD, and BSWAIT allow the user to specify a PV to be written to before every scan starts. (If the sscan record is part of a multidimensional scan, each participating sscan record has its own set of before-scan parameters, so you can cause an action to occur before the whole scan starts, and before each nested loop starts.) To specify a before-scan PV write, write the name of the PV to BSPV, and the value to be written to BSCD. If you want the sscan record to wait for completion of processing triggered by the write, before going on with the rest of the scan, set BSWAIT to "YES" (1). You can check to status of the link by looking at BSNV. If the link is good, BSNV will be zero. >  > Note that the before-scan link is permitted to change only selected fields of its own sscan record: it cannot change PV names (i.e., links); and it cannot change the acquisition type (ACQT) or mode (ACQM). If this sscan record is part of a multidimensional scan, the before-scan link can change any field of a lower-level sscan record (i.e., one that its record it driving), and no field of a higher level scan record.

| Field | Summary | Type | DCT | Initial/Default | Read | Modify | Posted | PP |
|---|---|---|---|---|---|---|---|---|
| ASPV | After-Scan Process Variable link | STRING \[40\] | Yes | Null | Yes | Yes | No | No |
| ASNV | ASPV Name Valid | MENU("PV OK","No PV", "PV NoRead", "PV illegal1", "PV NoWrite", "PV illegal2", "PV BAD")   "PV OK" and "No PV" are good states; all others will prevent a scan from starting | No | 0 | Yes | No | Yes | No |
| ASCD | After-Scan Command Data | FLOAT | Yes | 1 | Yes | Yes | No | No |
| ASWAIT | Wait for completion? | MENU ("YES", "NO") | Yes | "YES" (0) | Yes | Yes | Yes | No |

> ASPV, ASNV, ASCD, and ASWAIT allow the user to specify a PV to be written to after every scan is finished. (If the sscan record is part of a multidimensional scan, each participating sscan record has its own set of after-scan parameters, so you can cause an action to occur after the whole scan is done, and after each nested loop is done.) To specify an after-scan PV write, write the name of the PV to ASPV, and the value to be written to ASCD. If you want the sscan record to wait for completion of processing triggered by the write, before going on with the rest of the scan wrap-up, set ASWAIT to "YES" (1). You can check to status of the link by looking at ASNV. If the link is good, ASNV will be zero. >  > Note that the after-scan link is permitted to change only selected fields of its own sscan record: it cannot change PV names (i.e., links); and it cannot change the acquisition type (ACQT) or mode (ACQM). If this sscan record is part of a multidimensional scan, the after-scan link can change any field of a lower-level sscan record (i.e., one that its record it driving), and no field of a higher level scan record.


| Field | Summary | Type | DCT | Initial/Default | Read | Modify | Posted | PP |
|---|---|---|---|---|---|---|---|---|
| A1PV | Array-read trigger 1 PV Name | STRING \[40\] | Yes | Null | Yes | Yes | No | No |
| A1NV | A1PV Name Valid | MENU("PV OK","No PV", "PV NoRead", "PV illegal1", "PV NoWrite", "PV illegal2", "PV BAD")   "PV OK" and "No PV" are good states; all others will prevent a scan from starting | No | 0 | Yes | No | Yes | No |
| A1CD | A1 Cmnd | FLOAT | Yes | 1 | Yes | Yes | No | No |

> A1PV, A1NV, and A1CD allow the user to specify a PV to be written to before the sscan record tries to read array-valued data. (It may be necessary, for example, to cause data to be read from hardware into a set of EPICS PVs, or to execute some calculation on the data, before the sscan record acquires it. The sscan record will wait for processing triggered by this write to complete before reading arrays. To specify an array-preparation PV write, write the name of the PV to A1PV, and the value to be written to A1CD. You can check to status of the link by looking at A1NV. If the link is good, A1NV will be zero.


| ATIME | Array post time period | FLOAT | Yes | 0.0 | Yes | Yes | No | No |
| COPYTO | Copy Last Array Point Thru This Element Number | LONG | Yes | 0 | Yes | Yes | No | No |

> These fields control the posting of array data during a scan. ATIME is the minimal time period in seconds between array postings during a scan. If ATIME is greater than 0.1 (seconds), and if more than this time has elapsed since the last array posting of this scan's data, then the current-data arrays will be posted after the next data point has been acquired. __NOTE__: Posting current-data arrays also causes completed-scan data arrays to be posted (uselessly, because they were posted at the end of the previous scan, and the data they contain has not changed). Some display or storage clients may have a problem with this new behavior of the sscan record. If so, there are two alternatives: 1) leave ATIME at its default value of 0.0, or 2) have the client specify DBE\_LOG when it subscribes to the data array (using ca\_add\_event() or ca\_create\_subscription()). (If a client does not monitor data arrays, but instead uses ca\_get() to read them, then it won't care how often they are posted.) >  > Some data-display clients (notably, MEDM) cannot use a PV to tell them how many valid data points are being sent. This results in bizarre looking plots that can be made to look correct by repeating the last valid array values to fill the unused array elements. This can be a time-consuming process, so by default it's only done once, at the end of a scan. But arrays posted during a scan also will not be plotted correctly by such clients, so you can specify that the last valid array elements be copied for arrays posted during a scan, by setting COPYTO to the number of array elements in the client's data buffer. If COPYTO == 0, no copying will be done; if COPYTO == -1, the last value will be copied to all unused array elements in the sscan record's data buffers. If COPYTO is set to a value larger than MPTS, the value used will be MPTS.

<a name="HEADING_2-2"></a>

2.2. Positioner Fields
----------------------

Each sscan record can control up to four *positioners*, by which it sets conditions under which data will be acquired. A positioner is any numeric PV to which the sscan record can write, and you specify that a positioner is to be scanned by typing its PV name into one of the sscan record's fields PnPV. If the value written to the PV (the *desired* value) might not accurately indicate the true value of the underlying hardware positioner, you can specify a readback PV to retrieve a more accurate value. I'll sometimes call the PV that the sscan record writes to the "drive" PV. If no readback PV is specified, the drive PV will also be used as the readback PV. There are three possible modes for determining desired values for a positioner: LINEAR, TABLE, and FLY. Each positioner has its own mode PV, and you specify which mode you want for a positioner by setting its PnSM field (e.g., P1SM for positioner 1). If PnSM== LINEAR, the desired values are determined from parameters such as start position, step increment, number of points, and end position. If PnSM==TABLE, the desired values are found in an array (PnPA), which must have been loaded into the sscan record prior to initiating a scan. If PnSM==FLY, the desired values are the start and end positions for LINEAR mode.

> In addition to the positioner scan modes PnSM, there is another sscan record field that influences how positioners are scanned. The ACQT (acquisition type) field affects all positioners, and either directs them to behave as described above (when ACQT==SCALAR), or to all be effectively in fly mode (when ACQT==1D ARRAY. I'll sometimes refer to this as "array mode"). See the "Fly Scans" section for more detail.

For each positioner, the user may specify a process variable in the R1PV-R4PV fields that corresponds to the actual (or measured) position of the motor. If this readback field is configured, the sscan record will confirm after each movement that the readback position differs by no more than a specified value from the desired position. The difference limit is specified in the R1DL -R4DL fields. If it's zero, no check is performed. Otherwise, if the difference limit is exceeded, the scan will abort and the record will go into an alarm state. A text field within the record (SMSG) will inform the operator of the error condition.

The positioner-readback field normally contains the name of a PV from which readback values are read, but it may also contain the static text "TIME", or "time". In this case, the sscan record sets the scalar readback field R*n*CV to the time in seconds since the beginning of the scan, and fills the readback array P*n*RA with those values.

#### Drive Fields

For *n* in \[1..4\]:

| Field | Summary | Type | DCT | Initial/Default | Read | Modify | Posted | PP |
|---|---|---|---|---|---|---|---|---|
| P*n*PV | Positioner *n* Process Variable ame | STRING \[40\] | Yes | Null | Yes | Yes | No | No |
| P*n*NV | P*n*PV Name Valid | MENU("PV OK","No PV", "PV NoRead", "PV illegal1", "PV NoWrite", "PV illegal2", "PV BAD")   "PV OK" and "No PV" are good states; all others will prevent a scan from starting | No | 0 | Yes | Yes | Yes | No |
| P*n*SM | Positioner *n* step-mode | Menu ("LINEAR", "TABLE", "FLY") | Yes | "LINEAR" (0) | Yes | Yes | No | No |
| P*n*AR | Positioner *n* Absolute/Relative Mode | Menu ("ABSOLUTE", "RELATIVE") | Yes | "ABSOLUTE" (0) | Yes | Yes | No | No |
| P*n*DV | Pos. *n* Desired Value | DOUBLE | No | 0 | Yes | No | Yes | No |
| P*n*LV | Pos. *n* Last Value | DOUBLE | No | 0 | Yes | No | No | No |
| P*n*DV | Pos. *n* Desired Value | DOUBLE | No | 0 | Yes | No | Yes | No |
| P*n*LV | Pos. *n* Last Value | DOUBLE | No | 0 | Yes | No | No | No |
| P*n*EU | Positioner *n* Eng. Units | STRING \[16\] | Yes | 16 | Yes | Yes | No | No |
| P*n*HR | Pos. *n* High Range | DOUBLE | Yes | 0 | Yes | Yes | No | No |
| P*n*LR | Pos. *n* Low Range | DOUBLE | Yes | 0 | Yes | Yes | No | No |
| P*n*PR | Pos. *n* Precision | SHORT | Yes | 0 | Yes | Yes | No | No |
| P*n*PA | P*n* Step Array | DOUBLE\[\] | No | 0 | Yes | Yes | No | No |
| P*n*PP | P*n* Position before scan | DOUBLE | No | 0 | Yes | No | No | No |

#### Readback fields

For *n* in \[1..4\]:

| Field | Summary | Type | DCT | Initial/Default | Read | Modify | Posted | PP |
|---|---|---|---|---|---|---|---|---|
| R*n*PV | Readback *n* Process Variable | STRING \[40\] | Yes | Null | Yes | Yes | No | No |
| R*n*NV | Readback */n* Name Valid | MENU("PV OK","No PV", "PV NoRead", "PV illegal1", "PV NoWrite", "PV illegal2", "PV BAD")   "PV OK" and "No PV" are good states; all others will prevent a scan from starting, though "PV NoWrite" is impossible for this readback PV | No | 0 | Yes | Yes | Yes | No |
| R*n*DL | Readback *n* Difference Limit | DOUBLE | Yes | 0 | Yes | Yes | No | No |
| R*n*CV | Readback *n* Current Value | DOUBLE | No | 0 | Yes | No | Yes | No |
| R*n*LV | Readback *n* Last Value | DOUBLE | No | 0 | Yes | No | No | No |
| P*n*RA | P*n* Readback Array | DOUBLE\[\] | No | 0 | Yes | No | Yes | No |
| P*n*CA | P*n* Current Readback Array | DOUBLE\[\] | No | 0 | Yes | No | Yes | No |

Clients that display scan data will most likely be interested in only one of the two positioner-array fields: P*n*CA or P*n*RA. These array fields are backed by the same double-buffered arrays, so they cannot be posted separately.

P*n*CA will yield data from the scan that currently is executing. This array can be read at any time during the scan, and it may be posted with the mask, DBE\_VALUE, while the scan is in progress. (ATIMEcontrols this.) When the scan completes, P*n*CA will be posted with the mask, DBE\_VALUE\|DBE\_LOG.

P*n*RA will yield data from the most recently completed scan. This array's data will remain available while the next scan's data are being acquired, and will become unavailable when that scan completes. Clients interested only in completed-scan data should use this field. Clients that monitor this field should always specify the mask, DBE\_LOG, in their ca\_add\_event() or ca\_create\_subscription() call. If this field is monitored with the mask, DBE\_VALUE, the client may receive multiple postings of the same data.

<a name="HEADING_2-2-1"></a>

###  2.2.1 LINEAR Mode

If a positioner's step-mode field (e.g., P1SM) has the value LINEAR, a scan can be fully defined by three parameters, e.g., the start position (P1SP), the step increment (P1SI), and the number of data points (NPTS). A scan involving *N* positioners is defined by merely 2*N*+1 parameters, since NPTS applies to all positioners. For the convenience of interactive users, and to support channel access clients that define scans differently, the first positioner can be specified by as many as six parameters: starting position (P1SP), ending position (P1EP), center position (P1CP), scan width (P1WD), step increments (P1SP), and NPTS. For the other three positioners, the same parameters are available minus the NPTS field, since that applies to all. The parameters that pertain to the same positioner are a set. The record imposes an upper limit (MPTS) on NPTS. Both MPTS and NPTS are configured by the user. The positioner width, configurable in the P1WD -P4WD fields, may be negative. For *n* in \[1..4\]:

| Field | Summary | Type | DCT | Initial/Default | Read | Modify | Posted | PP |
|---|---|---|---|---|---|---|---|---|
| P*n*SP | Positioner *n* Starting Point | DOUBLE | Yes | 0 | Yes | Yes | Yes | No |
| P*n*EP | Positioner *n* Ending Point | DOUBLE | Yes | 0 | Yes | Yes | Yes | No |
| P*n*CP | Positioner *n* Center Point | DOUBLE | Yes | 0 | Yes | Yes | Yes | No |
| P*n*WD | Positioner *n* Width | DOUBLE | Yes | 0 | Yes | Yes | Yes | No |
| P*n*SI | Positioner *n* Step Increment | DOUBLE | Yes | 0 | Yes | Yes | Yes | No |

Some of these fields can be redundant. For instance, the positioner width (P1WD -P4WD) is simply the distance from the starting position to the ending position (P*n*EP - P*n*SP). The record calculates redundant parameters for the same set, if the parameters are left undefined. However, the user can still configure the redundant parameters anyway.

There is no unique prescription for removing inconsistencies among redundant parameters, and no hard-coded set of preferences among parameters is likely to please everyone. Therefore, the sscan record allows the user to "freeze" parameters with flags so that they will not be changed by the record's internal attempts to ensure consistency among the parameter set. Frozen parameters can be changed by the user and by any other client, but not by the record. It is the user's responsibility to ensure that frozen parameters do not prevent freely specifying unfrozen parameters. For example, if both P*n*SI and NPTS are frozen, changes to P*n*WD will be rejected. Similarly, if both P*n*SP and P*n*CP are frozen, changes to P*n*EP and P*n*WD will have no effect. By default, P*n*SP , P*n*SI , and NPTS are frozen. When the record cannot adjust the parameters to be consistent, a flag is raised in the alert field (ALRT) and a message reported in the state message field (SMSG).

The freeze flag override field (FFO) has two choices: Use F-Flags and Override. Override causes the current settings of all the freeze flags to be saved and monitors to be called for those that have changed. Use F-Flags causes the flags saved with the Override command to be restored if any have changed. Changing the choice of this field at run-time causes the special record support routines to perform these actions. So if Override is chosen at run-time, then all current settings are saved, and can be restored at a later time by changing the FFO field to Use F-Flags.

For *n* in \[1..4\]:

| Field | Summary | Type | DCT | Initial/Default | Read | Modify | Posted | PP |
|---|---|---|---|---|---|---|---|---|
| FPTS | Freeze Flag for NPTS | Menu ("NO", "FREEZE") | Yes | "FREEZE" (1) | Yes | Yes | No | No |
| FFO | Freeze Flag Override | Menu ("USE F-FLAGS", "OVERRIDE") | Yes | "USE F-FLAGS" (0) | Yes | Yes | No | No |
| P*n*FS | Positioner *n* Freeze Flag for P*n*SP | Menu ("NO", "FREEZE") | Yes | "NO" (0) | Yes | Yes | No | No |
| P*n*FE | Positioner *n* Freeze Flag for P*n*EP | Menu ("NO", "FREEZE") | Yes | "NO" (0) | Yes | Yes | No | No |
| P*n*FI | Positioner *n* Freeze Flag for P*n*SI | Menu ("NO", "FREEZE") | Yes | "NO" (0) | Yes | Yes | No | No |
| P*n*FC | Positioner *n* Freeze Flag for P*n*CP | Menu ("NO", "FREEZE") | Yes | "NO" (0) | Yes | Yes | No | No |
| P*n*FW | Positioner n Freeze Flag for P*n*WD | Menu ("NO", "FREEZE") | Yes | "NO" (0) | Yes | Yes | No | No |

Although this approach may seem to present the user with an overwhelming number of choices when it comes to linear scans, it should be noted that by default the user only has to configure NPTS, and the starting position (P*n*SP) and the step increment (P*n*SI) fields for each positioner in order to fully define the scan of a positioner. The operator interface (usually MEDM or another CA client) need only present the user with these fields. However, by changing the freeze flags from the defaults and presenting the user with different fields to fill in, the scan can be defined in a completely flexible way. The result is that a simple scan can be defined easily, but advanced users are not limited in flexibility.

<a name="HEADING_2-2-2"></a>

### 2.2.2 TABLE Mode

If a positioner's step-mode field (e.g., P1SM) has the value TABLE mode, the user specifies all positions to be visited during the scan by writing them into an array (e.g., P1PA) prior to the start of a scan. These arrays are used only in TABLE mode. For *n* in \[1..4\]:

| Field | Summary | Type | DCT | Initial/Default | Read | Modify | Posted | PP |
|---|---|---|---|---|---|---|---|---|
| P*n*PA | Positioner *n* Position Array | DOUBLE array | No | Null | Yes | Yes | Yes | No |

To load an array of positions into P*n*PA, you can use any channel-access client that knows how to write to numeric arrays. There are several versions of the command-line program caput that can do this. For one version, you specify the switch `-m`, and write a comma-separated list of values:

```
caput -m 2idb1:scan1.P1PA 0.,1.,2.
```

works. For another version, you specify the flag `-a`, specify the number of values to be written, and specify the values separated by spaces: 
```
caput -a 2idb1:scan1.P1PA 3 0. 1. 2.
```
You might also do this from Python, using [pyepics](http://cars9.uchicago.edu/software/python/pyepics3):

```
wheaties% setenv LD_LIBRARY_PATH /home/oxygen/MOONEY/epics/base-3.14.12.1/lib/solaris-sparc
wheaties% python
>>> import epics
>>> epics.caput("xxx:scan1.P1PA", [1,2,3,4,5,6,7])
>>> epics.caget("xxx:scan1.P1PA")
array([ 1.,  2.,  3.,  4.,  5.,  6.,  7.,  0.,  0.,  0.,  0.,  0.,  0.,
...
```

<a name="HEADING_2-2-3"></a>

### 2.2.3 FLY Mode

If a positioner's step-mode field (e.g., P1SM) has the value FLY, the positioner is said to be in "fly mode", and it will make only two motions during the scan. The first motion is the same as that of a linear- or table-mode positioner: the sscan record sends the positioner to its start point, and waits for it to get there. The next motion is different: when the sscan record triggers detectors for the first time, it also launches fly-mode positioners to their end points. The sscan record doesn't wait for fly-mode positioners to reach their end points, and fly-mode positioners are not commanded again, unless the Positioner After-Scan Mode (PASM) requires this (for example, by specifying that all positioners return to their pre-scan positions). Note that the PV ACQT (ACQuisition Type) also affects positioner motion: when ACQT==1D ARRAY, all positioners are effectively in fly mode, because the sscan record will acquire only one (array valued) data point. In this case, the PVs P*n*SM serve only to determine the starting and ending points of the positioners' motions, as detailed in the following table for positioner 1:

| scan mode (P1SM) | acquisition type (ACQT) | start point | end point | motion |
|---|---|---|---|---|
| LINEAR | SCALAR | P1SP | P1EP | point-to-point |
| TABLE | SCALAR | P1PA\[0\] | P1PA\[npts-1\] | point-to-point |
| FLY | SCALAR | P1SP | P1EP | fly |
| LINEAR | 1D ARRAY | P1SP | P1EP | fly |
| TABLE | 1D ARRAY | P1PA\[0\] | P1PA\[npts-1\] | fly |
| FLY | 1D ARRAY | P1SP | P1EP | fly |

While fly-mode positioners are moving toward their end points, the sscan record goes through all the normal scan phases -- triggering detectors and waiting for them to finish, reading any detectors and positioner readbacks, sending any non-fly-mode positioners to their next positions and waiting for them to get there.

If a fly-mode positioner has a specified readback PV (R*n*PV), its value will be read during the scan, but in many cases the value will be only approximately correct, because the positioner is in motion during the read, and because the sscan record doesn't cause the readback PV to process. If the positioner is a motor, for example, and the readback PV is posted periodically, the sscan record will read values that are imperfectly synchronized with the scan.

<a name="HEADING_2-3"></a>

2.3. Detector-Trigger Fields
----------------------------

If valid process variable names are entered into the detector trigger fields (T1PV-T4PV ) fields, the sscan record will write the specified command data (the floating point numbers T1CD-T4CD) to those process variables between the positioning phase and the data acquisition phase. If no detector trigger field contains a valid PV, the sscan record will skip this step and acquire the data immediately.For *n* in \[1..4\]:

| Field | Summary | Type | DCT | Initial/Default | Read | Modify | Posted | PP |
|---|---|---|---|---|---|---|---|---|
| T*n*PV | Detector Trigger *n* Process Variable | STRING \[40\] | Yes | Null | Yes | Yes | No | No |
| T*n*NV | Trigger *n* Name Valid | MENU("PV OK","No PV", "PV NoRead", "PV illegal1", "PV NoWrite", "PV illegal2", "PV BAD")   "PV OK" and "No PV" are good states; all others will prevent a scan from starting | No | 0 | Yes | Yes | Yes | No |
| T*n*CD | Trigger *n* Command Data | FLOAT | Yes | 1 | Yes | Yes | No | No |

<a name="HEADING_2-4"></a>

2.4. Delay Fields
-----------------

Generally, after the sscan record has written to positioners and waited for all positioners to declare themselves done, it waits an additional settling time, specified in seconds by the PDLY field, before entering the next scan phase. Similarly, after detector triggers have declared themselves done, the sscan record waits for DDLY seconds before reading positioner and detector data. If no positioners are defined, then PDLY is ignored. If no detector triggers are defined, then DDLY is ignored. PDLYdoes not apply to after-scan positioner motions.

<a name="HEADING_2-5"></a>

2.5. Client Handshaking Fields
------------------------------

Immediately before data are to be read from positioners and detectors, the sscan record checks the WCNT field. If this field is nonzero, the sscan record waits until it gets set to zero before reading data and continuing with the scan. The WCNT is not directly writable by clients. Instead, a client wanting to put a hold on the scan writes a 1 to the WAIT field, which increments WCNT by one. When the client is ready for the scan to continue, it writes a 0 to the WAIT field, which decrements the WCNT field. This mechanism allows several clients independently to handshake with the sscan record, and it is intended or two purposes: 1\) A data-storage client can put a hold on a sscan record whose data it is writing by writing to the AWAIT field. This hold doesn't prevent the record from executing, or even from acquiring new data, but it does prevent the record from switching data buffers.

2\) In a multidimensional scan, a data-storage client can put a hold on scan2 while it is writing data from scan1, by writing to the WAIT field. This relatively inefficient handshake is still used by some data-storage clients.

3\) A data-acquisition client that doesn't declare completion via EPICS' putNotify mechanism can declare completion using WAIT.

A client may not be able to write quickly enough to WAIT to ensure that the scan holds before data acquisition. In this case, the client can cause the sscan record to write automatically to WCNT whenever detectors are triggered, by incrementing the value of the AWCT field. The client must remember to decrement AWCT before exiting, otherwise scans will hang waiting for a nonexistent client.

A client may not be able to write quickly enough to AWAIT to ensure that the scan holds before switching buffers. In this case, the sscan record can be made to write automatically to AWAIT whenever data are posted, by setting the AAWAIT field to 1.

| Field | Summary | Type | DCT | Initial | Read | Modify | Posted | PP |
|---|---|---|---|---|---|---|---|---|
| WAIT | Wait for client | SHORT | No | 0 | Yes | Yes | No | No |
| WCNT | Wait count | SHORT | No | 0 | Yes | No | Yes | No |
| AWCT | Auto Wait | SHORT | No | 0 | Yes | Yes | No | No |
| WTNG | Waiting | SHORT | No | 0 | Yes | No | Yes | No |
| AWAIT | Waiting for data-storage client | SHORT | No | 0 | Yes | Yes | Yes | Yes |
| AAWAIT | AutoWait for data-storage client | MENU ("NO","YES") | Yes | 0 | Yes | Yes | No | No |

  
- - - - - -

<a name="HEADING_2-6"></a>

2.6 Detector Fields
-------------------

- - - - - -

Each sscan record can acquire data from up to 74 process variables (70 detector signals, D01-D70, and four positioner readbacks, R1-R4) at each point in the scan. These data will most commonly be from a detector or from a position readback (which would record the actual motor positions at each point and could then be compared to the desired position array). Although positioner readbacks, R1-R4, are normally used to confirm the position at which data actually were acquired (as opposed to the position to which the sscan record *told* a positioner to go), they can be used to record any data. These four variables are the only place to record double-precision scan data. Note that these readbacks are not full-fledged detectors, because the sscan record currently cannot read into them from a array-valued PV's, as it can for actual detectors.

The scan results will most frequently be read as position arrays (P1RA-P4RA) and detector arrays (D01DA-D70DA).

A one-dimensional scan is complete when the BUSY field goes back to zero (during the scan its value is 1). A client program monitoring the scan can read the position and data arrays when the DATA field is set to 1. (The client could have a monitor set on the data-array fields so the record will post them when the scan is finished.)

For two-dimensional scans, the client should read the arrays from the scan1 record after the completion of each inner scan and associate these data with the current outer-scan information. (Let's call the inner scan 'x', and the outer scan 'y'.) This will allow the client to display data after each x scan. The sscan record will buffer the data for only one x scan, so the client must read the arrays before the next x scan is completed. If the scan is too fast for this, see [section 1.3.4 - Handshaking with data-storage clients](#HEADING_1-3-4)

During slow scans, the application program may want to display scan progress point-by-point. The sscan record posts monitors on fields that it updates each point, but it doesn't post point-by-point monitors faster than 20 times per second. If a scan is proceeding at a rate less than 20 points per second, every point will be posted. If a scan is proceeding at 100 steps per second, scalar values will be posted approximately every 5th point. In either case, the array data will contain every point at the completion of the scan.

Special Acquisition Parameters:

| Field | Summary | Type | DCT | Initial/Default | Read | Modify | Posted | PP |
|---|---|---|---|---|---|---|---|---|
| version 5.16 and earlier: |
| ACQM | Acquisition Mode | Menu ("NORMAL", "ACCUMULATE", "ADD TO PREV", "GET ARRAYS") | Yes | "NORMAL" (0) | Yes | Yes | No | No |
| version 5.17 and later: |
| ACQM | Acquisition Mode | Menu ("NORMAL", "ACCUMULATE", "ADD TO PREV") | Yes | "NORMAL" (0) | Yes | Yes | No | No |
| ACQT | Acquisition Type | Menu ("SCALAR", "1D ARRAY") | Yes | "SCALAR" (0) | Yes | Yes | No | No |

Data and related PV's:
For *nn* in \[01..70\] (e.g., "D01PV", "D02PV", ... "D70PV")

| Field | Summary | Type | DCT | Initial/Default | Read | Modify | Posted | PP |
|---|---|---|---|---|---|---|---|---|
| D*nn*PV | data *nn* Process Variable name | STRING \[40\] | Yes | Null | Yes | Yes | No | No |
| D*nn*NV | data *nn* Name Valid | MENU("PV OK","No PV", "PV NoRead", "PV illegal1", "PV NoWrite", "PV illegal2", "PV BAD")   "PV OK" and "No PV" are good states; all others will prevent a scan from starting, though "PV NoWrite" is impossible for these readback PVs | No | 0 | Yes | Yes | Yes | No |
| D*nn*DA | Detector *nn* End-Of-Scan Data Array | FLOAT\[ \] | No | Null | Yes | No | Yes | No |
| D*nn*CA | Detector *nn* Current-Data Array | FLOAT\[ \] | No | Null | Yes | No | Yes | No |
| D*nn*EU | Detector *nn* Eng. Units | STRING \[16\] | Yes | 16 | Yes | Yes | No | No |
| D*nn*HR | Det. *nn* High Range | DOUBLE | Yes | 0 | Yes | Yes | No | No |
| D*nn*LR | Det. *nn* Low Range | DOUBLE | Yes | 0 | Yes | Yes | No | No |
| D*nn*PR | Det. *nn* Precision | SHORT | Yes | 0 | Yes | Yes | No | No |
| D*nn*CV | Detector *nn* Current Value | FLOAT | No | 0 | Yes | No | Yes | No |
| D*nn*LV | Detector *nn* Last Value | FLOAT | No | 0 | Yes | No | No | No |

  
  
  
- - - - - -

<a name="HEADING_2-7"></a>

2.7 Execution fields
--------------------

- - - - - -

A scan is started when a client writes 1 to the EXSC field.

Prior to beginning an actual scan, the record can be commanded to check the scan parameters to ensure that all positioner requests are within positioner limits. This is done by writing 1 to the CMND field. The record will do a "dry run" by calculating every positioner value (or looking it up in the table) and comparing it with the high range and low range values (P1HR-P4HR and P1LR-P4LR) associated with that positioner's Process Variable. (Drive limits are an attribute of most process variables). If any step would exceed the drive limits, the operator is notified via the SMSG field. (Note that the sscan record does not retrieve positioner limits whenever they are changed, but only when the sscan record connects (makes a link) to the positioner. The sscan record disconnects and reconnects to positioners at the beginning of every scan for this reason, though it declines to do this if the most recent scan ended less than `sscanRecordLookupTime` seconds ago. The default value of `sscanRecordLookupTime` is 1.)

| Field | Summary | Type | DCT | Initial/Default | Read | Modify | Posted | PP |
|---|---|---|---|---|---|---|---|---|
| EXSC | Execute Scan Flag | SHORT | No | 0 | Yes | Yes | Yes | No |
| CMND | Command Field | ENUM | No | 0 | Yes | Yes | Yes | No |

The command (CMND) field supports eight commands, as follows:

| CMND | Command |
|---|---|
| 0 | Clear the State Message field (SMSG) |
| 1 | Execute a "dry run", checking positioners against their limits |
| 2 | Show a preview of the scan, using the positioner and detector arrays DnnCA and PnCA: Write data-point numbers to DnnCA, and corresponding positioner values to PnCA. |
| 3 | Clear all PVs, freeze flags, modes, switches, etc. |
| 4 | Clear all positioner-name PVs, freeze flags, modes, and switches. |
| 5 | Clear positioner-name PVs. |
| 6 | Clear all positioner-name and readback-name PVs, freeze flags, modes, and switches. |
| 7 | Clear positioner-name and readback-name PVs. |

  
  
  
- - - - - -

<a name="HEADING_2-8"></a>

2.8 Status/Progress Fields
==========================

- - - - - -

These fields are used to process the record, to implement monitors for certain fields, and/or to keep track of data for processing and/or for the operator. None of these fields are configurable by a database configuration tool. Most of them can be accessed at run-time, and many can be modified at run-time. The Current Point (CPT) field contains the current point of an active scan.

 The BUSY field indicates whether (1) or not (0) a scan is in progress.

The DATA field indicates the state of the data arrays. DATAis set to 0 at the beginning of a scan, and is set to 1 after the data arrays have been posted. Note that data arrays are not posted during a scan, but only at the end.

The VAL field is used only as a progress indicator. It is posted after all point-by-point PVs (e.g., R1CV, D01CV) have been posted. (So, if a PV you're interested in hasn't been posted by the time you get the VAL-field monitor, that PVs value hasn't changed since the last time it was posted.)

The State Message (SMSG) field holds a message sent by the record that alerts the operator to an error condition. It can be cleared by writing a 0 to the Command (CMND) field.

The Alert (ALRT) field is a flag which indicates if an error condition currently exists. 1 means YES; 0, NO. The cause of the condition will be displayed in the SMSG field.

| Field | Summary | Type | DCT | Initial/Default | Read | Modify | Posted | PP |
|---|---|---|---|---|---|---|---|---|
| CPT | Current Point | LONG | No | 0 | Yes | No | Yes | No |
| BUSY | Scan-is-busy Flag | SHORT | No | 0 | Yes | No | Yes | No |
| DATA | Data-are-ready flag | SHORT | No | 0 | Yes | No | Yes | No |
| VAL | Value Field | DOUBLE | No | 0 | Yes | Yes | No | No |
| SMSG | State Message | STRING \[40\] | No | Null | Yes | Yes | Yes | No |
| ALRT | Alert Field | UCHAR | No | 0 | Yes | No | Yes | No |

The scan-phase (FAZE) field indicates in which phase of a scan the record currently is. The possible phases are as follows:

| phase | message | meaning |
|---|---|---|
| 0 | IDLE | Nothing is going on. |
| 1 | INIT\_SCAN | A scan is starting |
| 2 | DO:BEFORE\_SCAN | The next thing to do is trigger the before-scan link. |
| 3 | WAIT:BEFORE\_SCAN | The before-scan link has been triggered. We're waiting for its callback to come in. |
| 4 | MOVE\_MOTORS | The next thing to do is to write to positioners. |
| 5 | WAIT:MOTORS | We've told motors to move. Now we're waiting for their callbacks to come in. |
| 6 | TRIG\_DETECTORS | The next thing to do is to trigger detectors. |
| 7 | WAIT:DETECTORS | We've triggered detectors. Now we're waiting for their callbacks to come in. |
| 8 | RETRACE\_MOVE | The next thing to do it send positioners to their post-scan positions. |
| 9 | WAIT:RETRACE | We've told positioners to go to their post-scan positions. Now we're waiting for their callbacks to come in. |
| 10 | DO:AFTER\_SCAN | The next thing to do is trigger the after-scan link. |
| 11 | WAIT:AFTER\_SCAN | The after-scan link has been triggered. We're waiting for its callback to come in. |
| 12 | SCAN\_DONE | The scan is finished. |
| 13 | SCAN\_PENDING | A scan has been commanded, but has not yet started |
| 14 | PREVIEW | We're doing a preview of the scan. |
| 15 | RECORD SCALAR DATA | Record scalar data. |

The data-state (DSTATE) field indicates in what state is the processing of data arrays. The possible states are as follows:

| state | message | meaning |
|---|---|---|
| 0 | UNPACKED | Data arrays are either idle or being filled.    If a client should read an array now, it would get last scan's data. |
| 1 | TRIG\_ARRAY\_READ | The next thing to do is trigger the array-read PV, A1PV.    If a client should read an array now, it would get last scan's data. |
| 2 | ARRAY\_READ\_WAIT | A1PV has been triggered, and the callback is still outstanding.    If a client should read an array now, it would get last scan's data. |
| 3 | ARRAY\_GET\_CALLBACK\_WAIT | recDynLinkGetCallback() has been issued for array-valued PVs, and one or more callbacks are still outstanding. |
| 4 | RECORD\_ARRAY\_DATA | It's time to read array data. If any array-valued PVs exist, the data state will change to ARRAY\_GET\_CALLBACK\_WAIT while waiting for the callbacks. |
| 5 | SAVE\_DATA\_WAIT | Arrays are filled, but cannot be posted yet because the data-storage client is not finished writing last scan's data.    If a client should read an array now, it would get last scan's data. |
| 6 | PACKED | Arrays are filled, and buffers have been switched, but they haven't yet been posted.    If a client should read an array now, it would get last scan's data. |
| 7 | POSTED | Data arrays have been posted.    Now the data-storage client can read this scan's array data. |

  
  
  
- - - - - -

<a name="HEADING_2-10"></a>

2.10 Miscellaneous Fields
-------------------------

- - - - - -

| Field | Summary | Type | DCT | Initial/Default | Read | Modify | Posted | PP |
|---|---|---|---|---|---|---|---|---|
| NAME | Record Name | STRING \[29\] | Yes | 0 | Yes | No | No | No |
| DESC | Description | STRING \[29\] | Yes | Null | Yes | Yes | No | No |
| PCPT | Previous Current Point | LONG | No | 0 | Yes | No | No | No |
| PXSC | Previous Execute Scan | UCHAR | No | 0 | Yes | No | No | No |
| TOLP | Time of Last Posting | ULONG | No | 0 | Yes | No | No | No |
| TLAP | Time of Last Array Posting | ULONG | No | 0 | Yes | No | No | No |
| VERS | Code Version (This field has not been kept up to date.) | FLOAT | No | 1.0 | Yes | No | No | No |
| XSC | Internal copy of EXSC | SHORT | No | 0 | Yes | No | Yes | No |


### Private fields

| Field | Summary | Type | DCT | Initial/Default | Read | Modify | Posted | PP |
|---|---|---|---|---|---|---|---|---|
| RPVT | Record Private | NOACCESS | No | Null | No | No | No | No |
| P*n*DB | Pos. *n* dbAddr | NOACCESS | No | Null | No | No | No | No |
| R*n*DB | Readback *n* dbAddr | NOACCESS | No | Null | No | No | No | No |
| D*nn*DB | Detector *nn* dbAddr | NOACCESS | No | Null | No | No | No | No |


> The database Address fields (*xx*DB) contain pointers to the dbAddr structures of the corresponding process variables. For instance, P1DB points to the dbAddr structure of P1PV.
