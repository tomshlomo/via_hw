import numpy as np
from ortools.graph import pywrapgraph
from typing import List
from data import load


class Node:
    def __init__(self, supply: int, problem: pywrapgraph.SimpleMinCostFlow):
        self.supply: int = int(supply)
        self.id = problem.NumNodes()
        problem.SetNodeSupply(self.id, self.supply)


class Edge:
    def __init__(self, source_node: Node, target_node: Node, capacity: int, unit_cost: int,
                 problem: pywrapgraph.SimpleMinCostFlow):
        self.source_node: Node = source_node
        self.target_node: Node = target_node
        self.capacity: int = int(capacity)
        self.unit_cost: int = int(unit_cost)
        self.idx = problem.NumArcs()
        problem.AddArcWithCapacityAndUnitCost(self.source_node.id,
                                              self.target_node.id,
                                              self.capacity,
                                              self.unit_cost)


class Request:
    def __init__(self, pickup: int, dropoff: int, request_id: int, time: int, depo_source_node: Node,
                 depo_sink_node: Node, duration_mat: np.ndarray, problem: pywrapgraph.SimpleMinCostFlow):
        self.pickup: int = pickup
        self.dropoff: int = dropoff
        self.time: int = time
        self.request_id: int = request_id
        self.pickup_node: Node = Node(-1, problem)
        self.dropoff_node: Node = Node(1, problem)
        self.from_depo_edge: Edge = Edge(depo_source_node, self.pickup_node, 1, duration_mat[0, self.pickup], problem)
        self.to_depo_edge: Edge = Edge(self.dropoff_node, depo_sink_node, 1, duration_mat[self.dropoff, 0], problem)
        self.duration: int = int(duration_mat[self.pickup, self.dropoff])


def solve(req_file, dur_file, num_cars):
    req_df, duration_mat = load(req_file, dur_file)
    problem = pywrapgraph.SimpleMinCostFlow()

    depo_source_node = Node(num_cars, problem)
    depo_sink_node = Node(-num_cars, problem)
    depo2depo = Edge(depo_source_node, depo_sink_node, num_cars, 0, problem)

    reqs = []
    for i in range(len(req_df)):
        reqs.append(Request(req_df['pickup'][i], req_df['dropoff'][i], i, req_df['t_start'][i], depo_source_node,
                            depo_sink_node, duration_mat, problem))

    drive_len = duration_mat[req_df['dropoff'].to_numpy()[:, np.newaxis], req_df['pickup'].to_numpy()[np.newaxis, :]]
    delta_time = req_df['t_start'].to_numpy()[np.newaxis, :] - req_df['t_end'].to_numpy()[:, np.newaxis]
    valid_edges = delta_time >= drive_len
    req2req = {}
    for idx_from, idx_to in zip(*np.where(valid_edges)):
        req2req[(idx_from, idx_to)] = Edge(reqs[idx_from].dropoff_node, reqs[idx_to].pickup_node, 1,
                                           delta_time[idx_from, idx_to], problem)

    sol = problem.Solve()

    if sol == problem.OPTIMAL:
        print(f'{num_cars} cars: minimum cost = ', problem.OptimalCost())
        routes = get_routes(problem, reqs, req2req)
        print(f'{problem.Flow(depo2depo.idx)} cars stay in depo.')
    else:
        routes = None
        print(f'{num_cars} cars: No solution found.')
    return routes


def get_routes(problem: pywrapgraph.SimpleMinCostFlow, reqs: List[Request], req2req):
    next_req = {}
    for (from_req_idx, to_req_idx), edge in req2req.items():
        if problem.Flow(edge.idx):
            next_req[reqs[from_req_idx]] = reqs[to_req_idx]

    routes = []
    for req in reqs:
        if problem.Flow(req.from_depo_edge.idx):
            route = [req]
            while req in next_req:
                req = next_req[req]
                route.append(req)
            routes.append(route)

            # print
            string = '->'.join([str(req.request_id) for req in route])
            time_start = route[0].time - route[0].from_depo_edge.unit_cost
            time_end = route[-1].time + route[-1].duration + route[-1].to_depo_edge.unit_cost
            duration = time_end - time_start
            print(f'route {len(routes)}: length = {len(route)}, duration = {duration}, sequence = {string}')
    return routes
