// This script is used in order to compute a part of the adjecency matrix for the comments graph.
// This is used alongside a python script in order to not overload the RAM.

#include <cstdint>
#include <fstream>
#include <iostream>
#include <string>

using namespace std;

#define i32 int32_t
#define i64 int64_t

#define CACHE_SIZE 100000000
#define AUTHOR_CHANNELS_MAX_SIZE 13000
#define CHANNEL_NUM 136470

int main(int argc, char** argv) {
    ifstream channel_in_stream(argv[1], ios::in | ios::binary | ios::ate);
    ifstream author_in_stream(argv[2], ios::in | ios::binary | ios::ate);
    auto author_length = author_in_stream.tellg() / sizeof(i64);
    auto channel_length = channel_in_stream.tellg() / sizeof(i32);

    i32 start_channel = stoi(argv[5]);
    i32 end_channel = stoi(argv[6]);

    author_in_stream.seekg(0);
    channel_in_stream.seekg(0);

    i64 *author_cache = (i64*) malloc(sizeof(i64) * CACHE_SIZE);
    i32 *channel_cache = (i32*) malloc(sizeof(i32) * CACHE_SIZE);
    i32 *target_channel_cache = (i32*) malloc(sizeof(i32) * AUTHOR_CHANNELS_MAX_SIZE);
    i32 *author_channel_cache = (i32*) malloc(sizeof(i32) * AUTHOR_CHANNELS_MAX_SIZE);
    i32 *channel_unique_authors_count = (i32*) calloc(end_channel-start_channel, sizeof(i32));
    i32 *adjecency_matrix_part = (i32*) calloc(CHANNEL_NUM * (end_channel-start_channel), sizeof(i32));
    
    i64 author_index = 0;
    i64 channel_index = 0;
    i64 channel_cache_index = 0;
    i32 author_load_size = CACHE_SIZE;
    i32 channel_load_size = 0;
    auto author_start = channel_in_stream.tellg();
    while(true) {
        if(author_index == author_length) break;
        author_load_size = ((author_length-author_index) > CACHE_SIZE) ? CACHE_SIZE : (author_length-author_index);
        author_in_stream.read((char *) author_cache, sizeof(i64) * author_load_size);
        
        for(i64 author_cache_index = 0; author_cache_index < author_load_size; author_index++, author_cache_index++) {
            if(author_cache[author_cache_index] == 0) continue;

            auto author_end = author_cache[author_cache_index];
            i64 author_length = (author_end-author_start)/(2*sizeof(i32));

            i32 author_target_channels = 0;
            for(i32 author_channel_id = 0; author_channel_id < author_length; author_channel_id++, channel_index+=2, channel_cache_index+=2) {
                if(channel_cache_index >= channel_load_size) {
                    channel_load_size = ((channel_length-channel_index) > CACHE_SIZE) ? CACHE_SIZE : (channel_length-channel_index);
                    channel_in_stream.read((char *) channel_cache, sizeof(i32) * channel_load_size);
                    channel_cache_index = 0;
                }

                author_channel_cache[author_channel_id] = channel_cache[channel_cache_index];
                if(channel_cache[channel_cache_index] >= start_channel && channel_cache[channel_cache_index] < end_channel) {
                    target_channel_cache[author_target_channels] = channel_cache[channel_cache_index] - start_channel;
                    channel_unique_authors_count[channel_cache[channel_cache_index]-start_channel]++;
                    author_target_channels++;
                }
            }

            for(i32 author_channel_id = 0; author_channel_id < author_length; author_channel_id++) {
                for(i32 target_channel_id = 0; target_channel_id < author_target_channels; target_channel_id++) {
                    if(author_channel_cache[author_channel_id] > target_channel_cache[target_channel_id]) {
                        adjecency_matrix_part[target_channel_cache[target_channel_id]*CHANNEL_NUM + author_channel_cache[author_channel_id]] += 1;
                    }
                }
            }
            
            author_start = author_end;
        }
    }

    author_in_stream.close();
    channel_in_stream.close();



    ofstream adjecency_out_stream(argv[3], ios::out | ios::binary);
    for(int i = start_channel; i < end_channel; i++) {
        adjecency_out_stream.write((char*) &adjecency_matrix_part[(i-start_channel)*CHANNEL_NUM+(i+1)], (CHANNEL_NUM-i-1)*sizeof(i32));
    }
    adjecency_out_stream.close();

    ofstream unique_authors_out_stream(argv[4], ios::out | ios::binary);
    unique_authors_out_stream.write((char*) channel_unique_authors_count, (end_channel-start_channel)*sizeof(i32));
    unique_authors_out_stream.close();
}