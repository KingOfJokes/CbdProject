#!/usr/bin/env python
# coding: utf-8
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

#合併三個文章檔案
collections = pd.concat([bbs],axis=0, ignore_index=True,sort=False)

# In[12]:

#蘋果相關文章(沒有apple和iphone)
#設定起始日和結束日
#start_date = datetime(2016,1,1).date()
#end_date = datetime(2018,12,31).date()
filtered_list_apple_noENG = []
start_date = datetime(2016,1,1)
end_date = datetime(2016,1,31)

for index,value in collections.iterrows():
    if (start_date <= value["post_time"].to_pydatetime()) and (end_date >=value["post_time"].to_pydatetime()):
        if ("蘋果" in (str(value["content"])+str(value["title"]))) or("蘋概股" in (str(value["content"])+str(value["title"]))) or ("台積電" in (str(value["content"])+str(value["title"]))) or ("鴻海" in (str(value["content"])+str(value["title"])))or ("和碩" in (str(value["content"])+str(value["title"]))) or("大立光" in (str(value["content"])+str(value["title"]))) or ("可成" in (str(value["content"])+str(value["title"])))or ("鴻準" in (str(value["content"])+str(value["title"]))) or ("日月光" in (str(value["content"])+str(value["title"]))) or ("廣達" in (str(value["content"])+str(value["title"])))or ("台郡" in (str(value["content"])+str(value["title"]))) or("臻鼎" in (str(value["content"])+str(value["title"]))) or ("穩懋" in (str(value["content"])+str(value["title"])))or ("宏捷科" in (str(value["content"])+str(value["title"]))):
            filtered_list_apple_noENG.append([value["post_time"].to_pydatetime(),str(value["title"])+str(value["content"])])

# In[13]:

#將未開盤日的文章日期改為上一次開盤日(while，按太多次不會怎樣)
Index_date = []
for i in range(Indexprice.shape[0]):
    Index_date.append(Indexprice.iloc[i][0].date())
    
for i in range(len(filtered_list_apple_noENG)):
    if filtered_list_apple_noENG[i][0].date() >= datetime(2016,1,4).date():
        while filtered_list_apple_noENG[i][0].date() not in Index_date:
            filtered_list_apple_noENG[i][0] = filtered_list_apple_noENG[i][0] - timedelta(days=1)


# In[18]:

def remove_stopwords(content):
    content = re.sub(r'[^\w]','',content)        #移除非文字字元(符號)
    content = re.sub(r'[A-Za-z0-9]','',content)  #移除英文&數字
    for s in stopword:
        re.sub(s,'',content)
    return content

increase_article = {}
decrease_article = {}

print('標價')
a = 0
b = 0
day = 3
multi = 0.5
iday = 0
dday = 0
for i in range(10,Indexprice.shape[0] - day):
    if Indexprice.iloc[i,4] - Indexprice.iloc[i + day,4] < (multi * Indexprice["ATR"][i] * -1) :
        date1 = Indexprice.iloc[i,0].date()
        #print(type(date1))
        iday = iday + 1
        for j in range(len(filtered_list_apple_noENG)):
            #print(type(filtered_list[j][0].date()))
            if filtered_list_apple_noENG[j][0].date() == date1:
                increase_article[a] = filtered_list_apple_noENG[j][1]
                a += 1
    if Indexprice.iloc[i,4] - Indexprice.iloc[i + day,4] > (multi * Indexprice["ATR"][i]) :
        date2 = Indexprice.iloc[i,0].date()
        dday = dday + 1
        for j in range(len(filtered_list_apple_noENG)):
            if filtered_list_apple_noENG[j][0].date() == date2:
                decrease_article[b] = filtered_list_apple_noENG[j][1]
                b += 1
print('漲日:',iday)
print('跌日:',dday)
# In[ ]:


num_all = 0
num_doc = 0
for index in increase_article:
    increase_article[index] = remove_stopwords(increase_article[index])
for index in decrease_article:
    decrease_article[index] = remove_stopwords(decrease_article[index])

def jbcut(content):
    seg_list = jieba.cut(content,cut_all = False)
    result = ("/".join(seg_list))
    result = result.split('/')
    return result

increase_keyword = []
decrease_keyword = []
increase_keyword_dict = {}
decrease_keyword_dict = {}
for index in increase_article:
    wordlist = jbcut(increase_article[index])
    wordset = set(wordlist)
    for ele in wordset:
        if ele not in increase_keyword_dict:
            increase_keyword_dict[ele] = [0,1]
        elif ele in increase_keyword_dict:
            increase_keyword_dict[ele][1] = increase_keyword_dict[ele][1] + 1
    for ele in wordlist:
        increase_keyword_dict[ele][0] = increase_keyword_dict[ele][0] + 1

for index in decrease_article:
    wordlist = jbcut(decrease_article[index])
    wordset = set(wordlist)
    for ele in wordset:
        if ele not in decrease_keyword_dict:
            increase_keyword_dict[ele] = [0,1]
        elif ele in decrease_keyword_dict:
            decrease_keyword_dict[ele][1] = decrease_keyword_dict[ele][1] + 1
    for ele in wordlist:
        decrease_keyword_dict[ele][0] = decrease_keyword_dict[ele][0] + 1

num_doc = len(increase_article) + len(decrease_article)
def tfidf(indict):
    for index in indict:
        indict[index].append((1 + math.log(indict[index][0])) * math.log(num_doc / indict[index][1]))
    return indict

tfdf(increase_keyword_dict)
tfdf(decrease_keyword_dict)

Dict_all = []
for con in filtered_list_apple_noENG:
    Dict_all.append(remove_stopwords(con[1]))

for key in increase_keyword_dict.keys():
    increase_keyword_dict[key].append(0)
    for art in Dict_all:
        increase_keyword_dict[key][3] += art.count(key)

for key in decrease_keyword_dict.keys():
    decrease_keyword_dict[key].append(0)
    for art in Dict_all:
        decrease_keyword_dict[key][3] += art.count(key)

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

increase_keyword = increase_keyword_dict[0:50]
decrease_keyword = decrease_keyword_dict[0:50]


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

for i in increase_keyword:
    print(i)

print("我是分隔線我是分隔線我是分隔線我是分隔線我是分隔線我是分隔線我是分隔線我是分隔線我是分隔線我是分隔線我是分隔線")
# In[ ]:

for d in decrease_keyword:
    print(d)


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


np.save('./output_X_bbsj_3d0.5atr.npy', output_x_numpy)
np.save('./output_Y_bbsj_3d0.5atr.npy', output_y_numpy)

with open('increaseword_bbsj_3d0.5atr.pkl', 'wb') as f: 
    pickle.dump(increase_keyword, f)
with open('decreaseword_bbsj_3d0.5atr.pkl', 'wb') as f: 
    pickle.dump(decrease_keyword, f)

