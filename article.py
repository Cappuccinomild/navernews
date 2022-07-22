import requests
from bs4 import BeautifulSoup
import datetime
import time
import re
import ast
import multiprocessing
import os
import math
import sys
from tqdm import tqdm

newspaper = open("언론사.txt", encoding = 'utf-8').read().replace('\ufeff','').split(" ")

# 텍스트 정제 함수
def text_cleaning(text, office):

    text = " ".join(text)
    #앞쪽 공백 삭제
    p = re.compile('[^\s|^\t|^\n].+')
    text = "".join(p.findall(text))

    #뒤쪽 공백 삭제
    p = re.compile('.+[^\s|^\t|^\n]')
    text = "".join(p.findall(text))

    author = r'[(]?\w{2,4}[ ]?기자[)]?'

    #cleaned_text = re.sub('[a-zA-Z]', '', item)
    p = re.compile('[([]'+office+'[])]')
    cleaned_text = p.sub('', text)#신문사 삭제
    cleaned_text = cleaned_text.replace('[', '')
    cleaned_text = cleaned_text.replace(']', '')
    cleaned_text = cleaned_text.replace('\n', '')#엔터 삭제
    cleaned_text = re.sub(author, '', cleaned_text)#기자이름 삭제

    return cleaned_text

def cut_tail(word_corpus):

    if('@' in word_corpus):#이메일 삭제
        word_corpus = re.sub('\w+[@].+?[\s]', '', word_corpus)

    elif('ⓒ' in word_corpus):
        word_corpus = re.sub('\w+[ⓒ].+[\s]', '', word_corpus)

    word_corpus = word_corpus[:word_corpus.rfind('.')+1]

    return word_corpus

def str_to_date(input):#yyyymmdd 문자열을 datetime 객체로 변경
    #                             yyyy              mm              dd
    return datetime.datetime(int(input[:4]), int(input[4:6]), int(input[6:]))

def date_to_str(input):
    output = ''
    output += str(input.year)

    if(input.month < 10):
        output +='0'

    output += str(input.month)
    if(input.day < 10):
        output +='0'
    output += str(input.day)

    return output

def get_html(url):

    hdr = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36 Edg/103.0.1264.49'}
    _html = ""

    while True:

        try:
            resp = requests.get(url, headers = hdr, timeout=10)
        except requests.exceptions.Timeout as timeout:

            print(timeout)
            print(url)
            time.sleep(10)
            continue

        except requests.exceptions.ConnectionError as cut:

            print(cut)
            print(url)
            #연결 끊김 발생시 15분 대기
            time.sleep(900)
            continue

        if resp.status_code == 200:
            _html = resp.text
            break

    return _html

def extract_article(output_path, line, soup):

    text = ''
    img_desc = []
    doc = None

    i = 0
    tag_list = ['dic_area','articleBodyContents', 'articleBody', 'newsEndContents', 'newsct_article']

    for tags in tag_list:
        try:
            if soup.find_all('div', id=tags):
                for item in soup.find_all('div', id=tags):
                    text = text + str(item.find_all(text=True))

                    text = ast.literal_eval(text)

                    text = "".join(text)
                    #앞쪽 공백 삭제
                    p = re.compile('[^\s|^\t|^\n].+')
                    text = "".join(p.findall(text))

                    #뒤쪽 공백 삭제
                    p = re.compile('.+[^\s|^\t|^\n]')
                    text = "".join(p.findall(text))

                    '''
                    doc = text_cleaning(text, line[1])#본문 내 언론사 삭제

                    word_corpus = cut_tail(doc)

                    return word_corpus
                    '''

                    return text

        except:
            print("bs4 err")
            print(line)
            return False

    #일치하는 패턴이 없는경우
    print("패턴 불일치")
    print(line)
    return False


#기사 본문 추출
def get_article(map_val):#return list
    print(map_val)
    errcnt = 0

    #map_val[대분류코드, 시작날짜, 종료날짜]
    sid1 = map_val[0]
    sid2 = map_val[1]
    date_s = map_val[2]
    date_e = map_val[3]

    #기사링크모음 경로
    path = './'+sid1+'/'+sid1+sid2+"_link"
    #분할된 날짜 내의 파일만 가져옴
    link_set = []
    for fname in os.listdir(path):

        fdate = fname.split("_")[1][:-4]
        fdate = str_to_date(fdate)

        if date_s >= fdate and fdate >= date_e:
            link_set.append(fname)

    line_cnt = 0
    for i in tqdm(range(len(link_set))):
        fname = link_set[i]
        f = open(path + "/" + fname, "r", encoding = 'utf-8')

        #파일 형식
        #line -> #100273_media_20200101_headline_2_link
        line = f.readline()
        while line:

            if not line:
                break

            if line == "\n":
                break
            try:
                line = line.split("_")
            except:
                print("------------------ split err ------------------")

                print(line)
                line = f.readline()
                continue

            #ex) line[2][:-4] = 2022
            #ex) line[2][4:-2] = 07

            #year 폴더 만들기
            os.makedirs(line[2][:-4], exist_ok=True)
            #output path = ./2022/07
            output_path = './' + line[2][:-4] + "/" + line[2][4:-2]
            os.makedirs(output_path, exist_ok=True)

            #월별로 나눠진 폴더에 저장
            #20220701_신문사_일련번호
            output = open(output_path + "/" + "_".join([line[2], line[1], line[0] + str(line_cnt)]) + ".txt", "a", encoding='utf-8')
            #저장된 링크를 통한 기사 크롤링
            #print(line[5].replace("\n", ''))
            html = get_html(line[5].replace("\n", ''))#끝부분 줄바꿈문자 제거


            #사진 설명 삭제
            html = re.sub('<em class="img_desc.+?/em>', '', html)

            # 각 기사에서 텍스트만 정제하여 추출
            soup = BeautifulSoup(html, 'lxml')


            #100273_media_20200101_headline_2_link
            output.write(line[2] + "\t")#날짜
            output.write(line[0] + "\t")#분류
            output.write(line[1] + "\t")#신문사
            output.write(line[3] + "\t")#헤드라인

            word_corpus = extract_article(output_path, line, soup)

            #본문을 추출한 경우
            if word_corpus:
                output.write(word_corpus + '\t')#본문 내용

            #본문을 추출하지 못한경우
            else:
                errcnt+=1
                output.close()

                #output 파일 삭제
                os.remove(output_path + "/" + "_".join([line[2], line[1], line[0] + str(line_cnt)]) + ".txt")

                #에러로그 작성
                err = open(output_path + "/" + "_".join([line[2], line[1], line[0] + str(line_cnt)]) + "_err.txt", "w", encoding='utf-8')
                err.write("_".join(line))
                err.close()

                line = line.readline()
                continue

            #기사링크 저장
            #100273_media_20200101_headline_2_link
            output.write(line[-1])
            output.close()
            line = f.readline()
            line_cnt += 1

    total = line_cnt
    print(sid1 + sid2 + " : " + str(total - errcnt)+ "/" + str(total))
    f.close()


if __name__ == '__main__':

    start = datetime.datetime.now()

    #cmd 입력으로 crawl.py 2022-03-06 2022-01-01 [언론사 목록]실행
    if len(sys.argv) == 3:
        date_s = sys.argv[1]
        date_e = sys.argv[2]

    else:
        print("날짜를 입력해주세요.")
        sys.exit()

    #map_val = [대분류, 소분류, 시작날짜, 종료날짜]
    #분할처리를 위해 대분류 코드가 들어간 map_val을 6개 만듦

    #대분류코드 = 정치:100   경제:101  사회:102  생활/문화:103   세계:104   IT/과학:105

    #소분류코드
    #정치sid2 = 청와대:264  국회/정당:265   북한:268 행정:266 국방/외교:267  정치일반:269
    #경제sid2 = 금융:259    증권:258  산업/재계:261   중기/벤처:771   부동산:260 글로벌 경제:262  생활경제:310    경제일반:263
    #사회sid2 = 사건사고:249  교육:250  노동:251  언론:254  환경:252  인권/복지:59b   식품/의료:255   지역:256  인물:276  사회일반:257
    #생활/문화sid2 = 건강정보:241   자동차/시승기:239    도로/교통:240  여행/레저:237 음식/맛집:238  패션/뷰티:376  공연/전시:242  책:243  종교:244  날씨:248  생활문화 일반:245
    #세계sid2 = 아시아/호주:231    미국/중남미:232  유럽:233   중동/아프리카:234    세계일반:322
    #IT/과학sid2 = 모바일:731    인터넷/SNS:226    통신/뉴미디어:227    IT일반:230   보안/해킹:732  컴퓨터:283    게임/리뷰:229  과학 일반:228

    #대분류 소분류에 사용되는 sid 목록
    sid = {
    '100':["264","265","268","266","267","269"],
    '101':["259","258","261","771","260","262","310","263"],
    '102':["249","250","251","254","252","59b","255","256","276","257"],
    '103':["241","239","240","237","238","376","242","243","244","248","245"],
    '104':["231","232","233","234","322"],
    '105':["731","226","227","230","732","283","229","228"]
    }


    #언론사 디렉토리 생성
    '''
    for media in newspaper:
        for sid1 in sid.keys():
            for sid2 in sid[sid1]:
                os.makedirs("./" + media + "/" + sid1 + "/" + sid1 + sid2, exist_ok=True)
    '''

    date_s = date_s.split("-")
    date_e = date_e.split("-")

    for i in range(0, 3):
        date_s[i] = int(date_s[i])
        date_e[i] = int(date_e[i])

    date_s = datetime.datetime(date_s[0],date_s[1],date_s[2])
    date_e = datetime.datetime(date_e[0],date_e[1],date_e[2])

    for sid1 in sid.keys():
        for sid2 in sid[sid1]:
            #날짜를 N개의 묶음으로 나눔
            days = (date_s - date_e).days

            #process의 개수
            N = 6

            temp_e = []
            for i in range(0,days, math.ceil(days/N)):

                temp_e.append(date_s - datetime.timedelta(days=i))

            map_val=[]
            for i in range(len(temp_e)-1):
                map_val.append([sid1, sid2, temp_e[i], temp_e[i+1] - datetime.timedelta(days=1)])

            map_val.append([sid1, sid2, temp_e[-1], date_e])


            process_num = len(sid[sid1])
            print(map_val, "process : ", process_num)

            #get_link_test(map_val[0])

            pool = multiprocessing.Pool(processes=N)
            pool.map(get_article, map_val)

            pool.close()
            pool.join()

            print(sid1, sid2, "end")


    print(datetime.datetime.now() - start)
