import numpy as np
from chainer import serializers

FLAG_GPU = False
if FLAG_GPU:
    xp = cuda.cupy
    cuda.get_device_from_id(0).use()
else:
    xp = np


class Decoder(object):
    def __init__(self, model, data_converter, decode_max_size, npz):
        self.model = model
        self.data_converter = data_converter
        self.decode_max_size = decode_max_size
        serializers.load_npz(npz, self.model)

    def __call__(self, query):
        # モデルの勾配などをリセット
        self.model.reset()
        # userからの入力文をIDに変換
        enc_query = self.data_converter.sentence2ids(query)
        enc_query = enc_query.T
        # エンコード時のバッチサイズ
        encode_batch_size = len(enc_query[0])
        # エンコードの計算
        self.model.encode(enc_query, encode_batch_size)
        # <eos>をデコーダーに読み込ませる
        t = xp.array([0] * encode_batch_size, dtype="int32")
        # デコーダーが生成する単語IDリスト
        ys = []
        for i in range(self.decode_max_size):
            y = self.model.decode(t)
            y = xp.argmax(y.data)  # 確率で出力されたままなので、確率が高い予測単語を取得する
            ys.append(y)
            t = xp.array([y], dtype="int32")
            if y == 0:  # <EOS>を出力したならばデコードを終了する
                break
        # IDから，文字列に変換する
        response = self.data_converter.ids2words(ys)

        if "<eos>" in response:  # 最後の<eos>を回避
            res = "".join(response[0:-1])
        else:  # 含んでない時もある．(出力wordサイズが，15を超えた時？？？)
            res = "".join(response)
        return res
