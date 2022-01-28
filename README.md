# matsukenbot

<a href="https://lin.ee/FPQ9DqS"><img src="https://scdn.line-apps.com/n/line_add_friends/btn/en.png" alt="Add friend" height="36" border="0"></a>

matsukenbot is a LINE bot implemented in seq2seq with attention.

## Steps

1. Create a GCP project
2. Deploy [`ken-matsui/cloud-run-mecab`](https://github.com/ken-matsui/cloud-run-mecab) to Cloud Run
3. Select `mecab-service` on [Cloud Run page](https://console.cloud.google.com/run), and click `Add principal`
4. Enter `${YOUR_PROJECT_ID}@appspot.gserviceaccount.com`, select `Cloud Run Invoker` (`roles/run.invoker`), and click `Save`
5. Create a bucket on Google Cloud Storage
6. Upload a `.npz` file and `vocab.txt` to the bucket
7. Deploy to Cloud Functions
```bash
gcloud functions deploy line-bot --region us-west1 --trigger-http --runtime python39 --allow-unauthenticated --env-vars-file .env.yaml --entry-point callback
```
6. Set the Webhook URL on https://manager.line.biz/account/@YOUR_ID/setting/messaging-api

### Environment Variables

* `BUCKET_NAME`: Name of a bucket created on the step 5
* `CHANNEL_ACCESS_TOKEN`
* `CHANNEL_SECRET`
* `MECAB_SERVICE_DOMAIN`: Copy the domain from the step 2 without protocol and two slashes like `https://`
