class cO:
    def __init__(self,category):
        self.__category = category
        self.__dic ={}
    
    def add_process(self,process):
        if isinstance(process, pO):
            self.__dic[process.getName]= process
            
    def __getitem__(self, process):
        for proc in self.__dic:
            if proc.getName==process:
                return proc
            
    def __str__(self):
        s = []
        s.append("Category Name:\t%s" % self.__category)
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
print p1.getNumber()
c1.add_process(p1)
print c1
c1["process1"].getNumber