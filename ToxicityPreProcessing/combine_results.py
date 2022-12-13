import os
import numpy as np
import pandas as pd

channel_names = [fname[:-17] for fname in os.listdir('./toxicity_res/')]

for i, channel_name in enumerate(channel_names):
    channel_df = pd.read_csv(f'./yt/{channel_name}.csv')
    channel_toxicity = pd.read_feather(f'./toxicity_res/{channel_name}_toxicity.feather')
    video_map = np.load(f'./aux_data/{channel_name}_comm_video_loc_idx.npy')

    channel_toxicity['video_map'] = video_map
    channel_toxicity['view_count'] = channel_df.loc[video_map]['view_count'].tolist()
    channel_toxicity['upload_date'] = channel_df.loc[video_map]['upload_date'].tolist()

    channel_toxicity.to_feather(f'./export/{channel_name}_toxicity.feather')

    print(i/len(channel_names))