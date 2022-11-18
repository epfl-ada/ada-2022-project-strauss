make clean
make all

:: <YouNiverse dataset dir>, <channel_ids dest>, <channel_video_ids dest>, <starting_year>
:: This scripts reads YouNiverse dataset and exports two files: channel_ids contains a list YouTube channel ID's, in the other commands
:: enumerated channel ID (an integer) represents the index in this list (starting with 0).
:: Second exported file: channel_video_ids contains a list of video ID's (display_id) and the normal (non-enumerated) ID's of their YouTube channels
:: Final parameters represents starting year for considered videos, for ex. if it's 2018, only videos which were uploaded after 01.01.2018 are considered.
:: If a video was uploaded before this date, their channel id is exported as "000000000000000000000000", rest of the scripts thake this into consideration.
python enumerate_channel_video.py C:\Users\<user>\Downloads .\data\channel_ids.txt .\data\channel_video_ids_2018.txt 2018

:: <channel_ids dest>, <channel_video_ids dest>, <starting_year>, <channel_video_ids_enumerated>
:: This scripts takes as it's input, files exported in the previous script and it replaces normal (non-enumerated) YouTube channel ID's with the enumerated ones.
:: For channels with ID "000000000000000000000000", a -1 is written.
enumerate_channel_ids.exe .\data\channel_ids.txt .\data\channel_video_ids_2018.txt .\data\channel_video_ids_enumerated_2018.txt

:: <channel_video_ids_enumerated>, <YouNiverse youtube_comments file>, <offset_start, offset_end>, <comments_channels binary>
:: Takes file comuted by the previous script and uses it to replace video ID's (string) with a enumerated channel ID. Then author ID and channel ID's are packed
:: as a pack of two integers and written to a comments_channels binary. Any videos wich are connected to the channel -1 are ignored. This is a heavy step so it's designed
:: to be computed in multiple parallel processes. Be warned that each one needs around 6GB of RAM(due to the map with 77 million BST keys).
start /b enumerate_comments.exe .\data\channel_video_ids_enumerated_2018.txt C:\Users\<user>\Downloads\youtube_comments.tsv.gz          0 4350000000 .\data\out0.bin
start /b enumerate_comments.exe .\data\channel_video_ids_enumerated_2018.txt C:\Users\<user>\Downloads\youtube_comments.tsv.gz 4350000000 9000000000 .\data\out1.bin

:: Combine binaries.
copy /b .\data\out*.bin .\data\comments_channels_2018.bin
del .\data\out0.bin
del .\data\out1.bin

:: <comments_channels binary>, <comments_channels_aggregated binary>, <comments_channels_aggregated_author index binary>
:: This enables further aggregation and a reduction in total file size. Instead of repeating multiple multiple comments from the same author to the same channel,
:: for each author, enumerated channel ID's are taken and the number of occurances per channel are summed. <comments_channels_aggregated> contains integer pairs
:: of enumerated channel ID and the number of comments made to that channel (for a particular author). <comments_channels_aggregated_author index binary> contains
:: memory offsets in the <comments_channels_aggregated> binary for each existing author. Author's who don't have any comments have memory offset of -1. Others
:: have their offsets as a 64bit integer in the order of the ID. For example, 40 bytes from the begining of the <comments_channels_aggregated_author> a memory offset
:: of the author with the ID 5 (40/8=5) can be ready. If that memory offset is used to seek <comments_channels_aggregated> binary, data related with the author with
:: ID 5 can we read.
comment_channel_aggregation.exe .\data\comments_channels_2018.bin .\data\comments_channels_aggregated_2018.bin .\data\comments_channels_aggregated_author_index_2018.bin
del .\data\comments_channels_2018.bin