# coding: utf-8

import os
import sys
import logging
import json
from datetime import datetime, timedelta

from linebot import LineBotApi, WebhookHandler
from linebot.models import (
    TextSendMessage,
)
from google.cloud import storage

from att_seq2seq.model import AttSeq2Seq
from att_seq2seq.decoder import Decoder
from converter import DataConverter


EMBED_SIZE = 100
HIDDEN_SIZE = 100
BATCH_SIZE = 20
BATCH_COL_SIZE = 15


line_bot_api = LineBotApi(os.environ["CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["CHANNEL_SECRET"])

# Instantiates a client
storage_client = storage.Client()


def create_decoder():
    data_converter = DataConverter()
    vocab_size = len(data_converter.vocab)
    model = AttSeq2Seq(
        vocab_size=vocab_size,
        embed_size=EMBED_SIZE,
        hidden_size=HIDDEN_SIZE,
        batch_col_size=BATCH_COL_SIZE,
    )
    # Download the model file from CloudStorage.
    npz = "80.npz"
    npz_path = "/tmp/" + npz
    # tmp comment
    if not os.path.isfile(npz_path):
        bucket = storage_client.get_bucket(
            os.environ["BUCKET_NAME"]
        )  # rootとなるbucketを指定
        blob = storage.Blob("att-seq2seq/v1/" + npz, bucket)  # rootから子を指定
        with open(npz_path, "wb") as file_obj:  # localに保存するファイルを指定
            blob.download_to_file(file_obj)
        return Decoder(model, data_converter, BATCH_COL_SIZE, npz_path)
    else:
        return Decoder(model, data_converter, BATCH_COL_SIZE, npz_path)


DECODER = create_decoder()


def parse_body(body):
    receive_json = json.loads(body)
    message = receive_json["events"][0]
    return message


def callback(request):
    try:
        # get X-Line-Signature header value
        signature = request.headers["X-Line-Signature"]
        # get request body as text
        body = request.get_data(as_text=True)
        print("Request body: " + body)
        receive_json = parse_body(body)
        query = receive_json["message"]["text"]
        response = DECODER(query)
        # handle webhook body
        line_bot_api.reply_message(
            receive_json["replyToken"], TextSendMessage(text=response)
        )
    except:
        logging.error(sys.exc_info())
        return "ERROR"
    return "OK"
