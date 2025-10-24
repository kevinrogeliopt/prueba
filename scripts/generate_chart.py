from elasticsearch import Elasticsearch
import pandas as pd
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv

def generate_top_songs_chart():
    # Cargar variables de entorno
    load_dotenv()
    
    # Conexión a Elasticsearch Cloud
    es = Elasticsearch(
        cloud_id=os.getenv('ELASTIC_CLOUD_ID'),
        basic_auth=(
            os.getenv('ELASTIC_USERNAME'),
            os.getenv('ELASTIC_PASSWORD')
        )
    )
    
    # Verificar conexión
    if not es.ping():
        print("Error al conectar con Elasticsearch Cloud")
        return
    
    # Consulta para top 10 canciones por views
    query = {
        "size": 0,
        "aggs": {
            "top_songs": {
                "terms": {
                    "field": "title.keyword",
                    "size": 10,
                    "order": {"max_views": "desc"}
                },
                "aggs": {
                    "max_views": {"max": {"field": "view_count"}}
                }
            }
        }
    }
    
    response = es.search(index="youtube_songs", body=query)
    
    # Procesar resultados
    buckets = response['aggregations']['top_songs']['buckets']
    
    songs = []
    views = []
    
    for bucket in buckets:
        songs.append(bucket['key'])
        views.append(bucket['max_views']['value'])
    
    # Crear DataFrame
    df = pd.DataFrame({
        'song': songs,
        'views': views
    })
    
    # Generar gráfico
    plt.figure(figsize=(12, 8))
    bars = plt.barh(df['song'], df['views'], color='skyblue')
    plt.xlabel('Vistas')
    plt.title('Top 10 Canciones de YouTube 2025 por Vistas')
    plt.gca().invert_yaxis()
    
    # Añadir etiquetas de valores
    for bar, value in zip(bars, df['views']):
        plt.text(bar.get_width() + bar.get_width() * 0.01, 
                bar.get_y() + bar.get_height()/2, 
                f'{value:,}', 
                ha='left', va='center', fontsize=9)
    
    plt.tight_layout()
    
    # Guardar gráfico
    if not os.path.exists('docs'):
        os.makedirs('docs')
    
    plt.savefig('docs/top_songs_chart.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Generar HTML para GitHub Pages
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Top 10 Canciones YouTube 2025</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .chart-container {{ text-align: center; }}
            .data-table {{ margin: 20px auto; border-collapse: collapse; width: 80%; }}
            .data-table th, .data-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            .data-table th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <h1>Top 10 Canciones de YouTube 2025</h1>
        <div class="chart-container">
            <img src="top_songs_chart.png" alt="Top 10 Songs Chart" style="max-width: 100%; height: auto;">
        </div>
        <table class="data-table">
            <tr>
                <th>Posición</th>
                <th>Canción</th>
                <th>Vistas</th>
            </tr>
            {"".join([f'<tr><td>{i+1}</td><td>{row["song"]}</td><td>{row["views"]:,}</td></tr>' 
                     for i, row in df.iterrows()])}
        </table>
        <p><em>Última actualización: {pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")}</em></p>
    </body>
    </html>
    """
    
    with open('docs/index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("Chart and HTML generated successfully from Elasticsearch Cloud!")

if __name__ == "__main__":
    generate_top_songs_chart()