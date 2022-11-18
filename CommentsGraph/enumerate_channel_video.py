# <YouNiverse dataset dir>, <channel_ids dest>, <channel_video_ids dest>, <starting_year>
# This scripts reads YouNiverse dataset and exports two files: channel_ids contains a list YouTube channel ID's, in the other commands
# enumerated channel ID (an integer) represents the index in this list (starting with 0).
# Second exported file: channel_video_ids contains a list of video ID's (display_id) and the normal (non-enumerated) ID's of their YouTube channels
# Final parameters represents starting year for considered videos, for ex. if it's 2018, only videos which were uploaded after 01.01.2018 are considered.
# If a video was uploaded before this date, their channel id is exported as "000000000000000000000000", rest of the scripts thake this into consideration.

import sys
import pandas as pd
import numpy as np
import datetime


data_loc = sys.argv[1]
cutoff_year = datetime.datetime(int(sys.argv[4]),1,1)

channels = pd.read_csv(f'{data_loc}\\df_channels_en.tsv.gz', sep="\t")
videos = pd.read_feather(f'{data_loc}\\yt_metadata_helper.feather')

channel_ids = channels['channel'].tolist()

videos.loc[videos['upload_date'] < cutoff_year, 'channel_id'] = '000000000000000000000000'

channel_video_ids = (videos['channel_id'] + ' ' + videos['display_id']).tolist()

np.savetxt(sys.argv[2], channel_ids, delimiter='\n', fmt='%s')
np.savetxt(sys.argv[3], channel_video_ids, delimiter='\n', fmt='%s')