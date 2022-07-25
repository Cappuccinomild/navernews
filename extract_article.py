import os
import re
from tqdm import tqdm
import multiprocessing
import math

def divide_list(l, n):
    # 리스트 l의 길이가 n이면 계속 반복
    for i in range(0, len(l), n):
        yield l[i:i + n]

def search_keyword(map_val):

    #map_val = [저장폴더 이름, 키워드, 탐색 폴더]
    for i in tqdm(range(len(map_val))):
        param = map_val[i]

        output_dir = param[0]
        keyword = param[1]
        fname = param[2]

        keyword = keyword.split("&")

        #부정일 경우 keyword[1]에 0을 넣어줘서 부정임을 표시
        for j in range(len(keyword)):
            #부정일 경우
            if "!" in keyword[j]:
                keyword[j] = [re.compile(keyword[j].replace("!", '')), 0]

            else:
                keyword[j] = [re.compile(keyword[j]), 1]


        f = open(fname, encoding = 'utf-8')

        line = f.readline()

        while line:

            #매치 확인
            match = False
            for key in keyword:

                #not이 있을 경우
                if key[1] == 0:
                    if len(key[0].findall(line)) >= 1:
                        match = False
                        break
                    else:
                        match = True

                #not이 없을 경우
                else:
                    if len(key[0].findall(line)) >= 1:
                        match = True
                    else:
                        match = False
                        break

            #매칭되어 저장함
            if match:

                #map_val = [저장폴더 이름, 키워드, 탐색 폴더]
                os.makedirs(output_dir, exist_ok = True)
                output = open(output_dir + "/" + fname.split("\\")[-1], "a", encoding = "utf-8")
                output.write(fname + "\t")
                output.write(line)
                output.close()

            #엔터 제거
            f.readline()
            line = f.readline()

if __name__ == '__main__':

    f = open("검색어.txt", encoding = 'utf-8')
    line = f.readline()

    process_num = 10

    while line:
        print(line)

        #저장폴더 이름
        dirname = line.replace("&", "AND").replace("|", "OR").replace("\n", "")
        os.makedirs(dirname, exist_ok=True)

        #기사 폴더 내의 모든 파일 추출
        map_val = []
        cnt = 0
        dir_path = "./기사"
        for (root, directories, files) in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)

                map_val.append([root.replace(dir_path, dirname), line.replace("\n", ""), file_path])
                cnt = cnt + 1

                if cnt == 3000:

                    #프로세스 개수로 map_val 분할
                    map_val = divide_list(map_val, int(math.ceil(len(map_val) / process_num)))

                    pool = multiprocessing.Pool(processes=process_num)
                    pool.map(search_keyword, map_val)

                    pool.close()
                    pool.join()

                    cnt = 0
                    map_val = []

        #프로세스 개수로 map_val 분할
        map_val = divide_list(map_val, int(math.ceil(len(map_val) / process_num)))

        pool = multiprocessing.Pool(processes=process_num)
        pool.map(search_keyword, map_val)

        pool.close()
        pool.join()

        cnt = 0
        map_val = []

        line = f.readline()
