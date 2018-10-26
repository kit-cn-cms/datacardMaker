from datacardMaker import datacardMaker

d=datacardMaker()
d.load_from_file("combinedtestdatacard.txt")
for name,category in d._categories.items():
	print name
	print category
for name,category in d._categories.items():
	d.update_systematics(category)
for name,syst in d._systematics.items():
	print syst
d.collect_processes()