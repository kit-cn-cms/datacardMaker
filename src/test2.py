class cO:
    
        
    def __init__(self,category):
        self.__name= category
        self.dic = {}
        
    def add_process(self,process):
        if isinstance(process, pO):
            name=process.getName()
            print name
            self.dic[name]= process
            
    def __getitem__(self, process):
        for name,proc in self.dic.items():
            if name == process:
                return proc
            
    def printdict(self):
        for name,process in self.dic.items():
            print name, "corresponds to", process.getName()
            
    def __str__(self):
        s = []
        s.append("Category Name:\t%s" % self.__category)
        #for name,process in self.__dic.items():
            #s.append("Process Name:\t%s" % name)
        return "\n".join(s)
 
class pO:
    def __init__(self,process):
        self.__process = process 
        self.__number = None
    
        
    def getName(self):
        return self.__process
    def setNumber(self,num):
        self.__number=num 
    def getNumber(self):
        return self.__number
    
    
c1=cO("ch1")
p1=pO("process1")
p1.setNumber(1)
p2=pO("process2")
p2.setNumber(2)
print p1.getNumber()
print p1.getName()
print p2.getName()
c1.add_process(p1)
c1.add_process(p2)
c1.printdict()
print c1["process1"].getNumber()
