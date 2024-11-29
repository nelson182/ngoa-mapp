from flask import Flask, request, jsonify
import osmnx as ox
import networkx as nx

app = Flask(__name__)

# Load campus OSM data
def load_campus_graph(osm_file):
    graph = ox.graph_from_xml(osm_file, simplify=True, network_type='all')
    return graph

# Calculate shortest path
@app.route('/route', methods=['POST'])
def calculate_route():
    data = request.json
    start_lat = data['start_lat']
    start_lon = data['start_lon']
    end_lat = data['end_lat']
    end_lon = data['end_lon']

    graph = load_campus_graph('map.osm')
    
    # Find nearest nodes
    start_node = ox.distance.nearest_nodes(graph, start_lon, start_lat)
    end_node = ox.distance.nearest_nodes(graph, end_lon, end_lat)
    
    # Calculate route
    route = nx.shortest_path(graph, start_node, end_node, weight='length')
    
    # Convert route to coordinates
    route_coords = [(graph.nodes[node]['y'], graph.nodes[node]['x']) for node in route]
    
    return jsonify({'route': route_coords})

# Validate campus location
@app.route('/validate_location', methods=['POST'])
def validate_location():
    data = request.json
    lat = data['latitude']
    lon = data['longitude']
    
    # Implement campus boundary check logic
    is_within_campus = check_campus_boundary(lat, lon)
    
    return jsonify({'valid': is_within_campus})

def check_campus_boundary(lat, lon):
    # Boundary coordinates (example values)
    boundaries = {
        'north': 3.8800,
        'south': 3.8700,
        'east': 11.5200,
        'west': 11.5000
    }
    
    return (boundaries['south'] <= lat <= boundaries['north'] and
            boundaries['west'] <= lon <= boundaries['east'])

if __name__ == '__main__':
    app.run(debug=True)