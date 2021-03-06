# datacardMaker src
classes for object-oriented datacard maker

- datacardMaker.py: Wrapper to automatically create data cards from analysis objects
	- write Datacard with write_datacard()
- analysisObject.py: Container for categoryObjects
	- an analysis object is able to have multiple categories with multiple processes with corresponding systematics
	- uses category, process and systematic objects
	- add category with add_category()
- categoryObject.py: object for categories
	- a category has multiple processes with a number of systematic uncertainties
	- categoryObject knows generic keys for files and histogram names for data and uncertainties
	- categories have a list of signal and background processes
	- uses processObject
	- add process with add_signal_process() or add_background_process()
	- set generic keys with 
		- default_file
		- generic_key_nominal_hist
		- generic_key_systematic_hist
- processObject.py: object for process (e.g. ttH_hbb)
	- process knows its category: category_name
	- process knows yield: get_yield
	- process knows corresponding keys:
		- file
		- nominal_hist_name
		- systematic_hist_name
	- process knows what systematics it has
	- process knows the correlation to a given systematic
- systematicObject.py: object for nuisance parameters (e.g. bgnorm_ttbarPlusBBbar)
	- systematic knows which processes it affects
	- systematic knows the correlation to a given process
