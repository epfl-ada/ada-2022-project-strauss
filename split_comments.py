import pandas as pd
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

print("split comments is executing ... ")

data_folder = './youtube_radicalization/cm/' # all my data is in one folder 
df_final = pd.DataFrame()
n = 0
for file_name in os.listdir(data_folder):
    if n>=2: break
    path_file = os.path.join(data_folder, file_name)
    if os.path.isfile(path_file):
        df_comments = pd.read_csv(path_file, compression='gzip').dropna(axis=0)
        df_head = df_comments.head(2)
        print(df_head)
        df_results = pd.DataFrame(df_head["comments"].apply(df_list))
        df_results['video_id'] = df_head['video_id']
        df_results['channel_id'] = file_name[:-7]
        
        if n==0:
            df_final = df_results
        else:
            df_final = pd.concat([df_final, df_results])
    n+=1

df_final.to_csv('out.csv')