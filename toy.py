from ortools.graph import pywrapgraph
#           0   1  2   3  4   5
supplies = [2, -1, 1, -1, 1, -2]
edges =      [(0, 1), (2, 3), (4, 5), (2, 5), (0, 3), (0, 5)]
unit_costs = [2,      8,      1,      3,      2,      0]
capacities = [None]*len(edges)
# start_nodes = [edge[0] for edge in edges]
# end_nodes = [edge[1] for edge in edges]

min_cost_flow = pywrapgraph.SimpleMinCostFlow()

for (edge, capacity, unit_cost) in zip(edges, capacities, unit_costs):
    min_cost_flow.AddArcWithCapacityAndUnitCost(edge[0], edge[1],
                                                capacity, unit_cost)

for i in range(0, len(supplies)):
    min_cost_flow.SetNodeSupply(i, supplies[i])

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
