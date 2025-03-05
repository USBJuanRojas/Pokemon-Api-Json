import requests
import json
import dash
import pandas as pd
import plotly.express as px
from dash import html, dcc
from pymongo import MongoClient

URI = "mongodb+srv://jrojasn:jrojasnusbjajaxd@cluster0.h9fcn.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
try:
    connection = MongoClient(URI)
except Exception as e:
    print("Error al conectarse a la base de datos:", e)

db = connection["Pokemon"]
collection = db["Equipo"]

pokemon_list = ["pikachu", "bulbasaur", "charmander", "squirtle", "mew"]

def obtenerDatos():
    documents = []
    
    for pokemon in pokemon_list:
        url = f"https://pokeapi.co/api/v2/pokemon/{pokemon}"
        data = requests.get(url).json()
        
        stats = data.get("stats", [])
        
        if not stats:
            print(f"No se encontraron datos para {pokemon}.")
            continue
        
        stat_names = [s["stat"]["name"] for s in stats]
        stat_values = [s["base_stat"] for s in stats]
        
        df = pd.DataFrame({"stat": stat_names, "value": stat_values, "pokemon": pokemon})
        documents.append({"name": pokemon, "stats": stats})
    
    if documents:
        existing_names = {doc["name"] for doc in collection.find({}, {"name": 1})}
        new_docs = [doc for doc in documents if doc["name"] not in existing_names]
        
        if new_docs:
            collection.insert_many(new_docs)
    
    return df

dataF = obtenerDatos()

app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Estadísticas de Pokémon"),
    dcc.Graph(
        id="grafico",
        figure=px.bar(dataF, x="stat", y="value", color="pokemon", title="Estadísticas Base de Pokémon")
    )
])

if __name__ == "__main__":
    app.run_server(debug=True)
