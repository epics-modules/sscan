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
DBD += sscanVXSupport.dbd
DBD += sscanMenu.dbd

INC += recDynLink.h

#=============================

LIBRARY_IOC += sscan

sscan_SRCS += sscanRecord.c
sscan_SRCS += scanparmRecord.c
sscan_SRCS += busyRecord.c
sscan_SRCS += recDynLink.c

# save scan data stuff
sscan_SRCS_vxWorks += xdr_stdio.c
sscan_SRCS_vxWorks += xdr_lib.c
sscan_SRCS_vxWorks += saveData.c
sscan_SRCS_vxWorks += req_file.c

sscan_LIBS += $(EPICS_BASE_IOC_LIBS)

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD RULES AFTER THIS LINE

