
import pandas as pd 
from dash import Dash, html, dcc, Input, Output,dash_table,State
from django_plotly_dash import DjangoDash
import numpy as np 
from elasticsearch import Elasticsearch
import plotly.graph_objects as go 
import plotly.express as px
import os
from dotenv import load_dotenv
from dotenv import dotenv_values
from src.app_dash.module.templateGraphPlotly import *
from src.app_dash.module.connectionDB import *
from shapely import wkt
from shapely.geometry import Point
import geopandas as gpd
import textwrap
load_dotenv()
config = dotenv_values(".env")


#### TEMPLATES ####
color_kvk ="#ec4899"
color_background="#e2e8f0"
color_background_bg_plot = "rgba(255,255,255,1)"
color_background_plot = "#ffffff"
color_text  = "#475569"
color_plot = "#475569"



external_stylesheets = ['https://cdn.jsdelivr.net/npm/tailwindcss/dist/tailwind.min.css',
                        'https://cdn.jsdelivr.net/npm/font-awesome@4.7.0/css/font-awesome.min.css'
                    ]
className={
    "graph":"shadow-lg shadow-indigo-500 rounded-xl bg-white my-1 p-1 md:my-2 md:p-2 mx-1  w-full xl:w-6/12 w-max-full",
    "graph-1/3":"shadow-lg shadow-indigo-500 rounded-xl bg-white my-1 p-1 md:my-2 md:p-2 mx-1  w-full lg:w-4/12",
    "graph-full":"shadow-lg shadow-indigo-500 rounded-xl bg-white sm:m-1 sm:p-1 md:m-2 md:p-2 w-full",
    "graph-xl":"shadow-lg shadow-indigo-500 rounded-xl bg-white sm:m-1 sm:p-1 md:m-2 md:p-2 w-full",
    "tab_class":"bg-blue-300 border-t-0 p-3 m-2 font-semibold border-0",
    "tab_selected":"bg-white p-3 m-2 font-semibold border-0",
}
styles={
        "tab_class":{"border":"none",
                 "background":"#3b82f6",
                 "color":"#f9fafb",
                 "font-weight":"600","padding":"1em",
                 "margin":"1em",
                 "border-radius":"0.5em",
                 "max-width":"100%",
                 "box-shadow":"0 16px 26px -10px rgba(63,106,216,.56), 0 4px 25px 0 rgba(0,0,0,.12), 0 8px 10px -5px rgba(63,106,216,.2)"},
    "tab_selected":{"border":"none",
                    "max-width":"100%",
                    "background":"#93c5fd",
                    "padding":"1em",
                    "margin":"1em",
                    "border-radius":"0.5em","color":"#f9fafb","font-weight":"600",
                     "box-shadow":"0 16px 26px -10px rgba(63,106,216,.56), 0 4px 25px 0 rgba(0,0,0,.12), 0 8px 10px -5px rgba(63,106,216,.2)"}


}
password = os.getenv("password")
user = os.getenv("user")
host = os.getenv("host")
port = os.getenv("port")
db = os.getenv("db")
db_ =ConnectionMySQL(host,port,user,password,db).get_connection()

auth = (os.getenv("user_elastic"), os.getenv("password_elastic"))

# Create the Elasticsearch client with authentication
es = Elasticsearch(
    [{'host': host, 'port': os.getenv(os.getenv("user_elastic")), 'scheme': 'http'}],
    http_auth=auth
)
index="immobilier"


def get_geojson_file(region_name=None,dep_name=None,detail=None):
    db_ =ConnectionMySQL(host,port,user,password,db).get_connection()
    req_dep = f'SELECT * FROM geo_json_cities WHERE region_name = "{region_name}" AND dep_name ="{dep_name}"'
    req_reg = f'SELECT * FROM geo_json_cities WHERE  region_name ="{region_name}"'
    if detail == None:
        if dep_name and region_name : 
            df = pd.read_sql_query(req_dep,db_)
            df['geometry'] = df['geometry'].apply(lambda x: wkt.loads(x))
            geo = gpd.GeoDataFrame(df, geometry='geometry')
      
        elif region_name: 
            df=pd.read_sql_query(f"SELECT * FROM geo_json_dep",db_)
            df['geometry'] = df['geometry'].apply(lambda x: wkt.loads(x))
            geo = gpd.GeoDataFrame(df, geometry='geometry')
        else:
            df=pd.read_sql_query(f"SELECT * FROM geo_json_reg",db_)
            df['geometry'] = df['geometry'].apply(lambda x: wkt.loads(x))
            geo = gpd.GeoDataFrame(df, geometry='geometry')
    else:
        if detail == "dep_name":
            df=pd.read_sql_query(f"SELECT * FROM geo_json_dep",db_)
            df['geometry'] = df['geometry'].apply(lambda x: wkt.loads(x))
            geo = gpd.GeoDataFrame(df, geometry='geometry')
        elif detail =="nom_commune":
            if dep_name and region_name:
                df = pd.read_sql_query(req_dep,db_)
            else:
                df = pd.read_sql_query(req_reg,db_)
            df['geometry'] = df['geometry'].apply(lambda x: wkt.loads(x))
            geo = gpd.GeoDataFrame(df, geometry='geometry')
            
        
        else:
            df=pd.read_sql_query(f"SELECT * FROM geo_json_reg",db_)
            df['geometry'] = df['geometry'].apply(lambda x: wkt.loads(x))
            geo = gpd.GeoDataFrame(df, geometry='geometry')

    return geo
    
    

def get_templates(fig):
    style_graph=TemplateGraphPlotly(fig=fig,
    family_font = "Arial Black",tickangle = 0,paper_bgcolor = color_background_bg_plot ,
    plot_bg_color=color_background_plot,color = color_text,size=12,linewidth=2,linecolor = "black",color_plot=color_plot)
    fig.update_annotations(font_size=12)
    style_graph.get_template_axes()
    style_graph.get_template_layout()
    try:
        fig.update_traces(line=dict(width=4))
    except:
        pass
    fig.update_yaxes(title="")
    fig.update_xaxes(title="")


    fig.update_xaxes(tickangle=45)
    return style_graph


app = DjangoDash(name ='app_cities',external_stylesheets=external_stylesheets)



def get_query(year,region_name=None,dep_name=None,cities_name=None):
    query = {
        "size": 10000,
        "_source": ["prix_m2", "year", "surface_reelle_bati","month_name","location","valeur_fonciere","adresse_complete"],
        "query": {
            "bool": {
                "filter": [
                   
                ]
            }
        }
    }
    if year:
        query["query"]["bool"]["filter"].append({"term": {"year": year}})
        if region_name is not None:
            query["query"]["bool"]["filter"].append({"term": {"region_name.keyword": region_name}})
        if dep_name is not None:
            query["query"]["bool"]["filter"].append({"term": {"dep_name.keyword": dep_name}})
            if cities_name is not None:
                query["query"]["bool"]["filter"].append({"term": {"nom_commune.keyword": cities_name}})
            

    results = es.search(index=index, body=query, scroll="1m")
    scroll_id = results['_scroll_id']
    total_hits = results['hits']['total']['value']
    hits = results['hits']['hits']

    # Liste pour stocker les documents
    documents = []

    # Récupération des documents initiaux
    for hit in hits:
        documents.append(hit['_source'])
    
    # Pagination et récupération des documents suivants
    while len(documents) < min(total_hits, 50000):
        results = es.scroll(scroll_id=scroll_id, scroll="1m")
        scroll_id = results['_scroll_id']
        hits = results['hits']['hits']
        for hit in hits:
            documents.append(hit['_source'])
       
        
               
            
    

# Création du DataFrame

    df= pd.DataFrame(documents)

    df["latitude"]= df.location.apply(lambda x:x.get("lat"))
    df["longitude"]= df.location.apply(lambda x:x.get("lon"))

    return df 

def get_query_agg(year,region_name,dep_name,cities_name):
    query = {
         "size":0,
        "query": {
           
            "bool": {
                "filter": [        
                ]
            }
        },
        "aggs": {
            "annee_agg": {
                "terms": {
                    "field": "year",
                    "size": 10000
                },
                "aggs": {
                    "prix_m2_moyen": {
                        "avg": {
                            "field": "prix_m2"
                        }
                    },
                    "prix_m2_median": {
                        "percentiles": {
                            "field": "prix_m2",
                            "percents": [50]
                        }
                    },
                    "valeur_fonciere_moyenne": {
                        "avg": {
                            "field": "valeur_fonciere"
                        }
                    },
                    "valeur_fonciere_mediane": {
                        "percentiles": {
                            "field": "valeur_fonciere",
                            "percents": [50]
                        }
                    },
                    "nombre_transactions": {
                        "value_count": {
                            "field": "valeur_fonciere"
                        }
                    },
                    "volume_transactions": {
                        "sum": {
                            "field": "valeur_fonciere"
                        }
                    }
                }
            }
        }
    }
    if year:
        query["query"]["bool"]["filter"].append({"term": {"year": year}})
        if region_name is not None:
            query["query"]["bool"]["filter"].append({"term": {"region_name.keyword": region_name}})
            if dep_name is not None:
                query["query"]["bool"]["filter"].append({"term": {"dep_name.keyword": dep_name}})
                if cities_name is not None:
                    query["query"]["bool"]["filter"].append({"term": {"nom_commune.keyword": cities_name}})
            
    response = es.search(index=index, body=query)
    df=pd.DataFrame(response["aggregations"].get("annee_agg").get("buckets"))
    for col in df.columns:
        if col != "key" or col!="doc_count":
            try:
                if "_median" in col:
                     df[col]=df[col].apply(lambda x:x.get("values").get("50.0"))
                else:
                    df[col]=df[col].apply(lambda x:x.get("value"))
            except Exception as e:
                pass
    return df

def get_query_map_view(year, region_name=None, dep_name=None,detail=None,value_to_see=None):
    if value_to_see in ["nombre_transactions","volume_transactions"]:
            field="valeur_fonciere"
            if value_to_see == "nombre_transactions":
                aggregat ="value_count"
               
            else:
                aggregat="sum"
    else:
        aggregat="avg"
        field = value_to_see
    query = {
        "_source": ["prix_m2", "year","nom_commune"],
        "aggs": {
            "value_agg": {
                
                
                "aggs": {
                    "agg_col": {
                        aggregat: {
                            "field": field
                        }
                    }
                },
        }
        },
        "size": 0, 
        "query": {
            "bool": {
                "filter": []
            }
        }
    }

    if year:
        query["query"]["bool"]["filter"].append({"term": {"year": year}})
        if detail:
            query["aggs"]["value_agg"].update({"terms":{"field":f"{detail}.keyword","size":"100"}})
        else:
            query["aggs"]["value_agg"].update({"terms":{"field":"region_name.keyword","size":"100"}})
        
        
        if region_name and dep_name is None:
            query["query"]["bool"]["filter"].append({"term": {f"region_name.keyword": region_name}})
            if detail:

                query["aggs"]["value_agg"].update({"terms":{"field":f"{detail}.keyword","size":"20000"}})
            else:
    
                query["aggs"]["value_agg"].update({"terms":{"field":"dep_name.keyword","size":"100"}})
                
        elif dep_name:
        
            query["query"]["bool"]["filter"].append({"term": {"dep_name.keyword": dep_name}})
            query["aggs"]["value_agg"].update({"terms":{"field":"nom_commune.keyword","size":"20000"}})
   

    
    results = es.search(index=index, body=query)
  
    data = []

    for bucket in results["aggregations"]["value_agg"]["buckets"]:
        value = bucket["key"]
        avg_price = bucket["agg_col"]["value"]
        data.append({"value_agg": value, "agg_col": avg_price})



    df = pd.DataFrame(data)

    return df

### Récupération agg ####
def get_data_agg_by_local_by_year(region_name, dep_name,cities_name):
    query = {
    "size": 0,
    "query": {
        "bool": {
            "filter": []
        }
    },
    "aggs": {
        "annee_agg": {
            "terms": {
                "field": "year",
                "size": 10000
            },
            "aggs": {
                "type_local_agg": {
                    "terms": {
                        "field": "type_local.keyword",
                        "size": 10000
                    },
                    "aggs": {
                        "prix_m2_moyen": {
                            "avg": {
                                "field": "prix_m2"
                            }
                        },
                        "prix_m2_median": {
                            "percentiles": {
                                "field": "prix_m2",
                                "percents": [50]
                            }
                        },
                        "valeur_fonciere_moyenne": {
                            "avg": {
                                "field": "valeur_fonciere"
                            }
                        },
                        "valeur_fonciere_mediane": {
                            "percentiles": {
                                "field": "valeur_fonciere",
                                "percents": [50]
                            }
                        },
                        "nombre_transactions": {
                            "value_count": {
                                "field": "valeur_fonciere"
                            }
                        },
                        "volume_transactions": {
                            "sum": {
                                "field": "valeur_fonciere"
                            }
                        }
                    }
                }
            }
        }
    }
}


    if region_name is not None:
        query["query"]["bool"]["filter"].append({"term": {"region_name.keyword": region_name}})
    
        if dep_name is not None:
            query["query"]["bool"]["filter"].append({"term": {"dep_name.keyword": dep_name}})
            if cities_name is not None:
                query["query"]["bool"]["filter"].append({"term": {"nom_commune.keyword": cities_name}})
    
    
    response = es.search(index=index, body=query)
    #return response
    data=[]
    for i in response.get("aggregations").get("annee_agg").get("buckets"):
        i.get("type_local_agg").get("buckets")[0].update({"year":i.get("key")})
        i.get("type_local_agg").get("buckets")[1].update({"year":i.get("key")})
        data.append(i.get("type_local_agg").get("buckets")[0])
        data.append(i.get("type_local_agg").get("buckets")[1])
    
    df = pd.DataFrame(data)
    
    for col in df.columns:
        if col != "key" or col!="doc_count":
            try:
                if "_median" in col:
                     df[col]=df[col].apply(lambda x:x.get("values").get("50.0"))
                else:
                    df[col]=df[col].apply(lambda x:x.get("value"))
            except:
                pass
    return df

def get_data_per_year_per_month(region_name, dep_name,cities_name):
    query = {
    "size": 0,
    "query": {
        "bool": {
            "filter": []
        }
    },
    "aggs": {
        "annee_agg": {
            "terms": {
                "field": "year",
                "size": 10000
            },
            "aggs": {
                "mois_agg": {
                    "terms": {
                        "field": "month_name.keyword",
                        "size": 12
                    },
                    "aggs": {
                        "type_local_agg": {
                            "terms": {
                                "field": "type_local.keyword",
                                "size": 10000
                            },
                            "aggs": {
                                "prix_m2_moyen": {
                                    "avg": {
                                        "field": "prix_m2"
                                    }
                                },
                                "prix_m2_median": {
                                    "percentiles": {
                                        "field": "prix_m2",
                                        "percents": [50]
                                    }
                                },
                                "valeur_fonciere_moyenne": {
                                    "avg": {
                                        "field": "valeur_fonciere"
                                    }
                                },
                                "valeur_fonciere_mediane": {
                                    "percentiles": {
                                        "field": "valeur_fonciere",
                                        "percents": [50]
                                    }
                                },
                                "nombre_transactions": {
                                    "value_count": {
                                        "field": "valeur_fonciere"
                                    }
                                },
                                "volume_transactions": {
                                    "sum": {
                                        "field": "valeur_fonciere"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
    if region_name is not None:
        query["query"]["bool"]["filter"].append({"term": {"region_name.keyword": region_name}})
    
        if dep_name is not None:
            query["query"]["bool"]["filter"].append({"term": {"dep_name.keyword": dep_name}})
            if cities_name is not None:
                query["query"]["bool"]["filter"].append({"term": {"nom_commune.keyword": cities_name}})
    
    
    response = es.search(index=index, body=query)
    
    data = []
    buckets = response['aggregations']['annee_agg']['buckets']

    for year_bucket in buckets:
        year = year_bucket['key']
        mois_buckets = year_bucket['mois_agg']['buckets']

        for mois_bucket in mois_buckets:
            month = mois_bucket['key']
            type_local_buckets = mois_bucket['type_local_agg']['buckets']

            for type_local_bucket in type_local_buckets:
                type_local = type_local_bucket['key']
                prix_m2_moyen = type_local_bucket['prix_m2_moyen']['value']
                valeur_fonciere_moyenne = type_local_bucket['valeur_fonciere_moyenne']['value']
                valeur_fonciere_mediane = type_local_bucket['valeur_fonciere_mediane']['values']['50.0']
                volume_transactions = type_local_bucket['volume_transactions']['value']
                prix_m2_median = type_local_bucket['prix_m2_median']['values']['50.0']
                nombre_transactions = type_local_bucket['nombre_transactions']['value']

                data.append([year, month, type_local, prix_m2_moyen, valeur_fonciere_moyenne, valeur_fonciere_mediane, volume_transactions, prix_m2_median, nombre_transactions])

    df = pd.DataFrame(data, columns=['year', 'month', 'type_local', 'prix_m2_moyen', 
                                     'valeur_fonciere_moyenne', 'valeur_fonciere_mediane', 
                                     'volume_transactions', 'prix_m2_median', 'nombre_transactions'])
    return df
#### RECUPERATION DES FILTRES #### 
def get_region_name():
    query={
    "size": 0,
    "aggs": {
        "regions": {
        "terms": {
            "field": "region_name.keyword",
            "size": 30
        }
        }
    }
        }


    results = es.search(index=index, body=query)

    r  = (results.get("aggregations").get("regions").get("buckets"))


    data=[]

    for data_ in r:
        data.append(data_["key"])
    
        
    return pd.DataFrame(data).rename(columns={0:"region_name"}).region_name.to_list()
region_name = get_region_name()
@app.callback(Output("dep_name","options"),[Input("region_name","value")])
def get_dep_name(region_name):
    query={
            "query": {
                "term": {
                "region_name.keyword": {
                    "value": region_name
                }
                }
            },
            "size": 0,
            "aggs": {
                "departements": {
                "terms": {
                    "field": "dep_name.keyword",
                    "size": 20
                }
                }
            }
            }
    results = es.search(index=index, body=query)

    r  = results.get("aggregations").get("departements").get("buckets")
    data=[]

    for data_ in r:
        data.append(data_["key"])
    
    dep_name =  pd.DataFrame(data).rename(columns={0:"dep_name"}).dep_name.to_list()
    return [{"label":dep, "value":dep} for dep in sorted(dep_name)]

@app.callback(Output("cities_name","options"),[Input("dep_name","value")])

def get_cities_name(dep_name):
    query={
            "query": {
                "term": {
                "dep_name.keyword": {
                    "value": dep_name
                }
                }
            },
            "size": 0,
            "aggs": {
                "cities": {
                "terms": {
                    "field": "nom_commune.keyword",
                    "size": 10000
                }
                }
            }
            }
    results = es.search(index=index, body=query)

    r  = results.get("aggregations").get("cities").get("buckets")
    data=[]

    for data_ in r:
        data.append(data_["key"])
    
    cities_name =  pd.DataFrame(data).rename(columns={0:"cities"}).cities.to_list()
    return [{"label":cities, "value":cities} for cities in sorted(cities_name)]

@app.callback(Output("street","options"),[Input("cities_name","value")])
def get_street_name(cities_name):
    query={
            "query": {
                "term": {
                "nom_commune.keyword": {
                    "value": cities_name
                }
                }
            },
            "size": 0,
            "aggs": {
                "street": {
                "terms": {
                    "field": "adresse_nom_voie.keyword",
                    "size": 10000
                }
                }
            }
            }
    results = es.search(index=index, body=query)

    r  = results.get("aggregations").get("street").get("buckets")
    data=[]

    for data_ in r:
        data.append(data_["key"])
    
    streets=  pd.DataFrame(data).rename(columns={0:"street"}).street.to_list()
    return [{"label":street, "value":street} for street in sorted(streets)]

@app.callback(Output("key_number","children"),[Input("year","value"),Input("region_name","value"),Input("dep_name","value"),Input("cities_name","value")])
def get_key_number(year,region_name,dep_name,cities_name) :
    df = get_query_agg(year,region_name,dep_name,cities_name)
    data=[]
    cols=["prix_m2_moyen","valeur_fonciere_moyenne","nombre_transactions","volume_transactions"]
    liste_title={
        "prix_m2_moyen":"Moyenne du Prix au m² en €",
        "valeur_fonciere_moyenne":"Moyenne de la valeur foncière en €",
        "nombre_transactions":"Nombre de Transaction",
        "volume_transactions":"Volume de Transaction en €"

        

    }
    for col in cols:
            if col != "nombre_transactions":
                sym=" €"
            else:
                sym=""
            data.append(html.Div(id="metric",children=[
                html.Div(children=[
                    html.H3(children=liste_title.get(col),className="font-semibold text-2xl text-gray-700 p-3 m-2"),
                    html.P(children='{:,.0f}'.format(df[col][0]).replace(","," ")+sym,className="font-semibold text-xl text-gray-700 p-3 m-2")
            ])
            ],className="flex flex-col p-3 m-2 bg-white shadow-xl rounded-2xl w-full justify-center items-center")
            )

    return data
@app.callback(Output("graph_evol_number","children"),[Input("region_name","value"),Input("dep_name","value"),Input("cities_name","value"),Input("control","value"),
                                                      Input("control_type","value"),Input("group_type","value"),Input("value_step","value")])
def get_graph_evol(region_name,dep_name,cities_name,control,control_type,group_type,value_step):
    df = get_data_per_year_per_month(region_name, dep_name,cities_name)
    df["month_year"] = df["year"].astype(str) + "-" + df["month"]
    df["num_mois"]=pd.to_datetime(df.month, format='%B').dt.month
    
    df=df.sort_values(by=["year","num_mois"])
    df.year = pd.to_datetime(df.year,format="%Y")
    df.year = df.year.dt.year
    if region_name is None:
            region_name=""
    if dep_name is None:
            dep_name=""
    if cities_name is None:
            cities_name = ""

    aggregat = control
    if len(control_type)%2==0:

        keys = df['type_local'].unique()
    else:
        keys=control_type

    color=["#bfdbfe","#3b82f6","#fecaca","#ef4444"]
    liste_fig=[]

    # choix des colonnes pour le graphiques 
   
    if "median" in aggregat and "mean" in aggregat:
         cols=[["prix_m2_moyen","prix_m2_median"],["valeur_fonciere_moyenne","valeur_fonciere_mediane"]]
    else:
        if "median" in aggregat:
            cols =["prix_m2_median","valeur_fonciere_mediane"]
        elif "mean" in aggregat:
            cols=["prix_m2_moyen","valeur_fonciere_moyenne"]
        else:
             cols=[["prix_m2_moyen","prix_m2_median"],["valeur_fonciere_moyenne","valeur_fonciere_mediane"]]
    

    # filtrage 
    if len(aggregat) ==1:
        if group_type != "year":
            # si/ sinon Appartement ou Maison sont choisis
            df = df.sort_values(by=["type_local","year","num_mois"])
            if len(control_type) > 0:
                df =df.groupby(["year","month_year","num_mois","type_local"]).agg(aggregat[0],numeric_only=True).reset_index()
                df = df.sort_values(by=["type_local","year","num_mois","month_year"])
            else:
                df =df.groupby(["year","month_year","num_mois"]).agg(aggregat[0],numeric_only=True).reset_index()
                df = df.sort_values(by=["year","num_mois","month_year"])
  
        else:
            if len(control_type) > 0:
                df =df.groupby(["year","type_local"]).agg(aggregat[0],numeric_only=True).reset_index()
                df = df.sort_values(by=["type_local","year"])
            else:
                df =df.groupby(["year"]).agg(aggregat[0],numeric_only=True).reset_index()
                df = df.sort_values(by=["year"])


        if value_step == "percent":
            
            df_concat = pd.DataFrame()
            if len(control_type)>0:
                if group_type == "year":

                    df =df.sort_values(by=["type_local","year"])
                else:
                     df =df.sort_values(by=["type_local","year","num_mois","month_year"])
    
                for type_ in control_type:
                    df_filter =df[df.type_local==type_]
                    for col in cols:
                        df_filter[col]=df_filter[col].pct_change(periods=1)
                    df_concat=pd.concat([df_concat,df_filter])
                df=df_concat

            else:
                if group_type == "year":
                    df =df.sort_values(by=["year"])
                else:
                     df =df.sort_values(by=["year","num_mois","month_year"])

          
                for col in cols:
                    df[col]=df[col].pct_change(periods=1)



    for liste in cols:
    
        fig=go.Figure()
        if group_type != "year":

            if len(control_type) == 0:
                fig.add_trace(go.Scatter(
                            x=df['month_year'],
                            y=df[liste],
                            mode='lines',
                            line_width=3,
                            name=f"{liste}- ",marker_color=color[1],
                            # text=[f"""<b>Période:</b>{x}<br><b>Type local:</b> {key}<br><b>{liste.replace("_"," ").capitalize()}:</b><span style="color:#1e40af;font-weight:bold">{y}€</span>"""
                            #     for x, key, y in zip(data_key['month_year'], data_key['type_local'], round(data_key[liste],2))],
                            # hovertemplate='%{text}<extra></extra>'
                        ))
                title="<br>".join(textwrap.wrap(f"{liste.replace('_',' ').capitalize()} {region_name} {dep_name} {cities_name} {','.join(control_type)} - {','.join(control)}",width=50))
                fig.update_layout(xaxis=dict(dtick=4, tickangle=45))


       
            else:
                for index,key in enumerate(keys):
                        print(keys)
                        data_key = df[df['type_local'] == key.capitalize()]
            
                        print(liste)
                        if len(liste)!= 2:
                            fig.add_trace(go.Scatter(
                                x=data_key['month_year'],
                                y=data_key[liste],
                                mode='lines',
                                line_width=3,
                                name=f"{liste}- {key}",marker_color=color[index],
                                text=[f"""<b>Période:</b>{x}<br><b>Type local:</b> {key}<br><b>{liste.replace("_"," ").capitalize()}:</b><span style="color:#1e40af;font-weight:bold">{y}€</span>"""
                                    for x, key, y in zip(data_key['month_year'], data_key['type_local'], round(data_key[liste],2))],
                                hovertemplate='%{text}<extra></extra>'
                            ))
                            fig.update_layout(xaxis=dict(dtick=4, tickangle=45))
                            
                            title="<br>".join(textwrap.wrap(f"{liste.replace('_',' ').capitalize()} {region_name} {dep_name} {cities_name} {','.join(control_type)} ",width=50))
             
                        else:
                            fig.add_trace(go.Scatter(
                            x=data_key['month_year'],
                            y=data_key[liste[0]],
                            mode='lines',
                            line_width=3,
                            name=f"{liste[0]}- {key}",marker_color=color[index if index==0 else index+1],
                            text=[f"""<b>Période:</b>{x}<br><b>Type local:</b> {key}<br><b>{liste[0].replace("_"," ").capitalize()}:</b><span style="color:#1e40af;font-weight:bold">{y}€</span>"""
                                for x, key, y in zip(data_key['month_year'], data_key['type_local'], round(data_key[liste[0]],2))],
                            hovertemplate='%{text}<extra></extra>'
                            ))

                            fig.add_trace(go.Scatter(
                            x=data_key['month_year'],
                            y=data_key[liste[1]],
                            mode='lines',
                            line_width=3,
                            name=f"{liste[1]} - {key}",marker_color=color[index+1 if index==0 else index+2],
                            text=[f'<br><b>Période:</b> {x}<br><b><span style="font-size:13px">Type local</span></b> {key}<br><b>{liste[1].replace("_"," ").capitalize()}</b> <span style="color:#1e40af;font-weight:bold">{y}€</span>' 
                                for x, key, y in zip(data_key['month_year'], data_key['type_local'], round(data_key[liste[1]],2))],
                            hovertemplate='%{text}<extra></extra><br>'
                            ))
                            fig.update_layout(xaxis=dict(dtick=4, tickangle=45))
                            title="<br>".join(textwrap.wrap(f"{','.join(liste).replace('_',' ').capitalize()} {region_name} {dep_name} {cities_name} {','.join(control_type)} ",width=50))
            
        elif group_type == "year":
            if len(control_type) > 0:
                df = df[df.type_local.isin(control_type)]   
                if value_step == "percent":
                    barmode="group"
                else:
                    barmode="group"
                fig = px.bar(data_frame = df, x="year",y=liste,color="type_local",color_discrete_sequence=color,barmode=barmode)
                fig.update_layout(xaxis=dict(dtick=1, tickangle=45))
                title="<br>".join(textwrap.wrap(f"{liste.capitalize()} {region_name} {dep_name} {cities_name} {','.join(control_type)}",width=50))


                   
            else:
                    fig = px.bar(data_frame = df,x="year",y=liste,color_discrete_sequence=color)
                    fig.update_layout(xaxis=dict(dtick=1, tickangle=45))
                    title="<br>".join(textwrap.wrap(f"{liste} {region_name} {dep_name} {cities_name} {','.join(control_type)}",width=50))
                    fig.update_layout(hovermode="x unified", margin=dict(t=0,l=0,r=0,b=0),title=title)

        else:
                fig = px.line(data_frame = df,x="month_year",y=liste,color_discrete_sequence=color)
                fig.update_layout(xaxis=dict(dtick=4, tickangle=45))
                title="<br>".join(textwrap.wrap(f"{','.join(liste).replace('_',' ').capitalize()} {region_name} {dep_name} {cities_name} {','.join(control_type)}",width=50))


        fig.update_layout(hovermode="x unified", margin=dict(t=0,l=0,r=0,b=0),title=title)


        get_templates(fig)
        liste_fig.append(fig)

    return html.Div(id="fig_number",children=[
        dcc.Graph(id="",figure=fig,className=className.get("graph")) for fig in liste_fig ],
        className="flex flex-col xl:flex-row  flex-wrap w-full xl:flex-nowrap justify-around p-3 m-2 ")

   
@app.callback(Output("graph_evol_transaction","children"),[Input("region_name","value"),Input("dep_name","value"),Input("cities_name","value"),Input("control_type","value"),
                                                           Input("group_type","value"),Input("value_step","value")])
def get_graph_transaction(region_name,dep_name,cities_name,control_type,group_type,value_step):
    df = get_data_per_year_per_month(region_name, dep_name,cities_name)

    df["month_year"] = df["year"].astype(str) + "-" + df["month"]
    df["num_mois"]=pd.to_datetime(df.month, format='%B').dt.month

    df=df.sort_values(by=["year","num_mois"])
    df.year = pd.to_datetime(df.year,format="%Y")
    df.year = df.year.dt.year
    keys = df['type_local'].unique()
    color=["#bfdbfe","#3b82f6","#fecaca","#ef4444"]
    liste_fig=[]




    cols=["nombre_transactions","volume_transactions"]


    if group_type == "year":
        if len(control_type)>0:
            df = df.groupby(["year","type_local"]).agg({"nombre_transactions":"sum","volume_transactions":"sum"}).reset_index()
        else:
            df = df.groupby("year").agg({"nombre_transactions":"sum","volume_transactions":"sum"}).reset_index()#.rename(columns={"nombre_transactions":"total_transaction","volume_transactions":"volume_transaction"})
    else:
        if len(control_type)>0:
                df = df.groupby(["year","month_year","num_mois","type_local"]).agg({"nombre_transactions":"sum","volume_transactions":"sum"}).reset_index()#.rename(columns={"nombre_transactions":"total_transaction","volume_transactions":"volume_transaction"})
        
        else:
            df = df.groupby(["year","month_year","num_mois",]).agg({"nombre_transactions":"sum","volume_transactions":"sum"}).reset_index()#.rename(columns={"nombre_transactions":"total_transaction","volume_transactions":"volume_transaction"})

    if value_step =="percent":
            
            if len(control_type)>0:
                
                if group_type !="year":
                    df=df.sort_values(by=["type_local","year","num_mois"])
                    if len(control_type) == 2:
                        for col in cols:
                            for control in control_type:
                                df.loc[df.type_local == control, col] = df.loc[df.type_local == control, col].pct_change(periods=1)*100
                        
                    else:
                       for col in cols:
                            df[col]=df[df.type_local.isin(control_type)].volume_transactions.pct_change(periods=1)
                else:
                    df=df.sort_values(by=["type_local","year"])
                    if len(control_type) == 2:
                        for col in cols:
                            for control in control_type:
                                df.loc[df.type_local == control, col] = df.loc[df.type_local == control, col].pct_change(periods=1)*100
                        
                    else:
                        for col in cols:
                            df[col]=df[df.type_local.isin(control_type)].volume_transactions.pct_change(periods=1)
                       
                   

            else:
                if group_type != 'year':
                    df=df.sort_values(by=["year","num_mois"])
                else:
                     df=df.sort_values(by=["year"])
                df["volume_transactions"]=df.volume_transactions.pct_change(periods=1)
                df["nombre_transactions"]=df.nombre_transactions.pct_change(periods=1)


    for liste in cols:
        fig=go.Figure()
        if len(control_type)>0 and group_type != "year":
            for index,key in enumerate(control_type):
                data_key = df[df['type_local'] == key]

                fig.add_trace(go.Scatter(
                        x=data_key['month_year'],
                        y=data_key[liste],
                        mode='lines',
                        line_width=3,
                        name=f"{liste}- {key}",marker_color=color[index],
                        text=[f'<br><b>Période:</b> {x}<br><b><span style="font-size:13px">Type local</span></b> {key}<br><b>{liste.replace("_"," ")}:</b> <span style="color:#1e40af;font-weight:bold">{y}</span>' 
                    for x, key, y in zip(data_key['month_year'], data_key['type_local'], round(data_key[liste],2))],
                hovertemplate='%{text}<extra></extra><br>'

                    ))
                fig.update_layout(xaxis=dict(dtick=4, tickangle=45))
        elif group_type == "year":
            if len(control_type) > 1:   
                if value_step == "percent":
                    barmode="group"
                else:
                    barmode="relative"
                fig = px.bar(data_frame = df, x="year",y=liste,color="type_local",color_discrete_sequence=color,barmode=barmode)
                fig.update_layout(xaxis=dict(dtick=1, tickangle=45))

                   
            else:
                    fig = px.bar(data_frame = df,x="year",y=liste,color_discrete_sequence=color)
                    fig.update_layout(xaxis=dict(dtick=1, tickangle=45))

        else:
                fig = px.line(data_frame = df,x="month_year",y=liste,color_discrete_sequence=color)
                fig.update_layout(xaxis=dict(dtick=4, tickangle=45))



        if region_name is None:
            region_name=""
        if dep_name is None:
            dep_name=""
        if cities_name is None:
            cities_name = ""
        fig.update_layout(hovermode="x unified", margin=dict(t=0,l=0,r=0,b=0),title=f"{liste.replace('_',' ').capitalize()} {region_name} {dep_name} {cities_name}")
        get_templates(fig)
        liste_fig.append(fig)
    

    return html.Div(id="fig_transaction",children=[
        dcc.Graph(id="",figure=fig,className=className.get("graph")) for fig in liste_fig ],
        className="flex flex-col xl:flex-row  flex-wrap w-full xl:flex-nowrap justify-around p-3 m-2 ")
         
@app.callback(Output("map","children"),[Input("year","value"),Input("region_name","value"),Input("dep_name","value"),Input("cities_name","value")])
def get_map_vente(year,region_name,dep_name,cities_name):

    df =get_query(year,region_name,dep_name,cities_name)
    
    zoom=4
    if region_name:
        zoom=6
    if dep_name:
        zoom=8
        if dep_name == "Paris":
            zoom=12
    if cities_name:
        zoom=12
    df=df.astype({"latitude":"float64","longitude":"float64"})
    jt ="pk.eyJ1IjoiYXJ6aXZhbCIsImEiOiJjbGRidjRlZjYwNGRoM3Vucm92dDMxNzE4In0.UqAauxFxNJFDOBH42kmUHg"
    px.set_mapbox_access_token(jt)
    color=px.colors.diverging.RdYlGn_r
    max_range = df.prix_m2.describe(percentiles=np.arange(0.8,1,0.02))["90%"].round(2)
    max_price = df.valeur_fonciere.describe(percentiles=np.arange(0.8,1,0.02))["98%"].round(2)
    fig = px.scatter_mapbox(df[df.valeur_fonciere<=max_price], lat="latitude", lon="longitude",     color="prix_m2", size="valeur_fonciere",
                      color_continuous_scale=color, range_color=[df.prix_m2.min(),max_range],size_max=20, 
                       center =go.layout.mapbox.Center ( lat = df.latitude[0] , lon =df.longitude[0] ), 
                       zoom=zoom,hover_name="adresse_complete",hover_data= {

                            "latitude": False,
                            "longitude": False,
                            "month_name":True,
                            "surface_reelle_bati":True,
                  
                            "year":True,
                            "prix_m2":True
                        
                            },
                           )
    get_templates(fig)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},height=800, coloraxis_colorbar=dict(title=''))
    
    return html.Div(
        id="",children=[
            dcc.Graph(id="graph_map",figure=fig,className="")
        ]
    )



        
    
@app.callback(Output("map_view_detail","children"),
              [Input("year","value"),Input("region_name","value"),Input("dep_name","value"),Input("detail_view","value"),Input("value_to_see","value")]
              )
def get_view_map(year,region_name,dep_name,detail_view,value_to_see):
    zoom=4
    detail=detail_view

    if region_name is None and dep_name is None:
        if detail  != "dep_name":
            geo=get_geojson_file(region_name=region_name)
        else:
            detail="dep_name"
     
            geo=get_geojson_file(detail=detail)
        
    if region_name :
        geo=get_geojson_file(region_name=region_name)
        detail = "dep_name"
        zoom=6
    
     
    if dep_name : 
        detail = "nom_commune"
        geo=get_geojson_file(region_name=region_name,dep_name=dep_name)
        zoom=7.5
        if dep_name == "Paris":
            zoom=10
     
    
    df =get_query_map_view(year,region_name,dep_name,detail,value_to_see)

    if df['value_agg'].str.contains('Arrondissement').any():
        pattern = "\d"
        df.value_agg = df.value_agg.replace(" ","")
        
        df["code_arrondissement"]= df.value_agg.apply(lambda x:re.findall(pattern,x)[0] if len(re.findall(pattern,x))> 0 else x )

        geo["code_arrondissement"]=geo.nom.apply(lambda x:re.findall(pattern,x)[0] if len(re.findall(pattern,x))> 0 else x )
        df=df.merge(geo,how="inner",left_on="code_arrondissement",right_on="code_arrondissement")
        
        df['geometry'] = df['geometry'].apply(lambda x: wkt.loads(str(x)))
        geo= gpd.GeoDataFrame(df, geometry='geometry')
        location="nom"
    else:
        location="value_agg"

    geo=geo.reset_index()

    data_geo = geo['geometry'][3].centroid

    data_geo = Point(data_geo)

    # Extraire les coordonnées de latitude et de longitude
    lon = data_geo.x
    lat = data_geo.y
    color=px.colors.diverging.RdYlGn_r

    fig = px.choropleth_mapbox(df, geojson=geo, locations=location, color='agg_col',
                            color_continuous_scale=color,
                            mapbox_style="carto-positron",
                            featureidkey='properties.nom',  
                            zoom=zoom, 
                            center = {"lat": lat, "lon": lon},
                            opacity=0.5,
                            
                            )
    get_templates(fig)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},height=800, coloraxis_colorbar=dict(title=''))
    fig.update_layout(legend=dict(xanchor="left",x=0.9,yanchor="top",y=0.8,orientation="h"))
    
    return html.Div(
        id="view_map_container",
        children=[
            dcc.Graph(id="view_map",figure=fig)
        ]
    )


app.layout=html.Div([

    html.Div(
                children=[
                    html.H1(children="Données de valeur foncière depuis 2018",className="text-6xl text-gray-700 font-bold p-3 m-2 "),
                    html.Div(
                        children=[
                            html.H2(children="Traitements des données",className="text-4xl text-gray-700 font-bold p-3 m-2 "),
                            html.A("Récupération des données sur DVF open data", href="https://files.data.gouv.fr/geo-dvf/latest/csv/", target="_blank"
                                   ,className="m-3 p-2 font-semibold text-gray-700 hover:text-blue-500 hover:font-bold"),

                            html.P(children="Les données ont été récupérées via le lien précédent, en utilisant "),
                            html.Ul(
                                children=[
                                    html.Li("Spark"),
                                    html.Li("MySQL"),
                                    html.Li("Récupération et insertion de données GEO-Json "),
                                    html.Li("Elastic Search ")
                                ],  className="p-3 m-2 text-lg font-medium"
                            ),
                            html.P(children="Les biens conservées sont"),
                            html.Ul(children=[html.Li(i) for i in ["Maison","Appartement"]],className="p-3 m-2 text-lg font-medium"),
                            html.P(children="""Les données ont été récupérés via l'utilisation d'Apache Spark , afin de créer un dataframe. Les données ont ensuite eté nettoyées, standardisées, et filtrées"""),
                            html.P(children=""" Les données conservéees ,concernant les biens sus-designés ainsi que posédant une surface bâti inférieur à 450 m2 , et une valeur foncière supérieure à 1 500 000 €"""),

                            html.P(children=""" A partir de cela, les données ainsi conservées ont été insérées dans ElasticSearch"""),
                            html.P(children=""" Les requêtes ont été ensuite préparées afin de pouvoir généré des filtres à la volée, réduisant la quantité de données récupérées"""),
                            html.P(children=""" L'application web a donc été réalisée avec Dash pour la visualisation de données et Django pour la partie back-end""")
                        ],className="font-medium text-gray-800"
                    )
                ],className="bg-white rounded-2xl p-5 m-2 shadow-lg"
            ),
    html.Div(
        id="filter_menu",
    
            children=[
                html.Div(
                    children=[
                        dcc.Dropdown(
                        id="year",
                        options=[{"label":year,"value":year} for year in range(2018,2023)],
                        value=2022,
                       className="p-3 m-2 rounded-lg ",
                        
                    ),
                    ],className="w-full xl: w-1/5"
                ),
                  html.Div(children=[
                           dcc.Dropdown(
                    id="region_name",
                    options=[{"label":reg, "value":reg }for reg in sorted(region_name)],
                    value="Nouvelle-Aquitaine",
                    placeholder="region",
                   className="p-3 m-2 rounded-lg ",
                   # style={"min-width":"18vw","max-width":"90vw","border-radius":"0.5em"}
                    ),
                    ],className="w-full xl: w-1/5"
                ),
                   html.Div(children=[
                            dcc.Dropdown(
                    id="dep_name",
                    options="",
                    value=None,
                        placeholder="départements",
                  className="p-3 m-2 rounded-lg ",
                    
                    ),
                    ],className="w-full xl: w-1/5"
                ),
                   html.Div(children=[
                        dcc.Dropdown(
                    id="cities_name",
                    options="",
                    value=None,
                    placeholder="villes",
                    className="p-3 m-2 rounded-lg ",
                    
                    ),
                   
                    ],className="w-full xl: w-1/5"
                ),
                #  html.Div(children=[
                #         dcc.Dropdown(
                #     id="street",
                #     options="",
                #     value=None,
                #     placeholder="rue",
                #     className="p-3 m-2 rounded-lg ",
                    
                #     ),
                   
                #     ],className="w-full xl: w-1/5"
                # ),
                
            ],className="p-3 m-2 flex flex-col xl:flex-row flex-nowrap w-full justify-between items-center bg-white rounded-2xl  "
        ),
        ## message markdonw ###
     
        ## key numbe    r ###
            html.Div(
                children=[
                html.Div(children=[
                    html.H3(children="Chiffres clés",className="text-4xl text-gray-700 font-bold p-3 m-2 "),
                    html.Div(id="key_number",children=[],className="flex flex-col xl:flex-row flex-nowrap w-full justify-between"),
                ])
]),
                

        ## graph ##
        html.Div(
            id="",
            children=[
 html.H3(children="Evolution depuis 2018",className="text-4xl text-gray-700 font-bold p-3 m-2 "),
         html.Div(id="",children=[
            
            html.Div(children=[
                html.H4(children="Calcul d'Agrégat",className="text-2xl text-gray-700 font-bold p-3 m-2 "),
                html.Div([
                dcc.Dropdown(
                    id="control",
                    options={
                            'mean': 'moyenne',
                            'median': 'médiane',
                    },
                        
                        multi=True,
                    value=['mean'],
                    placeholder="choix de l'agrégat",
                    className="p-3 m-2 rounded-lg ",
                  
                    ),
               ])
          
            ],className="w-full xl: w-1/4"),
            html.Div(id="",children=[
                html.H4(children="Choix du type de local",className="text-2xl text-gray-700 font-bold p-3 m-2 "),
                html.Div(
                    children=[
                            dcc.Dropdown(
                                id="control_type",
                                placeholder="choix du type de local",
                                options={
                                        'Maison': 'maison',
                                        'Appartement': 'appartement',
                                },
                                    
                                    multi=True,
                                value="",
                                className="p-3 m-2 rounded-lg ",
                                ),
               ])
          
            ],className="w-full xl: w-1/4"),
            html.Div(id="",children=[
                    html.H4(children="Choix du regroupement",className="text-2xl text-gray-700 font-bold p-3 m-2 "),
                    html.Div([
                                     dcc.Dropdown(
                                id="group_type",
                                placeholder="choix de l'affichage",
                                options={
                                        'year': 'année',
                                        'month': 'mois',
                                },
                                    
                            
                                value="month",
                                 className="p-3 m-2 rounded-lg ",
             
                                ),
               ])
          
            ],className="w-full xl: w-1/4"),
            html.Div(id="",children=[
                     html.H4(children="Choix du type d'affichage",className="text-2xl text-gray-700 font-bold p-3 m-2 "),
                     html.Div([
                                     dcc.Dropdown(
                        id="value_step",
                        options={
                            "percent":"évolution en pourcentage",
                            "absolute":"valeur"
                        },
                        className="p-3 m-2 rounded-lg ",
                      
                    )
                         
               ])
          
            ],className="w-full xl: w-1/4"),
           
           
                
          
                          
          
       ],className="p-3 m-2 flex flex-col xl:flex-row flex-nowrap w-full justify-around items-center bg-white rounded-2xl"),
                html.Div(id="graph_evol_number",children=[]),
                html.Div(id="graph_evol_transaction",children=[]),
                
            ]
           
        ),

        ## map ###

            html.Div(
                id="map_view_container",
                children=[
                   html.H3(children="Cartographies",className="text-4xl text-gray-700 font-bold p-3 m-2 "),
                   html.Div(
                        id="",
                        children=[
                            html.Div(children=[
                            dcc.Dropdown(
                                id="value_to_see",
                                options={
                                    "valeur_fonciere":"valeur foncière",
                                    "prix_m2":"prix au m2",
                                    "surface_reelle_bati":"Surface bâti",
                                    "volume_transactions":"Volume de transaction en € ",
                                    "nombre_transactions":"Nombre de Transaction"
                                },
                                value="prix_m2",
                                className="flex flex-row  p-3 m-2 items-center w-full ",
                               

                            ),
                            ],className="w-full xl:w-1/4"),
                      
                            html.P("Option uniquement valable pour une visualisation France entière"),
                            html.Div(
                                children=[
                            dcc.Dropdown(
                                id="detail_view",
                                options={
                                    "dep_name":"vue par département",
                                    "region_name":"vue par Région"
                                },
                                value="region_name",
                                className="flex flex-row  p-3 m-2 items-center w-full ",
                               
                            )
                                ],className="w-full xl:w-1/4"
                            )
              
                        ],className="p-3 m-2 flex flex-col xl:flex-row  w-full justify-around items-center bg-white rounded-2xl"
                    ),
                   html.Div(
                       id="map_view_detail",
                       children=[]
                   ),
                ]
            ),
           html.Div(
            children=[
                html.H3(children="Cartes des ventes",className="text-4xl text-gray-700 font-bold p-3 m-2 "),
                html.P(children="Pour des raisons techniques et de rapidité les résultats sont plafonnés à 50 000 éléments"
                       ,className="text-lg p-3 m-2 font-semibold"),
                html.P(children="L'échelle de couleur représente le prix au m2 moyen, la taille du cercle lui correspond à la valeur foncière"
                       ,className="text-lg p-3 m-2 font-semibold")
            ]
        ),
    
   
             html.Div(id="map",children=[])

],className="bg-gray-100 p-5 m-0 h-screen overflow-y-auto overflow-x-hidden")
    
