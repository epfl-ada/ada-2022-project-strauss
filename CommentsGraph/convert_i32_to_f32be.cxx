// Use this script in order to convert LE int32 binary files to BE float32 in order to load into Petsc.

#include <cstdint>
#include <fstream>
#include <iostream>
#include <cmath>
#include <map>

#define i32 int32_t
#define i64 int64_t

using namespace std;

#define CACHE_SIZE 268435456

int main(int argc, char** argv) {
    if(sizeof(float) != 4) {
        cerr << "Float is not defined as a 32 data type!" << endl;
        return 1;
    }

    int32_t test_byte_array[1];
    test_byte_array[0] = 1;

    if(((char *) test_byte_array)[0] == 0) {
        cerr << "System is Big-Endian!" << endl;
        return 2;
    }

    ifstream in_stream(argv[1], ios::in | ios::binary | ios::ate);
    ofstream out_stream(argv[2], ios::out | ios::binary);

    auto length = in_stream.tellg() / sizeof(i32);
    in_stream.seekg(0);

    i64 input_index = 0;
    i32 load_size = CACHE_SIZE;

    char *out_cache = (char *) malloc(sizeof(float)*CACHE_SIZE);
    i32 *cache = (i32 *) malloc(sizeof(i32)*CACHE_SIZE);

    while(true) {
        if(length == input_index) break;
        load_size = ((length-input_index) > CACHE_SIZE) ? CACHE_SIZE : (length-input_index);
        in_stream.read((char *) cache, sizeof(i32) * load_size);

        for(i32 cached_index = 0; cached_index < load_size; cached_index++, input_index++) {
            i32 number = cache[cached_index];
            float byte_array[1];
            byte_array[0] = 1.0f*number;
            out_cache[sizeof(float)*cached_index + 0] = ((char *) byte_array)[3];
            out_cache[sizeof(float)*cached_index + 1] = ((char *) byte_array)[2];
            out_cache[sizeof(float)*cached_index + 2] = ((char *) byte_array)[1];
            out_cache[sizeof(float)*cached_index + 3] = ((char *) byte_array)[0];
        }

        out_stream.write(out_cache, sizeof(float) * load_size);
    }
    in_stream.close();
    out_stream.close();
    return 0;
}