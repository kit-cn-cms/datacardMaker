from os import path
from sys import path as spath
thisdir = path.realpath(path.dirname(__file__))
basedir = path.join(thisdir, "../base")
if not basedir in spath:
    spath.append(basedir)
from identificationLogic import identificationLogic
from valueConventions import valueConventions
from fileHandler import fileHandler

class processObject(object):
    _id_logic = identificationLogic()
    identificationLogic.belongs_to = "process"
    _value_rules = valueConventions()
    
    
    def init_variables(self):
        self._name = ""
        self._file = None
        self._categoryname = ""
        self._nominalhistname = ""
        self._systkey = ""
        self._eventcount = -1
        self._uncertainties = {}
        self._debug = 0
        self._calculate_yield = False
        self._file_handler = fileHandler()


    def __init__(   self, processName = None, pathToRootfile = None, 
                    nominal_hist_key = None, systematic_hist_key = None, 
                    categoryName = None):
        self.init_variables()
        if not processName is None:
            self._name              = processName
        if not categoryName is None:
            self._categoryname      = categoryName
        if not pathToRootfile is None:
            self.file = pathToRootfile
        if not nominal_hist_key is None:
            self.key_nominal_hist   =nominal_hist_key
            if self._debug>=30:
                print "-"*130
                print "DEBUG PROCESSOBJECT INIT: setting key_nominal_hist to", self.key_nominal_hist
                print "-"*130
        if not systematic_hist_key is None:
            self.key_systematic_hist = systematic_hist_key
            if self._debug>=30:
                print "-"*130
                print "DEBUG PROCESSOBJECT INIT: setting key_systematic_hist to", self.key_systematic_hist
                print "-"*130
        
        #if self._calculate_yield:
        #    self._eventcount        = self.calculate_yield()
        if self._debug >= 3:
            s = "initialized process with name '%s'" % self._name
            s += " in category '%s'" % self._categoryname
            print s
        
    def calculate_yield(self):
        """
        returns yield (TH1D::Integral() ) for this process
        """
        y = -1

        temp = self._file_handler.get_integral(histname = self._nominalhistname)
        if temp:
            y = temp 
        return y

    #getter/setter for yields
    @property
    def eventcount(self):
        """
        get yield for process
        """
        y = self._eventcount
        if self._debug >= 99:
            print "returning yield of", y
        return y 

    @eventcount.setter
    def eventcount(self, val):
        """
        set yield for processes to value val
        """
        self._eventcount = val

    #logic for process name
    @property
    def name(self):
        """
        get name for process
        """
        return self._name
    @name.setter
    def name(self, s):
        """
        set process name
        """
        if self._debug >= 20: 
            print "setting name to", name
        self._name = name



    @property
    def category(self):
        """
        get name for category to which this process belongs to
        """
        return self._categoryname

    @category.setter
    def category(self, catname):
        """
        set name for category to which this process belongs to
        """
        if self._debug >= 20: 
            print "setting category to", catname
        self._categoryname = catname
    

    @property
    def file(self):
        return self._file_handler.filepath
    
    @file.setter
    def file(self, rootpath):
        if self._debug >= 20:
            print "setting filepath to", rootpath
        if path.exists(rootpath):
            self._file_handler.filepath = rootpath
            if not self.key_nominal_hist == "":
                self.eventcount = self.calculate_yield()
        else:
            print "file '%s' does not exist!" % rootpath

    @property
    def key_nominal_hist(self):
        return self._nominalhistname

    @key_nominal_hist.setter
    def key_nominal_hist(self, hname):
        if self._id_logic.is_nongeneric_key(hname):
            if path.exists(self.file):
                if self._file_handler.histogram_exists(histname = hname):
                    self._nominalhistname = hname
                    self._eventcount = self._file_handler.get_integral(hname)
        else:
            if self._debug>=30:
                print "-"*130
                print "DEBUG PROCESSOBJECT key_nominal_hist setter: detected generic key"
                print "-"*130
            hist = self._id_logic.build_nominal_histo_name(process_name = self._name, base_key = hname, 
                channel_name = self._categoryname)
            if self._debug>=30:
                print hist
            if self._file_handler.histogram_exists(histname = hist):
                self._nominalhistname = hist
                self._eventcount = self._file_handler.get_integral(hist)
        #else:
        #    s = "'%s' does not exist " % hname
        #    s += "in '%s'" % self._file_handler.filepath

    @property
    def key_systematic_hist(self):
        return self._systkey
    @key_systematic_hist.setter
    def key_systematic_hist(self, key):
        if self._id_logic.is_nongeneric_key(key):
            self._systkey = key
        else:
            systkey = self._id_logic.build_nominal_histo_name(process_name = self._name, base_key = key, 
                channel_name = self._categoryname)
            self._systkey = systkey
    
    @property
    def uncertainties(self):
        return list(self._uncertainties.keys())
     

    def add_uncertainty(self, syst, typ, value):
        """
        add an uncertainty to this process. This function checks
        - whether there already is an entry for 'systematicName'
        - the given value is suitable for a datacard 
            (see valueConventions.is_good_systval)
        and only adds the systematics if it's new and has a good value
        """
        if self._debug >=99:
            print "DEGUB: Entering function 'processObject.add_uncertainty'"
        if isinstance(syst, str) and isinstance(typ, str):
            if not syst in self._uncertainties:
                if not self._value_rules.is_allowed_type(typ=typ):
                    return False
                if self._debug >= 99:
                    print "DEBUG: type of uncertainty '%s' is '%s'" % (syst, typ)
                if typ == "shape":
                    if self._debug >= 99:
                        print "DEBUG: uncertainty type is shape!"
                    tmp = syst
                    if syst.startswith("#"):
                        tmp = tmp.replace("#","")
                        tmp = tmp.strip()
                    if self._debug>=30:
                        print "Looking for varied histograms for systematic", syst
                    keys = self._id_logic.build_systematic_histo_names(
                            systematic_name = tmp, base_key = self._systkey)
                    if self._debug >= 99:
                        print keys
                    if not all(self._file_handler.get_integral(k) > 0 for k in keys):
                        temp = "WARNING: Problems with histograms for " 
                        temp += "'%s' in process '%s'! " % (syst, self.name)
                        temp += "Will not add uncertainty '%s'" % syst
                        print temp
                        return False
                if self._value_rules.is_good_systval(value):
                    self._uncertainties[syst] = {}
                    self._uncertainties[syst]["type"] = typ
                    self._uncertainties[syst]["value"] = value
                    return True
                else:
                    print "Value '{0}' is not a good value!".format(value)
            else:
                temp = "There is already an entry for uncertainty " 
                temp += "'%s' in process '%s'! " % (syst, self.name)
                temp += "Please use 'set_uncertainty' instead."
                print temp
        else:
            s = "ERROR: Could not add uncertainty - "
            s += "both name and type of systematic are required to be strings!"
            print s
        return False


    def set_uncertainty(self, systematicName, typ, value):
        """
        set the uncertainty 'systematicName' for this process to type 'typ' 
        and value 'value'. This function checks
        - whether there is an entry for 'systematicName' in the first place
        - the given value is suitable for a datacard (see 'is_good_systval')
        and only adds the systematics if there is an entry and the value is good
        """
        if systematicName in self._uncertainties:
            if typ == "shape":
                keys = self._id_logic.build_systematic_histo_names(
                        systematic_name = tmp, base_key = self._systkey)
                if self._debug >= 99:
                        print keys
                if not all(self._file_handler.get_integral(k) > 0 for k in keys):
                    temp = "WARNING: Problems with histograms for " 
                    temp += "'%s' in process '%s'! " % (syst, self.name)
                    temp += "Will not add uncertainty '%s'" % syst
                    print temp
                    return False
            if self._value_rules.is_good_systval(value):
                self._uncertainties[systematicName]["value"] = str(value)
                self._uncertainties[systematicName]["type"] = typ
                return True
        else:
            s = "There is no entry for uncertainty %s" % systematicName
            s += " in process %s! Please add it first" % self.name
            print s
        return False

    def delete_uncertainty(self,systematicName):
        if systematicName in self._uncertainties:
            del self._uncertainties[systematicName]
            if self._debug>30:
                temp= "DEBUG: deleted uncertainty %s in process %s" % (systematicName,self.name)
                if not self.category=="":
                    temp+=" in category %s" % self.category
                print "".join(temp)


        else:
            print "ERROR: uncertainty %s not in process %s" % (systematicName,self.name)
        

    def delete_uncertainties(self,list_of_systnames):
        for systematic in list_of_systnames:
            self.delete_uncertainty(systematicName=systematic)


    def get_uncertainty_value(self, systematicName):
        """
        return correlation of uncertainty 'systematicName' with this process.
        If there is no entry for 'systematicName' in this process, the function 
        returns '-'
        """
        if systematicName in self._uncertainties:
            return self._uncertainties[systematicName]["value"]
        else:
            return "-"

    def get_uncertainty_type(self, systematicName):
        """
        return type of uncertainty 'systematicName' in this process.
        If there is no entry for 'systematicName' in this process, the function 
        returns ''
        """
        if systematicName in self._uncertainties:
            return self._uncertainties[systematicName]["type"]
        else:

            return ""

    def __str__(self):
        """
        current setup: print delivers:
            - process name
            - process yield
            - list of nuisance parameters
        """
        s = []
        s.append("Process infos:")
        s.append("\tname:\t%s" % self.name)
        s.append("\tcategory:\t%s" % self.category)
        s.append("\trootfile:\t%s" % self._file_handler.filepath)
        s.append("\tnominal histname:\t%s" % self._nominalhistname)
        s.append("\tsystematic histname:\t%s" % self._systkey)
        s.append("\tyield:\t{0}".format(self._eventcount))
        if len(self._uncertainties) != 0:
            s.append("\tlist of uncertainties:")

            temp = "\t\t%s" %  "uncertainty".ljust(15)
            temp += "\t%s" % "type".ljust(10)
            temp += "\t%s" % "correlation".ljust(15)
            s.append(temp)
            s.append("\t\t"+"_"*len(temp.expandtabs()))
        for syst in self._uncertainties:
            temp = "\t\t%s" % syst.ljust(15)
            temp += "\t%s" % self._uncertainties[syst]["type"].ljust(10)
            temp += "\t%s" % str(self._uncertainties[syst]["value"]).ljust(15)
            s.append(temp)
        return "\n".join(s)

    """
    overloaded get, in and for operator to get better access to systematics in 
    process object:
    self[systematicName]
    """

    def __getitem__(self, systematicName):
        if systematicName in self._uncertainties:
            return self._uncertainties[systematicName]
        else:
            print "ERROR: Process not in Category!"

    def __iter__(self):
        all_uncertainties=self._uncertainties
        return all_uncertainties.__iter__()

    def __contains__(self, systematicName):
        if systematicName in self._uncertainties:
            return True
        else:
            return False
