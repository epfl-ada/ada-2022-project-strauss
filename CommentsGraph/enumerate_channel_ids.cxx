/* <channel_ids dest>, <channel_video_ids dest>, <starting_year>, <channel_video_ids_enumerated>
 * This scripts takes as it's input, files exported in the previous script and it replaces normal (non-enumerated) YouTube channel ID's with the enumerated ones.
 * For channels with ID "000000000000000000000000", a -1 is written.
 */

#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <string>

#define i64 int64_t

using namespace std;

int main(int argc, char** argv) {
    ifstream channel_idsstream(argv[1], ios_base::in | ios_base::binary);
    string line;
    map<string, i64> channels;

    // Flag ignored videos
    channels["000000000000000000000000"] = -1;

    i64 id = 0;
    while(getline(channel_idsstream, line)) {
        line = line.substr(0, 24);
        channels[line] = id;
        id++;
    }
    channel_idsstream.close();
    ifstream channel_video_idsstream(argv[2], ios_base::in | ios_base::binary);
    ofstream channel_video_enumerated_stream(argv[3], ios_base::out | ios_base::binary);
    while(getline(channel_video_idsstream, line)) {
        string channel_id = line.substr(0,24);
        string video_id = line.substr(25,11);
        channel_video_enumerated_stream << channels[channel_id] << " " << video_id << "\n";
    }
    channel_video_idsstream.close();
    channel_video_enumerated_stream.close();
    return 0;
}