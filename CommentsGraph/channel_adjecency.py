# Run channel_adjecency_part many times in order to compute adjecency matrix in parallel.

import subprocess
from multiprocessing import Process, Manager, Lock

exe = "channel_adjecency_part.exe"
channel_file = "./data/comments_channels_aggregated_2018.bin"
author_index_file = "./data/comments_channels_aggregated_author_index_2018.bin"

CHANNEL_NUM = 136470

proc_num = 4

def compute_adjecency_matrix_part(q,l):
    while True:
        l.acquire()
        if q.qsize() == 0:
            l.release()
            break
        part = q.get()
        l.release()
        start_index = part*1000
        end_index = (part+1)*1000 if part < 136 else 136470
        process = subprocess.Popen(f'{exe} {channel_file} {author_index_file} ./data/channel_adjacency_2018_{"{0}".format(part).zfill(3)}.bin ./data/channel_unique_author_{"{0}".format(part).zfill(3)}.bin {start_index} {end_index}', shell=True, stdout=subprocess.PIPE)
        process.wait()
        print("Remaining: ", q.qsize())

if __name__ == '__main__':
    with Manager() as manager:
        q = manager.Queue()
        l = Lock()
        [q.put(i) for i in range(0,int(CHANNEL_NUM/1000)+1)]
        ps = [Process(target=compute_adjecency_matrix_part, args=(q,l)) for p in range(proc_num)]
        [p.start() for p in ps]
        [p.join() for p in ps]
        print(q.qsize())
        exit()