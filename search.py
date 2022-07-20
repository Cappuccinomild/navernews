import re
import ast
import multiprocessing
import os
import math
import sys
from tqdm import tqdm


# 텍스트 정제 함수
def text_cleaning(text, office):

    author = r'[(]?\w{2,4}[ ]?기자[)]?'

    result_list = []

    for item in text:
        #cleaned_text = re.sub('[a-zA-Z]', '', item)
        p = re.compile('[([]'+office+'[])]')
        cleaned_text = p.sub('', item)#신문사 삭제
        cleaned_text = cleaned_text.replace('[', '')
        cleaned_text = cleaned_text.replace(']', '')
        cleaned_text = cleaned_text.replace('\n', '')#엔터 삭제
        cleaned_text = re.sub(author, '', cleaned_text)#기자이름 삭제

        result_list.append(cleaned_text)

    return result_list

def cut_tail(word_corpus):

    if('@' in word_corpus):#이메일 삭제
        word_corpus = re.sub('\w+[@].+', '', word_corpus)

    elif('ⓒ' in word_corpus):
        word_corpus = re.sub('\w+[ⓒ].+', '', word_corpus)

    word_corpus = word_corpus[:word_corpus.rfind('.')+1]

    return word_corpus
