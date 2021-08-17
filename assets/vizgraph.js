//clientside dashboard functions
global = this
window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        update_graph: function(dataobj) {
            update_vis_graph(dataobj);
            return "";
        },
        update_options: function(opt) {
            update_vis_options(opt);
            return "";
        },
        reset_fixed_nodes: function(n_clicks) {
            fixed_node_reset();
            return "";
        }
    }
});
//graph container
container = null
data_values = null
options = {
    clickToUse : true,
    height : '650px',
    width : '100%',
    nodes : {
        font : {
            size : 0
        },
        shape :'dot'
    },
    edges : {
        font : {
            size: 0 
        },
        width : 2,
        smooth : {
            enabled : true,
            type : 'continuous',
            roundness : 0.6
        }
    },
    physics : {
        solver : 'forceAtlas2Based',
        forceAtlas2Based : {
            avoidOverlap : 0.6,
            springConstant : 0.01,
            springLength : 300,
            gravitationalConstant : -150
        },
        minVelocity : 0,
        maxVelocity : 50,
        stabilization : true
    },
    interaction : {
        navigationButtons : true
    }
}
fixedVals = {}
positions = {}
networkObj = null;

function add_node_to_simulation(params) {
    for (var i = 0; i < params.nodes.length; i++) {
        let nodeId = params.nodes[i];
        reset_node(nodeId);
    }
}

function reset_node(nodeId) {
    global.data_values.nodes.update({id: nodeId, fixed: {x: false, y: false}});
    global.fixedVals[nodeId] = {x:false,y:false};
    global.positions[nodeId] = {x:0,y:0}
}

function fixed_node_reset() {
    keylist = Object.keys(global.fixedVals);
    for(i = 0; i < keylist.length; i ++) {
        if(global.fixedVals[keylist[i]].x) {
            reset_node(keylist[i]);
        }
    }
}
//update setings of the graph
function update_vis_options(opt) {
    if(global.container == null || global.networkObj == null) {
        return;
    }
    global.options['nodes']['font']['size'] = opt['nodes']
    global.options['edges']['font']['size'] = opt['edges']
    global.networkObj.setOptions(global.options);
}

//update the graph with new nodes and edges
function update_vis_graph(dataobj) {
    for(i=0;i<dataobj['nodes'].length;i++) {
        if (dataobj['nodes'][i]['id'] in global.fixedVals) {
            dataobj['nodes'][i]['fixed'] = global.fixedVals[dataobj['nodes'][i]['id']];
            dataobj['nodes'][i]['x'] = global.positions[dataobj['nodes'][i]['id']]['x'];
            dataobj['nodes'][i]['y'] = global.positions[dataobj['nodes'][i]['id']]['y'];
        }
        else {
            dataobj['nodes'][i]['fixed'] = global.fixedVals[dataobj['nodes'][i]['id']] = {x : false , y : false};
            global.positions[dataobj['nodes'][i]['id']] = {x:0,y:0};
        }
    }
    global.fixedVals = {}
    global.positions = {}
    for(i=0;i<dataobj['nodes'].length; i++) {
        global.fixedVals[dataobj['nodes'][i]['id']] = dataobj['nodes'][i]['fixed'];
        global.positions[dataobj['nodes'][i]['id']] = {x:0,y:0}
        global.positions[dataobj['nodes'][i]['id']]['x'] = dataobj['nodes'][i]['x'];
        global.positions[dataobj['nodes'][i]['id']]['y'] = dataobj['nodes'][i]['y'];
    }
    if(global.container == null) {
        global.container = document.getElementById('graph-container');
    }
    if(global.networkObj == null) {
        global.data_values = { 
            nodes:new vis.DataSet([]),
            edges:new vis.DataSet([])
        }
        global.networkObj = new vis.Network(
            global.container,
            global.data_values,
            global.options);
        
        global.networkObj.on("dragEnd", function (params) {
            for (var i = 0; i < params.nodes.length; i++) {
                var nodeId = params.nodes[i];
                global.data_values.nodes.update({id: nodeId, fixed: {x: true, y: true}});
                global.fixedVals[nodeId] = {x:true,y:true};
                global.positions[nodeId] = {x:params.pointer.canvas.x,y:params.pointer.canvas.y}
            }
        });
        global.networkObj.on('dragStart', add_node_to_simulation);
        global.networkObj.on('doubleClick', add_node_to_simulation);
    }
    global.data_values['nodes'] = new vis.DataSet(dataobj['nodes'])
    global.data_values['edges'] = new vis.DataSet(dataobj['edges'])
    global.networkObj.setData(global.data_values);
}