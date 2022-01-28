import os

import google.auth.transport.requests
import google.oauth2.id_token
import numpy as np
import requests
from chainer import cuda
from google.cloud import storage

FLAG_GPU = False
if FLAG_GPU:
    xp = cuda.cupy
    cuda.get_device_from_id(0).use()
else:
    xp = np

MECAB_SERVICE_DOMAIN = os.environ["MECAB_SERVICE_DOMAIN"]
MECAB_SERVICE_URL = f"https://{MECAB_SERVICE_DOMAIN}/mecab/v1/parse-neologd"


# データ変換クラスの定義
class DataConverter:
    def __init__(self):
        """
        クラスの初期化
        """
        # 単語辞書の登録
        self.vocab = {}
        # CloudStorageからvocabファイルをDownload
        txt = "vocab.txt"
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(os.environ["BUCKET_NAME"])
        blob = storage.Blob("att-seq2seq/v1/" + txt, bucket)
        lines = blob.download_as_string().decode("utf-8").split("\n")
        i = 0
        for line in lines:
            if line:  # 空行を弾く
                self.vocab[line] = i
                i += 1

    @staticmethod
    def sentence2words(sentence):
        """
        文章を単語の配列にして返却する
        :param sentence: 文章文字列
        """
        sentence_words = []

        auth_req = google.auth.transport.requests.Request()
        id_token = google.oauth2.id_token.fetch_id_token(auth_req, MECAB_SERVICE_URL)
        headers = {"Authorization": f"Bearer {id_token}"}
        response = requests.post(
            MECAB_SERVICE_URL, headers=headers, json={"sentence": sentence}
        )

        for m in response.json()["results"]:
            w = m.split("\t")[0].lower()
            if (len(w) == 0) or (w == "eos"):
                continue
            sentence_words.append(w)
        sentence_words.append("<eos>")
        return sentence_words

    def sentence2ids(self, sentence):
        """
        文章を単語IDのNumpy配列に変換して返却する
        :param sentence: 文章文字列
        :sentence_type: 学習用でミニバッチ対応のためのサイズ補填方向をクエリー・レスポンスで変更するため"query"or"response"を指定
        :return: 単語IDのNumpy配列
        """
        ids = []  # 単語IDに変換して格納する配列
        sentence_words = DataConverter.sentence2words(sentence)  # 文章を単語に分解する
        for word in sentence_words:
            if word in self.vocab:  # 単語辞書に存在する単語ならば、IDに変換する
                ids.append(self.vocab[word])
            else:  # 単語辞書に存在しない単語ならば、<unk>に変換する
                ids.append(self.vocab["<unk>"])
        ids = xp.array([ids], dtype="int32")
        return ids

    def ids2words(self, ids):
        """
        予測時に、単語IDのNumpy配列を単語に変換して返却する
        :param ids: 単語IDのNumpy配列
        :return: 単語の配列
        """
        words = []  # 単語を格納する配列
        for i in ids:  # 順番に単語IDを単語辞書から参照して単語に変換する
            words.append(list(self.vocab.keys())[list(self.vocab.values()).index(i)])
        return words
