# datacardMaker
repo for object-oriented datacard maker

Writes Datacards 

Current structure:
- src/datacardMaker.py: Wrapper to automatically create data cards from analysis objects
- src/analysisObject.py: Container for categoryObjects
- src/categoryObject.py: Object for categories that contains processes
- src/processObject.py: Object for process (e.g. ttH_hbb), contains uncertainties corresponding to the process
- src/systematicObject.py: object for nuisance parameters (e.g. bgnorm_ttbarPlusBBbar)
- base/fileHandler.py: fileHandler class manages all access to files required for the analysis
- base/identificationLogic: identificationLogic class is meant to handle all logic concerning
    the key handling for the different categories required in datacards
- base/valueConventions.py: checks if value is allowed for systematic