import atrjie
import view
import time

for i in range(5):
	st = time.time()
	ld = 5
	mul = 2
	chit = 2+i
	ver = 'semi3y_'+str(ld)+'d'+str(mul)+'atr5mktc_dfsort'
	print('ver',ver)
	print(chit)
	atrjie.main(ld,mul,ver,chit)
	view.main(ver,chit)
	et = time.time()
	print(et-st)

'''
for i in range(5):
	st = time.time()
	ld = 3
	mul = 1.2
	dft = 2+i
	ver = '3y_'+str(ld)+'d'+str(mul)+'atr3_'
	print(dft)
	atrjie.main(ld,mul,ver,dft)
	view.main(ver,dft)
	et = time.time()
	print(et-st)
'''