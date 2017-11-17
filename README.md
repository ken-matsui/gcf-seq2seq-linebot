# python_appengine-linebot

```
pip install flask
pip freeze > requirements.txt

gcloud app deploy
gcloud app deploy -v [vername]
gcloud app deploy -v att-seq2seq
```

```:app.yaml
runtime: python
env: flex
service: linebot
entrypoint: gunicorn -b :$PORT main:app

runtime_config:
  python_version: 3

env_variables:
  CHANNEL_ACCESS_TOKEN: 'YOUR_CHANNEL_ACCESS_TOKEN'
  CHANNEL_SECRET: 'YOUR_CHANNEL_SECRET'
```

standard環境では，app.yamlで，library sslが必要だったが，flexible環境では不要