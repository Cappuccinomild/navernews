import os
import re
from tqdm import tqdm
import multiprocessing
import math

def merge(map_val):
    root = map_val

    flist = os.listdir(root)
    #기사가 있는 날짜 수집
    date_list = set()
    for fname in flist:
        #20220101 ~ 을 집합에 추가
        date_list.add(fname[:8])

    date_list = list(date_list)

    for date in date_list:
        output_link = "/".join([root, date])
        output = open(output_link + ".txt", "a", encoding = 'utf-8')

        rm_list = []
        #같은 날짜의 파일을 읽어옴
        for fname in flist:

            #같은 날짜의 파일만 가져옴
            if fname[:8] == date:
                f = open("/".join([root, fname]), "r", encoding = 'utf-8')
                output.write(f.read())
                f.close()

                rm_list.append("/".join([root, fname]))

        for rm_file in rm_list:
            os.remove(rm_file)

        output.close()

if __name__ == '__main__':

    f = open("검색어.txt", encoding = 'utf-8')
    line = f.readline()

    process_num = 10

    while line:
        #저장폴더 이름
        dirname = line.replace("&", "AND").replace("|", "OR").replace("\n", "")


        #기사 폴더 내의 모든 파일 추출
        map_val = []
        for year in os.listdir(dirname):

            #./기사/2022
            months = "/".join([dirname, year])
            for month in os.listdir(months):
                map_val.append("/".join([months, month]))

            process_num = len(map_val)
            pool = multiprocessing.Pool(processes=process_num)
            pool.map(merge, map_val)

            pool.close()
            pool.join()

        map_val = []

        line = f.readline()
