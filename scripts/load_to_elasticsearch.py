import pandas as pd
from elasticsearch import Elasticsearch
import json
import os
from dotenv import load_dotenv

def load_to_elasticsearch():
    # Cargar variables de entorno
    load_dotenv()
    
    # Configurar conexión a Elasticsearch Cloud
    es = Elasticsearch(
        cloud_id=os.getenv('ELASTIC_CLOUD_ID'),
        basic_auth=(
            os.getenv('ELASTIC_USERNAME'),
            os.getenv('ELASTIC_PASSWORD')
        )
    )
    
    # Verificar conexión
    if es.ping():
        print("Conexión exitosa a Elasticsearch Cloud")
    else:
        print("Error al conectar con Elasticsearch Cloud")
        return
    
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
    
    print(f"Loaded {len(df)} documents to Elasticsearch Cloud")

if __name__ == "__main__":
    load_to_elasticsearch()