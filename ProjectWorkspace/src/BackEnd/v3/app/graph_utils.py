import pandas as pd
from datetime import datetime, timedelta
import networkx as nx

def time_to_seconds(time_str):
    h, m, s = map(int, time_str.split(':'))
    return h * 3600 + m * 60 + s

def build_graph():
    # Load GTFS data
    stops = pd.read_csv('gtfs/stops.txt', dtype={'stop_id': str})
    stop_times = pd.read_csv('gtfs/stop_times.txt', dtype={'trip_id': str, 'stop_id': str})
    trips = pd.read_csv('gtfs/trips.txt', dtype={'trip_id': str, 'route_id': str})
    routes = pd.read_csv('gtfs/routes.txt', dtype={'route_id': str})

    # Convert times to seconds since midnight
    stop_times['arrival_seconds'] = stop_times['arrival_time'].apply(time_to_seconds)
    stop_times['departure_seconds'] = stop_times['departure_time'].apply(time_to_seconds)

    # Sort stop_times by trip_id and stop_sequence
    stop_times.sort_values(['trip_id', 'stop_sequence'], inplace=True)

    now = datetime.now()
    current_time_seconds = now.hour * 3600 + now.minute * 60 + now.second
    max_future_time = current_time_seconds + (4 * 3600)  # Next 4 hours

    # Filter stop_times within the time window
    stop_times = stop_times[
        (stop_times['departure_seconds'] >= current_time_seconds) &
        (stop_times['departure_seconds'] <= max_future_time)
    ]

    # Build the graph
    G = nx.DiGraph()

    # Add edges for trips
    for trip_id, group in stop_times.groupby('trip_id'):
        group = group.sort_values('stop_sequence')
        previous_node = None
        for idx, row in group.iterrows():
            stop_id = row['stop_id']
            arrival_time = row['arrival_seconds']
            departure_time = row['departure_seconds']
            node = (stop_id, arrival_time)
            G.add_node(node)
            
            if previous_node:
                # Add edge from previous node to current node
                G.add_edge(previous_node, node, weight=departure_time - previous_node[1])
            previous_node = (stop_id, departure_time)

    # Define a transfer time (e.g., 5 minutes)
    TRANSFER_TIME = 300  # 5 minutes in seconds

    # Add transfer edges
    for stop_id, group in stop_times.groupby('stop_id'):
        times = group['arrival_seconds'].unique()
        times.sort()
        for i in range(len(times)):
            for j in range(i + 1, len(times)):
                if times[j] - times[i] >= TRANSFER_TIME:
                    node_from = (stop_id, times[i])
                    node_to = (stop_id, times[j])
                    G.add_edge(node_from, node_to, weight=times[j] - times[i])

    return G

def find_earliest_path(G, start_stop_id, end_stop_id, current_time_seconds):
    # Find all nodes at the starting stop after the current time
    start_nodes = [node for node in G.nodes if node[0] == start_stop_id and node[1] >= current_time_seconds]
    if not start_nodes:
        return None  # No available starting nodes

    # Find all nodes at the ending stop
    end_nodes = [node for node in G.nodes if node[0] == end_stop_id]

    min_arrival_time = None
    best_path = None

    # Try to find the earliest arrival path for each starting node
    for start_node in start_nodes:
        for end_node in end_nodes:
            try:
                path = nx.shortest_path(G, start_node, end_node, weight='weight')
                arrival_time = path[-1][1]
                if min_arrival_time is None or arrival_time < min_arrival_time:
                    min_arrival_time = arrival_time
                    best_path = path
            except nx.NetworkXNoPath:
                continue  # No path between these nodes

    return best_path
