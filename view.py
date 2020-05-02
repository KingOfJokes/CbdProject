import pickle
import numpy as np
from ckiptagger import WS, POS, NER
import os
import time
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
pos = POS("./data")

increase = dict(np.load('increaseword_forum_3d1.5sigma.pkl',allow_pickle = True))
decrease = dict(np.load('decreaseword_forum_3d1.5sigma.pkl',allow_pickle = True))
wordbank = dict(increase,**decrease)
xt = np.load('output_Xa_forum_3d1.5sigma.npy',allow_pickle = True)
yt = np.load('output_Y_forum_3d1.5sigma.npy',allow_pickle = True)
print(len(xt[1]))
print(yt.shape)


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
		print(word,pos_char[word],wordbank[word])
		for xt_ind in xt:
			del xt_ind[word]
print(len(xt[1]))
np.save('output_Xa_forum_3d1.5sigma',xt)