from os import path
from sys import path as spath
thisdir = path.realpath(path.dirname(__file__))
basedir = path.join(thisdir, "base")
if not basedir in spath:
    spath.append(basedir)
from helperClass import helperClass

if not thisdir in spath:
    spath.append(thisdir)

from processObject import processObject

class systematicObject(object):
    helper = helperClass()
    def init_variables(self):
        self._name = ""
        self._type = ""
        self._dic = {}
    def __init__(self, name=None, nature=None, dic = None):
        
        if not name is None:
            try:
                self._name     = str(name)
            except ValueError:
                print "Could not cast name into a string! Name not set"
            
        if not nature is None:
            try:
                self._type   = str(nature)
            except ValueError:
                print "Could not cast type into a string! Type not set"
            
        
        if dic and isinstance(dic, dict):
            self._dic = dic
    
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        try:
            self._name     = str(name)
        except ValueError:
            print "Could not cast 'name' into a string! 'name' not set"

    @property
    def type(self):
        return self._type
    
    @type.setter
    def type(self, typ):
        try:
            self._type   = str(typ)
        except ValueError:
            print "Could not cast 'type' into a string! 'type' not set"
    
    def add_process(self, category, procname, value):
        if not category in self._dic:
            self._dic[category] = {}
        if not procname in self._dic[category]:
            if self.helper.is_good_systval(value):
                self._dic[category][procname] = value
        else:
            temp = "ERROR: process '%s'" % procname
            temp += " in category '%s'" % category
            temp += " is already known to systematic '%s'!" % self._name
            temp += " Use 'processObject.set_correlation()' instead"
            print temp
        
    def add_process(self, dic, category):
        if not category in self._dic:
            if dic and isinstance(dic, dict):
                if all(self.helper.is_good_systval(dic[key]) for key in dic):
                    self._dic[category] += dic
                else:
                    print "ERROR: input dictionary contains bad values!"
            else:
                print "Could not add process: input must be dictionary!"
        else:
            temp = "ERROR: category '%s'" % category
            temp += " is unknowns to systematic '%s'" % self._name
            print temp
    
    def add_process(self, process, correlation = "-"):
        if isinstance(process, processObject):
            cor = self.get_correlation(process.category, process.name)
            if cor == "-":
                if correlation == "-":
                    correlation = process.get_uncertainty_value(systname = self._name)
                self.add_process(   category = process.category, 
                                    procname = process.name, 
                                    value = correlation)
            else:
                temp = "process '%s' is already known to " % process.name
                temp += "systematic '%s'! " % self._name
                temp += "Use the 'set_correlation' function"
                print temp
        else:
            print "ERROR: Could not add process - input must be processObject"

    def get_correlation(self, category, procname):
        if category in self._dic:
            if procname in self._dic[category]:
                return str(self._dic[category][procname])
            else:
                return "-"

    def get_correlation(self, process):
        category = process.category
        procname = process.name
        return self.get_correlation(category = category, procname = procname)

    def set_correlation(self, category, procname, value):
        if category in self._dic:
            if procname in self._dic[category]:
                if self.helper.is_good_systval(value):
                    self._dic[category][procname] = value
            else:
                print "Could not add process: input must be dictionary!"
        else:
            temp = "ERROR: category '%s'" % category
            temp += " is unknown to systematic '%s'" % self._name
            print temp

    def set_correlation(self, process, value = "-"):
        if isinstance(process, processObject):
            procname = process.name
            category = process.category
            if value == "-":
                value = process.get_uncertainty_value(systname = self._name)
            if procname in self._dic[category]:
                if self.helper.is_good_systval(value):
                    self._dic[category][procname] = value
            else:
                s = "ERROR: Process '%s' is not known yet to" % procname
                s += " systematic '%s'!" % self._name
                s += " Please use 'systematicObject.add_process' instead"
                print s
        else:
            s = "ERROR: Could not set process! Input must be processObject"
    
