/* <channel_video_ids_enumerated>, <YouNiverse youtube_comments file>, <offset_start, offset_end>, <comments_channels binary>
 * Takes file comuted by the previous script and uses it to replace video ID's (string) with a enumerated channel ID. Then author ID and channel ID's are packed
 * as a pack of two integers and written to a comments_channels binary. Any videos wich are connected to the channel -1 are ignored. This is a heavy step so it's designed
 * to be computed in multiple parallel processes. Be warned that each one needs around 6GB of RAM(due to the map with 77 million BST keys).
 */

#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <string>

#include <boost/iostreams/filtering_streambuf.hpp>
#include <boost/iostreams/copy.hpp>
#include <boost/iostreams/filter/gzip.hpp>

// Fix boost error.
#include <boost_fix.h>

#define i32 int32_t
#define i64 int64_t

using namespace std;

int main(int argc, char** argv) {
    string line;

    string start_arg(argv[3]);
    string end_arg(argv[4]);
    i64 start_i = stoll(start_arg);
    i64 end_i = stoll(end_arg);

    ifstream comments_stream(argv[2], ios_base::in | ios_base::binary);
    boost::iostreams::filtering_streambuf<boost::iostreams::input> inbuf;
    inbuf.push(boost::iostreams::gzip_decompressor());
    inbuf.push(comments_stream);
    std::istream instream(&inbuf);

    //Skip header (first line)
    getline(instream, line);
    i64 i = -1;
    // Seek until ready to parse the section from the YouNiverse comments file.
    while(getline(instream, line)) {
        i++;
        if(i == start_i) {
            i--;
            break;
        }
    }

    // Create map linking video ID's (string) to enumerated channel ID's.
    ifstream enum_channel_video_idsstream(argv[1], ios_base::in | ios_base::binary);
    map<string, i32> video_enum_channel;
    while(getline(enum_channel_video_idsstream, line)) {
        string enum_channel_id = line.substr(0,line.find(' '));
        string video_id = line.substr(line.find(' ')+1, 11);
        video_enum_channel[video_id] = stoi(enum_channel_id);
    }
    enum_channel_video_idsstream.close();

     // Read compressed YouNiverse comments file and replace video ID string with enumerated channel ID.
     // Write the result to the output file.
    ofstream out_stream(argv[5], ios::out | ios::binary);
    while(getline(instream, line)) {
        i++;
        if (i >= end_i) {
            break;
        }

        // No need to remove \n.
        i32 author_id = stoi(line.substr(0,line.find(9)));
        string video_id = line.substr(line.find(9)+1,11);

        i32 channel_id = video_enum_channel[video_id];
        // Skip ignored videos
        if(channel_id == -1) {
            continue;
        }

        out_stream.write((char *) &author_id, sizeof(i32));
        out_stream.write((char *) &channel_id, sizeof(i32));
        
        // Flush every fifty million entries to keep memory usage "low".
        if(i%50000000 == 0) {
            out_stream.flush();
        }
    }
    out_stream.close();
    comments_stream.close();

    return 0;
}