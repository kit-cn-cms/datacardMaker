import sys
import operator
from os import path

directory = path.abspath(path.realpath(path.dirname(__file__)))
if not directory in sys.path:
    sys.path.append(directory)

from categoryObject import categoryObject
from processObject import processObject
from systematicObject import systematicObject

class analysisObject(object):
    _debug = 200
    def init_variables(self):
    	self._categories        = {}
        self._systematics       = {}

    def __init__(   self, pathToDatacard = "", 
                    processIdentifier = "$PROCESS",
                    channelIdentifier = "$CHANNEL",
                    systIdentifier = "$SYSTEMATIC"):
        self.init_variables()
        if pathToDatacard:
            self.load_from_file(pathToDatacard)

    def add_category(self, category):
    	"""
    	Adds a category object
    	"""
        if isinstance(category, categoryObject):
            catname = category.name
            if not catname in self._categories:
                self._categories[catname] = category
                # self.update_systematics(category = category)
            else:
                print "ERROR: Category %s is known to this datacard!" % catname
        else:
            print "ERROR: Input required to be instance of categoryObject!"

    def create_category(self,categoryName,default_file=None,generic_key_systematic_hist=None,
    				generic_key_nominal_hist=None):
        """
        Initializes a categoryObject with default file and generic keys.
        """
        self._categories[categoryName] = categoryObject(categoryName=categoryName,
                        defaultRootFile=default_file,systkey=generic_key_systematic_hist,
                        defaultnominalkey=generic_key_nominal_hist)
        if self._debug >= 50:
                    print "initialized category", categoryName
                    print self._categories[categoryName]

    def add_signal_process(self, process, categoryName=None):
    	"""
    	Adds a signal process and creates a categoryObject where the processObject is stored
    	if there is no categoryObject.
    	"""
    	if categoryName==None:
    		categoryName=process.category
    	if not categoryName in self._categories:
    		self.create_category(categoryName=categoryName)
    	self._categories[category].add_signal_process(process)

   	def add_background_process(self, process, categoryName=None):
   		"""
    	Adds a background process and creates a categoryObject where the processObject is stored
    	if there is no categoryObject.
    	"""
    	if categoryName==None:
    		categoryName=process.category
    	if not categoryName in self._categories:
    		self.create_category(categoryName=categoryName)
    	self._categories[category].add_background_process(process)


    def create_process(self,categoryName,processName,processType,file=None,key_nominal_hist=None,key_systematic_hist=None):
        """
        Adds a signal or background process dependant on the value x of the processType 
        (x<=0 signal process, x>=1 background process)
        If no list of file and key names is handed over, it uses the default information of the category object
        to initialize a process.
        """
        if self._debug>100:
            print key_nominal_hist
            print key_systematic_hist
        if int(processType)<=0:
            self._categories[categoryName].create_signal_process(processName=processName,
                            rootfile=file,histoname=key_nominal_hist,systkey=key_systematic_hist)
        elif int(processType)>0:
            self._categories[categoryName].create_background_process(processName=processName,
                            rootfile=file,histoname=key_nominal_hist,systkey=key_systematic_hist)

        if self._debug >= 50:
                    print "initialized process", processName, "in category", categoryName
                    print self._categories[categoryName]



    def load_from_file(self, pathToDatacard):
        """
        Reads datacard from file. Creates categoryObjects for each category and
        processObjects for the corresponding processes. 
        Adds filename, nominal histname and systematic histname.
        Adds systematics for corresponding processes.
        """
        if path.exists(pathToDatacard):
            print "loading datacard from", pathToDatacard
            #Read datacard from file.
            with open(pathToDatacard) as datacard:
                lines = datacard.read().splitlines()
                self._shapelines_ 		= []
                self._systematics_ 		= []
                self._processes_ 		= ""
                self._binprocesses_ 	= ""
                self._processtype_ 		= ""
                self._header            = []
                self._bins              = ""
                self._observation       = ""

                for n, line in enumerate(lines):
                    #missing lines for advanced datacards, only working for simple ones
                    if line.startswith("-"):
                            continue
                    elif line.startswith("Combination") or line.startswith("imax") or line.startswith("kmax") or line.startswith("jmax"):
                        self._header.append(line)
                    elif line.startswith("bin") and n != len(lines) and lines[n+1].startswith("observation"):
                        self._bins = line
                        self._observation = lines[n+1]
                    elif line.startswith("shapes"):
                        self._shapelines_.append(line)
                    elif line.startswith("process") and n != 0 and lines[n-1].startswith("bin"):
                        self._processes_= line
                        self._binprocesses_= lines[n-1]  
                        self._processtype_ = lines[n+1]
                    elif line.startswith("bin") and lines[n+1].startswith("process"):
                        pass
                    elif line.startswith("process") and lines[n+1].startswith("rate"):
                        pass
                    elif line.startswith("observation") or line.startswith("rate"):
                        pass
                    elif "autoMCStats" in line:
                        pass
                    else:
                        self._systematics_.append(line)
            
            #Create categoryObject for each category
            #first cleanup lines
            categories=self._bins.split()
            categories.pop(0)
            self.load_from_file_add_categories(list_of_categories= categories)
            
            #Create processObjects for each process in a category 
            #and add it to its correspoding categoryObjects 
            #first cleanup lines          
            processes = self._processes_.split()
            processes.pop(0)
            categoryprocesses = self._binprocesses_.split()
            categoryprocesses.pop(0) 
            processtypes = self._processtype_.split()
            processtypes.pop(0)
            #checks if file is properly written
            assert len(processes)==len(categoryprocesses) 
            assert len(processes)==len(processtypes)
            #add processes to categories
            self.load_from_file_add_processes(list_of_categories=categoryprocesses,
                list_of_processes=processes, list_of_processtypes=processtypes)

            # #adds systematics to processes
            self.load_from_file_add_systematics(list_of_categories=categoryprocesses,
                list_of_processes=processes)
            
             
        else:
            print "could not load %s: no such file" % pathToDatacard


    def load_from_file_add_categories(self,list_of_categories):
        """
        Line for categories: careful with combined categories, 
        key logic wont be working cause channels will be numerated
        original name in Combination line
        """
        for shapelines in self._shapelines_:
            shape = shapelines.split()
            category_name   = shape[2]
            process_name    = shape[1]
            file 			= shape[3]
            histname 		= shape[4]
            systname		= shape[5]
            if category_name=="*" and process_name=="*":
                    for category in list_of_categories:
                        self.create_category(categoryName=category,
                        default_file=file,generic_key_systematic_hist=systname,
                        generic_key_nominal_hist=histname)
            elif category_name in list_of_categories and process_name== "*":
                self.create_category(categoryName=category_name,
                        default_file=file,generic_key_systematic_hist=systname,
                        generic_key_nominal_hist=histname)
        for category in list_of_categories:
            if not category in self._categories:
                self._categories[categoryName]=categoryObject(categoryName=category)
        

    def load_from_file_add_processes(self,list_of_processes,list_of_categories,list_of_processtypes):
        """
        Adds processes to the corresponding categories.
        Initializes process with file and key information.
        """
        for shapelines in self._shapelines_:
            shape = shapelines.split()
            category_name   = shape[2]
            process_name    = shape[1]
            file 			= shape[3]
            histname 		= shape[4]
            systname		= shape[5]
            #if the process is explicitly written in the file, initialize process with file and key information of the readout file
            for category,process,processtype in zip(list_of_categories,list_of_processes,list_of_processtypes):
                if (category_name==category and process_name ==process) or (category_name=="*" and process_name==process):
                    self.create_process(categoryName=category, processName=process_name,
                    					processType=processtype, file=file, 
                    					key_nominal_hist=histname, key_systematic_hist=systname)
        # if the process is not explicitly written in the file, initialize process with 
        # the generic keys and default file of the corresponding category
        for category,process,processtype in zip(list_of_categories,list_of_processes,list_of_processtypes):
            if not process in self._categories[category]:
                self.create_process(categoryName=category,processName=process,processType=processtype)


    def load_from_file_add_systematics(self,list_of_categories,list_of_processes):
        """
        One line for one systematic, knows type: adds systematic to process with 
        value given in the file
        """
        for systematics in self._systematics_:
                systematic = systematics.split()
                sys=systematic[0]
                typ=systematic[1]
                systematic.pop(1)
                systematic.pop(0)
                for value,process,category in zip(systematic,list_of_processes,list_of_categories):
                    if value!="-":
                        self._categories[category][process].add_uncertainty( syst = sys,
                                                            typ = typ, value = value)


