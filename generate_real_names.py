import json
import random
from faker import Faker

fake = Faker()

# Famous people list
famous_people = [
    {"name": "Elon Musk", "attributes": ["Businessman", "Business owner", "CEO"]},
    {"name": "Barack Obama", "attributes": ["Former president of the United States"]},
    {"name": "Cristiano Ronaldo", "attributes": ["Portuguese Professional footballer"]},
    {"name": "Justin Bieber", "attributes": ["Singer", "songwriter", "Won song of the year", "Won most performed song"]}
]

# Function to generate a human name with attributes
def generate_human_name(role=None):
    if role:
        return {"name": f"{fake.first_name()} {fake.last_name()}", "attributes": [role]}
    return {"name": f"{fake.first_name()} {fake.last_name()}", "attributes": []}

# Function to possibly add famous people to anomalous nodes
def generate_social_user(anomalous=False):
    if anomalous and random.random() < 0.3:  # 30% chance to pick a famous person for anomalous nodes
        person = random.choice(famous_people)
        return {"name": person["name"], "attributes": ["famous"] + person["attributes"]}
    return generate_human_name()

# Function to possibly add "popular railway station" to anomalous nodes
def add_popular_railway_station(anomalous=False):
    if anomalous and random.random() < 0.3:  # 30% chance to add the attribute for anomalous nodes
        return "popular railway station"
    return None

# Function to update the graph with human names and popular railways
def update_graph_with_names(graph):
    anomaly_nodes = [node_key for node_key, node in graph["objects"].items() if node.get("anomaly_flag") == 1]
    for node_key, node in graph["objects"].items():
        if "developer" in node_key:
            role = "Senior Developer" if "senior_developer" in node_key else "Developer"
            human = generate_human_name(role)
            node["name"] = human["name"]
            node["attributes"] = human["attributes"]
        elif "finance" in node_key:
            human = generate_human_name("Finance Person")
            node["name"] = human["name"]
            node["attributes"] = human["attributes"]
        elif "doctor" in node_key:
            human = generate_human_name("Doctor")
            node["name"] = human["name"]
            node["attributes"] = human["attributes"]
        elif "patient" in node_key:
            human = generate_human_name("Patient")
            node["name"] = human["name"]
            node["attributes"] = human["attributes"]
        elif "social_user" in node_key:
            is_anomalous = node_key in anomaly_nodes
            human = generate_social_user(anomalous=is_anomalous)
            node["name"] = human["name"]
            node["attributes"] = human["attributes"]
        elif "plane_ticket_person" in node_key:
            human = generate_human_name("Traveler")
            node["name"] = human["name"]
            node["attributes"] = human["attributes"]
        elif "streaming_service_person" in node_key:
            human = generate_human_name("Subscriber")
            node["name"] = human["name"]
            node["attributes"] = human["attributes"]
        elif "station" in node_key:
            if "attributes" not in node:
                node["attributes"] = []
            is_anomalous = node_key in anomaly_nodes
            popular_railway = add_popular_railway_station(anomalous=is_anomalous)
            if popular_railway:
                node["attributes"].append(popular_railway)
    return graph

# Function to build the anomaly reason from scratch
def update_anomaly_reasons(graph):
    for node_key, node in graph["objects"].items():
        if node.get("anomaly_flag"):
            connected_nodes = []
            for relation in node["relations"]:
                connected_node_id = relation["object"]
                if connected_node_id in graph["objects"]:
                    connected_nodes.append(graph["objects"][connected_node_id]["name"])
            node["anomaly_reason"] = f"Huge node with many edges since it is connected to the nodes: {', '.join(connected_nodes)}"
    return graph

# Function to process the entire dataset
def process_dataset(input_file, output_file):
    with open(input_file, "r") as f:
        dataset = json.load(f)
    
    for graph_key in dataset:
        dataset[graph_key] = update_graph_with_names(dataset[graph_key])
        dataset[graph_key] = update_anomaly_reasons(dataset[graph_key])
    
    with open(output_file, "w") as f:
        json.dump(dataset, f, indent=4)

# Process the dataset
input_file = "extended_graph_dataset.json"
output_file = "updated_graph_dataset_with_names.json"
process_dataset(input_file, output_file)
