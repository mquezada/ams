from pathlib import Path
from sqlalchemy.orm import sessionmaker

import settings
from models import Cluster, DocumentCluster
'''
Insert a new cluster method in the DB
'''

def insert_clustering_db(clustering, n_clusters):
    cluster = Cluster(method = clustering, n_clusters = n_clusters)
    session.add(cluster)
    session.commit()
    print('Cluster insertado: {}'.format(cluster.id))
    # Inserta un nuevo tipo de clustering en la BD.
    return cluster.id


#Inserta los labels de cada cluster para un método de clustering dado.
def insert_labels_db(document_cluster):
    session.bulk_save_objects(document_cluster)
    session.commit()


if __name__ == '__main__':
    Session = sessionmaker(bind=settings.engine, expire_on_commit=False)
    session = Session()
    event_name = 'nepal_earthquake'
    clustering = 'Hierchical'
    path_file_cluster = Path(settings.LOCAL_DATA_DIR_2,'data',event_name,'clusters',clustering)
    files = [x.name for x in path_file_cluster.iterdir() if x.is_file() and x.suffix != '.pickle']
    docs = files[0]
    labels = files[3]
    tokens = labels.split('.')
    id_cluster = insert_clustering_db(tokens[2],tokens[3])
    path_labels = Path(path_file_cluster, labels)
    path_docs = Path(path_file_cluster, docs)
    docs_labels = []
    with path_labels.open() as file_1, path_docs.open() as file_2:
        for (doc, label) in zip(file_2, file_1):
            doc_id = doc.split('\t')[0]
            label = label.strip()
            doc_cluster = DocumentCluster(document_id = doc_id, cluster_id = id_cluster, label = label)
            docs_labels.append(doc_cluster)
            #docs_labels[tokens_docs[0]] = label.strip()
    insert_labels_db(docs_labels)