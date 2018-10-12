class identificationLogic(object):
    """docstring for identificationLogic"""
    def init_variables(self):
        self._nomkey   = "defaultnominalkey"
        self._systkey  = "systkey"
        self._procIden = "$PROCESS" #Identifier keyword for processes
        self._chIden   = "$CHANNEL" #Identifier keyword for categories/channels
        self._systIden = "$SYSTEMATIC"  #Identifier keyword for systematics

    def __init__(self):
        self.init_variables()   
        