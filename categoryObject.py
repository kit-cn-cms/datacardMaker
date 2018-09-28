from os import path
import sys
directory = path.abspath(path.join(path.dirname("./"), "."))
if not directory in sys.path:
    sys.path.append(directory)

from processObject import *

class categoryObject:
    
    def __init__(   self, categoryName, defaultRootFile, 
                    defaultnominalkey,
                    systkey = None, 
                    listOfSignals = None, 
                    listOfBkg = None, 
                    processIdentifier = "$PROCESS",
                    channelIdentifier = "$CHANNEL",
                    systIdentifier = "$SYSTEMATIC" ):
        """
        init category. A category has a name, a root file containing
        the process histograms and a key to find the nominal histograms
        in the root file. You can also give it a key to find the
        systematic histograms and a list of signal or background 
        processes. You can also set the identifier which will be used
        in the datacard.
        
        Variables:
        categoryName        --  name for this category
        defaultRootFile     --  use this root file path as default for all processes
        defaultnominalkey   --  key to find the nominal histograms
        systkey             --  key to find the histograms corresponding to a nuisance parameter shape variation
        processIdentifier   --  string that is to be replaced with the process name in the keys
        channelIdentifier   --  string that is to be replaced with the channel name in the keys
        systIdentifier      --  string that is to be replaced with the nuisance parameter name in the keys
        """
        
        self._name     = categoryName
        self._nomkey   = defaultnominalkey
        self._systkey  = systkey
        self._procIden = processIdentifier
        self._chIden   = channelIdentifier
        self._systIden = systIdentifier
        self._data_obs = None
        self._signalprocs = []
        self._bkgprocs    = []
        
        #check if process/channel identifiers are in nominal histo key
        if self._procIden in self._nomkey:
            print "WARNING:\tProcess identifier is still part of nominal histo key!"
        if self._chIden in self._nomkey:
            print "WARNING:\tChannel identifier is still part of nominal histo key! Will replace it"
            self._nomkey = self._nomkey.replace(self._chIden, self._name)
        
        #check if systematics/process/channel identifiers are in systematics histo key
        if not self._systIden in self._systkey:
            print "WARNING:\tSystematic identifier still not part of nominal histo key!"
        if self._chIden in self._systkey:
            print "WARNING:\tChannel identifier is still part of systematic histo key! Will replace it"
            self._systkey = self._systkey.replace(self._chIden, self._name)
        if not self._systIden in self._systkey:
            print "WARNING:\tSystematic identifier still not part of nominal histo key!"
        
        #if a list of signal processes is given, add them with default vals
        if listOfSignals:
            for proc in listOfSignals:
                self.add_signal_process(name = proc,
                                        rootfile = defaultRootFile)
        
        #if a list of bkg processes is given, add them with default vals
        if listOfBkg:
            for proc in listOfBkg:
                self.add_background_process(name = proc,
                                        rootfile = defaultRootFile)
        
        
    def add_signal_process( self, name, rootfile, 
                            histoname = self._nomkey, 
                            systkey = self._systkey):
        """
        add a signal process. Calls function add_process with 
        list of signal processes
        """
        self.add_process(   dic = self._signalprocs, name = name,
                            rootfile = rootfile, histoname = histoname,
                            systkey = systkey)      
    
    def add_background_process( self, name, rootfile, 
                                histoname = self._nomkey, 
                                systkey = self._systkey):
        """
        add a background process. Calls function add_process with 
        list of background processes
        """
                                    
        self.add_process(   dic = self._bkgprocs, name = name,
                            rootfile = rootfile, histoname = histoname,
                            systkey = systkey)
                            
    def add_process(self, dic, name, rootfile, 
                    histoname = self._nomkey, systkey = self._systkey
                    ):
        changedKey = False
        if self._procIden in histoname:
            print "WARNING:\tProcess identifier is still part of nominal histo key! Will replace it"
            histoname = histoname.replace(self._procIden, name)
        if self._chIden in histoname:
            print "WARNING:\tChannel identifier is still part of nominal histo key! Will replace it"
            histoname = histoname.replace(self._chIden, name)
        if self._procIden in systkey:
            print "WARNING:\tProcess identifier is still part of nominal histo key! Will replace it"
            systkey = systkey.replace(self._procIden, name)
        if self._chIden in systkey:
            print "WARNING:\tChannel identifier is still part of nominal histo key! Will replace it"
            systkey = systkey.replace(self._chIden, name)
            
        controlNomKey = self._nomkey.replace(self._procIden, name)
        controlSysKey = self._systkey.replace(self._procIden, name)
        if not (histoname = self._nomkey and systkey = self._systkey):
            changedKey = True
        
        if name in dic:
            print ""
