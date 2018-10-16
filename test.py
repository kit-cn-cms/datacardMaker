import sys
from os import path

directory = path.abspath(path.realpath(path.dirname(__file__)))
srcdir = path.join(directory, "src")
if not srcdir in sys.path:
    sys.path.append(srcdir)

basedir = path.join(directory, "base")
if not basedir in sys.path:
    sys.path.append(basedir)
from helperClass import helperClass

from processObject import processObject
from categoryObject import categoryObject
from datacardMaker import datacardMaker
from test_cls import testClass

def datacard_tests():
	testproc = processObject()
	
	testproc.name = "nominal"
	testproc.category = "jge6_tge4"
	print "setting rootfile"
	testproc.file = "test.root"
	testproc.nominal_hist_name = "nominal"
	testproc.systematic_hist_name = "nominal_$SYSTEMATIC"
	testproc.add_uncertainty("lumi", "lnN", "1.025")
	testproc.add_uncertainty("pdf_gg", "lnN", "0.98/1.02")
	testproc.add_uncertainty(syst = "JES", typ = "shape", value = 1.0)
	#not working yet
	testproc.add_uncertainty(syst = 5, typ = "shape", value = 1.0)
	testproc.add_uncertainty(syst = "JES", typ = "shape", value = "five")
	testproc.add_uncertainty(syst = "JES2", typ = "shape", value = "five")
	print testproc

	category = categoryObject()
	category.name = "jge6_tge4"
	category.add_signal_process(testproc)
	print category

def init_tests():
	a = testClass()

	b = testClass()
	c = testClass()

	a.x = 7
	print a.x
	print b.x
	print c.x

	a.helper = helperClass()

	print a.helper
	print b.helper
	print c.helper

	testClass.helper = helperClass()

	print a.helper
	print b.helper
	print c.helper

	print "deleting helper of a"
	del a.helper

	print a.helper
	print b.helper
	print c.helper

	a.helper = b.helper

	print a.helper
	print b.helper
	print c.helper

def main():
	datacard_tests()
	# init_tests()

if __name__ == '__main__':
	main()