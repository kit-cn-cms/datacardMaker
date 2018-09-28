import sys
from os import path

directory = path.abspath(path.realpath(path.dirname(__file__)))
if not directory in sys.path:
    sys.path.append(directory)

from categoryObject import categoryObject

class datacardMaker:
            
    def __init__(   self, pathToDatacard = None, 
                    processIdentifier = "$PROCESS",
                    channelIdentifier = "$CHANNEL",
                    systIdentifier = "$SYSTEMATIC"):
        self._header        = []
        self._bins          = ""
        self._observation   = ""
        self._categories     = []
        if pathToDatacard:
            self.load_from_file(pathToDatacard)


    def load_from_file(self, pathToDatacard):
        if path.exists(pathToDatacard):
            print "loading datacard from", pathToDatacard
            with open(pathToDatacard) as datacard:
                lines = datacard.read().splitlines()
                self._shapelines_ = []
                for n, line in enumerate(lines):
                    if line.startswith("-"):
                            continue
                    elif    line.startswith("Combination") or
                            line.startswith("imax") or
                            line.startswith("kmax") or
                            line.startswith("jmax"):
                        self._header.append(line)
                    elif    line.startswith("bin") and
                            n != len(lines) and
                            lines[n+1].startswith("observation"):
                        self._bins = line
                        self._observation = lines[n+1]
                    elif line.startswith("shapes"):
                        self._shapelines_.append(line)
                    elif    line.startswith("process") and
                            n != 0 and
                            lines[n-1].startswith("bin")
                    else:
                        
                        
                        
        else:
            print "could not load %s: no such file" % pathToDatacard
