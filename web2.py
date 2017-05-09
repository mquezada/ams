from flask import Flask, render_template
from sqlalchemy.orm import sessionmaker
import logging

from models import *
from settings import engine

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s | %(levelname)s : %(message)s', level=logging.INFO)

app = Flask(__name__)
app.url_map.strict_slashes = False


@app.route('/<event_name>/documents/')
def documents(event_name):
