import pandas as pd
import numpy as np
from ortools.graph import pywrapgraph
from data import req, dur_mat

# create all nodes
req['start_node_id'] = range(len(req))
req['end_node_id'] = range(len(req), 2*len(req))
depo_start_node_id = 2*len(req)
depo_end_node_id = depo_start_node_id + 1

# create all edges between rides
edges = []
# edges = pd.DataFrame(columns=['start_node_id', 'end_node_id', 'cost'])

for source in range(len(req)):
    for target in range(len(req)):
        if req['t_end'][source] + dur_mat[req['dropoff'][source], req['pickup'][target]] <= req['t_start'][target]:
            # edges.append({'start_node': req['end_node_id'][source],
            #               'end_node': req['start_node_id'][target],
            #               'cost': req['t_start'][target] - req['t_end'][source]})
            edges.append([req['end_node_id'][source],
                          req['start_node_id'][target],
                          req['t_start'][target] - req['t_end'][source],
                          source, target])
# create edges from depo requests
for i in range(len(req)):
    edges.append([depo_start_node_id,
                  req['start_node_id'][i],
                  dur_mat[0, req['pickup'][i]],
                  -1, i])
    edges.append([req['end_node_id'][i],
                  depo_end_node_id,
                  dur_mat[req['dropoff'][i], 0],
                  i, -1])

edges = pd.DataFrame(edges, columns=['start_node_id', 'end_node_id', 'cost', 'from_request', 'to_request'])

# solve
min_cost_flow = pywrapgraph.SimpleMinCostFlow()

for i in range(len(edges)):
    min_cost_flow.AddArcWithCapacityAndUnitCost(int(edges['start_node_id'][i]),
                                                int(edges['end_node_id'][i]),
                                                1,
                                                int(edges['cost'][i]))

for i in range(len(req)):
    min_cost_flow.SetNodeSupply(int(req['start_node_id'][i]), -1)
    min_cost_flow.SetNodeSupply(int(req['end_node_id'][i]), 1)

min_cost_flow.SetNodeSupply(depo_start_node_id, 20)
min_cost_flow.SetNodeSupply(depo_end_node_id, -20)

if min_cost_flow.Solve() == min_cost_flow.OPTIMAL:
    print('Minimum cost:', min_cost_flow.OptimalCost())
    print('')
    print('  Arc    Flow / Capacity  Cost')
    for i in range(min_cost_flow.NumArcs()):
        cost = min_cost_flow.Flow(i) * min_cost_flow.UnitCost(i)
        print('%1s -> %1s   %3s  / %3s       %3s' % (
            min_cost_flow.Tail(i),
            min_cost_flow.Head(i),
            min_cost_flow.Flow(i),
            min_cost_flow.Capacity(i),
            cost))
else:
    print('There was an issue with the min cost flow input.')

pass