from os import path
from sys import path as spath
thisdir = path.realpath(path.dirname(__file__))
basedir = path.join(thisdir, "base")
if not basedir in spath:
    spath.append(basedir)

if not thisdir in spath:
    spath.append(thisdir)

from processObject import processObject
from valueConventions import valueConventions

class systematicObject(object):
    _value_rules = valueConventions()
    def init_variables(self):
        self._name = ""
        self._type = ""
        self._dic = {}
    def __init__(self, name=None, nature=None, dic = None):
        self.init_variables()
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
    
    def add_process_raw(self, category_name, process_name, value):
        if not category_name in self._dic:
            self._dic[category_name] = {}
        if not process_name in self._dic[category_name]:
            if self._value_rules.is_good_systval(value):
                self._dic[category_name][process_name] = {}
                self._dic[category_name][process_name] = value
            
        else:
            temp = "ERROR: process '%s'" % process_name
            temp += " in category '%s'" % category
            temp += " is already known to systematic '%s'!" % self._name
            temp += " Use 'processObject.set_correlation()' instead"
            print temp
        
    def add_process_by_dictionary(self, dic, category):
        if not category_name in self._dic:
            if dic and isinstance(dic, dict):
                if all(self.helper.is_good_systval(dic[key]) for key in dic):
                    self._dic[category_name] += dic
                else:
                    print "ERROR: input dictionary contains bad values!"
            else:
                print "Could not add process: input must be dictionary!"
        else:
            temp = "ERROR: category '%s'" % category_name
            temp += " is unknowns to systematic '%s'" % self._name
            print temp
    
    def add_process(self, process, correlation = "-"):
        if isinstance(process, processObject):
            cor = self.get_correlation(process = process) 
            if cor == "-":
                if correlation == "-":
                    correlation = process.get_uncertainty_value(systematicName = self._name)
                self.add_process_raw(   category_name = process.category, 
                                    process_name = process.name, 
                                    value = correlation)
            else:
                temp = "process '%s' is already known to " % process.name
                temp += "systematic '%s'! " % self._name
                temp += "Use the 'set_correlation' function"
                print temp
        else:
            print "ERROR: Could not add process - input must be processObject"

    def get_correlation_raw(self, category_name, process_name):
        if category_name in self._dic:
            if process_name in self._dic[category_name]:
                return str(self._dic[category_name][process_name])
            else:
                return "-"
        else:
            return "-"
    def get_correlation(self, process):
        category = process.category
        process_name = process.name
        return self.get_correlation_raw(    category_name = category, 
                                        process_name = process_name)

    def set_correlation_raw(self, category_name, process_name, value):
        if category_name in self._dic:
            if process_name in self._dic[category_name]:
                if self._value_rules.is_good_systval(value):
                    self._dic[category_name][process_name] = value
            else:
                print "Could not add process: input must be dictionary!"
        else:
            temp = "ERROR: category '%s'" % category_name
            temp += " is unknown to systematic '%s'" % self._name
            print temp

    def set_correlation(self, process, value = "-"):
        if isinstance(process, processObject):
            process_name = process.name
            category = process.category
            if value == "-":
                value = process.get_uncertainty_value(systematicName = self._name)
            if process_name in self._dic[category]:
                if self._value_rules.is_good_systval(value):
                    self._dic[category][process_name] = value
            else:
                s = "ERROR: Process '%s' is not known yet to" % process_name
                s += " systematic '%s'!" % self._name
                s += " Please use 'systematicObject.add_process' instead"
                print s
        else:
            s = "ERROR: Could not set process! Input must be processObject"
    
    def __str__(self):
        s = []
        s.append("Systematic Name:\t%s" % self._name)
        s.append("Systematic Type:\t%s" % self._type)
        if len(self._dic) != 0:
            s.append("list of processes:")
            temp = "\t\t%s" %  "category".ljust(15)
            temp += "\t\t%s" %  "process".ljust(15)
            temp += "\t%s" % "value".ljust(15)
            s.append(temp)
            s.append("\t\t"+"_"*len(temp.expandtabs()))
        for category in self._dic:
            for process in self._dic[category]:
                temp = "\t\t%s" % category.ljust(15)
                temp += "\t\t%s" % process.ljust(15)
                temp += "\t%s" % str(self._dic[category][process]).ljust(10)
                s.append(temp)

        return "\n".join(s)    
