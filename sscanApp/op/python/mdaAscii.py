#!/usr/bin/env python

import sys
import readMDA

def main():
	if len(sys.argv) < 2:
		fname = None
	elif sys.argv[1] == '?' or sys.argv[1] == "help" or sys.argv[1][:2] == "-h":
		print "usage: %s [filename]" % sys.argv[0]
		return()
	else:
		fname = sys.argv[1]

	d = readMDA.readMDA(fname, 1, 0, 0)
	# number of positioners, detectors
	np = d[1].np
	nd = d[1].nd

	min_column_width = 15
	# make sure there's room for the names, etc.
	phead_format = []
	dhead_format = []
	pdata_format = []
	ddata_format = []
	columns = 1
	for i in range(np):
		cw = max(min_column_width, len(d[1].p[i].name)+1)
		cw = max(cw, len(d[1].p[i].desc)+1)
		cw = max(cw, len(d[1].p[i].fieldName)+1)
		phead_format.append("%%-%2ds" % (cw-1))
		pdata_format.append("%%- %2d.8f" % (cw-1))
		columns = columns + cw
	for i in range(nd):
		cw = max(min_column_width, len(d[1].d[i].name)+1)
		cw = max(cw, len(d[1].d[i].desc)+1)
		cw = max(cw, len(d[1].d[i].fieldName)+1)
		dhead_format.append("%%-%2ds" % (cw-1))
		ddata_format.append("%%- %2d.8f" % (cw-1))
		columns = columns + cw

	for i in d[0].keys():
		if (i != 'sampleEntry'):
			print "# ", i, d[0][i]

	print "#\n# ", str(d[1])
	print "#  scan time: ", d[1].time
	sep = "#"*columns
	print sep

	# print table head

	print "#",
	for j in range(np):
		print phead_format[j] % (d[1].p[j].fieldName),
	for j in range(nd):
		print dhead_format[j] % (d[1].d[j].fieldName),
	print

	print "#",
	for j in range(np):
		print phead_format[j] % (d[1].p[j].name),
	for j in range(nd):
		print dhead_format[j] % (d[1].d[j].name),
	print

	print "#",
	for j in range(np):
		print phead_format[j] % (d[1].p[j].desc),
	for j in range(nd):
		print dhead_format[j] % (d[1].d[j].desc),
	print

	print sep

	for i in range(d[1].curr_pt):
		print "",
		for j in range(d[1].np):
			print pdata_format[j] % (d[1].p[j].data[i]),
		for j in range(d[1].nd):
			print ddata_format[j] % (d[1].d[j].data[i]),
		print


if __name__ == "__main__":
        main()
