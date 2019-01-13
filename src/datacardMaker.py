import sys
import operator
from os import path

directory = path.abspath(path.realpath(path.dirname(__file__)))
if not directory in sys.path:
    sys.path.append(directory)

from analysisObject import analysisObject
from categoryObject import categoryObject
from processObject import processObject
from systematicObject import systematicObject

class datacardMaker(object):
    _debug = 200
    def init_variables(self):
        self._block_separator   = "\n" + "-"*130 + "\n"
        self._hardcode_numbers = True
        self._replace_files = False

    def __init__(   self, analysis = None,
                    outputpath = "", replacefiles=False,
                    hardcodenumbers=False):
        self.init_variables()
        if replacefiles:
            self.replace_files = replacefiles
        if hardcodenumbers:
            self.hardcode_numbers = hardcodenumbers
        if outputpath:
            self.outputpath = outputpath
            if analysis:
                self.write_datacard(analysis)


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
    def block_separator(self, seperator):
        self._block_separator = seperator

    
    def write_datacard(self,analysis):
        """
        Main function to write datacard from analysis object
        """
        if not isinstance(analysis,analysisObject):
            print "ERROR! No analysisObject!"
            return False
        text = ""
        if self._outputpath and not path.exists(self._outputpath):
            text = self.create_datacard_text(analysis=analysis)
        elif path.exists(self._outputpath) and self._replace_files:
            text = self.create_datacard_text(analysis=analysis)

        if not text == "":
            with open(self._outputpath, "w") as f:
               f.write(text)
        else:
            print "ERROR: Could not write datacard here:", self._outputpath

    def create_datacard_text(self,analysis):
        """
        collect all datacard parts and separates them with the 
        defined block separator 
        """
        content = []
        """
        create the header
        """
        content.append(self.create_header(analysis=analysis))
        """
        create the keyword block
        """
        content.append(self.create_keyword_block(analysis=analysis))
        """
        create observation block
        """
        content.append(self.create_observation_block(analysis=analysis))
        """
        create block for systematic variations and corresponding process
        and categories
        """
        content.append(self.create_process_block(analysis=analysis))
        content.append(self.create_systematics_block(analysis=analysis))
        
        return self._block_separator.join(content)
            

    def create_header(self,analysis):
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
        number_categories = "*"
        number_processes = "*"
        number_systematics = "*"
        if self._hardcode_numbers:
            if len(analysis.categories) != 0:
                number_categories = len(analysis.categories)
            else:
                print "Could not find categories! Cannot hard code 'imax'"
            
            #get number of processes
            number_processes = self.get_number_of_procs(analysis=analysis) - 1
            if number_processes is -1: number_processes = "*"
            
            #get number of systematics
            if len(analysis.systematics) != 0:
                number_systematics = len(analysis.systematics)
            else:
                print "WARNING: Did not find any systematics!"
        

        header.append("imax {0} number of bins".format(number_categories))
        header.append("jmax {0} number of processes minus 1".format(number_processes))
        # header.append("kmax {0} number of nuisance parameters".format(number_systematics))
        header.append("kmax * number of nuisance parameters")
        return "\n".join(header)

    def get_number_of_procs(self,analysis):
        """
        Get number of processes. Returns 0 if some categories have different
        amount of processes!
        """
        number = 0
        for category in analysis.categories:
            currentnumber = analysis[category].n_signal_procs
            currentnumber += analysis[category].n_background_procs
            if number is 0: number = currentnumber
            if not number is currentnumber:
                print "Mismatch! Categories have different number of processes!"
                number = 0
                break
        return number

    def create_keyword_block(self,analysis):
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
        size=self.get_max_size([analysis.categories,self.get_bkg_processes(analysis=analysis),self.get_signal_processes(analysis=analysis)])
        size+=5
        sizekeys=self.get_max_size_keys(analysis)
        sizekeys+=5
        if self._debug>99:
            print "DEBUGGING"
            print "-".ljust(50)
            print sizekeys 
            print "-".ljust(50)

        lines = []
        for category in analysis.categories:
            lines +=(self.write_keyword_process_lines(category=analysis[category],size=size,sizekeys=sizekeys))
        return "\n".join(lines)

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
        data_obs = category.observation
        if not data_obs is None and not data_obs.file == category.default_file:
            file = data_obs.file
            key_nominal_hist=data_obs.key_nominal_hist
            key_systematic_hist=data_obs.key_systematic_hist
            if not file=="" and not key_nominal_hist=="" and not key_systematic_hist=="":
                line.append(self.write_keyword_block_line(process_name=data_obs.name,category_name=category.name,file=file,
                    nominal_key=key_nominal_hist,syst_key=key_systematic_hist,size=size,sizekeys=sizekeys))
        return line

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

    
            
    def get_max_size_keys(self,analysis):
        keynames=[]
        for category_name in analysis.categories:
            category=analysis[category_name]
            keynames.append(category.default_file)
            keynames.append(category.generic_key_nominal_hist)
            keynames.append(category.generic_key_systematic_hist)
            for process_name in category:
                process=analysis[category_name][process_name]
                keynames.append(process.file)
                keynames.append(process.key_nominal_hist)
                keynames.append(process.key_systematic_hist)
            process=analysis[category_name].observation
            if not process is None:
                keynames.append(process.file)
                keynames.append(process.key_nominal_hist)
                keynames.append(process.key_systematic_hist)
        keynames = [x for x in keynames if x != "" and not x is None]
        print keynames
        return len(max(keynames,key=len))


    
        

    def create_observation_block(self,analysis):
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
        for category in analysis.categories:
            obs=0
            value=True

            bins.append("%s" % category)
            data_obs = analysis[category].observation
            if isinstance(data_obs, processObject):
                if not self._hardcode_numbers:
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

    def create_process_block(self,analysis):
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

        """
        get sorted list of signal processes and backgroundprocesses for 
        all categories for better readability
        """
        signalprocs=self.get_signal_processes(analysis=analysis)
        bkgprocs=self.get_bkg_processes(analysis=analysis)

        
        lines = []
        """
        Leaves one bin empty, necessary for systematics block
        """
        bins = ["bin",""]
        process = ["process",""]
        process_index = ["process",""]
        rate = ["rate","" ]

        for category in analysis.categories:
            """
            Signal processes first
            """
            for number,signal_process in enumerate(signalprocs):

                bins.append("%s" % category)
                process.append("%s" % signal_process)

                index=1+number-len(analysis[category].signal_processes)
                process_index.append("%s" % str(index))

                rate.append("%s" % str(analysis[category][signal_process].eventcount))
            """
            Same with background processes 
            """
            for number,bkg_process in enumerate(bkgprocs):
                bins.append("%s" % category)
                process.append("%s" % bkg_process)

                index=1+number
                process_index.append("%s" % str(index))
                rate.append("%s" % str(analysis[category][bkg_process].eventcount))
        size=self.get_max_size([bins,process,analysis.systematics])
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


    
    def get_signal_processes(self,analysis):
    	#Overwriting for more than 1 category, only working when same processes for all categories
        for category in analysis.categories:
        	sigprc=sorted(analysis[category].signal_processes)
      	return sigprc

    def get_bkg_processes(self,analysis):
    	#Overwriting for more than 1 category, only working when same processes for all categories
        for category in analysis.categories:
        	bkgprc=sorted(analysis[category].background_processes)
      	return bkgprc



    def get_max_size(self,liste):
        templiste=[]
        for element in liste:
            if not len(element) == 0:
                templiste.append(max(element,key=len))
        return len(max(templiste,key=len))


    def create_systematics_block(self,analysis):
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
        signalprocs=self.get_signal_processes(analysis)
        bkgprocs=self.get_bkg_processes(analysis)

        size=self.get_max_size([signalprocs,bkgprocs,analysis.systematics,analysis.categories])
        size+=5

        lines = []


        for systematic in sorted(analysis.systematics):
            temp="%s" % systematic.ljust(size)
            temp+="%s" % str(analysis.systematics[systematic].type).ljust(size)
            for category in analysis.categories:
                """
                Signal processes first, then background processes
                """
                for number,signal_process in enumerate(signalprocs):
                    temp += "%s" % str(analysis.systematics[systematic].get_correlation_raw(process_name=signal_process,
                                                                              category_name=category)).ljust(size)   
                for number,bkg_process in enumerate(bkgprocs):
                    temp += "%s" % str(analysis.systematics[systematic].get_correlation_raw(process_name=bkg_process,
                                                                             category_name=category)).ljust(size)
            lines.append(temp)
       	return "\n".join(lines)

    

    

