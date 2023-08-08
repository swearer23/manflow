import networkx as nx
import matplotlib.pyplot as plt
from entity.BaseTask import BaseTask, Timer

plt.rcParams['font.sans-serif'] = ['SimHei']

def trigger(time_elapsed):
    print(f'{time_elapsed} seconds elapsed.')
    if time_elapsed % 10 == 0:
        lead_storage.append_stack(100)
        wood_storage.append_stack(100)
        rubber_storage.append_stack(100)
    if pencil_assembly.stack >= orders[0][1]:
        pencil_assembly.output(orders[0][1])
        orders.pop(0)
        print(f'{time_elapsed} 秒之后，订单完成. {len(orders)} orders left.')
    if len(orders) == 0:
        print('所有订单完成.')
        timer.done = True

timer = Timer(0.01, trigger=trigger)
# 定义节点
# 原材料
lead_storage = BaseTask('铅原料', 0, timer=timer)
lead_storage.append_stack(100)
wood_storage = BaseTask('原木', 0, timer=timer)
wood_storage.append_stack(100)
rubber_storage = BaseTask('橡胶', 0, timer=timer)
rubber_storage.append_stack(100)
# 加工半成品
lead_processing = BaseTask('铅芯车间', 10, uses_resources=[
    (lead_storage, 1)
], timer=timer)
penholder_processing = BaseTask('笔杆车间', 10, uses_resources=[
    (wood_storage, 1)
], timer=timer)
eraser_processing = BaseTask('橡皮头车间', 10, uses_resources=[
    (rubber_storage, 1)
], timer=timer)
# 组装
pencil_assembly = BaseTask('铅笔车间', 10, uses_resources=[
    (lead_processing, 0.4),
    (penholder_processing, 0.4),
    (eraser_processing, 0.2)
], timer=timer, stack_limit=10000)
eraser_assembly = BaseTask('橡皮擦车间', 20, uses_resources=[
    (eraser_processing, 1)
], timer=timer, stack_limit=10000)

orders = [
    (pencil_assembly, 500),
    (eraser_assembly, 1000),
    (eraser_assembly, 1000),
    (eraser_assembly, 1000),
    (pencil_assembly, 600),
    (pencil_assembly, 300),
    (eraser_assembly, 1000),
    (eraser_assembly, 1000),
    (eraser_assembly, 1000),
    (pencil_assembly, 800),
    (pencil_assembly, 1000),
    (pencil_assembly, 200),
]

# timer.start()

G = nx.DiGraph()
G.add_edge(lead_storage, lead_processing)
G.add_edge(wood_storage, penholder_processing)
G.add_edge(rubber_storage, eraser_processing)
G.add_edge(lead_processing, pencil_assembly, weight=4)
G.add_edge(penholder_processing, pencil_assembly, weight=4)
G.add_edge(eraser_processing, pencil_assembly, weight=1)
G.add_edge(eraser_processing, eraser_assembly, weight=1)
for layer, nodes in enumerate(nx.topological_generations(G)):
    # `multipartite_layout` expects the layer as a node attribute, so add the
    # numeric layer value as a node attribute
    for node in nodes:
        G.nodes[node]["layer"] = layer

# Compute the multipartite_layout using the "layer" node attribute
pos = nx.multipartite_layout(G, subset_key="layer")

fig, ax = plt.subplots()
nx.draw_networkx(G, pos=pos, ax=ax)
ax.set_title("DAG layout in topological order")
fig.tight_layout()
plt.show()

