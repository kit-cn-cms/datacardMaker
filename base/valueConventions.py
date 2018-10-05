class valueConventions(object):
	"""docstring for valueConventions"""
	def __init__(self, arg):
		super(valueConventions, self).__init__()
		self.arg = arg
	
	def is_good_systval(self, value):
		"""
		check if 'value' is a format allowed for systematic uncertainties
		"""
		is_good = False
		if value is None: return is_good
		if value == "-": 
			is_good = True
		elif isinstance(value,float) or isinstance(value,int): 
			is_good = True
		elif isinstance(value,str):
			totest = value.split("/")
			if len(totest) in [1,2]:
				is_good = all(self.isfloat(v) for v in totest)
		if not is_good: 
			print "Given value not suitable for an uncertainty in a datacard!"
		return is_good