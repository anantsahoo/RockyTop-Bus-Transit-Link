from datetime import datetime, timedelta
import math
import logging


def time_to_seconds(time_str):
    h, m, s = map(int, time_str.split(':'))
    return h * 3600 + m * 60 + s


def build_graph():
    import pandas as pd
    import networkx as nx
    # Load GTFS data
    stops = pd.read_csv('gtfs/stops.txt', dtype={'stop_id': str})
    stop_times = pd.read_csv('gtfs/stop_times.txt', dtype={'trip_id': str, 'stop_id': str})
    trips = pd.read_csv('gtfs/trips.txt', dtype={'trip_id': str, 'route_id': str})
    routes = pd.read_csv('gtfs/routes.txt', dtype={'route_id': str})

    # Convert times to seconds since midnight, accounting for times beyond 24:00:00
    stop_times['arrival_seconds'] = stop_times['arrival_time'].apply(time_to_seconds)
    stop_times['departure_seconds'] = stop_times['departure_time'].apply(time_to_seconds)

    # Sort stop_times by trip_id and stop_sequence
    stop_times.sort_values(['trip_id', 'stop_sequence'], inplace=True)

    # Build the graph as a MultiDiGraph to allow multiple edges
    G = nx.MultiDiGraph()

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
                travel_time = arrival_time - previous_node[1]
                if travel_time < 0:
                    # Handle overnight trips (time wrap-around)
                    travel_time += 24 * 3600
                G.add_edge(previous_node, node, weight=travel_time, trip_id=trip_id)
            previous_node = (stop_id, departure_time)

    # Define transfer time constraints
    TRANSFER_TIME = 300     # 5 minutes in seconds
    MAX_TRANSFER_TIME = 7200  # 2 hours in seconds

    # Add transfer edges
    for stop_id, group in stop_times.groupby('stop_id'):
        times = group['departure_seconds'].unique()
        times.sort()
        for i in range(len(times)):
            time_i = times[i]
            for j in range(i + 1, len(times)):
                time_j = times[j]
                time_diff = time_j - time_i
                if time_diff < 0:
                    time_diff += 24 * 3600  # Handle overnight wrap-around
                if time_diff > MAX_TRANSFER_TIME:
                    break  # Exceeds max transfer time, break inner loop
                if time_diff >= TRANSFER_TIME:
                    node_from = (stop_id, time_i)
                    node_to = (stop_id, time_j)
                    G.add_edge(node_from, node_to, weight=time_diff, transfer=True)
    return G



def find_earliest_path(G, start_stop_id, end_stop_id, current_time_seconds):
    import networkx as nx

    # Find all nodes at the starting stop after the current time
    start_nodes = [node for node in G.nodes if node[0] == start_stop_id and node[1] >= current_time_seconds]
    if not start_nodes:
        # If no nodes after current time, include nodes from the next day
        start_nodes = [node for node in G.nodes if node[0] == start_stop_id]

    # Find all nodes at the ending stop
    end_nodes = [node for node in G.nodes if node[0] == end_stop_id]

    if not start_nodes or not end_nodes:
        return None  # No available starting or ending nodes

    # Create a copy of the graph to avoid modifying the original
    H = G.copy()

    # Create a virtual source node
    source_node = 'source'
    H.add_node(source_node)
    for start_node in start_nodes:
        H.add_edge(source_node, start_node, weight=0)

    # Create a virtual sink node
    sink_node = 'sink'
    H.add_node(sink_node)
    for end_node in end_nodes:
        H.add_edge(end_node, sink_node, weight=0)

    # Run Dijkstra's algorithm from source_node to sink_node
    try:
        length, path = nx.single_source_dijkstra(H, source=source_node, target=sink_node, weight='weight')
    except nx.NetworkXNoPath:
        return None

    # Exclude the virtual nodes from the path
    actual_path = path[1:-1]  # Exclude 'source' and 'sink'

    return actual_path

def get_nearest_stops(stop_id, stops_df, num_stops=20):
    # Get the coordinates of the given stop
    stop = stops_df[stops_df['stop_id'] == stop_id]
    if stop.empty:
        return []
    lat1 = stop.iloc[0]['stop_lat']
    lon1 = stop.iloc[0]['stop_lon']

    # Compute distances to all other stops
    stops_df = stops_df.copy()  # Avoid SettingWithCopyWarning
    stops_df['distance'] = ((stops_df['stop_lat'] - lat1)**2 + (stops_df['stop_lon'] - lon1)**2)

    # Exclude the original stop
    nearby_stops = stops_df[stops_df['stop_id'] != stop_id]
    # Sort by distance
    nearby_stops = nearby_stops.sort_values('distance')
    # Return the stop_ids
    return nearby_stops['stop_id'].iloc[:num_stops].tolist()
