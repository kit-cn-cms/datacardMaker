categories = []
with open("testdatacard.txt") as datacard:
                lines = datacard.read().splitlines()
                for n, line in enumerate(lines):
                    if line.startswith("process") and lines[n+1].startswith("process"):
                        categories.append(line)
                        
#for entry in categories:
category = categories[0].split()

class test:
    def __init__( self, pathToDatacard):
        self._categories = []
        self._header = []
        self._process = ""
        self._categoryprocess = ""
        self._category = []
        self._bin = ""
        
    def load_from_file(self, pathToDatacard):
            print "loading datacard from", pathToDatacard
            with open(pathToDatacard) as datacard:
                lines = datacard.read().splitlines()
                self._shapelines_ = []
                self._processes_= ""
                self._binprocesses_= ""
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
                        self._processes_=line
                        self._binprocesses_=lines[n-1]                        
                    else:
                        pass
                    
            self._categories_ = {}
            self._category_ = []
            bins = self._bins.split()
            bins.pop(0)
            for category in bins:
                self._categories_[category] = {}
                self._category_.append(category)
            
            self._process_ = {}    
            processes = self._processes_.split()
            processes.pop(0)
            binprocesses = self._binprocesses_.split()
            binprocesses.pop(0)
            if len(processes)==len(binprocesses):
                for process,binprocess in zip(processes, binprocesses):
                    self._categories_[binprocess][process]={}
                    self._process_[binprocess]=[]
                    self._process_[binprocess].append(process)
            print self._process_
            print self._category_
            for shapelines in self._shapelines_:
                shape = shapelines.split()
                for category in self._category_:
                        self._categories_[category]["shapes"]={}
                        if shape[2] == category or shape[2]=="*":
                            for process in self._process_[category]:
                                if shape[1] == "*":
                                    print shape[3]
                                    self._categories_[category]["shapes"]["default"]={}
                                    self._categories_[category]["shapes"]["default"]["rootfile"]=shape[3]
                                    self._categories_[category]["shapes"]["default"]["hist"]=shape[4]
                                    self._categories_[category]["shapes"]["default"]["systhist"]=shape[5]
                                #elif shape[1] == process
                                #self._categories_[category][shapes][process]={}
                                #self._categories_[category][shapes][process][rootfile]=shape[3]
                                #self._categories_[category][shapes][process][hist]=shape[4]
                                #self._categories_[category][shapes][process][systhist]=shape[5]
        

    
    
                        
s = test("testdatacard.txt")
s.load_from_file("testdatacard.txt")
print s._categories_
#print s._categories_["ljets_j5_tge4_DeepCSV"]["shapes"]["rootfile"]



