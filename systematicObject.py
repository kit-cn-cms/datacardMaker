class systematicObject(object):
    def __init__(self, name, nature, dic = None):
        
        self._name     = name
        self._type   = nature
        self._dic      = {}
        
        if dic and isinstance(dic, dict):
            self._dic = dic
    
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = str(value)

    @property
    def type(self):
        return self._type
    
    @type.setter
    def type(self, typ):
        self._type = typ
    
    def add_process(self, category, procname, correlation):
        if category in self._dic:
            self._dic[category][procname] = correlation
        else:
            print "ERROR: category is not known to uncertainty '%s'" % self._name
        
    def add_process(self, dic, category):
        if category in self._dic:
            if dic and isinstance(dic, dict):
                self._dic[category] += dic
            else:
                print "Could not add process: input must be dictionary!"
        else:
            print "ERROR: category is not known to uncertainty '%s'" % self._name
    
    def get_correlation(self, category, procName):
        if category in self._dic:
            if procName in self._dic[category]:
                return str(self._dic[category][procName])
            else:
                return "-"
