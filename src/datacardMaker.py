import sys
import operator
from os import path

directory = path.abspath(path.realpath(path.dirname(__file__)))
if not directory in sys.path:
    sys.path.append(directory)

from categoryObject import categoryObject
from processObject import processObject
from systematicObject import systematicObject

class datacardMaker(object):
    _debug = 200
    def init_variables(self):
        self._header            = []
        self._bins              = ""
        self._observation       = ""
        self._categories        = {}
        self._systematics       = {}
        self._hardcode_numbers  = False
        self._replace_files     = False
        self._outputpath        = ""
        self._block_separator   = "\n" + "-"*130 + "\n"

    def __init__(   self, pathToDatacard = "", 
                    processIdentifier = "$PROCESS",
                    channelIdentifier = "$CHANNEL",
                    systIdentifier = "$SYSTEMATIC"):
        self.init_variables()
        if pathToDatacard:
            self.load_from_file(pathToDatacard)

    @property
    def hardcode_numbers(self):
        return self._hardcode_numbers
    @hardcode_numbers.setter
    def hardcode_numbers(self, val):
        if type(val) == bool:
            self._hardcode_numbers = val
        else:
            print "Value given is not boolean! Did not set 'hardcode_numbers'"

    @property
    def replace_files(self):
        return self._replace_files
    @replace_files.setter
    def replace_files(self, val):
        if type(val) == bool:
            self._replace_files = val
            if self._debug >= 99:
                print "DEBUG: setting 'replace_files' to", val
        else:
            print "Value given is not boolean! Did not set 'replace_files'"

    @property
    def outputpath(self):
        return self._outputpath
    @outputpath.setter
    def outputpath(self, outpath):
        if outpath is None:
            print "'outpath' cannot be None!"
        elif path.exists(outpath):
            outpath = path.abspath(outpath)
            self._outputpath = outpath
            if self._replace_files:
                print "will replace", self._outputpath
            else:
                s = "WARNING: File %s already exists" % outpath
                s += " and I'm not allowed to overwrite"
                print s
        else:
            outpath = path.abspath(outpath)
            dirname = path.dirname(outpath)
            if path.exists(dirname):
                self._outputpath = outpath
                print "Will create new datacard here:", self._outputpath
            else:
                s = "Directory %s does not exist" % dirname
                s += ", cannot use path", outpath
                print s

    @property
    def block_separator(self):
        return self._block_separator
    @block_separator.setter
    def block_separator(self, sep):
        self._block_separator = sep
    
    
    def add_category(self, category):
        if isinstance(category, categoryObject):
            catname = category.name
            if not catname in self._categories:
                self._categories[catname] = category
                # self.update_systematics(category = category)
            else:
                print "ERROR: Category %s is known to this datacard!" % catname
        else:
            print "ERROR: Input required to be instance of categoryObject!"


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
                self._shapelines_ = []
                self._systematics_ = []
                self._processes_= ""
                self._binprocesses_= ""
                self._processtype_ = ""
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
            #add processes to categoryObjects
            self.load_from_file_add_processes(list_of_categories=categoryprocesses,
                list_of_processes=processes, list_of_processtypes=processtypes)

            #add filename, nominal histnam and systematic histname
            #for processObjects and categoryObjects
            self.load_from_file_add_file_and_keynames()


            #adds systematics to processes
            self.load_from_file_add_systematics(list_of_categories=binprocesses,
                list_of_processes=processes )
            
             
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
            category_name = shape[2]
            process_name = shape[1]
            if category_name=="*" and process_name=="*":
                    for category in list_of_categories:
                        self.load_from_file_add_category(list_of_filekeylines=shape,
                                                categoryName=category)
            elif category_name in list_of_categories and process_name== "*":
                self.load_from_file_add_category(list_of_filekeylines=shape,
                                            categoryName=category_name)
        for category in list_of_categories:
            if not category in self._categories:
                self._categories[categoryName]=categoryObject(categoryName=category)
        


    def load_from_file_add_category(self,list_of_filekeylines,categoryName):
        default_file = list_of_filekeylines[3]
        generic_key_nominal_hist = list_of_filekeylines[4]
        generic_key_systematic_hist = list_of_filekeylines[5]
        self._categories[categoryName] = categoryObject(categoryName=categoryName,
                        defaultRootFile=default_file,systkey=generic_key_systematic_hist,
                        defaultnominalkey=generic_key_nominal_hist)
        if self._debug >= 50:
                    print "initialized category", categoryName
                    print self._categories[categoryName]


    def load_from_file_add_processes(self,list_of_processes,list_of_categories,list_of_processtypes):
        for shapelines in self._shapelines_:
            shape = shapelines.split()
            category_name = shape[2]
            process_name = shape[1]
            if (category_name in list_of_categories) and (process_name in list_of_processes):
                self.load_from_file_add_process(list_of_filekeylines=shape,categoryName=category_name,processName=process_name)
            elif category_name==0 and process_name in list_of_processes:
        for category,process,processtype in zip(list_of_categories,list_of_processes,list_of_processtypes):
            if not process in self._categories[category]:
                if processtype<=0:
                    self._categories[category].create_signal_process(processName=process)
                else:
                    self._categories[category].create_background_process(processName=process)


    def load_from_file_add_process(self,list_of_filekeylines,categoryName,processName):
        file = list_of_filekeylines[3]
        key_nominal_hist = list_of_filekeylines[4]
        key_systematic_hist = list_of_filekeylines[5]
        self._categories[categoryName].create_process(processName=processName,
                        rootfile=file,systkey=key_systematic_hist,
                        histoname=key_nominal_hist)
        if self._debug >= 50:
                    print "initialized process", processName, "in category", categoryName
                    print self._categories[categoryName]

    # def load_from_file_add_processes_raw(self,list_of_processes,list_of_categories,
    #                                     list_of_processtypes):
    #     """
    #     Adds empty processObject to categoryObject
    #     """
    #     for process,category,pt in zip(list_of_processes,list_of_categories,list_of_processtypes):

    #             proc=processObject(processName=process, categoryName=category)
    #             processtype = int(pt)
    #             #checks if process is a background or signal process and 
    #             #adds it to the categoryObject
    #             if processtype >= 1:
    #                 self._categories[category].add_background_process(proc)
    #             else:
    #                 self._categories[category].add_signal_process(proc)

    def load_from_file_add_file_and_keynames(self):
        for shapelines in self._shapelines_:
                shape = shapelines.split()
                category_name = shape[2]
                process_name = shape[1]
                if category_name=="*":
                    for category in self._categories:
                        if process_name=="*":
                            self.load_from_file_add_generic_keys(category_name=category,
                                list_of_shapelines=shape)
                        self.load_from_file_manage_processes(category_name=category,
                            process_name=process_name,list_of_shapelines=shape)
                elif category_name in self._categories:
                    if process_name == "*":
                        self.load_from_file_add_generic_keys(category_name=category_name,
                            list_of_shapelines=shape)
                    self.load_from_file_manage_processes(category_name = category_name,
                         process_name=process_name,list_of_shapelines=shape)


    def load_from_file_add_generic_keys(self,category_name,list_of_shapelines):
    	#adds generic key for categories
        category=self._categories[category_name]
        category.default_file = list_of_shapelines[3]
        category.generic_key_nominal_hist = list_of_shapelines[4]
        category.generic_key_systematic_hist = list_of_shapelines[5]

    def load_from_file_add_keys(self, category_name,process_name,list_of_shapelines):
        """
        add filename, nominal key and systematic key to processObject
        """
        process = self._categories[category_name][process_name]
        process.file = list_of_shapelines[3]
        process.key_nominal_hist = list_of_shapelines[4]
        process.key_systematic_hist = list_of_shapelines[5]


    def load_from_file_manage_processes(self, category_name, process_name, list_of_shapelines):
        """
        Search process corresponding to shapeline and add the explicit key names
        """
        if process_name == "*":
            for process in self._categories[category_name]:
                self.load_from_file_add_keys(category_name=category_name,
                    process_name=process,list_of_shapelines=list_of_shapelines)
        elif process_name in self._categories[category_name]:
            self.load_from_file_add_keys(category_name=category_name,
                    process_name=process_name,list_of_shapelines=list_of_shapelines)
        else:
            print "could not find process %s in category %s" % (process_name, category_name)


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

    def get_number_of_procs(self):
        """
        Get number of processes. Returns 0 if some categories have different
        amount of processes!
        """
        num = 0
        for cat in self._categories:
            currentnum = self._categories[cat].n_signal_procs
            currentnum += self._categories[cat].n_background_procs
            if num == 0: num = currentnum
            if not num == currentnum:
                print "Mismatch! Categories have different number of processes!"
                num = 0
                break
        return num

    def collect_uncertainties(self, process_dict):
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


    def update_systematics(self, category):
        
        self.collect_uncertainties(process_dict = category.signal_processes)
        self.collect_uncertainties(process_dict = category.background_processes)
            


    def create_header(self):
        """
        Create header for the datacard. The header has the following form:
        imax -> number of bins
        jmax -> number of processes minus 1
        kmax -> number of nuisance parameters

        If the flag 'hardcode_numbers' is set, the appropriate numbers are
        directly written to the datacard (recommended for debugging purposes).
        If not or a number cannot be obtained, '*' will be used. This forces
        text2workspace.py to calculate these numbers on the fly.
        """
        header = []
        ncats = "*"
        nprocs = "*"
        nsysts = "*"
        if True:
        #if self._hardcode_numbers: 
            #get number of categories
            if len(self._categories) != 0:
                ncats = len(self._categories)
            else:
                print "Could not find categories! Cannot hard code 'imax'"
            
            #get number of processes
            nprocs = self.get_number_of_procs() - 1
            if nprocs == -1: nprocs = "*"
            
            #get number of systematics
            if len(self._systematics) != 0:
                nsysts = len(self._systematics)
            else:
                print "WARNING: Did not find any systematics!"
        

        header.append("imax {0} number of bins".format(ncats))
        header.append("jmax {0} number of processes minus 1".format(nprocs))
        header.append("kmax {0} number of nuisance parameters".format(nsysts))
        return "\n".join(header)

    def write_keyword_block_line(self, process_name, category_name, file, 
                                    nominal_key, syst_key, size, sizekeys):
        if size<11: 
            size=11
        s = "shapes".ljust(size)
        s+= "%s" % (process_name).ljust(size)
        s+= "%s" %(category_name).ljust(size)
        s+= "%s" %(file).ljust(sizekeys)
        s+= "%s" %(nominal_key).ljust(sizekeys)
        s+= "%s" %(syst_key).ljust(sizekeys)

        print s
        return s

    def write_keyword_generic_lines(self, category, size, sizekeys):
        """
        Adds the generic key 
        """
        
        line = self.write_keyword_block_line(process_name = "*", 
           category_name = category.name, file = category.default_file, 
           nominal_key = category.generic_key_nominal_hist, 
           syst_key = category.generic_key_systematic_hist, size=size, 
           sizekeys=sizekeys)

        return line

    def write_keyword_process_lines(self,category,size,sizekeys):
        line=[]
        
        #adds the generic key
        line.append(self.write_keyword_generic_lines(category=category,sizekeys=sizekeys,size=size))
        #adds the process keys (need to add: only add process key if it doesnt match the generic key)
        for process in category:
            file=category[process].file
            key_nominal_hist=category[process].key_nominal_hist
            key_systematic_hist=category[process].key_systematic_hist
            if not file=="" and not key_nominal_hist=="" and not key_systematic_hist=="":
                line.append(self.write_keyword_block_line(process_name=process,category_name=category.name,file=file,
                    nominal_key=key_nominal_hist,syst_key=key_systematic_hist,size=size,sizekeys=sizekeys))
        return line
            
    def get_max_size_keys(self):
        keynames=[]
        for category_name in self._categories:
            category=self._categories[category_name]
            keynames.append(category.default_file)
            keynames.append(category.generic_key_nominal_hist)
            keynames.append(category.generic_key_systematic_hist)
            for process_name in category:
                process=self._categories[category_name][process_name]
                keynames.append(process.file)
                keynames.append(process.key_nominal_hist)
                keynames.append(process.key_systematic_hist)
        print keynames
        return len(max(keynames,key=len))


    def create_keyword_block(self):
        """
        Create block with keywords with which to find the systematic variations
        for different processes. This block has the following form:
        shape $PROCESS $CHANNEL /path/to/rootfile $NOMINAL_KEY $SYST_VAR_KEY

        with
        $PROCESS            - process name (can be '*' for all processes)
        $CHANNEL            - category name (can be '*' for all categories)
        /path/to/rootfile   - path to .root file with templates
        $NOMINAL_KEY        - key for nominal templates. If '*' was used before,
                              this should contain '$CHANNEL' and/or '$PROCESS'
        $SYST_VAR_KEY       - key for templates for systematic variations.
                              The key has to contain '$SYSTEMATIC'. If '*' was 
                              used before, this should contain '$CHANNEL' 
                              and/or '$PROCESS'
        """
        size=self.get_max_size([self._categories,self.get_bkg_processes(),self.get_signal_processes()])
        size+=5
        sizekeys=self.get_max_size_keys()
        sizekeys+=5
        if self._debug>99:
            print "DEBUGGING"
            print "-".ljust(50)
            print sizekeys 
            print "-".ljust(50)

        lines = []
        for category in self._categories:
            lines +=(self.write_keyword_process_lines(category=self._categories[category],size=size,sizekeys=sizekeys))
        return "\n".join(lines)
        

    def create_observation_block(self):
        """
        Create with observation. The block has the following format:
        
        bin         $CHANNEL_1      $CHANNEL_2      (...)
        observation $OBS_1_YIELD    $OBS_2_YIELD    (...)

        where
        $CHANNEL_X          - different categories
        $OBS_X_YIELD        - yield of template for data
        (...)               - place holder for more categories
                              THIS IS NOT PART OF THE DATACARD!
        """
        
        lines = []
        bins = ["bin"]
        observation = ["observation"]
        for category in self._categories:
            obs=0
            value=True

            bins.append("%s" % category)
            data_obs = self._categories[category].observation
            if isinstance(data_obs, processObject):
                if self._hardcode_numbers:
                    observation.append("-1")
                else:
                    observation.append("%s" % str(data_obs.eventcount))
            else:
                s = "WARNING: observed data in category %s" % category
                s += " is not set! Will set it to -1 - this could cause a crash"
                print s
                observation.append("-1")

        size= self.get_max_size([bins,observation])
        size+=5
        scaled_bins = [x.ljust(size) for x in bins]
        scaled_observation = [x.ljust(size) for x in observation]
        lines.append("".join(scaled_bins))
        lines.append("".join(scaled_observation))

        return "\n".join(lines)


    
    def get_signal_processes(self):
    	#Overwriting for more than 1 category, only working when same processes for all categories
        for category in self._categories:
        	sigprc=sorted(self._categories[category]._signalprocs)
      	return sigprc

    def get_bkg_processes(self):
    	#Overwriting for more than 1 category, only working when same processes for all categories
        for category in self._categories:
        	bkgprc=sorted(self._categories[category]._bkgprocs)
      	return bkgprc


    def create_process_block(self):
        """
        Create the process block of the datacard. It has the following format:
        bin         $CHANNEL_1          $CHANNEL_1        $CHANNEL_2       (...)
        process     $PROCESS_1          $PROCESS_2        $PROCESS_1       (...)
        process     $PROCESS_1_INDEX    $PROCESS_2_INDEX  $PROCESS_1_INDEX (...)
        rate        $PROCESS_1_YIELD    $PROCESS_2_YIELD  $PROCESS_1_YIELD (...)

        where
        $CHANNEL_X          - different categories
        $PROCESS_X          - name of process in respective channel
        $PROCESS_X_INDEX    - index of process (signal: <= 0, bkg: > 0)
        $PROCESS_X_YIELD    - yield of template for respective process
        (...)               - place holder for more categories
                              THIS IS NOT PART OF THE DATACARD!
        """

        signalprocs=self.get_signal_processes()
        bkgprocs=self.get_bkg_processes()

        
        lines = []
        #Leaves one bin empty, necessary for systematics block
        bins = ["bin",""]
        process = ["process",""]
        process_index = ["process",""]
        rate = ["rate","" ]

        for category in self._categories:
        	#Signal processes first
        	for number,signal_process in enumerate(signalprocs):

        		bins.append("%s" % category)
 	        	process.append("%s" % signal_process)

 	        	index=1+number-len(self._categories[category]._signalprocs)
	        	process_index.append("%s" % str(index))

 	        	rate.append("%s" % str(self._categories[category]._signalprocs[signal_process].eventcount))
        	#Same with background processes	
        	for number,bkg_process in enumerate(bkgprocs):
        		bins.append("%s" % category)
 	        	process.append("%s" % bkg_process)

 	        	index=1+number
	        	process_index.append("%s" % str(index))
	        	rate.append("%s" % str(self._categories[category]._bkgprocs[bkg_process].eventcount))
        size=self.get_max_size([bins,process,self._systematics])
        size+=5

        scaled_bins = [x.ljust(size) for x in bins]
        scaled_process = [x.ljust(size) for x in process]
        scaled_process_index = [x.ljust(size) for x in process_index]
        scaled_rate = [x.ljust(size) for x in rate]
        lines.append("".join(scaled_bins))
        lines.append("".join(scaled_process))
        lines.append("".join(scaled_process_index))
        lines.append("".join(scaled_rate))
        return "\n".join(lines)
        

    def get_max_size(self,liste):
        templiste=[]
        for element in liste:
            templiste.append(max(element,key=len))
        return len(max(templiste,key=len))


    def create_systematics_block(self):
        """
        Create block for nuisance parameters. Format is as follows:
        $SYST_1_NAME    $SYST_1_TYPE CORRELATION_PROC_1 CORRELATION_PROC_2 (...)
        $SYST_2_NAME    $SYST_2_TYPE CORRELATION_PROC_1 CORRELATION_PROC_2 (...)
        (...)           (...)           (...)           (...)              (...)

        where
        $SYST_X_NAME        - name of respective nuisance parameter
        $SYST_X_TYPE        - type of respective nuisance parameter
        $CORRELATION_PROC_X - correlation to respective processes

        IMPORTANT:  The order of process has to be the same as in the 
                    process block
        """
        signalprocs=self.get_signal_processes()
        bkgprocs=self.get_bkg_processes()

        size=self.get_max_size([signalprocs,bkgprocs,self._systematics,self._categories])
        size+=5

        lines = []
        for systematic in self._systematics:
            temp="%s" % systematic.ljust(size)
            temp+="%s" % str(self._systematics[systematic].type).ljust(size)
            for category in self._categories:
                #Signal processes first
                for number,signal_process in enumerate(signalprocs):
                    temp += "%s" % str(self._systematics[systematic].get_correlation_raw(process_name=signal_process,
                                                                              category_name=category)).ljust(size)   
                for number,bkg_process in enumerate(bkgprocs):
                    temp += "%s" % str(self._systematics[systematic].get_correlation_raw(process_name=bkg_process,
                                                                             category_name=category)).ljust(size)
            lines.append(temp)
       	return "\n".join(lines)

    def create_datacard_text(self):
        #create datacard header 
        content = []
        for cat in self._categories:
            self.update_systematics(self._categories[cat])
        content.append(self.create_header())
        #create keyword block
        content.append(self.create_keyword_block())
        #create observation block
        content.append(self.create_observation_block())
        #create block with keywords for systematic variations
        content.append(self.create_process_block())
        content.append(self.create_systematics_block())
        
        return self._block_separator.join(content)

    def write_datacard(self):
        text = ""
        if self._outputpath and not path.exists(self._outputpath):
            text = self.create_datacard_text()
        elif path.exists(self._outputpath) and self._replace_files:
            text = self.create_datacard_text()

        if not text == "":
            with open(self._outputpath, "w") as f:
               f.write(text)
        else:
            print "ERROR: Could not write datacard here:", self._outputpath

