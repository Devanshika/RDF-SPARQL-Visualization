#importing libraries
#from SPARQLWrapper import SPARQLWrapper, TURTLE
from io import StringIO
from rdflib import Graph as RDFGraph
from rdflib import Literal,URIRef
import itertools
import pandas as pd
import dash
import visdcc
import dash_daq as daq
import dash_core_components as dcc
import dash_html_components as html
from base64 import b64decode
from dash.dependencies import Input, Output, State

#set default sparql query
sparql_query_def = """PREFIX dbo: <http://dbpedia.org/ontology/>
CONSTRUCT {
    ?hero dbo:height ?height
} WHERE {
    ?hero dbo:height ?height
}"""

#set local file path or remote endpoint
#rdf_file_path = 'C:\\Users\\devan\\Downloads\\superhero-ttl\\superhero.ttl'
#rdf_file_format = 'turtle'
rdf_graph = None
#remote_endpoint = None
rdf_file="No file chosen"

#reference for setup
current_data = {'nodes':[],'edges':[]}

#functionality
def get_nodes_by_search(search_type,search_string):
    search_obj = None
    if search_type == 'Literal':
        search_obj = Literal(search_string)
    elif search_type == 'URIRef':
        search_obj = URIRef(search_string)
    if search_obj is None:
        return current_data
    
    node_df, edge_df = get_node_dict(search_obj,None,None,'red',10,'diamond')
    node_df_cpy, edge_df_cpy = get_node_dict(None,None,search_obj,'red',10,'diamond')
    node_df = pd.concat([node_df,node_df_cpy],ignore_index = True).drop_duplicates(subset=['id'],ignore_index=True)
    edge_df = pd.concat([edge_df_cpy,edge_df],ignore_index = True).drop_duplicates(subset=['from','to'],ignore_index=True)
    node_df_cpy, edge_df_cpy = get_node_dict(None,None,None)
    node_df = pd.concat([node_df,node_df_cpy],ignore_index = True).drop_duplicates(subset=['id'],ignore_index=True)
    edge_df = pd.concat([edge_df_cpy,edge_df],ignore_index = True).drop_duplicates(subset=['from','to'],ignore_index=True)

    current_data['nodes'] = node_df.to_dict(orient='records')
    current_data['edges'] = edge_df.to_dict(orient='records')

    return current_data

def get_node_dict(subject,object,predicate,color = 'blue',size = 7,shape = 'dot'):
    node_df = pd.DataFrame( columns=['id','label','color','size','shape'])
    edge_df = pd.DataFrame(columns=['from','to','label','id'])
    c=itertools.count()
    for triple in rdf_graph.triples((subject,predicate,object)):
        if triple[0] not in node_df.id.tolist():
            new_node = {"id":triple[0],"label":triple[0],"color":color,"size":size,"shape":shape}
            node_df = node_df.append(new_node,ignore_index =True)
        if triple[2] not in node_df.id.tolist():
            new_node = {"id":triple[2], "label":triple[2],"color":color,"size":size,"shape":shape}
            node_df = node_df.append(new_node,ignore_index = True)
        new_edge = {"from":triple[0],"to":triple[2],"label":triple[1],"id":triple[1] + "#"+str(next(c))}
        edge_df = edge_df.append(new_edge,ignore_index=True)
    return node_df,edge_df

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
    node_df,edge_df = get_node_dict(None,None,None)
    current_data['nodes'] = node_df.to_dict(orient='records')
    current_data['edges'] = edge_df.to_dict(orient='records')
    return current_data



#creating app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash("RDF SPARQL Visualization", external_stylesheets=external_stylesheets)

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


#sparql-query
sparql_query_label = html.Label('SPARQL Query')
sparql_query_textarea = dcc.Textarea(id='sparql-query', value=sparql_query_def, style={'height': 200})


#generate-sparql-graph
generate_graph_button = html.Button('Run SPARQL',id='generate-sparql-graph', n_clicks=0)

#search-type
search_label=html.Label("Search Type")
search_dropdown= dcc.Dropdown(id='search-type',
        options=[
            {'label': 'URIRef', 'value': 'URIRef'},
            {'label': 'Literal', 'value': 'Literal'},
            
        ],
        value='Literal'
    )
#search-query search-graph
search_query_input = dcc.Input(id='search-query',placeholder='Enter search string',type='text')
search_graph_button = html.Button('Search',id='search-graph')


#node-size
#node_size_label = html.Label('Node Size')
#node_size_slider = dcc.Slider(id='node-size',min=1,max=10,step=0.5,value=7)

#toggle-node-label
toggle_node_text = daq.ToggleSwitch(id='toggle-node-label', label='Show Node Text',labelPosition='left', value=True)  

#toggle-edge-label
toggle_edge_text = daq.ToggleSwitch(id='toggle-edge-label', label='Show Edge Text',labelPosition='left', value=True)

#graph
visualization_label = html.H3(children = 'Knowledge Graph', style = {'textAlign':'center','color': colors['text']})
visualization = visdcc.Network(
    id ='graph' ,
    options = dict(
        height='600px', 
        width='100%',
        edges= dict(
            width = 2
        )))

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
                        generate_graph_button,
                        html.Br(),
                        html.Div(children = [search_label, search_dropdown,search_query_input, search_graph_button]),
                        # html.Br(),
                        # html.Div(children = [node_size_label, node_size_slider]),
                        html.Br(),
                        html.Div(children=[toggle_node_text,toggle_edge_text]),
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
    [Output('graph','data'),
    Output('rdf-file', 'children')],
    [Input('search-graph','n_clicks'),
    Input('generate-sparql-graph','n_clicks'),
    Input('upload-data','contents'),
    State('sparql-query','value'),
    State('file-format','value'),
    State('search-type','value'),
    State('search-query','value'),
    State('upload-data', 'filename'),
    State('upload-data', 'last_modified')]
)
def generate_graph(
    search_graph, 
    generate_sparql_graph,
    contents, 
    sparql_query,  
    file_format,
    search_type,
    search_query, 
    filename, 
    last_modified):
    global rdf_file
    global rdf_graph
    ctx = dash.callback_context
    if not ctx.triggered:
        return current_data,rdf_file
    if ctx.triggered[0]['prop_id'] == 'generate-sparql-graph.n_clicks':
        return get_nodes_and_edges(query_value = sparql_query),rdf_file
    elif ctx.triggered[0]['prop_id'] == 'search-graph.n_clicks':
        return get_nodes_and_edges(search_type = search_type,search_string = search_query),rdf_file
    elif contents is not None:
        content_type, content_string= contents.split(',')
        decoded=b64decode(content_string)
        rdf_graph = RDFGraph()
        rdf_graph.parse(StringIO(decoded.decode('utf-8')),format=file_format)
        rdf_file= "Current File: "+filename
        return get_nodes_and_edges(),rdf_file



@app.callback(
    Output('graph','options'),
    Input('toggle-node-label','value'),
    Input('toggle-edge-label','value')
)
def customize_graph(node_bool,edge_bool):
    return {'nodes':
                    {
                        'font':{'size': 0 if not node_bool else 14}
                    },
            'edges':
                    {
                        'font':{'size':0 if not edge_bool else 14}
                    }
            }


if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)