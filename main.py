from flask import Flask, render_template
import requests
from flask import Flask
from flask_caching import Cache
from celery_client import make_celery

config ={
    "DEBUG": False, # some Flask specific configs
    "CACHE_TYPE": "FileSystemCache", # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300,
    "CACHE_DIR":"cache"
}


resourse_url ="https://jsonplaceholder.typicode.com/posts"

app = Flask(__name__)

app.config.update(CELERY_CONFIG={
    'broker_url':'amqp://guest:guest@localhost:5672',
    'result_backend':'db+sqlite:///db.db',
})

app.config.from_mapping(config)
cache = Cache(app)
celery = make_celery(app)

@celery.task(name="Задача")
def hard_task(word):
    with open(f'{word}.txt','w') as f:
        for i in range(100):
            f.write(word+'\n')
    return 'Success'

@app.route('/<word>')
def word_works(word):
    hard_task.delay(word)
    return 'Confirmed'

@app.route("/")
@cache.cached(timeout=60*60*12)
def hello_world():
    posts = requests.get(resourse_url).json()
    return render_template("index.html",posts=posts)

if __name__ == "__main__":
    app.run()
