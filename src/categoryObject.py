from os import path
import sys
directory = path.abspath(path.join(path.dirname("./"), "."))
if not directory in sys.path:
    sys.path.append(directory)

from processObject import processObject
from identificationLogic import identificationLogic

class categoryObject(object):
    _debug     = True
    def init_variables(self):
        self._name     = "categoryName"
        self._data_obs = None
        self._signalprocs = {}
        self._bkgprocs    = {}
        self._key_creator = identificationLogic()
        self._default_root_file = None
    
    def __init__(   self, categoryName=None, defaultRootFile=None, 
                    defaultnominalkey=None,
                    systkey = None, 
                    dict_of_signals = None, 
                    dict_of_bkgs = None, 
                    ):
        """
        init category. A category has a name, a root file containing
        the process histograms and a key to find the nominal histograms
        in the root file. You can also give it a key to find the
        systematic histograms and a list of signal or background 
        processes. You can also set the identifier which will be used
        in the datacard.
        
        Variables:
        categoryName        --  name for this category
        defaultRootFile     --  use this root file path as default for 
                                all processes
        defaultnominalkey   --  key to find the nominal histograms
        systkey             --  key to find the histograms corresponding to 
                                a nuisance parameter shape variation
        """
        self.init_variables()
        if not categoryName is None:
            self._name     = categoryName
        if not defaultnominalkey is None:
            self._key_creator.generic_nominal_key = defaultnominalkey
        if not systkey is None:
            self._key_creator.generic_systematics_key = systkey
        if not defaultRootFile is None:
            if path.exists(defaultRootFile):
                self._default_root_file = defaultRootFile

        

        # #check if process/channel identifiers are in nominal histo key
        # self.is_part_of(self._procIden, self._nomkey)
        # if self.is_part_of(self._chIden, self._nomkey):
        #     self._nomkey = self._nomkey.replace(self._chIden, self._name)
        
        # #check if systematics/process/channel identifiers
        # #are in systematics histo key
        # if not self.is_part_of(self._systIden, self._systkey):
        #     print "WARNING: Identifier for systematics not part of SystKey!"
        # if self.is_part_of(self._chIden, self._systkey):
        #     self._systkey = self._systkey.replace(self._chIden, self._name)

        
        #if a list of signal processes is given, add them with default vals
        if dict_of_signals:
            for proc in dict_of_signals:
                self.add_signal_process(name = proc,
                                        rootfile = defaultRootFile)
        
        #if a list of bkg processes is given, add them with default vals
        if dict_of_bkgs:
            for proc in dict_of_bkgs:
                self.add_background_process(name = proc,
                                        rootfile = defaultRootFile)
    # def is_part_of(self, identifier, key):
    #     if identifier in key:
    #         if self._debug:
    #             s = "Identifier '%s' is part of " % identifier
    #             s += "keyword '%s'" % key
    #             print s
    #         return True
    #     else:
    #         if self._debug:
    #             s = "Identifier '%s' is not part of " % identifier
    #             s += "keyword '%s'" % key
    #             print s
    #         return False

    @property
    def n_signal_procs(self):
        return len(self._signalprocs)

    @property
    def n_background_procs(self):
        return len(self._bkgprocs)
    
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, val):
        self._name = val

    @property
    def signal_processes(self):
        return self._signalprocs

    @property
    def background_processes(self):
        return self._bkgprocs
    
    @property
    def generic_key_nominal_hist(self):
        return self._key_creator.generic_nominal_key
    @generic_key_nominal_hist.setter
    def generic_key_nominal_hist(self, key):
        channelkey = self._key_creator.insert_channel(channel_name = self._name, 
                                                        base_key = key)
        self._key_creator.generic_nominal_key = channelkey

    @property
    def generic_key_systematic_hist(self):
        return self._key_creator.generic_systematics_key
    @generic_key_systematic_hist.setter
    def generic_key_systematic_hist(self, key):
        channelkey = self._key_creator.insert_channel(channel_name = self._name, 
                                                        base_key = key)
        self._key_creator.generic_systematics_key = channelkey
    


    

    def add_signal_process( self, name, rootfile = None, histoname = None, 
                            systkey = None):
        """
        add a signal process. Calls function add_process with 
        list of signal processes
        """
        if histoname is None:
            histoname = self._key_creator.insert_process(process_name = name,
                            base_key = self._key_creator.generic_nominal_key)
        if systkey is None:
            systkey = self._key_creator.insert_process(process_name = name,
                        base_key = self._key_creator.generic_systematics_key)
        if rootfile is None:
            rootfile = self._default_root_file
        self.add_process_raw(   dic = self._signalprocs, name = name,
                            rootfile = rootfile, histoname = histoname,
                            systkey = systkey)      
    
    def add_background_process( self, name, rootfile = None, 
                                histoname = None, systkey = None):
        """
        add a background process. Calls function add_process with 
        list of background processes
        """
        if histoname is None:
            histoname = self._nomkey
        if systkey is None:
            systkey = self._systkey                            
        self.add_process_raw(   dic = self._bkgprocs, name = name,
                            rootfile = rootfile, histoname = histoname,
                            systkey = systkey)
                            
    # def add_process(self, dic, name, rootfile, 
    #                 histoname = None, systkey = None
    #                 ):
    #     changedKey = False
    #     if histoname is None:
    #         histoname = self._nomkey
    #     if systkey is None:
    #         systkey = self._systkey  
    #     if self._procIden in histoname:
    #         print "WARNING:\tProcess identifier is still part of nominal histo key! Will replace it"
    #         histoname = histoname.replace(self._procIden, name)
    #     if self._chIden in histoname:
    #         print "WARNING:\tChannel identifier is still part of nominal histo key! Will replace it"
    #         histoname = histoname.replace(self._chIden, name)
    #     if self._procIden in systkey:
    #         print "WARNING:\tProcess identifier is still part of nominal histo key! Will replace it"
    #         systkey = systkey.replace(self._procIden, name)
    #     if self._chIden in systkey:
    #         print "WARNING:\tChannel identifier is still part of nominal histo key! Will replace it"
    #         systkey = systkey.replace(self._chIden, name)
            
    #     controlNomKey = self._nomkey.replace(self._procIden, name)
    #     controlSysKey = self._systkey.replace(self._procIden, name)
    #     if not (histoname == self._nomkey and systkey == self._systkey):
    #         changedKey = True
        
    #     if name in dic:
    #         print ""

    #overloaded functions if input variable is a process
    def add_signal_process( self, process):
        """
        add a signal process. Calls function add_process with 
        list of signal processes
        """
        self.add_process(   dic = self._signalprocs, process = process)      
    
    def add_background_process( self, process):
        """
        add a background process. Calls function add_process with 
        list of background processes
        """
                                    
        self.add_process(   dic = self._bkgprocs, process = process)
                            
    def add_process(self, dic, process):
        if isinstance(process, processObject):
            dic[process.name] = process
        else:
            print "ERROR: Category can only contain processes!"

    def add_process_raw(self, dic, name, rootfile, histoname, systkey):
        temp = processObject(processName = name, pathToRootfile = rootfile, 
                    nominal_hist_key = histoname, systematic_hist_key = systkey, 
                    categoryname = self._name)
        self.add_process(dic = dic, process = temp)

    def __str__(self):
        s = []
        s.append("Category Name:\t%s" % self._name)
        s.append("List of signal processes:")
        for sig in self._signalprocs:
            s.append("\t%s" % self._signalprocs[sig])

        s.append("List of background processes:")
        for bkg in self._bkgprocs:
            s.append("\t%s" % self._bkgprocs[bkg])
        return "\n".join(s)
