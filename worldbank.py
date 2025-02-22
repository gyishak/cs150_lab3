from dash import Dash, html, dcc, Input, Output, State
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
from pandas_datareader import wb
from datetime import datetime

app = Dash(__name__, external_stylesheets=[dbc.themes.QUARTZ])

indicators = {
    "IT.NET.USER.ZS": "Individuals using the Internet (% of population)",
    "SG.GEN.PARL.ZS": "Proportion of seats held by women in national parliaments (%)",
    "EN.GHG.CO2.AG.MT.CE.AR5": "CO2 emissions (kt)",

}

# get country name and ISO id for mapping on choropleth
countries = wb.get_countries()
countries["capitalCity"].replace({"": None}, inplace=True)
countries.dropna(subset=["capitalCity"], inplace=True)
countries = countries[["name", "iso3c"]]
countries = countries[countries["name"] != "Kosovo"]
countries = countries[countries["name"] != "Korea, Dem. People's Rep."]
countries = countries.rename(columns={"name": "country"})


def update_wb_data():
    # Retrieve specific world bank data from API
    df = wb.download(
        indicator=(list(indicators)), country=countries["iso3c"], start=2005, end=2016
    )

    df = df.reset_index()
    print(df.head())
    df.year = df.year.astype(int)

    # Add country ISO3 id to main df
    df = pd.merge(df, countries, on="country")
    df = df.rename(columns=indicators)

    return df


app.layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                [
                    html.H1(
                        "Comparison of World Bank Country Data",
                        style={"textAlign": "center"},
                    ),
                    html.H2(
                        datetime.now(),
                        style={"textAlign": "center"},
                    ),
                    dcc.Graph(id="my-choropleth", figure={}),
                ],
                width=12,
            )
        ),
        dbc.Row([
            dbc.Col(
                [
                    dbc.Label(
                        "Select Data Set:",
                        className="fw-bold",
                        style={"textDecoration": "underline", "fontSize": 20},
                    ),

                    dcc.Dropdown(
                        id="my-dropdown",
                        options=[{"label": i, "value": i} for i in indicators.values()],
                        value=list(indicators.values())[0],
                    ),
                ],
                width=4,
            ),
            dbc.Col(
                [
                    dbc.Label(
                        "Select Years:",
                        className="fw-bold",
                        style={"textDecoration": "underline", "fontSize": 20},
                    ),
                    dcc.RangeSlider(
                        id="years-range",
                        min=2005,
                        max=2016,
                        step=1,
                        value=[2005, 2006],
                        marks={
                            2005: "2005",
                            2006: "'06",
                            2007: "'07",
                            2008: "'08",
                            2009: "'09",
                            2010: "'10",
                            2011: "'11",
                            2012: "'12",
                            2013: "'13",
                            2014: "'14",
                            2015: "'15",
                            2016: "2016",
                        },
                    ),
                ],
                width=6,
            ),
        ]),
        dbc.Row(
            [dbc.Col([
                dbc.Button(
                    id="my-button",
                    children="Submit",
                    color="primary",
                ),
            ],
                width=12,
                className="fw-bold d-flex justify-content-end"
            )],
        ),
        dbc.Row([dbc.Col([html.Div(
                    id="clicked_times",
                    children="Clicks:",
                    style={"textAlign": "left"},
       )])]
        ),
        dcc.Store(id="storage", storage_type="session", data={}),
        dcc.Interval(id="timer", interval=1000 * 60, n_intervals=0),
    ]
)

@app.callback(Output("storage", "data"), Input("timer", "n_intervals"), )
def store_data(n_time):
    dataframe = update_wb_data()
    return dataframe.to_dict("records")

@app.callback(Output("clicked_times", "children"), Input("my-button", "n_clicks"), )
def store_time(n_clicks):
    if n_clicks is not None:
        return f'Clicks: {n_clicks}'
    else:
        return f'Clicks: {n_clicks}'


@app.callback(
    Output("my-choropleth", "figure"),
    Input("my-button", "n_clicks"),
    Input("storage", "data"),
    State("years-range", "value"),
    State("my-dropdown", "value"),
)
def update_graph(n_clicks, stored_dataframe, years_chosen, indct_chosen):
    dff = pd.DataFrame.from_records(stored_dataframe)
    print(years_chosen)

    print(n_clicks)

    if years_chosen[0] != years_chosen[1]:
        dff = dff[dff.year.between(years_chosen[0], years_chosen[1])]
        dff = dff.groupby(["iso3c", "country"])[indct_chosen].mean()
        dff = dff.reset_index()

        fig = px.choropleth(
            data_frame=dff,
            locations="iso3c",
            color=indct_chosen,
            scope="world",
            hover_data={"iso3c": False, "country": True},
            labels={
                indicators["SG.GEN.PARL.ZS"]: "% parliament women",
                indicators["IT.NET.USER.ZS"]: "pop % using internet",
                indicators["EN.GHG.CO2.AG.MT.CE.AR5"]: "CO2 emissions (kt)",
            },
        )
        fig.update_layout(
            geo={"projection": {"type": "natural earth"}},
            margin=dict(l=50, r=50, t=50, b=50),
        )
        return fig

    if years_chosen[0] == years_chosen[1]:
        dff = dff[dff["year"].isin(years_chosen)]
        fig = px.choropleth(
            data_frame=dff,
            locations="iso3c",
            color=indct_chosen,
            scope="world",
            hover_data={"iso3c": False, "country": True},
            labels={
                indicators["SG.GEN.PARL.ZS"]: "% parliament women",
                indicators["IT.NET.USER.ZS"]: "pop % using internet",
                indicators["EN.GHG.CO2.AG.MT.CE.AR5"]: "CO2 emissions (kt)",
            },
        )
        fig.update_layout(
            geo={"projection": {"type": "natural earth"}},
            margin=dict(l=50, r=50, t=50, b=50),

        )
        return fig


if __name__ == "__main__":
    app.run_server(debug=True)
