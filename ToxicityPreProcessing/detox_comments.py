import pickle
import os
import torch
import time
import pandas as pd
import numpy as np
from detoxify import Detoxify
from file_list import file_list

total_files_size = 0
total_processed_size = 0

for ele in os.scandir('./comments/'):
    total_files_size += os.path.getsize(ele)

batch_size = 10
classifier = Detoxify('unbiased', device=torch.device('cuda'))

t_start = time.time()
for file_name in file_list:
    if f'{file_name}_comments.pickle' not in  os.listdir('./comments'):
        continue

    total_processed_size += os.path.getsize(f'./comments/{file_name}_comments.pickle')
    with open(f'./comments/{file_name}_comments.pickle', 'rb') as handle:
        cms = pickle.load(handle)
        if(len(cms) == 0):
            continue
        slices = np.array([list(range(0,len(cms), batch_size)),[*list(range(0,len(cms), batch_size)[1:]),len(cms)]]).T
        batch_results = [pd.DataFrame(classifier.predict(cms[slice[0]:slice[1]])) for slice in slices]
        final_fm = pd.concat(batch_results).reset_index(drop=True)
        final_fm.to_feather(f'./toxicity_res/{file_name}_toxicity.feather')
        t_curr_end = time.time()
        print("Total processed: ", total_processed_size/total_files_size)
        print("Time passed: ", t_curr_end-t_start)
        print("Speed: ", total_processed_size/((t_curr_end-t_start)/60))