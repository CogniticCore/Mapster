import networkx as nx
from networkx.readwrite import json_graph

# Your JSON data (simplified version for demonstration)
data = {
    "links": [
        {"source": "Fingerstyle to play Moonlight Sonata III on Classical Guitar", "target": "Reading Sheet Music for Guitar"},
        {"source": "Fingerstyle to play Moonlight Sonata III on Classical Guitar", "target": "Basic Guitar Techniques and Basics"},
        {"source": "Fingerstyle to play Moonlight Sonata III on Classical Guitar", "target": "Basic Music Theory"},
        {"source": "Reading Sheet Music for Guitar", "target": "Rhythm and Timing"},
        {"source": "Reading Sheet Music for Guitar", "target": "Interval Recognition in Music"},
        {"source": "Reading Sheet Music for Guitar", "target": "Guitar Tuning Techniques"},
        {"source": "Classical Guitar Techniques", "target": "Basic Guitar Knowledge"},
        {"source": "Classical Guitar Techniques", "target": "Classical Guitar Fingerstyle Techniques"},
        {"source": "Classical Guitar Techniques", "target": "Basic Music Theory"},
        {"source": "Basic Notation", "target": "Music Theory"},
        {"source": "Basic Notation", "target": "Basic Guitar Techniques and Basics"},
        {"source": "Basic Guitar Techniques and Basics", "target": "Guitar Anatomy"},
        {"source": "Basic Guitar Techniques and Basics", "target": "Basic Music Theory"},
        {"source": "Basic Music Theory", "target": "Basic Notation"},
        {"source": "Basic Music Theory", "target": "Scales and Intervals in Music Theory"},
        {"source": "Scales and Intervals in Music Theory", "target": "Basic Guitar Techniques and Basics"},
        {"source": "Scales and Intervals in Music Theory", "target": "Basic Music Theory"},
        {"source": "Interval Recognition in Music", "target": "Ear Training"},
        {"source": "Interval Recognition in Music", "target": "Musical Notation"},
        {"source": "Guitar Tuning Techniques", "target": "Guitar Anatomy"}
    ]
}

# Create a directed graph from the JSON data
G = nx.DiGraph()

# Add edges to the graph
for link in data["links"]:
    G.add_edge(link["source"], link["target"])

# Check for cycles
try:
    cycle = nx.find_cycle(G, orientation='original')
    print("Cycle detected:", cycle)
except nx.NetworkXNoCycle:
    print("No cycles detected.")
