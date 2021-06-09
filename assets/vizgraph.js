
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
        }
    }
});

container = null
data_values = null
options = {
    clickToUse : true,
    height : '600px',
    width : '90%',
    nodes : {
        font : {
            size : 0
        }
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

networkObj = null;

function add_node_to_simulation(params) {
    for (var i = 0; i < params.nodes.length; i++) {
        var nodeId = params.nodes[i];
        global.data_values.nodes.update({id: nodeId, fixed: {x: false, y: false}});
        global.fixedVals[nodeId] = {x:false,y:false};
    }
}

function update_vis_options(opt) {
    if(global.container == null || global.networkObj == null) {
        return;
    }
    global.options['nodes']['font']['size'] = opt['nodes']
    global.options['edges']['font']['size'] = opt['edges']
    global.networkObj.setOptions(global.options);
}

function update_vis_graph(dataobj) {
    for(i=0;i<dataobj['nodes'].length;i++) {
        if (dataobj['nodes'][i]['id'] in fixedVals) {
            dataobj['nodes'][i]['fixed'] = fixedVals[dataobj['nodes'][i]['id']];
        }
        else {
            dataobj['nodes'][i]['fixed'] = fixedVals[dataobj['nodes'][i]['id']] = {x : false , y : false};
        }
    }
    global.fixedVals = {}
    for(i=0;i<dataobj['nodes'].length; i++) {
        fixedVals[dataobj['nodes'][i]['id']] = dataobj['nodes'][i]['fixed'];
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
            }
        });
        global.networkObj.on('dragStart', add_node_to_simulation);
        global.networkObj.on('doubleClick', add_node_to_simulation);
    }
    global.data_values['nodes'] = new vis.DataSet(dataobj['nodes'])
    global.data_values['edges'] = new vis.DataSet(dataobj['edges'])
    global.networkObj.setData(global.data_values);
}