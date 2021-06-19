#importing libraries
from io import StringIO
from os import name
from rdflib import Graph as RDFGraph
import itertools
import pandas as pd
import copy
import dash
import dash_daq as daq
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from base64 import b64decode
from dash.dependencies import Input, Output, State, ClientsideFunction
from dash.exceptions import PreventUpdate

rdf_graph = None
default_graph = None
rdf_file="No file chosen"

#reference for setup
current_data = {'nodes':[],'edges':[]}

#functionality
def get_nodes_by_search(search_type,search_string):
    search_string = search_string.lower()
    node_df = pd.DataFrame(current_data['nodes'])
    edge_df = pd.DataFrame(current_data['edges'])
    node_df['color'] ='#003f5c'
    node_df['size'] = 15
    node_df['font'] = None
    edge_df['font'] = None
    if search_type == 'Predicate':
        for edge_val in current_data['edges']:
            if search_string in edge_val['title'].lower():
                edge_val_to_ix = node_df.title == edge_val['to']
                node_df.loc[edge_val_to_ix,'color'] = '#bc5090'
                node_df.loc[edge_val_to_ix,'font'] = [dict(size=50)] * sum(edge_val_to_ix)
                node_df.loc[edge_val_to_ix,'size'] = 60
                edge_val_from_ix = node_df.title == edge_val['from']
                node_df.loc[edge_val_from_ix,'color'] = '#ffa600'
                node_df.loc[edge_val_from_ix,'font'] = [dict(size=50)] * sum(edge_val_from_ix)
                #node_df.loc[edge_val_from_ix,'size'] = 50
                #edge_df.loc[edge_df['id'] == edge_val['id'],'font'] = dict(size=50)
    elif search_type == 'SubjectObject':
        iterated_title = []
        for node_val in current_data['nodes']:
            if node_val['title'].lower() in iterated_title:
                continue
            iterated_title.append(node_val['title'].lower())
            if search_string in node_val['title'].lower():
                same_title_ix = node_df.title == node_val['title']
                node_df.loc[same_title_ix,'color'] = '#bc5090'
                node_df.loc[same_title_ix,'font'] = [dict(size=50)] * sum(same_title_ix)
                node_df.loc[same_title_ix,'size'] = 60
                list_of_to = edge_df[edge_df['from'] == node_val['title']]['to'].tolist()
                list_of_from = edge_df[edge_df['to'] == node_val['title']]['from'].tolist()
                list_of_to = list(set(list_of_to + list_of_from))
                edge_node_ix = (edge_df['from'] == node_val['title']) | (edge_df['to'] == node_val['title'])
                #edge_df.loc[edge_node_ix,'font'] = [dict(size=50)] * sum(edge_node_ix)
                node_adjacant_ix = (node_df['title'].isin(list_of_to)) & (node_df['color'] != '#bc5090')
                node_df.loc[node_adjacant_ix,'color'] = '#ffa600'
                node_df.loc[node_adjacant_ix,'font'] = [dict(size=50)] * sum(node_adjacant_ix)
                #node_df.loc[node_adjacant_ix,'size'] = 50
    current_data['nodes'] = node_df.to_dict(orient='records')
    current_data['edges'] = edge_df.to_dict(orient='records')
    return current_data

def getValue(val):
    ix = val.rfind("/")
    if ix != -1:
        val = val[ix+1:]
        ix = val.rfind("#")
        if ix != -1:
            val = val[ix+1:]
    return val

def set_current_data():
    node_df = pd.DataFrame(columns=['id','title','label','color','size'])
    edge_df = pd.DataFrame(columns=['from','to','title','label','id'])
    c=itertools.count()
    for triple in rdf_graph.triples((None,None,None)):
        subjVal = str(triple[0].toPython())
        labelsubj = getValue(str(subjVal))
        predVal = str(triple[1].toPython())
        labelpred = getValue(str(predVal))
        objVal = str(triple[2].toPython())
        labelobj = getValue(str(objVal))
        is_label_node = "rdf-schema#label" in predVal
        if subjVal not in node_df.id.tolist():
            new_node = {"id":subjVal,'title':subjVal,'label':labelobj if is_label_node else labelsubj,"color":'#003f5c','size':30}
            node_df = node_df.append(new_node,ignore_index =True)
        elif is_label_node:
            node_df.loc[node_df.id == subjVal,'label'] = labelobj
        if objVal not in node_df.id.tolist() and not is_label_node:
            new_node = {"id":objVal, 'title':objVal,'label':labelobj,"color":'#003f5c','size':30}
            node_df = node_df.append(new_node,ignore_index = True)
        if not is_label_node:
            new_edge = {"from":subjVal,"to":objVal,'title':predVal,'label':labelpred,"id":predVal + "#"+str(next(c))}
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
    set_current_data()
    return current_data

def reset_graph():
    global default_graph
    global rdf_graph
    rdf_graph = copy.deepcopy(default_graph)
    current_data = {'nodes':[],'edges':[]}
    return current_data



#creating app
external_stylesheets = [dbc.themes.BOOTSTRAP,'https://codepen.io/chriddyp/pen/bWLwgP.css',
                        'https://unpkg.com/vis-network@9.0.4/dist/dist/vis-network.min.css']
external_scripts = ['https://unpkg.com/vis-network@9.0.4/dist/vis-network.min.js']
app = dash.Dash(__name__,title="RDF SPARQL Visualization", external_stylesheets=external_stylesheets, external_scripts=external_scripts)

#UI objects

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
load_button= dcc.Upload(dbc.Button('Upload File', color='primary',size='sm'),id='upload-data', multiple=False)
#clear-graph
clear_graph_button = dbc.Button('Clear Graph',color='danger',size='sm',id='clear-graph', n_clicks=0)

#sparql-query
sparql_query_label = html.Label('SPARQL Query')
sparql_query_textarea = dcc.Textarea(id='sparql-query', style={'height': '200px','width':'100%'})


#generate-sparql-graph
generate_graph_button = dbc.Button('Generate Graph',color='success',size='sm',id='generate-sparql-graph', n_clicks=0)

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
search_graph_button = dbc.Button('Search',id='search-graph',color='primary',size='sm') 
#toggle-edge-label
toggle_edge_text = dbc.Button("Edge Label",id='toggle-edge-label',active=False,color='primary',size='sm')
#toggle-node-label
toggle_node_text = dbc.Button("Node Label",id='toggle-node-label',active=False,color='primary',size='sm')  
vis_opt_store = dcc.Store(id='graph-opt')
#graph
visualization_label = html.H6(children = 'Knowledge Graph',className='row',style = {'text-align':'center','color': '#7FDBFF'})
vis_data_store = dcc.Store(id= 'graph-data')
visualization = html.Div(id='graph-container',className='row',style={'height':'650px','width':'100%'})
#reset_nodes
reset_node_btn = dbc.Button("Reset Fixed Nodes",id="reset_nodes",n_clicks=0,color='danger',size='sm')
#App Layout
app.layout = dbc.Spinner(
    children = html.Div(
        children = [
            vis_data_store,
            vis_opt_store,
            html.H5(children = 'RDF SPARQL Visualizer', style = {'textAlign': 'center','color': '#7FDBFF'}),
            html.Br(),
            html.Div(
                className='row',
                children = [
                    html.Div(className='one columns'),
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
                            html.Br(),
                            html.Label(id='graph-dummy-output',children=""),
                            html.Label(id='graph-dummy-opt',children=""),
                            html.Label(id='dummy-reset',children="")
                        ],
                        className='two columns'
                    ),
                    html.Div(
                        children = [
                            visualization_label,
                            visualization,
                            html.Div(children = [toggle_node_text,toggle_edge_text,reset_node_btn], className='row')
                        ],
                        className='eight columns'),
                    html.Div(className='one columns')
            ])
        ]),
        debounce = 1,
        size='lg',
        fullscreen=True,
        color='primary'
    )

    


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
    if contents is None:
        raise PreventUpdate
    content_type, content_string= contents.split(',')
    decoded=b64decode(content_string)
    rdf_graph = RDFGraph()
    rdf_graph.parse(StringIO(decoded.decode('utf-8')),format=file_format)
    default_graph = copy.deepcopy(rdf_graph)
    rdf_file= "Current File: " + filename
    return rdf_file
    

@app.callback(
    Output('graph-data','data'),
    [Input('search-graph','n_clicks'),
    Input('generate-sparql-graph','n_clicks'),
    Input('clear-graph','n_clicks'),
    State('sparql-query','value'),
    State('search-type','value'),
    State('search-query','value'),
    State('graph-data','data')]
)
def generate_graph(
    search_graph, 
    generate_sparql_graph,
    clear_graph,
    sparql_query, 
    search_type,
    search_query,
    data):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate
    if ctx.triggered[0]['prop_id'] == 'generate-sparql-graph.n_clicks':
        return get_nodes_and_edges(query_value = sparql_query)
    elif ctx.triggered[0]['prop_id'] == 'search-graph.n_clicks':
        return get_nodes_and_edges(search_type = search_type,search_string = search_query)
    elif ctx.triggered[0]['prop_id'] == 'clear-graph.n_clicks':
        return reset_graph()


@app.callback(
    Output('graph-opt','data'),
    Output('toggle-node-label','active'),
    Output('toggle-edge-label','active'),
    Input('toggle-node-label','n_clicks'),
    Input('toggle-edge-label','n_clicks'),
    State('graph-opt','data'),
    State('toggle-node-label','active'),
    State('toggle-edge-label','active'),
)
def customize_graph(node_n_clicks,edge_n_clicks,graph_opt,node_active,edge_active):
    ctx=dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate
    if ctx.triggered[0]['prop_id'] == 'toggle-node-label.n_clicks':
        node_active = not node_active
    elif ctx.triggered[0]['prop_id'] == 'toggle-edge-label.n_clicks':
        edge_active = not edge_active
    return {
        'nodes':0 if not node_active else 50,
        'edges':0 if not edge_active else 50
        },node_active,edge_active


app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='update_graph'
    ),
    Output('graph-dummy-output','children'),
    Input('graph-data','data')
)

app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='update_options'
    ),
    Output('graph-dummy-opt','children'),
    Input('graph-opt','data')
)

app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='reset_fixed_nodes'
    ),
    Output('dummy-reset','children'),
    Input('reset_nodes','n_clicks')
)


if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)