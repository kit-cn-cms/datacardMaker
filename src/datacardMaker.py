import sys
from os import path

directory = path.abspath(path.realpath(path.dirname(__file__)))
if not directory in sys.path:
    sys.path.append(directory)

from categoryObject import categoryObject
from systematicObject import systematicObject

class datacardMaker(object):
    
    def init_variables(self):
        self._header            = []
        self._bins              = ""
        self._observation       = ""
        self._categories        = {}
        self._systematics       = {}
        self._hardcode_numbers  = False
        self._replace_files     = False
        self._outputpath        = "/path/for/datacard.txt"
        self._block_separator   = "-"*130

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
            if self._replace_files:
                outpath = path.abspath(outpath)
                self._outputpath = outpath
                print "will replace", self._outputpath
            else:
                s = "File %s already exists" % outpath
                s += " and I'm not allowed to overwrite - Skipping"
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
    
    
    def load_from_file(self, pathToDatacard):
        if path.exists(pathToDatacard):
            print "loading datacard from", pathToDatacard
            with open(pathToDatacard) as datacard:
                lines = datacard.read().splitlines()
                self._shapelines_ = []
                for n, line in enumerate(lines):
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
                        pass
                    else:
                        pass
                        
                        
        else:
            print "could not load %s: no such file" % pathToDatacard
    
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
                print "Mismatch! Categories have different number of process!"
                num = 0
                break
        return num

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
        if self._hardcode_numbers: 
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
        

        header.append("imax {0} number of bins".format(ncats))
        header.append("jmax {0} number of processes minus 1".format(nprocs))
        header.append("kmax {0} number of nuisance parameters".format(nsysts))
        return "\n".join(header)

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
        pass

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
        pass

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
        pass

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
        pass

    def write_datacard(self):
        if path.exists(self._outputpath):
            #create datacard header 
            content = []
            content.append(self.create_header())
            #create block with keywords for systematic variations

            #create observation block


            with open(self._outputpath, "w") as f:
                f.write(self._block_separator.join(content))
        else:
            print "ERROR: Could not write datacard here:", self._outputpath

