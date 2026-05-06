---
layout: default
title: saveData
nav_order: 6
---

# saveData

## Overview

saveData is a data-storage client included with the sscan module. It monitors sscan records via Channel Access, and writes scan data to disk in the [MDA (Multi-Dimensional Archive)](MDAFormat.md) binary file format. saveData runs as a dedicated high-priority thread within the IOC and handles 1D through 4D scans automatically, including nested multidimensional scans where multiple sscan records are chained together.

saveData coordinates with sscan records using the AWAIT/AAWAIT handshake mechanism to ensure that scan data arrays are not overwritten before they have been written to disk. For details on how the sscan record implements this handshake, see [section 1.3.5 of the sscan record documentation](sscanRecord.md#135-handshaking-with-data-storage-clients).

> **Important**: Once saveData is initialized, scan records that it monitors will *always* write data files. There is no runtime on/off switch for data storage. Data storage is configured at boot time by specifying which sscan records to monitor in the `saveData.req` file. The only way to disable data storage is to remove saveData from the startup script and reboot.

## Setup

### Loading the database

Load `saveData.db` to create the PVs that saveData uses for status, file paths, and user configuration:

```
dbLoadRecords("$(SSCAN)/sscanApp/Db/saveData.db", "P=xxx:")
```

Alternatively, the `sscan.iocsh` script loads this database (along with `standardScans.db` and `scanProgress.db`) automatically:

```
iocshLoad("$(SSCAN)/iocsh/sscan.iocsh", "PREFIX=xxx:,SSCAN=$(SSCAN)")
```

### Configuration file (saveData.req)

saveData is configured by a request file (typically named `saveData.req`) that must be placed in the IOC's startup directory. The file uses an INI-style format with `[section]` headers, `#` comments, and macro substitution using `$(MACRO)` syntax. Macros are defined by the second argument to `saveData_Init()`.

The following sections are recognized:

| Section | Required | Purpose |
|---------|----------|---------|
| `[prefix]` | No | IOC prefix, used in data file names. Punctuation characters are replaced with underscores. |
| `[status]` | **Yes** | PV name for the saveData status indicator (mbbi). |
| `[message]` | No | PV name for status messages (stringout). |
| `[filename]` | No | PV name where saveData writes the current MDA filename. |
| `[fullPathName]` | No | PV name where saveData writes the full file path. Accessed as a long string (appends `.$`). |
| `[counter]` | **Yes** | PV name for the scan number counter (longout). |
| `[fileSystem]` | **Yes** | PV name for the file system / mount point path. Accessed as a long string. |
| `[subdir]` | **Yes** | PV name for the subdirectory under the file system. Accessed as a long string. |
| `[basename]` | No | PV name for a user-specified file base name. If not provided or not connected, the IOC prefix is used. Accessed as a long string. |
| `[realTime1D]` | No | PV name for the real-time 1D writing toggle (bo). |
| `[scanRecord]` | No | List of sscan record names to monitor (one per line). saveData will set AAWAIT=1 on each. |
| `[extraPV]` | No | List of additional PVs to include in every data file. An optional quoted description string can follow each PV name. |

Example `saveData.req`:

```
[prefix]
$(P)

[status]
$(P)saveData_status

[message]
$(P)saveData_message

[filename]
$(P)saveData_fileName

[fullPathName]
$(P)saveData_fullPathName

[counter]
$(P)saveData_scanNumber

[fileSystem]
$(P)saveData_fileSystem

[subdir]
$(P)saveData_subDir

[basename]
$(P)saveData_baseName

[realTime1D]
$(P)saveData_realTime1D

[scanRecord]
$(P)scanH
$(P)scan1
$(P)scan2
$(P)scan3
$(P)scan4

[extraPV]
$(P)saveData_comment1
$(P)saveData_comment2
$(P)scaler1.TP
$(P)scan1.P1SM   "scan mode"
```

In the `[extraPV]` section, each line contains a PV name optionally followed by a quoted description string. If no description is provided, saveData will fetch the PV's `.DESC` field. Extra PVs are read at the beginning of each scan and their values are written into the MDA file's extra-PV section.

### Initialization

After `iocInit`, initialize saveData with:

```
saveData_Init("saveData.req", "P=xxx:")
```

Arguments:
- **fname** -- Name of the configuration file (searched in the IOC's startup directory).
- **macros** -- Macro substitution string (e.g., `"P=xxx:"`). Macros are substituted in PV names throughout the configuration file.

`saveData_Init` can only be called once. It spawns the saveData thread and suspends the calling thread (the IOC shell) until initialization is complete and all Channel Access connections have been attempted.

### Autosave

If you use autosave, include `saveData_settings.req` in your autosave request file:

```
file saveData_settings.req P=$(P)
```

This saves and restores the following fields across IOC reboots:

| PV | Description |
|----|-------------|
| `$(P)saveData_fileSystem.$` | File system path (long string) |
| `$(P)saveData_subDir.$` | Subdirectory (long string) |
| `$(P)saveData_baseName.$` | Base file name (long string) |
| `$(P)saveData_scanNumber` | Scan number counter |
| `$(P)saveData_realTime1D` | Real-time 1D writing toggle |
| `$(P)saveData_maxAllowedRetries` | Maximum allowed retries |
| `$(P)saveData_retryWaitInSecs` | Wait time between retries (seconds) |

## Runtime PVs

All PVs use the macro `$(P)` as a prefix. Load these by loading `saveData.db`.

### Status and messaging

| PV Suffix | Type | Description |
|-----------|------|-------------|
| `saveData_status` | mbbi | Status: 0="Inactive", 1="Active", 2="Mount err", 3="I/O err" |
| `saveData_message` | stringout | Status/error message from saveData |

### File path configuration

| PV Suffix | Type | Max Length | Description |
|-----------|------|-----------|-------------|
| `saveData_fileSystem` | lso | 256 | File system or mount point path (e.g., `/data/`) |
| `saveData_subDir` | lso | 256 | Subdirectory under the file system |
| `saveData_baseName` | lso | 256 | User-specified base name for data files |
| `saveData_fileName` | lso | 256 | Current MDA filename (written by saveData) |
| `saveData_fullPathName` | lso | 512 | Full path of the current data file (written by saveData) |

### Scan control

| PV Suffix | Type | Description |
|-----------|------|-------------|
| `saveData_scanNumber` | longout | Current scan file number (0-9999, auto-incremented) |
| `saveData_realTime1D` | bo | If "Yes", write 1D scan data point-by-point as it is acquired, rather than only at the end of the scan |
| `saveData_comment1` | stringout | User comment 1 (included in data files as an extra PV) |
| `saveData_comment2` | stringout | User comment 2 (included in data files as an extra PV) |

### Retry mechanism

If a file write fails (e.g., due to a network filesystem error), saveData will retry up to `maxAllowedRetries` times, waiting `retryWaitInSecs` seconds between each attempt. If all retries are exhausted, the write is abandoned.

| PV Suffix | Type | Default | Description |
|-----------|------|---------|-------------|
| `saveData_maxAllowedRetries` | longout | 10 | Maximum number of write retries |
| `saveData_retryWaitInSecs` | longout | 15 | Seconds to wait between retries |
| `saveData_currRetries` | longout | 0 | Current retry count (for the current write attempt) |
| `saveData_totalRetries` | longout | 0 | Cumulative retry count across all scans |
| `saveData_abandonedWrites` | longout | 0 | Number of writes that were abandoned after exhausting retries |

## File naming

Data files are named using the pattern `<basename>NNNN.mda`, where `NNNN` is a four-digit scan number from the `saveData_scanNumber` PV. The scan number auto-increments after each file is written.

- If `saveData_baseName` is set, its value is used as the base name.
- If `saveData_baseName` is empty, the IOC prefix (from the `[prefix]` section) is used, with punctuation characters replaced by underscores (e.g., prefix `xxx:` becomes `xxx_`).
- If a file with the computed name already exists, saveData appends a duplicate counter: `<basename>NNNN_MM.mda` (where `MM` increments until a unique name is found).

## Data file output

saveData writes scan data in the MDA binary format. See the [MDA File Format](MDAFormat.md) documentation for the complete format specification.

For multidimensional scans, saveData detects the scan hierarchy by examining the trigger PV fields (T1PV-T4PV) of each monitored sscan record. When a trigger PV points to another monitored sscan record's EXSC field (with trigger command value 1.0), saveData links the two scans as outer and inner dimensions.

### Real-time 1D writing

When `saveData_realTime1D` is set to "Yes", saveData writes 1D scan data point-by-point as each data point is acquired, rather than waiting for the entire scan to complete. This allows partial data recovery if a scan is aborted or the IOC crashes mid-scan. The file is updated in-place by seeking to the appropriate position and overwriting the current-point counter and data values.

## Diagnostic commands

The following iocsh commands are available for troubleshooting:

| Command | Arguments | Description |
|---------|-----------|-------------|
| `saveData_PrintScanInfo` | `name` | Print connection status and configuration for the named sscan record |
| `saveData_Priority` | `priority` | Change the saveData thread priority |
| `saveData_SetCptWait_ms` | `ms` | Set the minimum wait time (in milliseconds) between current-point monitor postings |
| `saveData_Version` | (none) | Print the saveData version string |
| `saveData_Info` | (none) | Print overall saveData status and configuration |

## Debug variables

The following variables can be set from the iocsh to control debug output:

| Variable | Default | Description |
|----------|---------|-------------|
| `debug_saveData` | 0 | General debug verbosity level. Higher values produce more output. |
| `debug_saveDataMsg` | 0 | Message queue debug verbosity level. |
| `saveData_MessagePolicy` | 0 | Controls how current-point monitor messages are queued. 0=wait for space; 1=drop if full; 2=drop if full and time hasn't elapsed; 3=wait if time has elapsed. |
