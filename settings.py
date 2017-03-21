from sqlalchemy import create_engine
from pathlib import Path


engine = create_engine('mysql://root@127.0.0.1/ams')
engine_m3 = create_engine('mysql://mquezada:phoophoh7ahdaiJahphoh3aicooz7uka3ahJe9oi@127.0.0.1/mquezada_db')


DATA_DIR = Path('data')