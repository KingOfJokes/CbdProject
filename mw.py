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
Indexprice = pd.read_excel('./Index_3.xlsx')
#Indexprice

#Indexprice轉換成datetime格式
for index,value in Indexprice.iterrows():
    value["Date"] = value["Date"].to_pydatetime().date()
    #print(type(value["Unnamed: 0"]))

#引入stopword
stopword = []
with open('./stopwords.txt','r',encoding = 'utf8') as file:
    for line in file.readlines():
        line = line.strip()
        stopword.append(line)

#讀入文章
bbs = pd.read_excel('./bbs.xlsx')
forum = pd.read_excel('./forum.xlsx')
news = pd.read_excel('./news.xlsx')

#合併三個文章檔案
collections = pd.concat([bbs,forum,news],axis=0, ignore_index=True,sort=False)

# In[12]:

#蘋果相關文章(沒有apple和iphone)
#設定起始日和結束日
#start_date = datetime(2016,1,1).date()
#end_date = datetime(2018,12,31).date()
def definetime(wn):
    sy = 2016
    sm = 1 + wn
    ey = 2016
    em = 4 + wn
    while sm > 12:
        sy = sy + 1
        sm = sm - 12      
    while em > 12:
        ey = ey + 1
        em = em - 12
    start_date = datetime(sy,sm,1)
    end_date = datetime(ey,em,1)
    print(sy,sm,ey,em)
    global filtered_list_apple_noENG,Index_date,start_index,end_index

    filtered_list_apple_noENG = []
    for index,value in collections.iterrows():
        if (start_date <= value["post_time"].to_pydatetime()) and (end_date >=value["post_time"].to_pydatetime()):
            if ("蘋果" in (str(value["content"])+str(value["title"]))) or("蘋概股" in (str(value["content"])+str(value["title"]))):
                filtered_list_apple_noENG.append([value["post_time"].to_pydatetime(),str(value["title"])+str(value["content"])])

    Index_date = []
    for i in range(Indexprice.shape[0]):
        Index_date.append(Indexprice.iloc[i][0].date())
        
    for d in range(len(Index_date)):
        if Index_date[d] > start_date.date():
            start_index = d
            break
    for d in range(len(Index_date)):
        if Index_date[d] > end_date.date():
            break
        temp = d
    end_index = temp
        
    for i in range(len(filtered_list_apple_noENG)):
        filtered_list_apple_noENG[i][0] = filtered_list_apple_noENG[i][0] - timedelta(hours = 13, minutes = 30)
        if filtered_list_apple_noENG[i][0].date() >= datetime(2016,1,4).date():
            while filtered_list_apple_noENG[i][0].date() not in Index_date:
                filtered_list_apple_noENG[i][0] = filtered_list_apple_noENG[i][0] - timedelta(days=1)

day = 3
multi = 1.2
dfthresh = 2
chithresh = 1
#將未開盤日的文章日期改為上一次開盤日(while，按太多次不會怎樣

def remove_stopwords(content):
    content = re.sub(r'[^\w]','',content)        #移除非文字字元(符號)
    content = re.sub(r'[A-Za-z0-9]','',content)  #移除英文&數字
   
    return content

for df in range(33):
    definetime(df)
    print(start_index,end_index)
    ver = 'period'+str(df)+'_'+str(day)+'d'+str(multi)+'atr3'
    increase_article_bef = []
    decrease_article_bef = []

    print('標價')
    iday = 0
    dday = 0
    for i in range(max(10,start_index),end_index - day):
        if Indexprice.iloc[i,4] - Indexprice.iloc[i + day,4] < (multi * Indexprice["ATR"][i] * -1) :
            date1 = Indexprice.iloc[i,0].date()
            #print(type(date1))
            iday = iday + 1
            for j in range(len(filtered_list_apple_noENG)):
                #print(type(filtered_list[j][0].date()))
                if filtered_list_apple_noENG[j][0].date() == date1:
                    increase_article_bef.append(filtered_list_apple_noENG[j][1])
                    
        if Indexprice.iloc[i,4] - Indexprice.iloc[i + day,4] > (multi * Indexprice["ATR"][i]) :
            date2 = Indexprice.iloc[i,0].date()
            dday = dday + 1
            for j in range(len(filtered_list_apple_noENG)):
                if filtered_list_apple_noENG[j][0].date() == date2:
                    decrease_article_bef.append(filtered_list_apple_noENG[j][1])

    print('看漲文章數:',len(increase_article_bef))
    print('看跌文章數:',len(decrease_article_bef))           
    print('共計漲日:',iday)
    print('共計跌日:',dday)
    # In[ ]:


    num_all = 0
    num_doc = 0
    increase_article = []
    decrease_article = []
    for art in increase_article_bef:
        increase_article.append(remove_stopwords(art))

    for art in decrease_article_bef:
        decrease_article.append(remove_stopwords(art))


    def jbcut(content):
        seg_list = jieba.cut(content,cut_all = False)
        result = ("/".join(seg_list))
        result = result.split('/')
        return result

    increase_keyword = []
    decrease_keyword = []
    increase_keyword_dict = {}
    decrease_keyword_dict = {}
    for art in increase_article:
        wordlist = jbcut(art)
        wordset = set(wordlist)
        for ele in wordset:
            if ele not in increase_keyword_dict:
                increase_keyword_dict[ele] = [0,1]
            elif ele in increase_keyword_dict:
                increase_keyword_dict[ele][1] = increase_keyword_dict[ele][1] + 1
        for ele in wordlist:
            increase_keyword_dict[ele][0] = increase_keyword_dict[ele][0] + 1

    for art in decrease_article:
        wordlist = jbcut(art)
        wordset = set(wordlist)
        for ele in wordset:
            if ele not in decrease_keyword_dict:
                decrease_keyword_dict[ele] = [0,1]
            elif ele in decrease_keyword_dict:
                decrease_keyword_dict[ele][1] = decrease_keyword_dict[ele][1] + 1
        for ele in wordlist:
            decrease_keyword_dict[ele][0] = decrease_keyword_dict[ele][0] + 1

    num_doc = len(increase_article) + len(decrease_article)
    def tfidf(indict):
        for index in indict:
            indict[index].append((1 + math.log(indict[index][0])) * math.log(num_doc / indict[index][1]))
        return indict

    increase_keyword_dict = tfidf(increase_keyword_dict)
    decrease_keyword_dict = tfidf(decrease_keyword_dict)

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

    num_all = len(Dict_all)
    print('標記篇數:',num_doc,'總篇數',num_all)
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

    with open('./bt/increaseword_'+ver+'_wb.pkl', 'wb') as f: 
        pickle.dump(increase_keyword_dict, f)
    with open('./bt/decreaseword_'+ver+'_wb.pkl', 'wb') as f: 
        pickle.dump(decrease_keyword_dict, f)

    increase_keyword = []
    decrease_keyword = []
    chithresh = 1
    for inc in increase_keyword_dict:
        if inc[1][1] > dfthresh and inc[1][4] > chithresh:
            increase_keyword.append(inc)
    for dec in decrease_keyword_dict:
        if dec[1][1] > dfthresh and dec[1][4] > chithresh:
            decrease_keyword.append(dec)
    #increase_keyword = increase_keyword_dict[0:length]
    #decrease_keyword = decrease_keyword_dict[0:length]
    print(increase_keyword[:5],increase_keyword[-5:-1])
    print(decrease_keyword[:5],decrease_keyword[-5:-1])
    #刪除重複關鍵字(兩邊都刪??)
    repeat_keyword_increase = []
    repeat_keyword_decrease = []

    for i in range(len(increase_keyword)):
        for j in range(len(decrease_keyword)):
            if increase_keyword[i][0] == decrease_keyword[j][0]:
                repeat_keyword_increase.append(increase_keyword[i])
                repeat_keyword_decrease.append(decrease_keyword[j])
    for i in range(len(repeat_keyword_increase)):
        increase_keyword.remove(repeat_keyword_increase[i])
    for j in range(len(repeat_keyword_decrease)):    
        decrease_keyword.remove(repeat_keyword_decrease[j])

    output_X = []
    output_Y = []
    for art in increase_article:
        x = {}
        for word in increase_keyword:
            temp = list(word)[0]
            x[temp] = art.count(temp)
        for word in decrease_keyword:
            temp = list(word)[0]
            x[temp] = art.count(temp)
        output_X.append(x)
        output_Y.append([1,0])


    # In[ ]:
    for art in decrease_article:
        x = {}
        for word in increase_keyword:
            temp = list(word)[0]
            x[temp] = art.count(temp)
        for word in decrease_keyword:
            temp = list(word)[0]
            x[temp] = art.count(temp)
        output_X.append(x)
        output_Y.append([0,1])

    # In[ ]:

    output_x_numpy = np.array(output_X)
    output_y_numpy = np.array(output_Y)

    # In[ ]:

    np.save('./bt/output_X_'+ver+'_dc'+str(dfthresh)+str(chithresh)+'.npy', output_x_numpy)
    np.save('./bt/output_Y_'+ver+'_dc'+str(dfthresh)+str(chithresh)+'.npy', output_y_numpy)
