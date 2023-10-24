import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from traceroute import mongo_client

client = mongo_client()
db = client.IP_Database
nodes = db.IP_Nodes.find()

G = nx.Graph()

for node in nodes:
    G.add_node(node["ip"])

    for link in node["links"]:

        if link != node["ip"]:

            G.add_edge(node["ip"], link)


client.close()

pos = nx.spring_layout(G, scale=40, k=400)
nx.draw(G, pos, with_labels=True)
plt.savefig('sample_plot.png')
