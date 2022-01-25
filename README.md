# gcf_linebot

## Steps

1. Create a GCP project
2. Enable `Cloud Natural Language API`
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
