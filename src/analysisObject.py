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
                print "ERROR: Category %s is known to this analysisObject!" % catname
        else:
            print "ERROR: Input required to be instance of categoryObject!"

    def create_category(self,categoryName,default_file=None,
                        generic_key_systematic_hist=None,
                        generic_key_nominal_hist=None):
        """
        Initializes a categoryObject with default file and generic keys.
        """
        self._categories[categoryName] = categoryObject(categoryName=categoryName,
                                    defaultRootFile=default_file,
                                    systkey=generic_key_systematic_hist,
                                    defaultnominalkey=generic_key_nominal_hist)
        if self._debug >= 50:
                    print "initialized category", categoryName
                    print self._categories[categoryName]

    def delete_category(self,categories):
        if isinstance(categories,list):
            for category in categories:
                if category in self._categories:
                    del self._categories[category]
                else:
                    if self._debug>30:
                        print "DEBUG: Category %s doesnt exist" % categoryName
        elif isinstance(categories,str):
            if categories in self._categories:
                    del self._categories[categories]
            else:
                if self._debug>30:
                    print "DEBUG: Category %s doesnt exist" % categoryName
        else: 
            print "ERROR: Enter list or string"


    def add_signal_process(self, process, categoryName=None):
        """
        Adds a signal process and creates a categoryObject where the processObject is stored
        if there is no categoryObject. Maps to the categoryObject function. 
        Logic if process is already known is found there.
        """
        if categoryName==None:
            categoryName=process.category
        if categoryName in self._categories:
            self._categories[category].add_signal_process(process)
        else:
            print "ERROR: No category %s in analysisObject" % categoryName

    def create_signal_process(self,categoryName,processName,
                        file=None,key_nominal_hist=None,
                        key_systematic_hist=None):
        """
        Adds a signal or background process dependant on the value x of the processType 
        (x<=0 signal process, x>=1 background process) 
        Maps to the categoryObjects function.
        If no list of file and key names is handed over, it uses the default information 
        of the category object in the categoryObject to initialize a process.
        """
        if self._debug>100:
            print key_nominal_hist
            print key_systematic_hist
        
        self._categories[categoryName].create_signal_process(processName=processName,
                           rootfile=file,histoname=key_nominal_hist,systkey=key_systematic_hist)

        if self._debug >= 50:
                    print "initialized process", processName, "in category", categoryName
                    print self._categories[categoryName]

    def add_background_process(self, process, categoryName=None):
        """
        Adds a background process and creates a categoryObject where the processObject is stored
        if there is no categoryObject. Maps to the categoryObject function.
        Logic if process is already known is found there.
        """
        if categoryName==None:
            categoryName=process.category
        if categoryName in self._categories:
            self._categories[category].add_background_process(process)
        else:
            print "ERROR: No category %s in analysisObject" % categoryName


    def create_background_process(self,categoryName,processName,
                        file=None,key_nominal_hist=None,
                        key_systematic_hist=None):
        """
        Adds a signal or background process dependant on the value x of the processType 
        (x<=0 signal process, x>=1 background process) 
        Maps to the categoryObjects function.
        If no list of file and key names is handed over, it uses the default information 
        of the category object in the categoryObject to initialize a process.
        """
        if self._debug>100:
            print key_nominal_hist
            print key_systematic_hist
        
        self._categories[categoryName].create_background_process(processName=processName,
                           rootfile=file,histoname=key_nominal_hist,systkey=key_systematic_hist)
        
        if self._debug >= 50:
                    print "initialized process", processName, "in category", categoryName
                    print self._categories[categoryName]

    def delete_process_for_all_categories(self,processes):
        if isinstance(processes,str):
            for category in self._categories:
                self._delete_process(processName=processes, categoryName=category)
        elif isinstance(processes,list):
            for process in processes:
                for category in self._categories:
                    self._delete_process(processName=process, categoryName=category)
                
    def _delete_process(self,processName,categoryName):
        if processName in self._categories[categoryName]:
            self._categories[categoryName].delete_process(processes=processName)
            if self._debug>30:
                print "DEBUG: deleted process %s in category %s" % (processName,categoryName)


    def delete_systematic_for_all_processes(self,systematics):
        if isinstance(systematics,str):
            for category in self._categories:
                continue
                # self._delete_process(processName=processes, categoryName=category)
        elif isinstance(systematics,list):
            for process in processes:
                for category in self._categories:
                    for process in self:
                        continue
                    # self._delete_process(processName=process, categoryName=category)

    def update_systematics(self, category):
        #does not update only collects first time?
        self._collect_uncertainties(process_dict = category.signal_processes)
        self._collect_uncertainties(process_dict = category.background_processes)


    def _collect_uncertainties(self, process_dict):
        """
        Loop over all process in the dictionary 'process_dict' and save
        the respective systematic uncertainties and correlations
        """
        for process_name in process_dict:
            process = process_dict[process_name]
            for syst in process.uncertainties:
                #first, check if uncertainty is already known
                #if not, create new systematicsObject
                if not syst in self._systematics:
                    self._systematics[syst] = systematicObject(name = syst,
                                    nature = process.get_uncertainty_type(syst))
                self._systematics[syst].add_process(process = process)


    """
    Function to create analysisObject from datacard
    """
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
                shape_lines             = []
                systematic_lines        = []
                process_line            = ""
                categoryprocess_line    = ""
                processtype_line        = ""
                categories_line         = ""
                #header_lines are not used right now
                header_lines            = []
                #observation_line is not used right now
                observation_line        = ""

                for n, line in enumerate(lines):
                    #missing lines for advanced datacards, only working for simple ones
                    if line.startswith("-"):
                            continue
                    elif line.startswith("Combination") or line.startswith("imax") or line.startswith("kmax") or line.startswith("jmax"):
                        header_lines.append(line)
                    elif line.startswith("bin") and n != len(lines) and lines[n+1].startswith("observation"):
                        categories_line = line
                        observation_line = lines[n+1]
                    elif line.startswith("shapes"):
                        shape_lines.append(line)
                    elif line.startswith("process") and n != 0 and lines[n-1].startswith("bin"):
                        process_line= line
                        categoryprocess_line= lines[n-1]  
                        processtype_line = lines[n+1]
                    elif line.startswith("bin") and lines[n+1].startswith("process"):
                        pass
                    elif line.startswith("process") and lines[n+1].startswith("rate"):
                        pass
                    elif line.startswith("observation") or line.startswith("rate"):
                        pass
                    elif "autoMCStats" in line:
                        pass
                    else:
                        systematic_lines.append(line)
            
            #Create categoryObject for each category
            #first cleanup lines
            categories=categories_line.split()
            categories.pop(0)
            self._load_from_file_add_categories(list_of_categories= categories,
                                                list_of_shapelines=shape_lines)
            
            #Create processObjects for each process in a category 
            #and add it to its correspoding categoryObjects 
            #first cleanup lines          
            processes = process_line.split()
            processes.pop(0)
            categoryprocesses = categoryprocess_line.split()
            categoryprocesses.pop(0) 
            processtypes = processtype_line.split()
            processtypes.pop(0)
            #checks if file is properly written
            assert len(processes)==len(categoryprocesses) 
            assert len(processes)==len(processtypes)
            #add processes to categories
            self._load_from_file_add_processes(list_of_categories=categoryprocesses,
                list_of_processes=processes, list_of_processtypes=processtypes,
                list_of_shapelines=shape_lines)

            #adds systematics to processes
            self._load_from_file_add_systematics(list_of_categories=categoryprocesses,
                list_of_processes=processes,list_of_systematics=systematic_lines)
            
             
        else:
            print "could not load %s: no such file" % pathToDatacard


    def _load_from_file_add_categories(self,list_of_categories,list_of_shapelines):
        """
        Line for categories: careful with combined categories, 
        key logic wont be working cause channels will be numerated
        original name in Combination line
        """
        for shapelines in list_of_shapelines:
            shape = shapelines.split()
            category_name   = shape[2]
            process_name    = shape[1]
            file            = shape[3]
            histname        = shape[4]
            systname        = shape[5]
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
        

    def _load_from_file_add_processes(self,list_of_processes,list_of_categories,
                                        list_of_processtypes,list_of_shapelines):
        """
        Adds processes to the corresponding categories.
        Initializes process with file and key information.
        """
        for shapelines in list_of_shapelines:
            shape = shapelines.split()
            category_name   = shape[2]
            process_name    = shape[1]
            file            = shape[3]
            histname        = shape[4]
            systname        = shape[5]
            #if the process is explicitly written in the file, initialize process with file and key information of the readout file
            for category,process,processtype in zip(list_of_categories,list_of_processes,list_of_processtypes):
                if (category_name==category and process_name ==process) or (category_name=="*" and process_name==process):
                    if int(processtype)<=0:
                        self.create_signal_process(categoryName=category, processName=process_name,
                                        processType=processtype, file=file, 
                                        key_nominal_hist=histname, key_systematic_hist=systname)
                    elif int(processtype)>0:
                        self.create_background_process(categoryName=category, processName=process_name,
                                        processType=processtype, file=file, 
                                        key_nominal_hist=histname, key_systematic_hist=systname)
        # if the process is not explicitly written in the file, initialize process with 
        # the generic keys and default file of the corresponding category
        for category,process,processtype in zip(list_of_categories,list_of_processes,list_of_processtypes):
            if not process in self._categories[category]:
                if int(processtype)<=0:
                    self.create_signal_process(categoryName=category,
                                    processName=process,processType=processtype)
                elif int(processtype)>0:
                    self.create_signal_process(categoryName=category,
                                    processName=process,processType=processtype)


    def _load_from_file_add_systematics(self,list_of_categories,list_of_processes,list_of_systematics):
        """
        One line for one systematic, knows type: adds systematic to process with 
        value given in the file
        """
        for systematics in list_of_systematics:
            systematic = systematics.split()
            sys=systematic[0]
            typ=systematic[1]
            systematic.pop(1)
            systematic.pop(0)
            for value,process,category in zip(systematic,list_of_processes,list_of_categories):
                if value!="-":
                    self._categories[category][process].add_uncertainty( syst = sys,
                                                            typ = typ, value = value)

    """
    Function to add processes to analysisObject from CSV File
    Categories in analysis object have to be declared first!
    """
    def load_from_csv_file(self,filename):
        if self._categories:
            for category in self._categories:
                self._categories[category].add_from_csv(filename)
        else:
            print "-"*130
            print "ERROR: no categories in analysisObject! Create categoryObjects first!"
            print "-"*130


    def __str__(self):
        s = []
        s.append("List of Categories:")
        s.append("_"*30)
        for category in self._categories:
            s.append("%s" % self._categories[category])
            s.append("_"*30)
        return "\n".join(s)

    def __getitem__(self, categoryName):
        
        if categoryName in self._categories:
            return self._categories[categoryName]
        else:
            print "ERROR: Process not in Category!"

    def __iter__(self):
        all_categories=self._categories
        return all_categories.__iter__()

    def __contains__(self, categoryName):
        if categoryName in self._categories:
            return True
        else:
            return False


