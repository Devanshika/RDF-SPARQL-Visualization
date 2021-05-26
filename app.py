#importing libraries
from SPARQLWrapper import SPARQLWrapper, TURTLE
from rdflib import Graph as RDFGraph
import itertools
import pandas as pd
import dash
import visdcc
import dash_daq as daq
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

#set default sparql query
sparql_query_def = """PREFIX dbo: <http://dbpedia.org/ontology/>
CONSTRUCT {
    ?hero dbo:height ?height
} WHERE {
    ?hero dbo:height ?height
}"""

#set local file path or remote endpoint
rdf_file_path = 'C:\\Users\\devan\\Downloads\\superhero-ttl\\superhero.ttl'
rdf_file_format = 'turtle'

remote_endpoint = None
current_data = {'nodes':[],'edges':[]}

#functionality
def get_nodes_and_edges(query_value = None):
    rdf_graph = None
    #create local rdf graph
    if rdf_file_path:
        rdf_graph = RDFGraph()
        rdf_graph.parse(rdf_file_path,format=rdf_file_format)
        if query_value:
            rdf_graph = rdf_graph.query(query_value).graph
    elif not query_value or not remote_endpoint:
        return current_data
    else:
        sparql_endpoint = SPARQLWrapper(remote_endpoint)
        sparql_endpoint.setQuery(query_value)
        sparql_endpoint.setReturnFormat(TURTLE)
        rdf_graph = RDFGraph()
        rdf_graph.parse(data=sparql_endpoint.query().convert(), format="turtle")
    
    node_df = pd.DataFrame( columns=['id','label'])
    edge_df = pd.DataFrame(columns=['from','to','label'])
    c=itertools.count()

    for triple in rdf_graph.triples((None,None,None)):
        if triple[0] not in node_df.id.tolist():
            new_node = {"id":triple[0],"label":triple[0]}
            node_df = node_df.append(new_node,ignore_index =True)
        if triple[2] not in node_df.id.tolist():
            new_node = {"id":triple[2], "label":triple[2]}
            node_df = node_df.append(new_node,ignore_index = True)
        new_edge = {"from":triple[0],"to":triple[2],"label":triple[1],"id":triple[1] + "#"+str(next(c))}
        edge_df = edge_df.append(new_edge,ignore_index=True)
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

#sparql-query
sparql_query_label = html.Label('SPARQL Query')
sparql_query_textarea = dcc.Textarea(id='sparql-query', value=sparql_query_def, style={'height': 200})

#generate-sparql-graph
generate_graph_button = html.Button('Run SPARQL',id='generate-sparql-graph', n_clicks=0)

#search-query search-graph
#search_query_input = dcc.Input(id='search-query',placeholder='Enter search string',type='text')
#search_graph_button = html.Button('Search',id='search-graph')

#node-size
node_size_label = html.Label('Node Size')
node_size_slider = dcc.Slider(id='node-size',min=1,max=10,step=0.5,value=7)

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
        nodes= dict(
            shape = 'dot', 
            size= 7),
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
                        #html.Div(children = [ sparql_endpoint_label, sparql_endpoint_input ]),
                        #html.Br(),
                        html.Div(children = [ sparql_query_label, sparql_query_textarea]),
                        generate_graph_button,
                        html.Br(),
                        #html.Div(children = [ search_query_input, search_graph_button]),
                        #html.Br(),
                        html.Div(children = [node_size_label, node_size_slider]),
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
    Output('graph','data'),
    Input('generate-sparql-graph','n_clicks'),
    Input('sparql-query','value')
)
def generate_sparql_graph(no_of_clicks, query_value):
    ctx = dash.callback_context
    if not ctx.triggered:
        return current_data
    if ctx.triggered[0]['prop_id'] == 'generate-sparql-graph.n_clicks':
        return get_nodes_and_edges(query_value)
    return current_data
    

@app.callback(
    Output('graph','options'),
    Input('toggle-node-label','value'),
    Input('toggle-edge-label','value'),
    Input('node-size','value')
)
def customize_graph(node_bool,edge_bool,node_size):
    return {'nodes':
                    {
                        'font':{'size': 0 if not node_bool else 14},
                        'size':node_size
                    },
            'edges':
                    {
                        'font':{'size':0 if not edge_bool else 14}
                    }
            }


if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)