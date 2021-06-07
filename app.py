#importing libraries
#from SPARQLWrapper import SPARQLWrapper, TURTLE
from io import StringIO
from rdflib import Graph as RDFGraph
from rdflib import Literal,URIRef
import itertools
import pandas as pd
import copy
import dash
import visdcc
import dash_daq as daq
import dash_core_components as dcc
import dash_html_components as html
from base64 import b64decode
from dash.dependencies import Input, Output, State

#set default sparql query
sparql_query_def = """"""

#set local file path or remote endpoint
#rdf_file_path = 'C:\\Users\\devan\\Downloads\\superhero-ttl\\superhero.ttl'
#rdf_file_format = 'turtle'
rdf_graph = None
default_graph = None
#remote_endpoint = None
rdf_file="No file chosen"

#reference for setup
current_data = {'nodes':[],'edges':[]}

#functionality
def get_nodes_by_search(search_type,search_string):
    search_string = search_string.lower()
    node_df = pd.DataFrame(current_data['nodes'])
    node_df['color'] ='blue'
    node_df['shape'] = 'dot'
    node_df['size'] = 15
    if search_type == 'Predicate':
        for edge_val in current_data['edges']:
            if search_string in edge_val['title'].lower():
                node_df.loc[(node_df.title == edge_val['from']) | (node_df.title == edge_val['to']),'color'] = 'red'
                node_df.loc[(node_df.title == edge_val['from']) | (node_df.title == edge_val['to']),'shape'] = 'diamond'
                node_df.loc[(node_df.title == edge_val['from']) | (node_df.title == edge_val['to']),'size'] = 40
    elif search_type == 'SubjectObject':
        for node_val in current_data['nodes']:
            if search_string in node_val['title'].lower():
                node_df.loc[node_df.title == node_val['title'],'color'] = 'red'
                node_df.loc[node_df.title == node_val['title'],'shape'] = 'diamond'
                node_df.loc[node_df.title == node_val['title'],'size'] = 40
    current_data['nodes'] = node_df.to_dict(orient='records')
    return current_data

def set_current_data():
    node_df = pd.DataFrame(columns=['id','title','color','shape','size'])
    edge_df = pd.DataFrame(columns=['from','to','title','id'])
    c=itertools.count()
    for triple in rdf_graph.triples((None,None,None)):
        subjVal = str(triple[0].toPython())
        predVal = str(triple[1].toPython())
        objVal = str(triple[2].toPython())
        if subjVal not in node_df.id.tolist():
            new_node = {"id":subjVal,'title':subjVal,"color":'blue',"shape":'dot','size':15}
            node_df = node_df.append(new_node,ignore_index =True)
        if objVal not in node_df.id.tolist():
            new_node = {"id":objVal, 'title':objVal,"color":'blue',"shape":'dot','size':15}
            node_df = node_df.append(new_node,ignore_index = True)
        new_edge = {
            "from":subjVal,
            "to":objVal,
            'title':predVal,
            "id":predVal + "#"+str(next(c))}
        edge_df = edge_df.append(new_edge,ignore_index=True)
    current_data['nodes'] = node_df.to_dict(orient='records')
    current_data['edges'] = edge_df.to_dict(orient='records')

def get_nodes_and_edges(query_value = None,search_type = None,search_string = None):
    global rdf_graph
    global current_data
    if rdf_graph is None:
        return current_data
    if query_value: 
       rdf_graph = rdf_graph.query(query_value).graph
    elif search_type and search_string:
        return get_nodes_by_search(search_type,search_string)
    # else:
    #     sparql_endpoint = SPARQLWrapper(remote_endpoint)
    #     sparql_endpoint.setQuery(query_value)
    #     sparql_endpoint.setReturnFormat(TURTLE)
    #     rdf_graph = RDFGraph()
    #     rdf_graph.parse(data=sparql_endpoint.query().convert(), format="turtle")
    set_current_data()
    return current_data

def reset_graph():
    global default_graph
    global rdf_graph
    rdf_graph = copy.deepcopy(default_graph)
    current_data = {'nodes':[],'edges':[]}
    return current_data



#creating app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css',
                        'https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.css']
external_scripts = ['https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.js']
app = dash.Dash("RDF SPARQL Visualization", external_stylesheets=external_stylesheets, external_scripts=external_scripts)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

#UI objects

#sparql-endpoint
#sparql_endpoint_label = html.Label('SPARQL Endpoint')
#sparql_endpoint_input = dcc.Input(id='sparql-endpoint',placeholder='Enter SPARQL Endpoint',type='text')

#rdf-file
rdf_file_label=html.Label(id='rdf-file',children= "No file chosen")

#file-format
file_format_label=html.Label("Choose File Format")
file_format_dropdown= dcc.Dropdown(id='file-format',
        options=[
            {'label': 'N3', 'value': 'n3'},
            {'label': 'Turtle', 'value': 'turtle'},
            {'label': 'XML', 'value': 'xml'}
        ],
        value='turtle'
    )
#upload-data
load_button_label= html.Label("Upload Data")
load_button= dcc.Upload(html.Button('Upload File'),id='upload-data', multiple=False)
#clear-graph
clear_graph_button = html.Button('Clear Graph',id='clear-graph', n_clicks=0)

#sparql-query
sparql_query_label = html.Label('SPARQL Query')
sparql_query_textarea = dcc.Textarea(id='sparql-query', value=sparql_query_def, style={'height': 200})


#generate-sparql-graph
generate_graph_button = html.Button('Generate Graph',id='generate-sparql-graph', n_clicks=0)

#search-type
search_label=html.Label("Search Type")
search_dropdown= dcc.Dropdown(id='search-type',
        options=[
            {'label': 'Search By Predicate', 'value': 'Predicate'},
            {'label': 'Search By Subject/Object', 'value': 'SubjectObject'},
            
        ],
        value='SubjectObject'
    )
#search-query search-graph
search_query_input = dcc.Input(id='search-query',placeholder='Enter search string',type='text')
search_graph_button = html.Button('Search',id='search-graph')


#node-size
#node_size_label = html.Label('Node Size')
#node_size_slider = dcc.Slider(id='node-size',min=1,max=10,step=0.5,value=7)

#toggle-node-label
#toggle_node_text = daq.ToggleSwitch(id='toggle-node-label', label='Show Node Text',labelPosition='left', value=True)  

#toggle-edge-label
#toggle_edge_text = daq.ToggleSwitch(id='toggle-edge-label', label='Show Edge Text',labelPosition='left', value=True)

#graph
visualization_label = html.H3(children = 'Knowledge Graph', style = {'textAlign':'center','color': colors['text']})
visualization = visdcc.Network(
    id ='graph' ,
    options = dict(
        clickToUse = True,
        height='600px', 
        width='100%',
        edges= dict(
            width = 2,
            smooth = dict(
                enabled = True,
                type='continuous',
                roundness = 0.6
            )
        ),
        # interactions= dict(
        #     hover=True,
        #     keyboard = True
        # )
        ))

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
                        html.Div(children=rdf_file_label),
                        html.Br(),
                        html.Div(children= [file_format_label, file_format_dropdown]),
                        html.Div(children = [ load_button_label, load_button ]),
                        html.Br(),
                        html.Div(children = [ sparql_query_label, sparql_query_textarea]),
                        html.Br(),
                        html.Div(children = [clear_graph_button, generate_graph_button]),
                        html.Br(),
                        html.Div(children = [search_label, search_dropdown,search_query_input, search_graph_button]),
                        # html.Br(),
                        # html.Div(children = [node_size_label, node_size_slider]),
                        # html.Br(),
                        # html.Div(children=[toggle_node_text,toggle_edge_text]),
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
    Output('rdf-file','children'),
    Input('upload-data','contents'),
    State('upload-data', 'filename'),
    State('upload-data', 'last_modified'),
    State('file-format','value')
)
def load_rdf_file(contents,filename,last_modified,file_format):
    global rdf_file
    global rdf_graph
    global default_graph
    if contents is not None:
        content_type, content_string= contents.split(',')
        decoded=b64decode(content_string)
        rdf_graph = RDFGraph()
        rdf_graph.parse(StringIO(decoded.decode('utf-8')),format=file_format)
        default_graph = copy.deepcopy(rdf_graph)
        rdf_file= "Current File: "+filename
    return rdf_file
    

@app.callback(
    Output('graph','data'),
    [Input('search-graph','n_clicks'),
    Input('generate-sparql-graph','n_clicks'),
    Input('clear-graph','n_clicks'),
    State('sparql-query','value'),
    State('search-type','value'),
    State('search-query','value')]
)
def generate_graph(
    search_graph, 
    generate_sparql_graph,
    clear_graph,
    sparql_query, 
    search_type,
    search_query):
    ctx = dash.callback_context
    if not ctx.triggered:
        return current_data
    if ctx.triggered[0]['prop_id'] == 'generate-sparql-graph.n_clicks':
        return get_nodes_and_edges(query_value = sparql_query)
    elif ctx.triggered[0]['prop_id'] == 'search-graph.n_clicks':
        return get_nodes_and_edges(search_type = search_type,search_string = search_query)
    elif ctx.triggered[0]['prop_id'] == 'clear-graph.n_clicks':
        return reset_graph()


# @app.callback(
#     Output('graph','options'),
#     Input('toggle-node-label','value'),
#     Input('toggle-edge-label','value')
# )
# def customize_graph(node_bool,edge_bool):
#     return {'nodes':
#                     {
#                         'font':{'size': 0 if not node_bool else 14}
#                     },
#             'edges':
#                     {
#                         'font':{'size':0 if not edge_bool else 14}
#                     }
#             }


if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)