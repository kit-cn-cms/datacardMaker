from ROOT import TFile, TH1
from os import path as opath
from sys import path as spath
baserepodir = "/nfs/dust/cms/user/pkeicher/projects/base/classes"
if not baserepodir in spath:
	spath.append(baserepodir)
from helperClass_base import helperClass_base
class helperClass(helperClass_base):
	def __init__(self):
		super(helperClass, self).__init__()

	def isfloat(self, value):
		try:
			float(value)
			return True
		except ValueError:
			return False

	def histogram_exists(self, file, histname):
		if opath.exists(file):
			f = TFile(file)
			print f
			if self.intact_root_file(f):
			    h = f.Get(histname)
			    if isinstance(h, TH1):
			    	f.Close()
			    	return True
			    else:
			    	print ("WARNING: histogram '%s' does not exist in '%s'"
			    			% (histname, file))
			else:
				print "ERROR: File '%s' is broken!" % file
		else:
			print "ERROR: File '%s' does not exist!" % file

