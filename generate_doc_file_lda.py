from collections import defaultdict
from pathlib import Path

from clustering import process_texts

event_name = 'oscar_pistorius'
texts, documents = process_texts(event_name)


def file_for_lda():
    path_docs = Path('data', event_name, 'docs')
    if not path_docs.exists():
        path_docs.mkdir()
    count = 0
    list_file = Path('data', event_name, 'docs', 'filelist_' + event_name + '.txt')
    with list_file.open('w') as list_file:
        for doc in documents:
            name = event_name + '_' + str(count) + '.txt'
            doc_file = Path('data', event_name, 'docs', name)
            with doc_file.open('w') as file:
                file.write(doc.url)
                file.close()
                count += 1
            list_file.write(name + '\n')
        list_file.close()


def format_files(n_topics, filename):
    path_files = Path('/home', 'luism', 'Universidad', 'ams', event_name, 'TextWithLabel_' + str(n_topics))
    files = [x for x in path_files.iterdir() if x.is_file()]
    labels_path = Path('data', event_name, 'clusters', 'LDA', filename)
    with labels_path.open('w') as labels:
        for file in files:
            with file.open('r') as f:
                line = f.readline()
                token = line.split('\t')[1]
                topic = token[2:token.index(':')]
                labels.write(topic + '\n')


# file_for_lda()
format_files(5, event_name + '.mat.clustering.5')
