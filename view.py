import pandas as pd
import re        #正規運算式
import math
import time
import numpy as np 
import csv
from datetime import datetime, timedelta
from datetime import date
import pickle
import jieba
import os
from ckiptagger import WS, POS, NER
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
pos = POS("./data")

def main(length,ver):
	#length = 850
	#ver = 'all3y_5d1atr5'
	xt = np.load('output_X_'+ver+'_'+str(length)+'.npy',allow_pickle = True)
	yt = np.load('output_Y_'+ver+'_'+str(length)+'.npy',allow_pickle = True)
	yt = np.array(yt)
	print(type(yt))
	print('ytshape ',yt.shape)
	print(len(xt[1]))

	'''
	outword = []
	for xt_key in xt[0]:
		if xt_key not in wordbank:
			outword.append(xt_key)
	for ow in outword:
		for xt_ind in xt:
			del xt_ind[ow]
	print(len(xt[1]))
	'''
	inc_wordbag = [[]]
	incs  = 0
	for inc in xt[1]:
		inc_wordbag[0].append(inc)
		incs = incs+1

	pos_results = pos(inc_wordbag)
	pos_char = {}
	ng_char = ['A','D','Cbb','Di','DM','Neqa','DE','P','I','Dfa']
	for j in range(len(inc_wordbag[0])):
		word = inc_wordbag[0][j]
		pos_char[word] = pos_results[0][j]
		if pos_char[word] in ng_char:
			#print(word,pos_char[word],wordbank[word])
			for xt_ind in xt:
				del xt_ind[word]
				
	print(len(xt[1]))

	np.save('output_Xa_'+ver+'_'+str(length)+'.npy',xt)