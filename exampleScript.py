"""
python exampleScript CSV
python exampleScript Datacard
"""

import sys
from os import path

"""
First define path to the directory where the datacardMaker is
and add the src and base directory to import all needed classes
"""
directory = path.realpath(path.dirname(__file__))

srcdir = path.join(directory, "src")
if not srcdir in sys.path:
    sys.path.append(srcdir)

basedir = path.join(directory, "base")
if not basedir in sys.path:
    sys.path.append(basedir)

from analysisObject 	import analysisObject
from categoryObject 	import categoryObject
from processObject 		import processObject
from systematicObject 	import systematicObject
from datacardMaker 		import datacardMaker

from fileHandler 			import fileHandler
from identificationLogic 	import identificationLogic
from valueConventions 		import valueConventions


"""
Create analysisObject first to store categories and processes
Structure of analysisObject:

-Analysis
	-Category 1
		-Signalprocess 1
		-Signalprocess 2
		-Backgroundprocess 1
		-...
	-Category 2
		-Signalprocess 1
		-Signalprocess 2
		-Backgroundprocess 1
		-...
	-...

Dictionaries are used.
To access a category use analysis[Category_Name]
To access a process use  analysis[Category_Name][Process_Name]

"""

analysis=analysisObject()

if sys.argv[1]=="CSV":

	"""
	------------------------------------------------
	To add processes from CSV File, first create the 
	categories.
	------------------------------------------------
	

	Possibility 1

	Only change generic key if it differs $PROCESS_finaldiscr_$CHANNEL
	or $PROCESS_finaldiscr_$CHANNEL_$SYSTEMATIC,
	else only set categoryName and default_file
	"""
	print '''
	Creating Category for analysisObject
	'''
	
	analysis.create_category(categoryName="ljets_j5_tge4_DeepCSV",
								default_file="output_limitInput.root",
								generic_key_nominal_hist="$PROCESS_finaldiscr_$CHANNEL",
                       			generic_key_systematic_hist="$PROCESS_finaldiscr_$CHANNEL_$SYSTEMATIC")

	"""
	Possibility 2

	Use the setters or getters to change the category properties
	- category.name
	- category.default_file 
	- category.generic_key_nominal_hist 
	- category.generic_key_systematic_hist

	"""
	print '''
	Creating Category for analysisObject
	'''

	analysis.create_category(categoryName="ljets_jge6_t3_DeepCSV") 
	#Set the default file name for the category
	analysis["ljets_jge6_t3_DeepCSV"].default_file = "output_limitInput.root"
	#Change the generic key for the nominal histogram if it differs $PROCESS_finaldiscr_$CHANNEL
	analysis["ljets_jge6_t3_DeepCSV"].generic_key_nominal_hist = "$PROCESS_finaldiscr_$CHANNEL"
	#Change the generic key for systematics histogram if it differs $PROCESS_finaldiscr_$CHANNEL_$SYSTEMATIC
	analysis["ljets_jge6_t3_DeepCSV"].generic_key_systematic_hist = "$PROCESS_finaldiscr_$CHANNEL_$SYSTEMATIC"


	"""
	Possibility 3

	create a categoryObject and then add it to the analysisObject
	"""

	print '''
	Create categoryObject
	'''
	#create categoryObject
	category=categoryObject(categoryName="ljets_jge6_tge4_DeepCSV",
							defaultRootFile="output_limitInput.root")

	print '''
	Adding to analysisObject
	'''
	#add Category Object to analysisObject
	analysis.add_category(category)

	
	"""
	------------------------------------------------
	Add processes to the categories using a CSV File
	Wont add processes that cant be found.
	------------------------------------------------
	"""
	print '''
	Adding processes from csv file
	'''
	analysis.load_from_csv_file(filename="test.csv")


	"""
	------------------------------------------------
	Add observation to categories
	category.observation = name_of_observation 
	default is "data_obs"
	------------------------------------------------
	"""
	print '''
	Adding Observation:
	'''
	for category in analysis:
		analysis[category].observation = "data_obs"

	"""
	Analysis Object printout
	"""
	print '''
	AnalysisObject:
	'''
	print analysis
	

if sys.argv[1]=="Datacard":

	"""
	------------------------------------------------
	Add processes from Datacard File
	------------------------------------------------

	only pathToDatacard necessary, 
	ReadSystematics can be set to False to skip adding Systematics
	observation_Flag needs to be set if name differs from "data_obs"
	"""
	analysis.load_from_datacard(pathToDatacard="testdatacard.txt",
			ReadSystematics=True,observation_Flag="data_obs")

	"""
	Analysis Object printout
	"""
	print '''
	AnalysisObject:
	'''
	print analysis