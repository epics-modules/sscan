---
layout: default
title: MDA File Format
nav_order: 7
---

# MDA File Format

MDA (Multi-Dimensional Archive) is the binary file format used by the sscan module's `saveData` component to write scan data to disk. MDA files use the `.mda` file extension.

Data in MDA files is encoded using XDR (External Data Representation, RFC 1014), a platform-independent big-endian binary encoding. This ensures that MDA files written on one architecture (e.g., vxWorks/PowerPC) can be read on another (e.g., Linux/x86\_64) without conversion.

The current file format version is **1.4**.

## Reading MDA files

The sscan module includes utilities for reading MDA files:

- **Python**: `mda.py` (in `sscanApp/op/python/`) provides functions for reading, writing, and performing arithmetic on MDA files up to 4 dimensions. `mdaAscii.py` can render 1D MDA files as ASCII text.
- **C**: `mdautils-src.tar.gz` (in `sscanApp/src/`) contains Dohn Arms' C library for reading MDA files into C structures, converting them to ASCII, and printing file metadata.

## XDR conventions

Note that an `xdr_counted_string` is not part of the XDR standard, but a definition added on top of the standard. It consists of an `xdr_short` containing the number of characters in the string, possibly followed by an `xdr_string`. Only if the `xdr_short` value is nonzero will an `xdr_string` follow it. Thus an empty string looks like this:

`<xdr_short=0>`

and a nonempty string looks like this:

`<xdr_short=3><xdr_string>`

A counted string looks like this:

```
	int number of characters
	# if number of characters>0:
		int number of characters
		char[number_of_characters]
```

## File structure

```
FILE HEADER
	xdr_float:	VERSION  (1.4 == 3FB33333)
	xdr_long:	scan number
	xdr_short	data's rank
	xdr_vector(rank, xdr_int) dims;
	xdr_int		isRegular (true=1, false=0)
	xdr_long:	pointer to the extra pvs


SCAN
	HEADER:
	xdr_short:		this scan's rank
	xdr_long:		number of requested points (NPTS)
	xdr_long:		current point (CPT)
	if the scan rank is > 1
	  xdr_vector(NPTS, xdr_long)	pointer to the lower scans

	INFO:
	xdr_counted_string:	scan name
	xdr_counted_string:	time stamp


	xdr_int:		number of positioners
	xdr_int:		number of detectors
	xdr_int:		number of triggers

	for each positioner
	  xdr_int:		positioner number
	  xdr_counted_string:	positioner name
	  xdr_counted_string:	positioner desc
	  xdr_counted_string:	positioner step mode
	  xdr_counted_string:	positioner unit
	  xdr_counted_string:	readback name
	  xdr_counted_string:	readback description
	  xdr_counted_string:	readback unit

	for each detector
	  xdr_int:		detector number
	  xdr_counted_string:	detector name
	  xdr_counted_string:	detector desc
	  xdr_counted_string:	detector unit

	for each trigger
	  xdr_int:		trigger number
	  xdr_counted_string:	trigger name
	  xdr_float:		trigger command

	DATA:
	for each positioner
	  xdr_vector(NPTS, xdr_double):	readback array

	for each detector
	  xdr_vector(NPTS, xdr_float):	detector array

[SCAN]
...
...
...
[SCAN]

EXTRA PVs
	xdr_int:	number of extra pvs

	for each pv
	  xdr_counted_string:	name
	  xdr_counted_string:	desc
	  xdr_int:		type
	  if type != DBR_STRING
	    xdr_long:		count
	    xdr_counted_string:	unit

	  depending on the type:
	    DBR_STRING:
		xdr_counted_string:		value
	    DBR_CTRL_CHAR:
		xdr_vector(count, xdr_char):	value
	    DBR_CTRL_SHORT:
		xdr_vector(count, xdr_short):	value
	    DBR_CTRL_LONG:
		xdr_vector(count, xdr_long):	value
	    DBR_CTRL_FLOAT:
		xdr_vector(count, xdr_float):	value
	    DBR_CTRL_DOUBLE:
		xdr_vector(count, xdr_double):	value

```

### Notes on specific fields

**VERSION**: The file format version, written as an XDR float. Version 1.4 (`0x3FB33333`) is written by the current `saveData_writeXDR.c`. Version 1.3 (`0x3FA66666`) was written by the older `saveData.c`. Most readers should accept both.

**isRegular**: Indicates whether the scan data forms a regular rectangular grid. When `isRegular` is 1 (true), all inner-dimension scans completed with the same number of points (e.g., every row of a 2D scan has the same number of columns). When `isRegular` is 0 (false), inner scans may have different numbers of points, which can occur if some inner scans were aborted or had their parameters changed during the outer scan. Readers should use each scan's CPT (current point) field to determine how many data points are valid, rather than relying on NPTS alone.

**Pointer fields**: The `pointer to the extra pvs` and `pointer to the lower scans` fields are byte offsets from the beginning of the file. They are used with `fseek()` to navigate directly to those sections.

**CPT vs NPTS**: Data arrays always contain NPTS elements, but only the first CPT elements contain valid data. If a scan was aborted, CPT will be less than NPTS.

## Scan layout examples

A 1D scan looks like this:

```
	header
	scan1
	extra PV's
```

A 2D scan looks like this

```
	header
	scan2
		scan1
		scan1
		...
	extra PV's
```

A 3D scan looks like this
```
	header
	scan3
		scan2
			scan1
			scan1
			...
		scan2
			scan1
			scan1
			...
		...
	extra PV's
```
