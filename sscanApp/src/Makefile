TOP=../..

include $(TOP)/configure/CONFIG
#----------------------------------------
#  ADD MACRO DEFINITIONS AFTER THIS LINE
#=============================


#PROD_HOST += caExample
#caExample_SRCS	+= caExample.c
#caExample_LIBS	+= ca
#caExample_LIBS	+= Com
ca_DIR           = $(EPICS_BASE_LIB)
Com_DIR          = $(EPICS_BASE_LIB)


#=============================
# xxxRecord.h will be created from xxxRecord.dbd

DBDINC += scanparmRecord
DBDINC += sscanRecord
DBDINC += busyRecord

# <name>.dbd will be created from <name>Include.dbd
DBD += sscan.dbd
DBD += sscanSupport.dbd

#=============================

LIBRARY_IOC += sscan

sscan_SRCS += sscanRecord.c
sscan_SRCS += scanparmRecord.c
sscan_SRCS  += busyRecord.c

# save scan data stuff
sscan_SRCS_vxWorks += xdr_stdio.c
sscan_SRCS_vxWorks += xdr_lib.c
sscan_SRCS_vxWorks += saveData.c
sscan_SRCS_vxWorks += req_file.c

# <name>_registerRecordDeviceDriver.cpp will be created from <name>.dbd
sscan_SRCS += sscan_registerRecordDeviceDriver.cpp
#sscan_SRCS_DEFAULT += sscanMain.cpp #maybe only for win32
#sscan_SRCS_vxWorks += -nil- #?

#The following adds support from base/src/vxWorks
#sscan_OBJS_vxWorks += $(EPICS_BASE_BIN)/vxComLibrary

### The following builds SNL programs as components of sscan
# NOTE: for suffix .st, code is run through cpp; for .stt, it's not
#sscan_SRCS += example.st
#sscan_LIBS += seq pv
#seq_DIR    = $(SNCSEQ_LIB)
#pv_DIR     = $(SNCSEQ_LIB)

sscan_LIBS += $(EPICS_BASE_IOC_LIBS)

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD RULES AFTER THIS LINE

