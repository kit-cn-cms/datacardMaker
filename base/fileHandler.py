from ROOT import TFile, TH1
from os import path as opath

class fileHandler(object):
    """
    The fileHandler class manages all access to files required for the analysis
    TODO: Improve memory handling by cleverly closing files
    """
    _debug = 200

    def init_variables(self):
        self._filepath = "/path/to/file"
        self._file     = None

    def __init__(self):
        if self._debug >= 10:
            print "Initializing fileHandler"
        self.init_variables()
        if opath.exists(self._filepath):
            self._file = self.load_file(filepath)

    def __del__(self):
        self.close_file()

    def is_file_open(self):
        if self._debug >= 99:
            print "DEBUG: checking for open file"
        if not self._file is None and isinstance(self._file, TFile):
            return self._file.IsOpen()
        if self._debug >= 99:
            print "DEBUG: file is not a TFile!"
        return False

    def close_file(self):
        if self._debug >= 99:
            print "DEBUG: Closing file if it's open"
        if self.is_file_open():
            self._file.Close()

    def open_file(self, path):
        if self._debug >= 99:
            print "opening file '%s'" % path
        if opath.exists(path):
            f = TFile.Open(path)
            if self.is_intact_file(f):
                self._file = f
                self._filepath = path
            else:
                if self._debug >= 3:
                    print "Could not open file '%s'" % path
        else:
            if self._debug >= 3:
                print "File '%s' does not exist!" % path
        return None

    @property
    def filepath(self):
        return self._filepath
    @filepath.setter
    def filepath(self, path):
        if self._debug >= 20:
            print "trying to set file path to", path

        self.close_file()
        self.open_file(path)

    def is_intact_file(self, f):

        if f and isinstance(f, TFile):
            if f.IsOpen():
                if not f.IsZombie():
                    if not f.TestBit(TFile.kRecovered):
                        return True
                    else:
                        if self._debug >= 99: 
                            print "ERROR: file '%s' is recovered!" % f.GetName()
                else:
                    if self._debug >= 99:
                        print "ERROR: file '%s' is zombie!" % f.GetName()
            else:
                if self._debug >= 99:
                    print "ERROR: file '%s' is not open" % f.GetName()
        return False     

    def load_histogram(self, histname):
        if self._debug >= 99:
            print "DEBUG: entering 'fileHandler.load_histogram'"
        if self._file:
            if self._debug >= 10:
                print "DEBUG: loading histogram '%s' from '%s'" % (histname, file)
            h = self._file.Get(histname)
            if isinstance(h, TH1):
                return h
            else:
                print ("WARNING: histogram '%s' does not exist in '%s'"
                        % (histname, file))
        return None

    def histogram_exists(self, histname):
        h = self.load_histogram(histname = histname)
        if self._debug >= 99:
            print "found histogram at", h
        if h:
            return True
        return False
    
    def get_integral(self, histname):
        h = self.load_histogram(histname = histname)
        if h:
            return h.Integral()
        else:
            return None