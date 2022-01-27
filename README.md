# matsukenbot

<a href="https://lin.ee/FPQ9DqS"><img src="https://scdn.line-apps.com/n/line_add_friends/btn/en.png" alt="Add friend" height="36" border="0"></a>

matsukenbot is a LINE bot implemented in seq2seq with attention.

## Steps

1. Create a GCP project
2. Deploy [`ken-matsui/cloud-run-mecab`](https://github.com/ken-matsui/cloud-run-mecab) to Cloud Run
3. Create a bucket on Google Cloud Storage
4. Upload a `.npz` file and `vocab.txt` to the bucket
5. Deploy to Cloud Functions
```bash
gcloud functions deploy line-bot --region us-west1 --trigger-http --runtime python39 --allow-unauthenticated --env-vars-file .env.yaml --entry-point callback
```
6. Set the Webhook URL on https://manager.line.biz/account/@YOUR_ID/setting/messaging-api

### Environment Variables

* `BUCKET_NAME`
* `CHANNEL_ACCESS_TOKEN`
* `CHANNEL_SECRET`
* `MECAB_SERVICE_DOMAIN`: Copy the domain from the step 2 without protocol and two slashes like `https://`
