# datacardMaker
repo for object-oriented datacard maker


Current ideas for structure

- datacardMaker.py: Wrapper to automatically create data cards from category/process/systematic objects
	- should be able to know how many categories are to be written (-> j parameter)
	- should be able to know how many systematics are involved (-> k parameter)
- processObject.py: object for process (e.g. ttH_hbb)
	- process should know what systematics it has
	- process should know the correlation to a given systematic
- systematicObject.py: object for nuisance parameters (e.g. bgnorm_ttbarPlusBBbar)
	- systematic should know which processes it affects
	- systematic should know the correlation to a given process
- categoryObject.py: object for categories
	- a category has multiple processes with a number of systematic uncertainties