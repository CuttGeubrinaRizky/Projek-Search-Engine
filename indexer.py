from pathlib import Path
import re
import math
import sys
from tqdm import tqdm

BASE_DIR = Path(__file__).resolve().parent
IN_DIR = BASE_DIR / 'clean'

total_file = 0


def get_text(text, tag):
    try:
        get = re.search(f'(?<={tag}\>)(.[\s\S]*)(?=\<\/{tag})', text)
        return get.group(1)
    except:
        get = re.search(f'(<{tag}>(.*?)</{tag}>)', text)
        return get.group(1)


def index(hash, words):
    for word in words:
        if word in hash:
            hash[word] += 1
        else:
            hash[word] = 1


tf, df = {}, {}

for path in IN_DIR.glob('*.html'):
    with open(path.resolve(), 'r', encoding='utf-8') as file:
        df[path.name] = {}
        text = file.read()
        content = get_text(text, 'title') + ' ' + get_text(text, 'top') + ' ' + \
            get_text(text, 'middle') + ' ' + get_text(text, 'bottom')
        words = content.split()

        index(df[path.name], words)
        index(tf, words)

        total_file += 1
        if total_file == 3000:
            break


def calculate_idf():
    idf = {}
    for word in tf:
        total_doc = 0
        for doc_id in df:
            if word in df[doc_id]:
                total_doc += 1
        try:
            idf_doc = math.log2(len(df)/total_doc)
        except:
            idf_doc = 0
        idf[word] = idf_doc
    return idf


# inverted_index = {}
idf = calculate_idf()

total_iter = 0
with open('src/inverted/inverted_index.txt', 'w', encoding='utf-8') as file:
    for word, freq in tqdm(tf.items()):

        file.write('{}-idf:{}'.format(word, idf[word]))
        total_iter += 1
        for doc_id in df.keys():
            doc_tf = 0
            total_word = 0
            if word in df[doc_id]:
                doc_tf = df[doc_id][word]
            total_word += sum(df[doc_id].values())
            word_frequency = doc_tf / total_word
            tfidf = word_frequency * idf[word]

            if tfidf > 0:
                file.write(f'|%s:%.3f' % (doc_id, tfidf))
        file.write('\n')
