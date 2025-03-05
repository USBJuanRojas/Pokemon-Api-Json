import requests
import json
import dash
import pandas as pd
import plotly.express as px
from dash import html, dcc
from pymongo import MongoClient

# Conexión a MongoDB
URI = "mongodb+srv://jrojasn:jrojasnusbjajaxd@cluster0.h9fcn.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
try:
    connection = MongoClient(URI)
except Exception as e:
    print("Error al conectarse a la base de datos:", e)

db = connection["Pokemon"]
collection = db["stats"]

# Lista de Pokémon a obtener
pokemon_list = ["pikachu", "bulbasaur", "charmander", "squirtle", "mew"]

def obtenerDatos():
    all_data = []  # Lista para almacenar datos de todos los Pokémon
    documents = []  # Lista para insertar en MongoDB
    
    for pokemon in pokemon_list:
        url = f"https://pokeapi.co/api/v2/pokemon/{pokemon}"
        data = requests.get(url).json()
        
        stats = data.get("stats", [])
        
        if not stats:
            print(f"No se encontraron datos para {pokemon}.")
            continue
        
        # Construimos la lista de estadísticas para el DataFrame
        for s in stats:
            all_data.append({
                "pokemon": pokemon,
                "stat": s["stat"]["name"],
                "value": s["base_stat"]
            })
        
        # Preparamos el documento para MongoDB
        documents.append({"name": pokemon, "stats": stats})
    
    # Insertar solo si hay nuevos documentos y evitar duplicados
    if documents:
        existing_names = {doc["name"] for doc in collection.find({}, {"name": 1})}
        new_docs = [doc for doc in documents if doc["name"] not in existing_names]
        
        if new_docs:
            collection.insert_many(new_docs)
    
    # Convertir la lista en un DataFrame de pandas
    df = pd.DataFrame(all_data)
    
    return df

# Obtener los datos
dataF = obtenerDatos()

# Creación de la aplicación Dash
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Estadísticas Base de Pokémon"),
    dcc.Graph(
        id="grafico",
        figure=px.bar(dataF, x="stat", y="value", color="pokemon", title="Estadísticas Base de Pokémon")
    )
])

if __name__ == "__main__":
    app.run_server(debug=True)
