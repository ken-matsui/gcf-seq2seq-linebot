# coding: utf-8

import os
import glob
from datetime import datetime, timedelta

from flask import Flask, request, abort
from linebot import (
	LineBotApi, WebhookHandler
)
from linebot.exceptions import (
	InvalidSignatureError
)
from linebot.models import (
	MessageEvent, TextMessage, TextSendMessage,
)
from google.cloud import datastore

from att_seq2seq.model import AttSeq2Seq
from att_seq2seq.decoder import Decoder
from data_utils.converter import DataConverter


EMBED_SIZE = 100
HIDDEN_SIZE = 100
BATCH_SIZE = 20
BATCH_COL_SIZE = 15
DATA_PATH = './data/'
TRAIN_PATH = './train/'

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])

# Instantiates a client
datastore_client = datastore.Client()

data_converter = DataConverter(DATA_PATH)
vocab_size = len(data_converter.vocab)
model = AttSeq2Seq(vocab_size=vocab_size,
				   embed_size=EMBED_SIZE,
				   hidden_size=HIDDEN_SIZE,
				   batch_col_size=BATCH_COL_SIZE)
# 最新のモデルデータを使用する．
# lst = glob.glob(TRAIN_PATH + "*.npz")
# npz = max(list(map(lambda s: int(s.replace(TRAIN_PATH, "").replace(".npz", "")), lst)))
# npz = TRAIN_PATH + str(npz) + ".npz"
npz = TRAIN_PATH + '60.npz'
decoder = Decoder(model, data_converter, npz)


@app.route("/callback", methods=['POST'])
def callback():
	# get X-Line-Signature header value
	signature = request.headers['X-Line-Signature']

	# get request body as text
	body = request.get_data(as_text=True)
	app.logger.info("Request body: " + body)

	# handle webhook body
	try:
		handler.handle(body, signature)
	except InvalidSignatureError:
		abort(400)

	return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
	query = event.message.text
	response = decoder(event.message.text)
	profile = line_bot_api.get_profile(event.source.user_id)
	store_data(event.timestamp, profile.display_name, query, response)

	line_bot_api.reply_message(
		event.reply_token,
		TextSendMessage(text=response)
	)

def store_data(timestamp, user, query, response):
	# The kind for the new entity
	kind = 'Talk'
	# The name/ID for the new entity
	time = datetime.fromtimestamp(timestamp//1000)
	time += timedelta(hours=9) # timezoneをJSTに調整
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


if __name__ == "__main__":
	app.run()