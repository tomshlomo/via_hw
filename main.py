import numpy as np
from ortools.graph import pywrapgraph

from data import load


class Node:
    def __init__(self, supply: int):
        self.supply: int = int(supply)
        self.id = None


class Edge:
    def __init__(self, source_node: Node, target_node: Node, capacity: int, unit_cost: int):
        self.source_node: Node = source_node
        self.target_node: Node = target_node
        self.capacity: int = int(capacity)
        self.unit_cost: int = int(unit_cost)


class Request:
    def __init__(self, pickup: int, dropoff: int, request_id: int, time: int, depo_source_node: Node,
                 depo_sink_node: Node, duration_mat: np.ndarray):
        self.pickup: int = pickup
        self.dropoff: int = dropoff
        self.time: int = time
        self.request_id: int = request_id
        self.pickup_node: Node = Node(-1)
        self.dropoff_node: Node = Node(1)
        self.from_depo_edge: Edge = Edge(depo_source_node, self.pickup_node, 1, duration_mat[0, self.pickup])
        self.to_depo_edge: Edge = Edge(self.dropoff_node, depo_sink_node, 1, duration_mat[self.dropoff, 0])
        self.duration: int = int(duration_mat[self.pickup, self.dropoff])


def add_node(problem: pywrapgraph.SimpleMinCostFlow, node: Node):
    node.id = problem.NumNodes()
    problem.SetNodeSupply(node.id, node.supply)


def add_edge(problem: pywrapgraph.SimpleMinCostFlow, edge: Edge):
    problem.AddArcWithCapacityAndUnitCost(edge.source_node.id,
                                          edge.target_node.id,
                                          edge.capacity,
                                          edge.unit_cost)


def solve(req_file, dur_file, num_cars):
    # todo: single pass on requests
    req_df, duration_mat = load(req_file, dur_file)

    depo_source_node = Node(num_cars)
    depo_sink_node = Node(-num_cars)
    depo2depo = Edge(depo_source_node, depo_sink_node, num_cars, 0)

    reqs = []
    for i in range(len(req_df)):
        reqs.append(Request(req_df['pickup'][i], req_df['dropoff'][i], i, req_df['t_start'][i], depo_source_node,
                            depo_sink_node, duration_mat))

    # todo: find legal req2req without loops
    req2req = {}
    for req_from in reqs:
        for req_to in reqs:
            delta_time = req_to.time - req_from.time - req_from.duration
            drive = duration_mat[req_from.dropoff, req_to.pickup]
            if delta_time >= drive:
                req2req[(req_from, req_to)] = Edge(req_from.dropoff_node, req_to.pickup_node, 1, delta_time)

    problem = pywrapgraph.SimpleMinCostFlow()
    for node in [depo_source_node, depo_sink_node]:
        add_node(problem, node)

    add_edge(problem, depo2depo)
    for req in reqs:
        for node in [req.pickup_node, req.dropoff_node]:
            add_node(problem, node)
        add_edge(problem, req.from_depo_edge)
        add_edge(problem, req.to_depo_edge)

    for edge in req2req.values():
        add_edge(problem, edge)

    sol = problem.Solve()

    if sol == problem.OPTIMAL:
        print('Minimum cost:', problem.OptimalCost())
        print('')
        print('  Arc    Flow / Capacity  Cost  Supply')
        for i in range(problem.NumArcs()):
            if problem.Flow(i) > 0:
                cost = problem.Flow(i) * problem.UnitCost(i)
                print('%1s -> %1s   %3s  / %3s       %3s    %1s -> %1s' % (
                    problem.Tail(i),
                    problem.Head(i),
                    problem.Flow(i),
                    problem.Capacity(i),
                    cost,
                    problem.Supply(problem.Tail(i)),
                    problem.Supply(problem.Head(i))))
    else:
        print('no solution found')


# solve('requests_toy.csv', 'durations_toy.csv', 2)
solve('requests.csv', 'durations.csv', 29)
