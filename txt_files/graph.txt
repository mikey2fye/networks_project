import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import mongo

client = mongo.mongo_client()
db = client.IP_Database
nodes = db.IP_Nodes.find()

G = nx.Graph()

for node in nodes:
    G.add_node(node["ip"])

    for link in node["links"]:

        if link != node["ip"]:

            G.add_edge(node["ip"], link)


client.close()

pos = nx.kamada_kawai_layout(G, scale=10)

# Increase the overall spacing by scaling the positions
scale_factor = 50.0  # Adjust this value as needed
pos = {node: (x * scale_factor, y * scale_factor) for node, (x, y) in pos.items()}

nx.draw(G, pos, with_labels=True)
plt.show()
# plt.savefig('sample_plot.png')
