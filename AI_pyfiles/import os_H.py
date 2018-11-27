import  v3_allstages_H_plus_opt as code
while(1):
	code.setL()
	try:
		code.doubleReserve()
		code.optimal()
	except OverflowError as e:
		print("error",e)
	code.writetocsv()
	print(":::::::::::::::::::::::::::::::::::::::::::::::::::::",code.counts())
	if(code.counts()>100):
		break