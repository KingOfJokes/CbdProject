import atrjie
import view
import time

for i in range(0,1):
	st = time.time()
	ld = 5
	mul = (2+0.5*i)
	ver = '6m_'+str(ld)+'d'+str(mul)+'atr5'
	print('ver',ver)
	atrjie.main(ld,mul,ver)
	view.main(ver)
	et = time.time()
	print(et-st)

'''
for i in range(0,7):
	ld = 3
	mul = (0.3+0.15*i)
	leng = 850
	ver = 'all3y_'+str(ld)+'d'+str(mul)+'atr5'
	print('ver',ver)
	atrjie.main(ld,mul,leng,ver)
	view.main(leng,ver)
'''