from dash import Dash, dcc, html, Input, Output

import pandas as pd
import numpy as np

import plotly.express as px
import plotly.graph_objects as go

import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

load_figure_template("minty")

app = Dash(__name__, external_stylesheets=[dbc.themes.MINTY])
server = app.server

df_data = pd.read_csv('supermarket_sales.csv')
df_data['Date'] = pd.to_datetime(df_data['Date'])

# LAYOUTS
app.layout = html.Div(children=[

    dbc.Row([
        # Coluna Esquerda
        dbc.Col([
            dbc.Card([
                html.H3("CIRODEV", style={"font-family": "Voltaire", "font-size": "3vw"}),
                html.Hr(),
                html.H5('Cidades: ', style={"font-weight": "bold", "font-size": "1vw"}),
                dcc.Checklist(df_data['City'].value_counts().index,
                df_data['City'].value_counts().index, id="check-city", inputStyle={"margin-left": "5px", "margin-right": "5px"},
                style={"font-size" : "1vw"}),

                html.Hr(),
                html.H5('Variáveis de Análise:', style={"font-weight":"bold", "font-size":"1vw", "margin-top":"10px"}),
                dcc.RadioItems(["Gross Income" , "Rating"], "Gross Income", id="main_variable", 
                               inputStyle={"margin-left": "5px", "margin-right": "5px"}, style={"font-size" : "1vw"}),

            ], style={"height" : "90vh", "margin" : "20px", "padding" : "20px"}),
        ], sm=2),
        # Coluna Direita
        dbc.Col([
            dbc.Row([
                dbc.Col([dcc.Graph(id="city_fig")], sm=4),
                dbc.Col([dcc.Graph(id="gender_fig")], sm=4),
                dbc.Col([dcc.Graph(id="pay_fig")], sm=4),
            ], style={"margin":"20px"}),
            dbc.Row([dcc.Graph(id="income_per_date")], style={"margin":"20px"}),
            dbc.Row([dcc.Graph(id="income_per_product_fig")], style={"margin":"20px"}),
            
        ], sm=10),
    ]),

    

])

# CALLBACKS
@app.callback([
        Output("city_fig", "figure"),
        Output("gender_fig", "figure"),
        Output("pay_fig", "figure"),
        Output("income_per_date", "figure"),
        Output("income_per_product_fig", "figure"),
    ],
        [
            Input("check-city", "value"),
            Input("main_variable", "value"),
        ],
)
def render_graph(cities, main_variable):
    
    operation = np.sum if main_variable == "Gross Income" else np.mean

    df_filtered = df_data[df_data["City"].isin(cities)]
    df_city = df_filtered.groupby("City")[main_variable].apply(operation).to_frame().reset_index()
    df_payment = df_filtered.groupby("Payment")[main_variable].apply(operation).to_frame().reset_index()
    df_gender = df_filtered.groupby(["Gender", "City"])[main_variable].apply(operation).to_frame().reset_index()
    df_income_time = df_filtered.groupby("Date")[main_variable].apply(operation).to_frame().reset_index()
    df_product_income = df_filtered.groupby(["Product line", "City"])[main_variable].apply(operation).to_frame().reset_index()

    fig_city = px.bar(df_city, x="City", y=main_variable)
    fig_payment = px.bar(df_payment, y="Payment", x=main_variable, orientation="h")
    fig_gender = px.bar(df_gender, y=main_variable, x="Gender", color="City", barmode="group")
    fig_income_time = px.bar(df_income_time, y=main_variable, x="Date")
    fig_product_income = px.bar(df_product_income, x=main_variable, y="Product line", color="City", orientation="h", barmode="group")

    for fig in [fig_city, fig_payment, fig_gender, fig_income_time]:
        fig.update_layout(margin=dict(l=0, r=0, t=20, b=20), height=200)
    
    fig_product_income.update_layout(margin=dict(l=0, r=0, t=20, b=20), height=500)

    return fig_city, fig_gender, fig_payment, fig_income_time, fig_product_income



# RUN SERVER

if __name__ == '__main__':
    app.run_server(debug=False)

