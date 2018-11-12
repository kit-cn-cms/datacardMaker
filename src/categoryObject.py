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
            self._key_creator.generic_nominal_key = defaultnominalkey
        if not systkey is None:
            self._key_creator.generic_systematics_key = systkey
        if not defaultRootFile is None:
            if path.exists(defaultRootFile):
                self._default_file = defaultRootFile

        

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
    
    @property
    def default_file(self):
        return self._default_file
    @default_file.setter
    def default_file(self, filepath):
        if path.exists(filepath):
            self._default_file = filepath
        else:
            print "ERROR: File '%s' does not exist!" % filepath

    def add_signal_process_raw( self, name, rootfile = None, histoname = None, 
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
            rootfile = self._default_file
        self.add_process_raw(   dic = self._signalprocs, name = name,
                            rootfile = rootfile, histoname = histoname,
                            systkey = systkey)      
    
    def add_background_process_raw( self, name, rootfile = None, 
                                histoname = None, systkey = None):
        """
        add a background process. Calls function add_process with 
        list of background processes
        """
        if histoname is None:
            histoname = self._key_creator.insert_process(process_name = name,
                            base_key = self._key_creator.generic_nominal_key)
        if systkey is None:
            systkey = self._key_creator.insert_process(process_name = name,
                        base_key = self._key_creator.generic_systematics_key)
        if rootfile is None:
            rootfile = self._default_file                         
        self.add_process_raw(   dic = self._bkgprocs, name = name,
                            rootfile = rootfile, histoname = histoname,
                            systkey = systkey)

    def create_process_raw(self, processName):
        return processObject(processName=processName, categoryName=self.name,
                            pathToRootfile = self.default_file, nominal_hist_key = self.generic_key_nominal_hist,systematic_hist_key = self.generic_key_systematic_hist)


    # def create_process(self, processName , rootfile = None, 
    #                             histoname = None, systkey = None):
    #     categoryName=self.name
    #     if histoname is None:
    #         histoname = self._key_creator.insert_process(process_name = processName,
    #                         base_key = self._key_creator.generic_nominal_key)
    #     if systkey is None:
    #         systkey = self._key_creator.insert_process(process_name = processName,
    #                     base_key = self._key_creator.generic_systematics_key)
    #     if rootfile is None:
    #         rootfile = self._default_file                         
    #     return processObject(processName=processName, categoryName=categoryName,
    #                         pathToRootfile = rootfile, nominal_hist_key = histoname,systematic_hist_key = systkey)
                            
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
            if self._debug >= 99:
                print "DEBUG: adding process", process.name
                print process
            if self._default_file is None:
                self._default_file = process.file
            dic[process.name] = process
        else:
            print "ERROR: Category can only contain processes!"

            
                


    def add_process_raw(self, dic, name, rootfile, histoname, systkey):
        temp = processObject(processName = name, pathToRootfile = rootfile, 
                    nominal_hist_key = histoname, systematic_hist_key = systkey, 
                    categoryName = self._name)
        self.add_process(dic = dic, process = temp)

    def is_compatible_with_default(self, process):
        """
        check whether information for 'process' is compatible with default
        information for this category
        """
        nominal_is_compatible = self._key_creator.matches_generic_nominal_key(  
            tocheck = process.nominal_hist_name, 
            process_name = process.name,
            category_name = self._name)
        systematic_is_compatible = self._key_creator.matches_generic_systematic_key(  
            tocheck = process.systematic_hist_name, 
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
                temp_process=self.create_process_raw(processName=process)
                for uncertainty,typ,value in zip(csv_reader[uncertainty_label],csv_reader[typ_label],csv_reader[process]):
                    if "lumi" in uncertainty:
                        value = 1.025
                    elif "bgnorm" in uncertainty:
                        value = 1.5
                    temp_process.add_uncertainty(syst=uncertainty,typ=typ,value=value)
                if signaltag in process:
                    self.add_signal_process(temp_process)
                else:
                    self.add_background_process(temp_process)   





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
