from os import path
from sys import path as spath
thisdir = path.realpath(path.dirname(__file__))
basedir = path.join(thisdir, "../base")
if not basedir in spath:
    spath.append(basedir)
from helperClass import helperClass
from identificationLogic import identificationLogic
from valueConventions import valueConventions
from fileHandler import fileHandler

class processObject(object):
    _helper = helperClass()
    _id_logic = identificationLogic()
    identificationLogic.belongs_to = "process"
    _value_rules = valueConventions()
    _file_handler = fileHandler()
    _helper._debug = 99
    
    def init_variables(self):
        self._name = ""
        # self._rootfile = ""
        self._categoryname = ""
        self._nominalhistname = ""
        self._systkey = ""
        self._eventcount = -1
        self._uncertainties = {}
        self._debug = True
        self._calculate_yield = False


    def __init__(   self, processName = None, pathToRootfile = None, 
                    nominal_hist_key = None, systematic_hist_key = None, 
                    categoryname = None):
        self.init_variables()
        if not processName is None:
            self._name              = processName
        if not pathToRootfile is None:
            self._file_handler.filepath = pathToRootfile
        if not nominal_hist_key is None:
            self._nominalhistname   = nominal_hist_key
        if not categoryname is None:
            self._categoryname      = categoryname
        
        if self._calculate_yield:
            self._eventcount        = self.calculate_yield()
        if not systematic_hist_key is None:
            self._systkey = systematic_hist_key
        if self._debug:
            s = "initialized process with name '%s'" % self._name
            s += " in category '%s'" % self._categoryname
            print s
        
    def calculate_yield(self):
        """
        returns yield (TH1D::Integral() ) for this process
        """
        y = -1

        temp = _file_handler.get_integral(histname = self._nominalhistname)
        if temp:
            y = temp 
        return y

    #getter/setter for yields
    @property
    def eventcount(self):
        return self.get_yield()
    @eventcount.setter
    def eventcount(self, val):
        self.set_yield(val)

    def set_yield(self, val):
        """
        set yield for processes to value val
        """
        self._eventcount = val
        
    def get_yield(self):
        """
        get yield for process
        """
        y = self._eventcount
        if self._debug >= 99:
            print "returning yield of", y
        return y

    #logic for process name
    @property
    def name(self):
        return self.get_name()
    @name.setter
    def name(self, s):
        if self._debug >= 99: 
            print "entered setter for name"
        self.set_name(s)

    
    def set_name(self, name):
        """
        set process name
        """
        if self._debug >= 20: 
            print "setting name to", name
        self._name = name
        
    def get_name(self):
        """
        create copy of process name
        """
        s = self._name
        return s

    @property
    def category(self):
        return self.get_category()

    @category.setter
    def category(self, catname):
        if self._debug >= 99: 
            print "entered setter for category"
        self.set_category(catname)
        # self._categoryname = catname
    
    def get_category(self):
        """
        get name for category to which this process belongs to
        """
        return self._categoryname

    def set_category(self, catname):
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
        else:
            print "file '%s' does not exist!" % rootpath

    @property
    def nominal_hist_name(self):
        return self._nominalhistname

    @nominal_hist_name.setter
    def nominal_hist_name(self, hname):
        
        if self._file_handler.histogram_exists(histname = hname):
            #following if statement should be redundand
            if self._id_logic.is_allowed_key(hname): 
                self._nominalhistname = hname
                self._eventcount = self._file_handler.get_integral(hname)
        else:
            s = "'%s' does not exist " % hname
            s += "in '%s'" % self._file_handler.filepath

    @property
    def systematic_hist_name(self):
        return self._systkey
    @systematic_hist_name.setter
    def systematic_hist_name(self, key):
        if self._id_logic.is_allowed_key(key):
            self._systkey = key
    
    @property
    def uncertainties(self):
        return list(self._uncertainties.keys())

    def __str__(self):
        """
        current setup: print delivers:
            - process name
            - process yield
            - list of nuisance parameters
        """
        s = []
        s.append("Process infos:")
        s.append("\tname:\t%s" % self.get_name())
        s.append("\tcategory:\t%s" % self.get_category())
        s.append("\trootfile:\t%s" % self._file_handler.filepath)
        s.append("\tnominal histname:\t%s" % self._nominalhistname)
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

    def add_uncertainty(self, syst, typ, value):
        """
        add an uncertainty to this process. This function checks
        - whether there already is an entry for 'systname'
        - the given value is suitable for a datacard 
            (see valueConventions.is_good_systval)
        and only adds the systematics if it's new and has a good value
        """
        
        if isinstance(syst, str) and isinstance(typ, str):
            if not syst in self._uncertainties:
                if typ == "shape":
                    print "Looking for varied histograms for systematic", syst
                    keys = self._id_logic.build_systematic_histo_names(
                            systematic_name = syst, base_key = self._systkey)
                    if not all(self._file_handler.histogram_exists(k) for k in keys):
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
                temp += "'%s' in process '%s'! " % (syst, self.get_name())
                temp += "Please use 'set_uncertainty' instead."
                print temp
        else:
            s = "ERROR: Could not add uncertainty - "
            s += "both name and type of systematic are required to be strings!"
            print s
        return False

    # def add_uncertainty_from_systematicObject(self, systematic, value = None):
    #     """
    #     add an uncertainty to this process. This function checks
    #     - whether there already is an entry for 'systname'
    #     - the given value is suitable for a datacard (see 'is_good_systval')
    #     and only adds the systematics if it's new and has a good value
    #     """
    #     if isinstance(systematic, systematicObject):
    #         if not sysname in self._uncertainties:
    #             if systematic.is_good_systval(value):
    #                 cor = systematic.set_correlation(process = self)
    #                 if cor == "-":
    #                     systematic.add_process( process = self, 
    #                                             correlation = value)
    #                 else:
    #                     systematic.set_correlation( process = self, 
    #                                                 value = value)
    #             self._uncertainties[sysname] = systematic

    #         else:
    #             temp = "There is already an entry for uncertainty " 
    #             temp += "%s in process %s" % (systname, self.get_name())
    #             print temp
    #     else:
    #         print "ERROR: systematic needs to be a systematicObject!"

    def set_uncertainty(self, systname, typ, value):
        """
        set the uncertainty 'systname' for this process to type 'typ' 
        and value 'value'. This function checks
        - whether there is an entry for 'systname' in the first place
        - the given value is suitable for a datacard (see 'is_good_systval')
        and only adds the systematics if there is an entry and the value is good
        """
        if systname in self._uncertainties:
            if self._value_rules.is_good_systval(value):
                self._uncertainties[systname]["value"] = str(value)
                self._uncertainties[systname]["type"] = typ
        else:
            s = "There is no entry for uncertainty %s" % systname
            s += " in process %s! Please add it first" % self.get_name()
            print s

    def get_uncertainty_value(self, systname):
        """
        return correlation of uncertainty 'systname' with this process.
        If there is no entry for 'systname' in this process, the function 
        returns '-'
        """
        if systname in self._uncertainties:
            return self._uncertainties[systname]["value"]
        else:
            return "-"

    def get_uncertainty_type(self, systname):
        """
        return type of uncertainty 'systname' in this process.
        If there is no entry for 'systname' in this process, the function 
        returns ''
        """
        if systname in self._uncertainties:
            return self._uncertainties[systname]["type"]
        else:

            return ""

    # def get_uncertainty(self, systname):
    #     """
    #     return systematicObject if there is one 
    #     """
    #     if systname in self._uncertainties:
    #         return self._uncertainties[systname]
    #     else:
    #         return None
