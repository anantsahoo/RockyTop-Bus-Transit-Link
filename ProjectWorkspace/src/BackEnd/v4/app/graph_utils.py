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

    # Define transfer time (e.g., 5 minutes)
    TRANSFER_TIME = 300  # 5 minutes in seconds

    # Add transfer edges
    for stop_id, group in stop_times.groupby('stop_id'):
        times = group['departure_seconds'].unique()
        times.sort()
        for i in range(len(times)):
            for j in range(len(times)):
                time_diff = times[j] - times[i]
                if time_diff < 0:
                    time_diff += 24 * 3600  # Handle overnight wrap-around
                if TRANSFER_TIME <= time_diff <= (24 * 3600):
                    node_from = (stop_id, times[i])
                    node_to = (stop_id, times[j])
                    if node_from != node_to:
                        G.add_edge(node_from, node_to, weight=time_diff, transfer=True)
                elif time_diff > (24 * 3600):
                    break  # No need to check further
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

    min_arrival_time = None
    best_path = None

    # Use Dijkstra's algorithm for multi-edge graphs
    for start_node in start_nodes:
        try:
            lengths, paths = nx.multi_source_dijkstra(G, {start_node}, weight='weight')
            for end_node in end_nodes:
                if end_node in paths:
                    path = paths[end_node]
                    arrival_time = end_node[1]
                    if min_arrival_time is None or arrival_time < min_arrival_time:
                        min_arrival_time = arrival_time
                        best_path = path
        except nx.NetworkXNoPath:
            continue  # No path from this start_node

    return best_path
