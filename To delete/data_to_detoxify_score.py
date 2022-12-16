import pandas as pd
from detoxify import Detoxify
import time
import os

#has a very very small runing-time, don't think it should be optimized
def df_list(X):
    new_list_=[] #creates a list with approximately one comment per item
    n=0
    for i in X.split("'id': "):
        if n!=0: #condition to avoid taking the very first i which doesn't have anything important
            [_, keep]=i.split(" 'text': ")
            [text, _]=keep.split(", 'likes'")
            new_list_.append(text)
        n+=1
    return new_list_

print("\n data to detoxify is executing ... ")


data_folder = './youtube_radicalization/cm/' # all my data is in one folder 
Detoxify_unbiased = Detoxify('unbiased')

n = 0
for file_name in os.listdir(data_folder):
    if n>=2: break
    path_file = os.path.join(data_folder, file_name)
    if os.path.isfile(path_file):
        df_comments = pd.read_csv(path_file, compression='gzip').dropna(axis=0)
        df_head=df_comments.head(20) #for now we only select the first 20 videos. maybe sampling? 
        toxic_df=pd.DataFrame()
        dict_list={"toxicity":[],'severe_toxicity':[], 'obscene':[], 'identity_attack':[], 'insult':[], 'threat':[], 'sexual_explicit':[]}
        video_id_list=[]

        t=time.time()
        for i in df_head.index:
            X=df_head.loc[i,"comments"]
            print("len : ", len(X))
            video_id=df_head.loc[i, "video_id"]
            print("video id: ", video_id)
            new_list_=df_list(X) #maybe sampling?
            data_detoxify=Detoxify_unbiased.predict(new_list_)
            dict_list["toxicity"]+=(data_detoxify["toxicity"])
            dict_list['severe_toxicity']+=(data_detoxify['severe_toxicity'])
            dict_list['obscene']+=(data_detoxify['obscene'])
            dict_list['identity_attack']+=(data_detoxify['identity_attack'])
            dict_list['insult']+=(data_detoxify['insult'])
            dict_list['threat']+=(data_detoxify['threat'])
            dict_list['sexual_explicit']+=(data_detoxify['sexual_explicit'])
            video_id_list+=[video_id]*len(data_detoxify['toxicity'])
            
        toxic_df=pd.DataFrame(data=dict_list)
        toxic_df['video_id']=video_id_list
        toxic_df['channel_id'] = file_name[:-7]
            
        print('for channel', file_name[:-7], ', runtime=', time.time()-t)
        toxic_df.to_csv('detoxified/' + file_name[:-7] + '.csv')

    n+=1
    


