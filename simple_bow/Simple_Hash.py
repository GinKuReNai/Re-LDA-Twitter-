# encoding  : utf-8
import MeCab
import pandas as pd
import hashlib
import csv

mc = MeCab.Tagger("-d ../../../usr/local/lib/mecab/dic/mecab-ipadic-neologd")
mc.parse('')
dictionary = {}
word_count=0

def genre_judge(line):
    # ジャンル添字：genreに格納
    genre = 0
    # 国際
    if "０７" in line:
        genre=0
    # 経済
    elif "０８" in line:
        genre=1
    # 家庭
    elif "１３" in line:
        genre=2
    # 文化
    elif "１４" in line:
        genre=3
    # 読書
    elif "１５" in line:
        genre=4
    # 科学
    elif "１６" in line:
        genre=5
    # 生活
    elif "１７" in line:
        genre=6
    # 芸能
    elif "１８" in line:
        genre=7
    # スポーツ
    elif "３５" in line:
        genre=8
    # 社会
    elif "４１" in line:
        genre=9
    return genre

def make_bow(text):
        # 語彙化
        vocab = {}
        for tokens in text:
                for token in tokens:
                        if token not in vocab:
                                vocab[token] = len(vocab)
        size_vocab = len(vocab)
                
        # BOWの作成
        # リストの初期化
        bow = [[0] * size_vocab for i in range(len(text))]
        for i, tokens in enumerate(text):
                for token in tokens:
                        index = vocab[token]
                        bow[i][index] += 1

        return vocab, bow

# 
def get_tokens(sent):
        node = mc.parseToNode(sent)
        tokens = []
        while node:
            if node.surface: # BOSとEOSを除く
                if ("アルファベット" or "数" or "助詞" or "記号") not in node.feature:
                    tokens.append(node.surface)
            node=node.next

        return tokens


file_path=['../public/newspapers/mainichi/1995/mai1995utf8.txt',
        '../public/newspapers/mainichi/2015/zenkoku/mai2015utf8.txt',
        '/home/public/newspapers/mainichi/2016/zenkoku/mai2016utf8.txt',
        '/home/public/newspapers/mainichi/2019/zenkoku/mai2019utf8.txt']

for file in file_path:
    with open(file)as f:
        count=0
        for line in f:
            if "ＡＤ" in line:
                genre = genre_judge(line)
                # print("ジャンル : " + str(genre))
                count += 1

            # 本文に対する処理
            # Bag-of-Wordsを作成
            if "Ｔ２" in line:
            # textは助詞を除いた文字列 
                texts = []
                texts.append(get_tokens(line))
                vocabulary, bow = make_bow(texts)        

                # ここから単語の辞書にカウントしていく処理を行う
                # dictionary : key=単語, 中身=ジャンルの大きさのベクトル
                for text in texts:
                    for word in text:
                        # もし辞書に単語が登録されていなかったら
                        # vector : 一時的に取ってくる変数
                        # hash：wordのハッシュ値を計算
                        hash=hashlib.md5(word.encode()).hexdigest()

                        if dictionary.get(word) == None:
                            word_count += 1
                            vector = [0,0,0,0,0,0,0,0,0,0]

                        # 既にある場合はジャンルに対応する位置に頻度を加えて更新する
                        else:
                            vector = dictionary[word]
                        vector[genre] += bow[0][vocabulary[word]]
                        dictionary[word] = vector
            
            if count > 2:
                break

for key, value in dictionary.items():
    sum = 0
    for i in range(len(value)):
        sum += value[i]
    genre_rates = [0,0,0,0,0,0,0,0,0,0]
    for i in range(len(value)):
        genre_rates[i] = value[i] / sum
    print(key + ' : ' + str(genre_rates))

print('総単語数：',word_count)

field_name=['ハッシュ値','bag-of-words']
with open('mainichi.csv','w',encoding='utf-8')as csvfile:
    writer = csv.writer(csvfile)
    for k, v in dictionary.items():
        writer.writerow([k, v])
