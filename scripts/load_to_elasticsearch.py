import pandas as pd
from elasticsearch import Elasticsearch
import json
import os

def load_to_elasticsearch():
    # Configurar conexión
    es = Elasticsearch(
        "http://localhost:9200",
        basic_auth=("elastic", "jS+4*01qAOxxXLqB10kp"),
        verify_certs=False
    )
    
    # Leer el CSV
    df = pd.read_csv('data/youtube-top-100-songs-2025.csv')
    
    # Limpiar y convertir datos
    df['view_count'] = pd.to_numeric(df['view_count'], errors='coerce').fillna(0).astype(int)
    df['duration'] = pd.to_numeric(df['duration'], errors='coerce').fillna(0).astype(int)
    df['channel_follower_count'] = pd.to_numeric(df['channel_follower_count'], errors='coerce').fillna(0).astype(int)
    
    # Indexar documentos
    for index, row in df.iterrows():
        doc = {
            'title': row['title'],
            'fulltitle': row['fulltitle'],
            'view_count': row['view_count'],
            'duration': row['duration'],
            'channel': row['channel'],
            'channel_follower_count': row['channel_follower_count'],
            'categories': row['categories']
        }
        
        es.index(index='youtube_songs', id=index, document=doc)
    
    print(f"Loaded {len(df)} documents to Elasticsearch")

if __name__ == "__main__":
    load_to_elasticsearch()