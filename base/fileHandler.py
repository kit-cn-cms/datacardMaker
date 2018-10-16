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
        if isinstance(self._file, TFile):
            return self._file.IsOpen()
        return False

    def close_file(self):
        if self.is_file_open:
            self._file.Close()

    def open_file(self, path):
        if self._debug >= 99:
            print "opening file '%s'" % filepath
        if opath.exists(filepath):
            f = TFile.Open(filepath)
            if self.intact_root_file(f):
                self._file = f
            else:
                if self._debug >= 3:
                    print "Could not open file '%s'" % filepath
        else:
            if self._debug >= 3:
                print "File '%s' does not exist!" % filepath
        return None

    @property
    def filepath(self):
        return self._filepath
    @filepath.setter
    def filepath(self, path):
        if opath.exists(path):
            self.close_file()
            self.open_file(path)

    def intact_root_file(self, f):

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

    def load_histogram(self, file, histname):
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

    def histogram_exists(self, file, histname):
        h = self.load_histogram(file = file, histname = histname)
        if h:
            return True
        return False
    
    def get_integral(self, file, histname):
        h = self.load_histogram(file = file, histname = histname)
        if h:
            return h.Integral()
        else:
            return None