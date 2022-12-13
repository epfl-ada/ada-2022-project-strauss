import pickle
import ast
import numpy as np
import pandas as pd
from file_list import file_list

for file_name in file_list:
    try:
        fm_c = pd.read_csv(f'./cm/{file_name}.csv.gz')
        fm_v = pd.read_csv(f'./yt/{file_name}.csv')
        fm_v = fm_v[['video_id', 'upload_date', 'view_count']]
        #Correct semantics for videos without comments
        fm_c.loc[np.array([type(c) for c in fm_c['comments'].tolist()]) != type(''), 'comments'] = '[]'

        cms = [cm['text'] for cms_raw in fm_c['comments'].tolist() for cm in ast.literal_eval(cms_raw) if 'text' in cm.keys()]

        video_ids = fm_v['video_id'].to_list()
        target_video_ids = [fm_c['video_id'].tolist()[i] for i in range(len(fm_c)) for cm in ast.literal_eval(fm_c['comments'].tolist()[i]) if 'text' in cm.keys()]

        video_ids_sorter = np.argsort(fm_v['video_id'].tolist())
        located_idx = np.searchsorted(video_ids, target_video_ids, sorter=video_ids_sorter)

        cms = [cms[i] for i in np.where(located_idx < len(video_ids))[0]]
        target_video_ids = [target_video_ids[i] for i in np.where(located_idx < len(video_ids))[0]]

        video_ids_sorter = np.argsort(fm_v['video_id'].tolist())
        comm_video_loc_idx = video_ids_sorter[np.searchsorted(video_ids, target_video_ids, sorter=video_ids_sorter)]
    except:
        print(f'{file_name}- BAD')
        continue

    np.save(f'./aux_data/{file_name}_comm_video_loc_idx.npy', comm_video_loc_idx)
    with open(f'./comments/{file_name}_comments.pickle', 'wb') as handle:
        pickle.dump(cms, handle)
    print(f'{file_name}- DONE')