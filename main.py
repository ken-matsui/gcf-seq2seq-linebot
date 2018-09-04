# coding: utf-8

import os
import sys
import logging
import json
from datetime import datetime, timedelta

from linebot import (
    LineBotApi, WebhookHandler
)
# from linebot.exceptions import (
#     InvalidSignatureError
# )
# from linebot.models import (
#     MessageEvent, TextMessage, TextSendMessage,
# )
from linebot.models import (
    TextSendMessage,
)
from google.cloud import datastore
from google.cloud import storage

from att_seq2seq.model import AttSeq2Seq
from att_seq2seq.decoder import Decoder
from converter import DataConverter


EMBED_SIZE = 100
HIDDEN_SIZE = 100
BATCH_SIZE = 20
BATCH_COL_SIZE = 15


line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])

# Instantiates a client
datastore_client = datastore.Client()
storage_client = storage.Client()


def create_decoder():
    data_converter = DataConverter()
    vocab_size = len(data_converter.vocab)
    model = AttSeq2Seq(vocab_size=vocab_size,
                       embed_size=EMBED_SIZE,
                       hidden_size=HIDDEN_SIZE,
                       batch_col_size=BATCH_COL_SIZE)
    # Download the model file from CloudStorage.
    npz = '80.npz'
    npz_path = '/tmp/' + npz
    # tmp comment
    if not os.path.isfile(npz_path):
        bucket = storage_client.get_bucket('model-files')  # rootとなるbucketを指定
        blob = storage.Blob('chainer/att-seq2seq/v1/' + npz, bucket)  # rootから子を指定
        with open(npz_path, 'wb') as file_obj:  # localに保存するファイルを指定
            blob.download_to_file(file_obj)
        return Decoder(model, data_converter, npz_path)
    else:
        return Decoder(model, data_converter, npz_path)


DECODER = create_decoder()


def store_data(timestamp, user, query, response):
    # The kind for the new entity
    kind = 'Talk'
    # The name/ID for the new entity
    time = datetime.fromtimestamp(timestamp)
    time += timedelta(hours=9)  # timezoneをJSTに調整
    name = str(time)
    # The Cloud Datastore key for the new entity
    talk_key = datastore_client.key(kind, name)
    # Prepares the new entity
    talk = datastore.Entity(key=talk_key)
    talk['1.TimeStamp'] = timestamp
    talk['2.User'] = user
    talk['3.Query'] = query
    talk['4.Response'] = response
    # Saves the entity
    datastore_client.put(talk)


def parse_body(body):
    receive_json = json.loads(body)
    message = receive_json['events'][0]
    return message


def callback(request):
    try:
        # get X-Line-Signature header value
        signature = request.headers['X-Line-Signature']
        # get request body as text
        body = request.get_data(as_text=True)
        print("Request body: " + body)
        receive_json = parse_body(body)
        query = receive_json['message']['text']
        response = DECODER(query)
        profile = line_bot_api.get_profile(receive_json['source']['userId'])
        timestamp = int(receive_json['timestamp']) // 1000
        store_data(timestamp, profile.display_name, query, response)
        # handle webhook body
        line_bot_api.reply_message(
            receive_json['replyToken'],
            TextSendMessage(text=response)
        )
    except:
        logging.error(sys.exc_info())
        return 'ERROR'
    return 'OK'
