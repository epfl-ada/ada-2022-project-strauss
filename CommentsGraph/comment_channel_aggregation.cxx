/* <comments_channels binary>, <comments_channels_aggregated binary>, <comments_channels_aggregated_author index binary>
 * This enables further aggregation and a reduction in total file size. Instead of repeating multiple multiple comments from the same author to the same channel,
 * for each author, enumerated channel ID's are taken and the number of occurances per channel are summed. <comments_channels_aggregated> contains integer pairs
 * of enumerated channel ID and the number of comments made to that channel (for a particular author). <comments_channels_aggregated_author index binary> contains
 * memory offsets in the <comments_channels_aggregated> binary for each existing author. Author's who don't have any comments have memory offset of -1. Others
 * have their offsets as a 64bit integer in the order of the ID. For example, 40 bytes from the begining of the <comments_channels_aggregated_author> a memory offset
 * of the author with the ID 5 (40/8=5) can be ready. If that memory offset is used to seek <comments_channels_aggregated> binary, data related with the author with
 * ID 5 can we read.
 */

#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>

#define i32 int32_t
#define i64 int64_t

using namespace std;

#define CACHE_SIZE 268435456

int main(int argc, char** argv) {
    ifstream in_stream(argv[1], ios::in | ios::binary | ios::ate);
    ofstream out_stream(argv[2], ios::out | ios::binary);

    auto length = in_stream.tellg() / sizeof(i32);
    in_stream.seekg(-2*sizeof(i32), ios_base::end);
    i32 last_author_id;
    in_stream.read((char *) &last_author_id, sizeof(i32));

    in_stream.seekg(0);

    // Load 1GB i32o memory to process
    i64 *author_pos = (i64 *) malloc(sizeof(i64) * last_author_id+1);
    i32 *cache = (i32 *) malloc(sizeof(i32)*CACHE_SIZE);
    i64 input_index = 0;
    i32 load_size = CACHE_SIZE;

    i32 prev_author_id = -1;

    map<i32, i32> channel_id_cache;

    while(true) {
        if(length == input_index) break;
        load_size = ((length-input_index) > CACHE_SIZE) ? CACHE_SIZE : (length-input_index);
        in_stream.read((char *) cache, sizeof(i32) * load_size);

        for(i32 cached_index = 0; cached_index < load_size; cached_index+=2, input_index+=2) {
            i32 author_id = cache[cached_index];
            i32 channel_id = cache[cached_index+1];


            if(author_id != prev_author_id) {
                i32 *out_cache = (i32 *) malloc(2*sizeof(i32)*channel_id_cache.size());
                for(auto iter = channel_id_cache.begin(); iter != channel_id_cache.end(); iter++) {
                    i32 out_cache_index = 2 * distance(channel_id_cache.begin(), iter);
                    out_cache[out_cache_index] = iter->first;
                    out_cache[out_cache_index+1] = iter->second;
                }
                out_stream.write((char *) out_cache, 2 * sizeof(i32) * channel_id_cache.size());
                channel_id_cache.clear();
                free(out_cache);
            } else {
                // Add 1 to the channel counter
                // If a new key is introduced, map implementation automatically gives it value 0.
                channel_id_cache[channel_id] += 1;
            }

            // Update index, tag all non-existing author_ids
            while(author_id > prev_author_id) {
                prev_author_id++;
                if(author_id != prev_author_id) {
                    author_pos[prev_author_id] = -1;
                } else {
                    author_pos[prev_author_id] = out_stream.tellp();
                }
            }


        }
    }
    in_stream.close();
    out_stream.close();
    free(cache);

    //Save memory offsets to a separate file.
    ofstream indices_stream(argv[3], ios::out | ios::binary);
    indices_stream.write((char *) author_pos, sizeof(i64) * (last_author_id+1));
    indices_stream.close();
    free(author_pos);
    return 0;
}