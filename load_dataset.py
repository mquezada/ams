import pandas as pd
from pandas.core.frame import DataFrame
from pathlib import Path
import logging
from typing import Tuple, List

logger = logging.getLogger(__name__)


def load(name: str, dataset: List[int], engine, urls=True):
    query = "SELECT * from tweet where event_id_id in ({})"
    query = query.format(','.join(map(str, dataset)))

    df = pd.read_sql_query(query, engine)
    logger.info(f"Loaded df '{name}' of dim {df.shape}")

    if urls:

        urls_dir = Path('data', name, 'data', 'resolved_urls.txt')
        urls_df = pd.read_table(urls_dir.as_posix(), sep='\t')
        logger.info(f"Loaded urls df '{name}' of dim {urls_df.shape}")

        return df, urls_df

    else:

        return df

