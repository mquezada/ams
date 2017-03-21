import pandas as pd
from pandas.core.frame import DataFrame
from pathlib import Path
import logging
from typing import Tuple
from sqlalchemy import create_engine


logger = logging.getLogger(__name__)


def load(name: str, engine) -> Tuple[DataFrame, DataFrame]:
    df = pd.read_sql_query("SELECT * from tweet", engine)
    logger.info(f"Loaded df '{name}' of dim {df.shape}")

    urls_dir = Path('data', name, 'urls.txt')
    urls_df = pd.read_table(urls_dir.as_posix(), sep=' ')
    logger.info(f"Loaded urls df '{name}' of dim {urls_df.shape}")

    return df, urls_df



