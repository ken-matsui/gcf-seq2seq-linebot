# coding: utf-8

from chainer import cuda
import numpy as np
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from google.cloud import storage

FLAG_GPU = False
if FLAG_GPU:
	xp = cuda.cupy
	cuda.get_device(0).use()
else:
	xp = np


# データ変換クラスの定義
class DataConverter:
	def __init__(self):
		'''
		クラスの初期化
		'''
		# Instantiates a client
		self.client = language.LanguageServiceClient()
		# 単語辞書の登録
		self.vocab = {}
		# CloudStorageからvocabファイルをDownload
		txt = 'vocab.txt'
		storage_client = storage.Client()
		bucket = storage_client.get_bucket('ml-datas')
		blob = storage.Blob('att-seq2seq/' + txt, bucket)
		lines = blob.download_as_string().decode('utf-8').split('\n')
		for i, line in enumerate(lines):
			if line: # 空行を弾く
				self.vocab[line] = i

	def sentence2words(self, sentence):
		'''
		文章を単語の配列にして返却する
		:param sentence: 文章文字列
		'''
		# Natural Language API
		# The text to analyze
		document = types.Document(
			content=sentence,
			type=enums.Document.Type.PLAIN_TEXT
		)
		# Detects syntax in the document. You can also analyze HTML with:
		#   document.type == enums.Document.Type.HTML
		tokens = self.client.analyze_syntax(document).tokens

		sentence_words = []
		for token in tokens:
			w = token.text.content # 単語
			if len(w) == 0: # 不正文字は省略
				continue
			sentence_words.append(w)
		sentence_words.append("<eos>") # 最後にvocabに登録している<eos>を代入する
		return sentence_words

	def sentence2ids(self, sentence, sentence_type="query"):
		'''
		文章を単語IDのNumpy配列に変換して返却する
		:param sentence: 文章文字列
		:sentence_type: 学習用でミニバッチ対応のためのサイズ補填方向をクエリー・レスポンスで変更するため"query"or"response"を指定　
		:return: 単語IDのNumpy配列
		'''
		ids = [] # 単語IDに変換して格納する配列
		sentence_words = self.sentence2words(sentence) # 文章を単語に分解する
		for word in sentence_words:
			if word in self.vocab: # 単語辞書に存在する単語ならば、IDに変換する
				ids.append(self.vocab[word])
			else: # 単語辞書に存在しない単語ならば、<unk>に変換する
				ids.append(self.vocab["<unk>"])
		ids = xp.array([ids], dtype="int32")
		return ids

	def ids2words(self, ids):
		'''
		予測時に、単語IDのNumpy配列を単語に変換して返却する
		:param ids: 単語IDのNumpy配列
		:return: 単語の配列
		'''
		words = [] # 単語を格納する配列
		for i in ids: # 順番に単語IDを単語辞書から参照して単語に変換する
			words.append(list(self.vocab.keys())[list(self.vocab.values()).index(i)])
		return words
