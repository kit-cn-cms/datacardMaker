from os import path
import sys
import csv
import pandas
directory = path.abspath(path.join(path.dirname("./"), "."))
if not directory in sys.path:
    sys.path.append(directory)

from processObject import processObject
from identificationLogic import identificationLogic

class categoryObject(object):
    _debug     = 200
    def init_variables(self):
        self._name     = "categoryName"
        self._data_obs = None
        self._signalprocs = {}
        self._bkgprocs    = {}
        self._key_creator = identificationLogic()
        self._key_creator.belongs_to = "channel"
        self._default_file = None
    
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
            self.generic_key_nominal_hist = defaultnominalkey
        if not systkey is None:
            self.generic_key_systematic_hist = systkey
        if not defaultRootFile is None:
            if path.exists(defaultRootFile):
                self.default_file = defaultRootFile

        

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
    def observation(self):
        return self._data_obs

    @observation.setter
    def observation(self, data_obs):
        if isinstance(data_obs, processObject):
            s = "adding %s as observation " % data_obs.name
            s+= "in category %s" % self._name
            print s
            self._data_obs = data_obs
        elif isinstance(data_obs, str):
            s = "Will generate observation with name '%s'" % data_obs
            s+= " in category %s" % self._name
            print s
            self._data_obs = self.create_process(process_name = data_obs)
        else:
            print "ERROR: Cannot add object of type %s as observation!" % type(data_obs)
    

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
    
    @property
    def default_file(self):
        return self._default_file

    @default_file.setter
    def default_file(self, filepath):
        if path.exists(filepath):
            self._default_file = filepath
        else:
            print "ERROR: File '%s' does not exist!" % filepath

    def create_signal_process( self, processName, rootfile = None, histoname = None, 
                            systkey = None):
        """
        add a signal process. Calls function add_process with 
        list of signal processes
        """
        self._create_process(processName = processName,
                            dic = self._signalprocs,
                            rootfile = rootfile, histoname = histoname,
                            systkey = systkey)      
    
    def create_background_process( self, processName, rootfile = None, 
                                histoname = None, systkey = None):
        """
        add a background process. Calls function add_process with 
        list of background processes
        """
        self._create_process(processName = processName,
                            dic=self._bkgprocs,
                            rootfile = rootfile, histoname = histoname,
                            systkey = systkey)


    def _create_process(self, processName, dic, rootfile = None, 
                                histoname = None, systkey = None):
        categoryName=self.name
        if histoname is None:
            histoname = self.generic_key_nominal_hist
        if systkey is None:
            systkey = self.generic_key_systematic_hist
        if rootfile is None:
            rootfile = self.default_file
        if self._debug>99:
            print "-"*130
            print "DEBUG PROCESSOBJECT: creating process"
            print "histoname =", histoname
            print "-"*130                 
        processObj=processObject(processName=processName, categoryName=categoryName,
                            pathToRootfile = rootfile, 
                            nominal_hist_key = histoname,
                            systematic_hist_key = systkey)
        self.add_process(dic=dic, process=processObj)
                            

    def add_signal_process( self, process):
        """
        add a signal process. Calls function add_process with 
        list of signal processes
        """
        self.add_process(dic = self._signalprocs, process = process)      
    
    def add_background_process( self, process):
        """
        add a background process. Calls function add_process with 
        list of background processes
        """
                                    
        self.add_process(dic = self._bkgprocs, process = process)
                            
    def add_process(self, dic, process):
        if isinstance(process, processObject):
            if not process.name in dic:
                if self._debug >= 99:
                    print "DEBUG: adding process", process.name
                    print process
                dic[process.name] = process
                if self.default_file is None:
                    self.default_file = process.file
            
            else:
                s= "ERROR: process '%s' already exists in" % process.name
                s+= " " + self._name
                print s
        else:
            print "ERROR: Category can only contain processes!"

    def delete_process(self,processes):
        if isinstance(processes,str):
            self._delete_process(processName=processes)
            if self._debug>30:
                print "DEBUG: deleted process %s" % processes
        if isinstance(processes,list):
            for processName in processes:
                self._delete_process(processName=processName)
            if self._debug>30:
                print "DEBUG: deleted process %s" % processName

    def _delete_process(self,processName):
        if processName in self._signalprocs:
            del self._signalprocs[processName]
        elif processName in self._bkgprocs:
            del self._bkgprocs[processName]
        else:
            if self._debug>30:
                print "DEBUG: no process %s found in category %s" % (processes,self.name)


    def is_compatible_with_default(self, process):
        """
        check whether information for 'process' is compatible with default
        information for this category
        """
        nominal_is_compatible = self._key_creator.matches_generic_nominal_key(  
            tocheck = process.key_nominal_hist, 
            process_name = process.name,
            category_name = self._name)
        systematic_is_compatible = self._key_creator.matches_generic_systematic_key(  
            tocheck = process.key_systematic_hist, 
            process_name = process.name,
            category_name = self._name)
        return (nominal_is_compatible and systematic_is_compatible)


    def add_from_csv(self,pathToFile,signaltag="ttH"):
        with open(pathToFile, mode="r") as csv_file:
            csv_reader = pandas.read_csv(pathToFile, skipinitialspace=True,)
            processes=list(csv_reader)
            #get rid of uncertainty and type entry to get processes
            typ_label=processes[1]
            processes.pop(1)
            uncertainty_label=processes[0]
            processes.pop(0)
            for process in processes:
                if not process in self:
                    if signaltag in process:
                        self.create_signal_process(processName=process)
                    else:
                        self.create_background_process(processName=process)  
                else:
                    print "found process", process
                    temp_process = self[process]

                for uncertainty,typ,value in zip(csv_reader[uncertainty_label],csv_reader[typ_label],csv_reader[process]):
                    value = value.replace(" ", "")
                    typ = typ.replace(" ", "")
                    uncertainty = uncertainty.replace(" ", "")
                    if self._debug >= 99:
                        print "DEBUG: adding combination ({0},\t{1},\t{2}) for {3}".format(uncertainty,typ,value, process)
                    if "lumi" in uncertainty and (value == "x" or value == "X"):
                        value = 1.025
                        print "changing value to", value
                    elif "bgnorm" in uncertainty and (value == "x" or value == "X"):
                        value = 1.5
                        print "changing value to", value
                    if not value=="-":
                        if uncertainty in self[process]._uncertainties:
                            if self._debug >=30:
                                print "DEBUG: setting {0} to \t{1} and \t{2} for process {3}".format(uncertainty,typ,value, process)
                            self[process].set_uncertainty(syst=uncertainty,typ=typ,value=value)
                        else:
                            self[process].add_uncertainty(syst=uncertainty,typ=typ,value=value)
                 

    def __getitem__(self, process):
        
        if process in self._bkgprocs:
            return self._bkgprocs[process]
        elif process in self._signalprocs:
            return self._signalprocs[process]
        else:
            print "ERROR: Process not in Category!"

    def __iter__(self):
        all_processes={}
        all_processes.update(self._bkgprocs)
        all_processes.update(self._signalprocs)
        return all_processes.__iter__()

    def __contains__(self, processName):
        if processName in self._bkgprocs:
            return True
        elif processName in self._signalprocs:
            return True
        else:
            return False


    def __str__(self):
        s = []
        s.append("Category Name:\t%s" % self._name)
        s.append("Default source file:\t%s" % self._default_file)
        s.append("List of signal processes:")
        for sig in self._signalprocs:
            s.append("\t%s" % self._signalprocs[sig])

        s.append("List of background processes:")
        for bkg in self._bkgprocs:
            s.append("\t%s" % self._bkgprocs[bkg])
        return "\n".join(s)
