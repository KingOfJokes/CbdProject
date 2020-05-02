#!/usr/bin/env python
# coding: utf-8

# In[7]:


import pandas as pd
import re        #正規運算式
import math
import time
import numpy as np 
import csv
from datetime import datetime, timedelta
from datetime import date
import pickle

# In[8]:

#讀入指數價格資料
Indexprice = pd.read_excel('./Index.xlsx')
#Indexprice


# In[9]:


#Indexprice轉換成datetime格式
for index,value in Indexprice.iterrows():
    value["Date"] = value["Date"].to_pydatetime().date()
    #print(type(value["Unnamed: 0"]))

# In[10]:

#引入stopword
stopword = []
with open('./stopwords.txt','r',encoding = 'utf8') as file:
    for line in file.readlines():
        line = line.strip()
        stopword.append(line)

#讀入文章
bbs = pd.read_excel('./bbs.xlsx')
forum = pd.read_excel('./forum.xlsx')
#news = pd.read_excel('./news.xlsx')


# In[11]:


#合併三個文章檔案
collections = pd.concat([forum],axis=0, ignore_index=True,sort=False)


# In[12]:

#蘋果相關文章(沒有apple和iphone)
#設定起始日和結束日
#start_date = datetime(2016,1,1).date()
#end_date = datetime(2018,12,31).date()
filtered_list_apple_noENG = []
start_date = datetime(2016,1,1)
end_date = datetime(2018,12,31)

for index,value in collections.iterrows():
    if (start_date <= value["post_time"].to_pydatetime()) and (end_date >=value["post_time"].to_pydatetime()):
        if ("蘋果" in (str(value["content"])+str(value["title"]))) or("蘋概股" in (str(value["content"])+str(value["title"]))) or ("台積電" in (str(value["content"])+str(value["title"]))) or ("鴻海" in (str(value["content"])+str(value["title"])))or ("和碩" in (str(value["content"])+str(value["title"]))) or("大立光" in (str(value["content"])+str(value["title"]))) or ("可成" in (str(value["content"])+str(value["title"])))or ("鴻準" in (str(value["content"])+str(value["title"]))) or ("日月光" in (str(value["content"])+str(value["title"]))) or ("廣達" in (str(value["content"])+str(value["title"])))or ("台郡" in (str(value["content"])+str(value["title"]))) or("臻鼎" in (str(value["content"])+str(value["title"]))) or ("穩懋" in (str(value["content"])+str(value["title"])))or ("宏捷科" in (str(value["content"])+str(value["title"]))):
            filtered_list_apple_noENG.append([value["post_time"].to_pydatetime(),str(value["title"])+str(value["content"])])

# In[13]:


#len(filtered_list_apple_noENG)


# In[16]:


#將未開盤日的文章日期改為上一次開盤日(while，按太多次不會怎樣)
Index_date = []
for i in range(Indexprice.shape[0]):
    Index_date.append(Indexprice.iloc[i][0].date())
    
for i in range(len(filtered_list_apple_noENG)):
    if filtered_list_apple_noENG[i][0].date() >= datetime(2016,1,4).date():
        while filtered_list_apple_noENG[i][0].date() not in Index_date:
            filtered_list_apple_noENG[i][0] = filtered_list_apple_noENG[i][0] - timedelta(days=1)


# In[18]:


def remove_stopwords(content,n_gram,stopword):
    content = re.sub(r'[^\w]','',content)        #移除非文字字元(符號)
    content = re.sub(r'[A-Za-z0-9]','',content)  #移除英文&數字
    
    returnlist = []
    
    for i in range(len(content) - n_gram + 1):
        word = content[i:i + n_gram]
        if word not in stopword:
            returnlist.append(word)
    return returnlist


# In[19]:


def tfdf(Dict_n_gram, tfdf_n):
    for key in Dict_n_gram.keys():
        for word in Dict_n_gram[key]:
            if word not in tfdf_n.keys():
                tfdf_n[word] = [1,0]
            if word in tfdf_n.keys():
                tfdf_n[word][0] += 1
        for word1 in set(Dict_n_gram[key]):
            tfdf_n[word1][1] += 1
    return tfdf_n


# In[20]:


def get_gram(Dict_n_gram,n,article,stopword):
    for i in article.keys():
        Dict_n_gram[i] = remove_stopwords(article[i],n,stopword)
    return Dict_n_gram


# In[21]:


def get_gram_per_article(Dict_n_gram,n,article,stopword):
    Dict_n_gram[0] = remove_stopwords(article,n,stopword)
    return Dict_n_gram


# In[22]:


def del_outlier(tfdf_n):
    for key in list(tfdf_n.keys()):
        if tfdf_n[key][1] <= 5 or tfdf_n[key][0] <= 10:
            del tfdf_n[key]
    return tfdf_n


# In[23]:


def del_repeat(tfdf_small,tfdf_big):
    for key_small in list(tfdf_small.keys()):
        for key_big in tfdf_big.keys():
            if (key_small in key_big) and (abs((tfdf_big[key_big][0] - tfdf_small[key_small][0])) / tfdf_small[key_small][0] < 0.1):
                del tfdf_small[key_small]
                break
    return tfdf_small


# In[67]:


def generate_keyword(article,all_article):
    Dict_2_gram = {}
    Dict_3_gram = {}
    Dict_4_gram = {}
    Dict_5_gram = {}
    Dict_6_gram = {}
    Dict_2_gram = get_gram(Dict_2_gram,2,article,stopword)
    Dict_3_gram = get_gram(Dict_3_gram,3,article,stopword)
    Dict_4_gram = get_gram(Dict_4_gram,4,article,stopword)
    Dict_5_gram = get_gram(Dict_5_gram,5,article,stopword)
    Dict_6_gram = get_gram(Dict_6_gram,6,article,stopword)
    
    print("gram")
    tfdf_2 = {}
    tfdf_3 = {}
    tfdf_4 = {}
    tfdf_5 = {}
    tfdf_6 = {}
    tfdf_2 = del_outlier(tfdf(Dict_2_gram,tfdf_2))
    tfdf_3 = del_outlier(tfdf(Dict_3_gram,tfdf_3))
    tfdf_4 = del_outlier(tfdf(Dict_4_gram,tfdf_4))
    tfdf_5 = del_outlier(tfdf(Dict_5_gram,tfdf_5))
    tfdf_6 = del_outlier(tfdf(Dict_6_gram,tfdf_6))
    #print(tfdf_2)
    
    #tfdf_2 = del_outlier(tfdf_2)
    #tfdf_3 = del_outlier(tfdf_3)
    #tfdf_4 = del_outlier(tfdf_4)
    #tfdf_5 = del_outlier(tfdf_5)
    #tfdf_6 = del_outlier(tfdf_6)
    #print(tfdf_2)
    print("outlier")
    tfdf_2 = del_repeat(tfdf_2,tfdf_3)
    tfdf_3 = del_repeat(tfdf_3,tfdf_4)
    tfdf_4 = del_repeat(tfdf_4,tfdf_5)
    tfdf_5 = del_repeat(tfdf_5,tfdf_6)
            
    tfdf_2to6 = dict(**tfdf_2 , **tfdf_3, **tfdf_4, **tfdf_5, **tfdf_6)
            
    num_doc = len(Dict_2_gram)
    
    for key in tfdf_2to6.keys():
        tfdf_2to6[key].append((1 + math.log(tfdf_2to6[key][0])) * math.log(num_doc / tfdf_2to6[key][1]))
    
    print("tfidf")
    
    Dict_all = {}
    for i in range(len(all_article)):
        Dict_all[i] = all_article[i][1]
        Dict_all[i] = re.sub(r'[^\w]','',Dict_all[i])        #移除非文字字元(符號)
        Dict_all[i] = re.sub(r'[A-Za-z0-9]','',Dict_all[i])  #移除英文&數字
    
    for key in tfdf_2to6.keys():
        tfdf_2to6[key].append(0)
        for index in Dict_all.keys():
            tfdf_2to6[key][3] += Dict_all[index].count(key)
    print("alldict") #這裡要跑1hr多

    
    num_all = len(Dict_all)   
    
    return tfdf_2to6,num_all,num_doc
    #for key in tfdf_2to6.keys():
         #tfdf_2to6[key].append(((tfdf_2to6[key][0] - ((tfdf_2to6[key][3]/num_all) * num_doc)) ** 2)/((tfdf_2to6[key][3]/num_all) * num_doc))
        
    
    #tfdf_2to6 = sorted(tfdf_2to6.items(),key = lambda x:x[1][4], reverse = True)    #按照tf卡方排
            
    #return tfdf_2to6[0:200]


# In[64]:


def generate_keyword_tf(per_article):
    Dict_2_gram = {}
    Dict_3_gram = {}
    Dict_4_gram = {}
    Dict_5_gram = {}
    Dict_6_gram = {}
    Dict_2_gram = get_gram_per_article(Dict_2_gram,2,per_article,stopword)
    Dict_3_gram = get_gram_per_article(Dict_3_gram,3,per_article,stopword)
    Dict_4_gram = get_gram_per_article(Dict_4_gram,4,per_article,stopword)
    Dict_5_gram = get_gram_per_article(Dict_5_gram,5,per_article,stopword)
    Dict_6_gram = get_gram_per_article(Dict_6_gram,6,per_article,stopword)
    
    tfdf_2 = {}
    tfdf_3 = {}
    tfdf_4 = {}
    tfdf_5 = {}
    tfdf_6 = {}
    tfdf_2 = tfdf(Dict_2_gram,tfdf_2)
    tfdf_3 = tfdf(Dict_3_gram,tfdf_3)
    tfdf_4 = tfdf(Dict_4_gram,tfdf_4)
    tfdf_5 = tfdf(Dict_5_gram,tfdf_5)
    tfdf_6 = tfdf(Dict_6_gram,tfdf_6)

    
    tfdf_2 = del_repeat(tfdf_2,tfdf_3)
    tfdf_3 = del_repeat(tfdf_3,tfdf_4)
    tfdf_4 = del_repeat(tfdf_4,tfdf_5)
    tfdf_5 = del_repeat(tfdf_5,tfdf_6)
            
    tfdf_2to6 = dict(**tfdf_2 , **tfdf_3, **tfdf_4, **tfdf_5, **tfdf_6)

    return tfdf_2to6


# In[70]:

increase_article = {}
decrease_article = {}
increase_keyword = []
decrease_keyword = []
increase_keyword_dict = {}
decrease_keyword_dict = {}

print('標價')
a = 0
b = 0
day = 3
sigma = 1.5
'''
for i in range(day,Indexprice.shape[0] - day):
    if Indexprice.iloc[i,1] - Indexprice.iloc[i + day,1] < (sigma * Indexprice["Index by 收盤價"][i-10:i-1].std() * -1) :
        date1 = Indexprice.iloc[i,0].date()
        #print(type(date1))
        for j in range(len(filtered_list_apple_noENG)):
            #print(type(filtered_list[j][0].date()))
            if filtered_list_apple_noENG[j][0].date() == date1:
                increase_article[a] = filtered_list_apple_noENG[j][1]
                a += 1
    if Indexprice.iloc[i,1] - Indexprice.iloc[i + day,1] > (sigma * Indexprice["Index by 收盤價"][i-10:i-1].std()) :
        date2 = Indexprice.iloc[i,0].date()
        for j in range(len(filtered_list_apple_noENG)):
            if filtered_list_apple_noENG[j][0].date() == date2:
                decrease_article[b] = filtered_list_apple_noENG[j][1]
                b += 1

'''
day = 3
multi = 1
for i in range(10,Indexprice.shape[0] - day):
    if Indexprice.iloc[i,4] - Indexprice.iloc[i + day,4] < (multi * Indexprice["ATR"][i] * -1) :
        date1 = Indexprice.iloc[i,0].date()
        #print(type(date1))
        for j in range(len(filtered_list_apple_noENG)):
            #print(type(filtered_list[j][0].date()))
            if filtered_list_apple_noENG[j][0].date() == date1:
                increase_article[a] = filtered_list_apple_noENG[j][1]
                a += 1
    if Indexprice.iloc[i,4] - Indexprice.iloc[i + day,4] > (multi * Indexprice["ATR"][i]) :
        date2 = Indexprice.iloc[i,0].date()
        for j in range(len(filtered_list_apple_noENG)):
            if filtered_list_apple_noENG[j][0].date() == date2:
                decrease_article[b] = filtered_list_apple_noENG[j][1]
                b += 1

# In[ ]:


num_all = 0
num_doc = 0
increase_keyword_dict,num_all,num_doc = generate_keyword(increase_article,filtered_list_apple_noENG)


# In[ ]:


decrease_keyword_dict,num_all,num_doc = generate_keyword(decrease_article,filtered_list_apple_noENG)


# In[ ]:


for key in increase_keyword_dict.keys():
    if increase_keyword_dict[key][0] - ((increase_keyword_dict[key][3]/num_all) * num_doc) >= 0:
        increase_keyword_dict[key].append(((increase_keyword_dict[key][0] - ((increase_keyword_dict[key][3]/num_all) * num_doc)) ** 2)/((increase_keyword_dict[key][3]/num_all) * num_doc))
    else:
        increase_keyword_dict[key].append((((increase_keyword_dict[key][0] - ((increase_keyword_dict[key][3]/num_all) * num_doc)) ** 2)/((increase_keyword_dict[key][3]/num_all) * num_doc))* -1)

increase_keyword_dict = sorted(increase_keyword_dict.items(),key = lambda x:x[1][4], reverse = True)  #照TF卡方排

for key in decrease_keyword_dict.keys():
    if decrease_keyword_dict[key][0] - ((decrease_keyword_dict[key][3]/num_all) * num_doc) >= 0:
        decrease_keyword_dict[key].append(((decrease_keyword_dict[key][0] - ((decrease_keyword_dict[key][3]/num_all) * num_doc)) ** 2)/((decrease_keyword_dict[key][3]/num_all) * num_doc))
    else:
        decrease_keyword_dict[key].append((((decrease_keyword_dict[key][0] - ((decrease_keyword_dict[key][3]/num_all) * num_doc)) ** 2)/((decrease_keyword_dict[key][3]/num_all) * num_doc))* -1)
decrease_keyword_dict = sorted(decrease_keyword_dict.items(),key = lambda x:x[1][4], reverse = True)  #照TF卡方排


# In[ ]:


#print(increase_keyword_dict[0:300])


# In[ ]:


#print(decrease_keyword_dict[0:300])


# In[ ]:


increase_keyword = increase_keyword_dict[0:500]
decrease_keyword = decrease_keyword_dict[0:500]


# In[ ]:


#刪除重複關鍵字(兩邊都刪??)
repeat_keyword_increase = []
repeat_keyword_decrease = []

for i in range(len(increase_keyword)):
    for j in range(len(decrease_keyword)):
        if increase_keyword[i][0] == decrease_keyword[j][0]:
            repeat_keyword_increase.append(increase_keyword[i])
            repeat_keyword_decrease.append(decrease_keyword[i])
for i in range(len(repeat_keyword_increase)):
    increase_keyword.remove(repeat_keyword_increase[i])
for i in range(len(repeat_keyword_decrease)):    
    decrease_keyword.remove(repeat_keyword_decrease[i])


# In[ ]:

for a in increase_keyword:
    print(a)

print("我是分隔線我是分隔線我是分隔線我是分隔線我是分隔線我是分隔線我是分隔線我是分隔線我是分隔線我是分隔線我是分隔線")
# In[ ]:

for b in decrease_keyword:
    print(b)


# In[ ]:


output_X = []
output_Y = []
for key in increase_article.keys():
    per_article = generate_keyword_tf(increase_article[key])
    x = {}
    for i in range(len(increase_keyword)):
        try:
            x[increase_keyword[i][0]] = per_article[increase_keyword[i][0]][0]
        except:
            x[increase_keyword[i][0]] = 0
    for i in range(len(decrease_keyword)):
        try:
            x[decrease_keyword[i][0]] = per_article[decrease_keyword[i][0]][0]
        except:
            x[decrease_keyword[i][0]] = 0
    output_X.append(x)
    output_Y.append([1,0])


# In[ ]:


for key in decrease_article.keys():
    per_article = generate_keyword_tf(decrease_article[key])
    x = {}
    for i in range(len(increase_keyword)):
        try:
            x[increase_keyword[i][0]] = per_article[increase_keyword[i][0]][0]
        except:
            x[increase_keyword[i][0]] = 0
    for i in range(len(decrease_keyword)):
        try:
            x[decrease_keyword[i][0]] = per_article[decrease_keyword[i][0]][0]
        except:
            x[decrease_keyword[i][0]] = 0
    output_X.append(x)
    output_Y.append([0,1])


# In[ ]:


output_x_numpy = np.array(output_X)
output_y_numpy = np.array(output_Y)


# In[ ]:


np.save('./output_X_news_3d1atr.npy', output_x_numpy)
np.save('./output_Y_news_3d1atr.npy', output_y_numpy)

with open('increaseword_forum_3d1atr.pkl', 'wb') as f: 
    pickle.dump(increase_keyword, f)
with open('decreaseword_forum_3d1atr.pkl', 'wb') as f: 
    pickle.dump(decrease_keyword, f)

