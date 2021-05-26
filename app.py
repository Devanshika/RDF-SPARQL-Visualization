#importing libraries
from SPARQLWrapper import SPARQLWrapper, RDFXML
from rdflib import Graph as RDFGraph
import pandas as pd
import dash
import visdcc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

#creating app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash("RDF SPARQL Visualization", external_stylesheets=external_stylesheets)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

#UI objects

#sparql-endpoint
sparql_endpoint_label = html.Label('SPARQL Endpoint')
sparql_endpoint_input = dcc.Input(id='sparql-endpoint',placeholder='Enter SPARQL Endpoint',type='text')

#sparql-query
sparql_query_label = html.Label('SPARQL Query')
sparql_query_textarea = dcc.Textarea(id='sparql-query', placeholder='Enter SPARQL Query', style={'height': 200})

#generate-sparql-graph
generate_graph_button = html.Button('Run SPARQL',id='generate-sparql-graph', n_clicks=0)

#search-query search-graph
search_query_input = dcc.Input(id='search-query',placeholder='Enter search string',type='text')
search_graph_button = html.Button('Search',id='search-graph')

#node-size
node_size_label = html.Label('Node Size')
node_size_slider = dcc.Slider(id='node-size',min=1,max=10,step=0.5,value=6)

#graph
visualization_label = html.H3(children = 'Knowledge Graph', style = {'textAlign':'center','color': colors['text']})
visualization = visdcc.Network(id ='graph', options = dict(height='100%', width='100%'))

#App Layout
app.layout = html.Div(
    children = [ 
        html.H1(children = 'RDF SPARQL Visualizer', style = {'textAlign': 'center','color': colors['text']}),
        html.Br(),
        html.Div(
            className='row',
            children = [
                html.Div(
                    children = [
                        html.Div(children = [ sparql_endpoint_label, sparql_endpoint_input ]),
                        html.Br(),
                        html.Div(children = [ sparql_query_label, sparql_query_textarea]),
                        html.Br(),
                        generate_graph_button,
                        html.Br(),
                        html.Br(),
                        html.Div(children = [ search_query_input, search_graph_button]),
                        html.Br(),
                        html.Br(),
                        html.Div(children = [ node_size_label, node_size_slider]),
                        html.Br(),
                        html.Br()
                    ],
                    className='three columns'),
                html.Div(
                    children = [
                        html.Div(children = [visualization_label, visualization])
                    ],
                    className='nine columns')
            ])
    ])


#dynamic callbacks

@app.callback(
    Output('graph','data'),
    Input('generate-sparql-graph','n_clicks'),
    Input('sparql-endpoint','value'),
    Input('sparql-query','value')
)
def generate_sparql_graph(no_of_clicks, endpoint_value, query_value):
    
    if not endpoint_value or not query_value:
        return None
    




if __name__ == '__main__':
    app.run_server(debug=True)