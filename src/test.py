from datacardMaker import datacardMaker

d=datacardMaker()
d.load_from_file("combinedtestdatacard.txt")
for name,category in d._categories.items():
	print name
	print category
