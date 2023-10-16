import networkx as nx
import matplotlib.pyplot as plt

G = nx.Graph()
G.add_edge("10.0.0.0", "10.0.0.1")

nx.draw(G, with_labels=True, font_weight='bold')
plt.savefig('sample_plot.png')
