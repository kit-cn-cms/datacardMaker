# from ROOT import TFile, TH1
from os import path
from sys import path as spath
thisdir = path.realpath(path.dirname(__file__))
basedir = path.join(thisdir, "../base")
if not basedir in spath:
    spath.append(basedir)
from helperClass import helperClass




class processObject(object):
    helper = helperClass()
    helper._debug = 99
    
    def init_variables(self):
        self._name = ""
        self._rootfile = ""
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
            self._rootfile          = pathToRootfile
        if not nominal_hist_key is None:
            self._nominalhistname   = nominal_hist_key
        if not categoryname is None:
            self._categoryname      = categoryname
        
        if self._calculate_yield:
            self._eventcount        = self.calculate_yield()
        if not systematic_hist_key is None:
            self._systkey = systematic_hist_key
        if self._debug:
            print "initialized process with name '%s' in category '%s'" % (self._name, self._categoryname)
        
    def calculate_yield(self):
        """
        returns yield (TH1D::Integral() ) for this process
        """
        #open rootfile if it exsists
        y = -1
        if path.exists(self._rootfile):
            infile = TFile(self._rootfile)
            #check if root file is intact
            if self.helper.intact_root_file(infile):
                #if yes, try to load histogram
                
                hist = infile.Get(self._nominalhistname)
                if isinstance(hist, TH1):
                    #if successful, save yield
                    y = hist.Integral()
                else:
                    print "ERROR:\tunable to load histogram! I will let combine calculate it on the fly, but it could crash"
                infile.Close()
            else:
                print "ERROR:\tunable to open root file for process {0}, cannot set yield".format(self._name)
        else:
            print "ERROR:\troot file does not exist! Cannot set yield for process {0}".format(self._name)
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
        return y

    #logic for process name
    @property
    def name(self):
        return self.get_name()
    @name.setter
    def name(self, s):
        if self._debug: print "entered setter for name"
        self.set_name(s)

    
    def set_name(self, name):
        """
        set process name
        """
        if self._debug: print "setting name to", name
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
        if self._debug: print "entered setter for category"
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
        if self._debug: print "setting category to", catname
        self._categoryname = catname

    @property
    def rootfile(self):
        return self._rootfile
    
    @rootfile.setter
    def rootfile(self, rootpath):
        if path.exists(rootpath):
            self._rootfile = rootpath
        else:
            print "file '%s' does not exist!" % rootpath

    @property
    def nominalhistname(self):
        return self._nominalhistname

    @nominalhistname.setter
    def nominalhistname(self, hname):
        
        if self.helper.histogram_exists(file = self._rootfile,
                                        histname = hname):
            self._nominalhistname = hname
        else:
            print "'%s' does not exist in '%s'" % (hname, self._rootfile)

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
        s.append("\trootfile:\t%s" % self._rootfile)
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
        - the given value is suitable for a datacard (see 'is_good_systval')
        and only adds the systematics if it's new and has a good value
        """
        
        if isinstance(syst, str) and isinstance(typ, str):
            if not syst in self._uncertainties:
                if typ == "shape":
                    print "Looking for varied histograms for systematic"
                    # if self.helper.histogram_exists(self._rootfile, 
                    #                     self._systkey.replace(self._sy))
                if self.helper.is_good_systval(value):
                    self._uncertainties[syst] = {}
                    self._uncertainties[syst]["type"] = typ
                    self._uncertainties[syst]["value"] = value
                    return True
            else:
                temp = "There is already an entry for uncertainty " 
                temp += "%s in process %s" % (systname, self.get_name())
                print temp
        else:
            print "ERROR: Could not add uncertainty - input arguments invalid!"
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
        if systname in self._uncertainties and self.is_good_systval(value):
            self._uncertainties[systname]["value"] = str(value)
            self._uncertainties[systname]["type"] = typ
        else:
            print "There is no entry for uncertainty %s in process %s" % (systname, self.get_name())

    def get_uncertainty_value(self, systname):
        """
        return correlation of uncertainty 'systname' with this process.
        If there is no entry for 'systname' in this process, the function returns '-'
        """
        if systname in self._uncertainties:
            return self._uncertainties[systname]["value"]
        else:
            return "-"

    def get_uncertainty_type(self, systname):
        """
        return type of uncertainty 'systname' in this process.
        If there is no entry for 'systname' in this process, the function returns ''
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