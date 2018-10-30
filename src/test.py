from datacardMaker import datacardMaker
import operator

d=datacardMaker()
d.load_from_file("combinedtestdatacard.txt")
for name,category in d._categories.items():
	print name
	print category
for name,category in d._categories.items():
	d.update_systematics(category)
for name,syst in d._systematics.items():
	print syst
#print d.create_process_block()
#print d.create_systematics_block()
d.replace_files = True
d.outputpath="test.txt"
d.write_datacard()
print d.create_observation_block()
print d.create_keyword_block()