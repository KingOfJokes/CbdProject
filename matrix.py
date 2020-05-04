#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
def confusion_matrix(y_pred,y_test): 
    TP = 0
    FP = 0
    FN = 0
    TN = 0
    for i in range(len(y_pred)):
        if y_pred[i] == [1,0] and y_pred[i] == y_test[i]:
            TP += 1
        if y_pred[i] == [1,0] and y_pred[i] != y_test[i]:
            FP += 1
        if y_pred[i] == [0,1] and y_pred[i] != y_test[i]:
            FN += 1
        if y_pred[i] == [0,1] and y_pred[i] == y_test[i]:
            TN += 1
    num = TP + FP + FN + TN
    accuracy = (TP + TN) / num
    print(accuracy)
    frame = pd.DataFrame({'n = {}'.format(num):['predicted rise','predicted fall'],'actual rise':[TP,FN],'actual fall':[FP,TN]},index = [' ']*2)
    return frame


# In[ ]:





# In[ ]:





# In[ ]:




