import json
import random

# Define node categories and relationship types for the extended contexts
senior_developers = ['Senior Developer A', 'Senior Developer B', 'Senior Developer C']
developers = ['Dev A', 'Dev B', 'Dev C', 'Dev D']
repos = ['Repo 1', 'Repo 2', 'Repo 3', 'Repo 4', 'Repo 5', 'Repo 6', 'Repo 7', 'Repo 8', 'Repo 9', 'Repo 10', 'Repo 11', 'Repo 12']
finance_people = ['Fin A', 'Fin B', 'Fin C']
credit_cards = ['Credit Card 1', 'Credit Card 2', 'Credit Card 3']
locations = ['New York City', 'Houston', 'Los Angeles', 'San Diego', 'Chicago', 'Philadelphia', 'Dallas', 'Phoenix', 'San Antonio', 'Indianapolis']
streaming_services = ['Service A', 'Service B', 'Service C', 'Service D', 'Service E', 'Service F', 'Service G', 'Service H', 'Service I']
plane_tickets = ['Ticket 1', 'Ticket 2', 'Ticket 3', 'Ticket 4', 'Ticket 5', 'Ticket 6', 'Ticket 7', 'Ticket 8', 'Ticket 9']
doctors = ['Doc A', 'Doc B', 'Doc C']
patients = ['Patient 1', 'Patient 2', 'Patient 3']
medications = ['Med 1', 'Med 2', 'Med 3', 'Med 4', 'Med 5', 'Med 6', 'Med 7', 'Med 8', 'Med 9']
species = ['Species A', 'Species B', 'Species C', 'Species D', 'Species E', 'Species F', 'Species G', 'Parasite', 'Mutualistic Species', 'Keystone Species']
food_chain = ['Plant', 'Herbivore', 'Carnivore']
social_users = ['Elon Musk', 'Barack Obama', 'Cristiano Ronaldo', 'Justin Bieber', 'User 1', 'User 2', 'User 3', 'User 4', 'User 5']
average_joe = ['Joe']

relationship_types = ['git_push', 'approve_transaction', 'uses', 'subscribes_to', 'purchases', 'prescribes', 'eats', 'follows']

# Predefined mean and standard deviation for number of edges per node
mean_edges = 3
std_edges = 1

# Function to create a normal graph ensuring nodes stay within 2 standard deviations of the mean
def create_normal_graph(node_set, rel_set):
    nodes = {}
    node_ids = []

    # Create nodes
    for category, names in node_set.items():
        for name in names:
            node_id = f'{category.lower().replace(" ", "_")}_{len(nodes) + 1}'
            nodes[node_id] = {
                'name': name,
                'attributes': [category],
                'relations': []
            }
            node_ids.append(node_id)

    # Create relationships
    for category, rels in rel_set.items():
        #if category == 'Senior Developer' and random.random() > 0.2:
        #    continue
        for start, rel, end_list in rels:
            start_nodes = [node_id for node_id, node in nodes.items() if category in node['attributes']]
            end_nodes = [node_id for node_id, node in nodes.items() if any(e in node['attributes'] for e in end_list)]
            for start_node in start_nodes:
                num_edges = random.randint(max(1, mean_edges - 2 * std_edges), mean_edges + 2 * std_edges)
                for _ in range(num_edges):
                    end_node = random.choice(end_nodes)
                    if not any(r['object'] == end_node and r['name'] == rel for r in nodes[start_node]['relations']):
                        nodes[start_node]['relations'].append({
                            'object': end_node,
                            'name': rel
                        })
    return nodes

# Function to create a random graph with anomalies
def create_anomalous_graph(node_set, rel_set, context):
    nodes = create_normal_graph(node_set, rel_set)
    add_anomalies(nodes, context)
    return nodes

# Function to add anomalies (page_rank anomaly and transaction approval anomaly)
def add_anomalies(nodes, context):
    existing_relationships = set((rel['object'], rel['name'], node_id) for node_id, node in nodes.items() for rel in node['relations'])
    
    if context == 'developer_repos':
        developer_nodes = [node_id for node_id, node in nodes.items() if 'Developer' in node['attributes']]
        if developer_nodes:
            anomaly_node = random.choice(developer_nodes)
            nodes[anomaly_node]['relations'] = []
            nodes[anomaly_node]['anomaly_flag'] = 1
            connected_nodes = []
            possible_repos = [node_id for node_id, node in nodes.items() if 'Repository' in node['attributes']]
            additional_repos = random.sample(possible_repos, random.randint(mean_edges + 2 * std_edges + 1, mean_edges + 2 * std_edges + 3))
            
            for repo in additional_repos:
                relationship = (anomaly_node, 'git_push', repo)
                if relationship not in existing_relationships:
                    nodes[anomaly_node]['relations'].append({
                        'object': repo,
                        'name': 'git_push'
                    })
                    connected_nodes.append(nodes[repo]['name'])
                    existing_relationships.add(relationship)

            nodes[anomaly_node]['anomaly_reason'] = f"Huge node with many edges since it is connected to the nodes: {', '.join(connected_nodes)}"

    elif context == 'credit_card_locations':
        credit_card_nodes = [node_id for node_id, node in nodes.items() if 'Credit Card' in node['attributes']]
        if credit_card_nodes:
            anomaly_node = random.choice(credit_card_nodes)
            nodes[anomaly_node]['relations'] = []
            nodes[anomaly_node]['anomaly_flag'] = 1
            connected_nodes = []
            possible_locations = [node_id for node_id, node in nodes.items() if 'Location' in node['attributes']]
            additional_locations = random.sample(possible_locations, random.randint(mean_edges + 2 * std_edges + 1, mean_edges + 2 * std_edges + 3))
            
            for location in additional_locations:
                relationship = (anomaly_node, 'uses', location)
                if relationship not in existing_relationships:
                    nodes[anomaly_node]['relations'].append({
                        'object': location,
                        'name': 'uses'
                    })
                    connected_nodes.append(nodes[location]['name'])
                    existing_relationships.add(relationship)

            nodes[anomaly_node]['anomaly_reason'] = f"Huge node with many edges since it is connected to the nodes: {', '.join(connected_nodes)}"

    elif context == 'person_subscriptions':
        person_nodes = [node_id for node_id, node in nodes.items() if 'streaming_service_person' in node['attributes']]
        if person_nodes:
            anomaly_node = random.choice(person_nodes)
            nodes[anomaly_node]['relations'] = []
            nodes[anomaly_node]['anomaly_flag'] = 1
            connected_nodes = []
            possible_services = [node_id for node_id, node in nodes.items() if 'Streaming Service' in node['attributes']]
            additional_services = random.sample(possible_services, random.randint(mean_edges + 2 * std_edges + 1, mean_edges + 2 * std_edges + 3))
            
            for service in additional_services:
                relationship = (anomaly_node, 'subscribes_to', service)
                if relationship not in existing_relationships:
                    nodes[anomaly_node]['relations'].append({
                        'object': service,
                        'name': 'subscribes_to'
                    })
                    connected_nodes.append(nodes[service]['name'])
                    existing_relationships.add(relationship)

            nodes[anomaly_node]['anomaly_reason'] = f"Huge node with many edges since it is connected to the nodes: {', '.join(connected_nodes)}"

    elif context == 'person_plane_tickets':
        person_nodes = [node_id for node_id, node in nodes.items() if 'plane_ticket_person' in node['attributes']]
        if person_nodes:
            anomaly_node = random.choice(person_nodes)
            nodes[anomaly_node]['relations'] = []
            nodes[anomaly_node]['anomaly_flag'] = 1
            connected_nodes = []
            possible_tickets = [node_id for node_id, node in nodes.items() if 'Plane Ticket' in node['attributes']]
            additional_tickets = random.sample(possible_tickets, random.randint(mean_edges + 2 * std_edges + 1, mean_edges + 2 * std_edges + 3))
            
            for ticket in additional_tickets:
                relationship = (anomaly_node, 'purchases', ticket)
                if relationship not in existing_relationships:
                    nodes[anomaly_node]['relations'].append({
                        'object': ticket,
                        'name': 'purchases'
                    })
                    connected_nodes.append(nodes[ticket]['name'])
                    existing_relationships.add(relationship)

            nodes[anomaly_node]['anomaly_reason'] = f"Huge node with many edges since it is connected to the nodes: {', '.join(connected_nodes)}"

    if context == 'doctor_medications':
        # Find patient nodes
        patient_nodes = [node_id for node_id, node in nodes.items() if 'Patient' in node['attributes']]
        if patient_nodes:
            # Choose a random patient node for the anomaly
            anomaly_node = random.choice(patient_nodes)
            nodes[anomaly_node]['relations'] = []  # Reset relations to avoid duplications
            nodes[anomaly_node]['anomaly_flag'] = 1
            connected_nodes = []
            
            # Find possible medication nodes
            possible_meds = [node_id for node_id, node in nodes.items() if 'Medication' in node['attributes']]
            
            # Select a random number of medications to connect to the anomaly node
            additional_meds = random.sample(possible_meds, random.randint(mean_edges + 2 * std_edges + 1, mean_edges + 2 * std_edges + 3))
            
            for med in additional_meds:
                relationship = (anomaly_node, 'takes', med)
                if relationship not in existing_relationships:
                    nodes[anomaly_node]['relations'].append({
                        'object': med,
                        'name': 'takes'
                    })
                    connected_nodes.append(nodes[med]['name'])
                    existing_relationships.add(relationship)
            
            nodes[anomaly_node]['anomaly_reason'] = f"Patient node with too many connections to medications: {', '.join(connected_nodes)}"

    elif context == 'species_food_chain':
        species_nodes = [node_id for node_id, node in nodes.items() if 'Species' in node['attributes']]
        if species_nodes:
            anomaly_node = random.choice(species_nodes)
            nodes[anomaly_node]['relations'] = []
            nodes[anomaly_node]['anomaly_flag'] = 1
            connected_nodes = []
            possible_prey = [node_id for node_id, node in nodes.items() if 'Species' in node['attributes'] and node_id != anomaly_node]
            additional_prey = random.sample(possible_prey, random.randint(mean_edges + 2 * std_edges + 1, mean_edges + 2 * std_edges + 3))
            
            for prey in additional_prey:
                relationship = (anomaly_node, 'eats', prey)
                if relationship not in existing_relationships:
                    nodes[anomaly_node]['relations'].append({
                        'object': prey,
                        'name': 'eats'
                    })
                    connected_nodes.append(nodes[prey]['name'])
                    existing_relationships.add(relationship)

            nodes[anomaly_node]['anomaly_reason'] = f"Huge node with many edges since it is connected to the nodes: {', '.join(connected_nodes)}"

    elif context == 'social_followers':
        person_nodes = [node_id for node_id, node in nodes.items() if 'social_user' in node['attributes']]
        if person_nodes:
            anomaly_node = random.choice(person_nodes)
            nodes[anomaly_node]['relations'] = []
            nodes[anomaly_node]['anomaly_flag'] = 1
            connected_nodes = []
            possible_followers = [node_id for node_id, node in nodes.items() if 'social_user' in node['attributes'] and node_id != anomaly_node]
            additional_followers = random.sample(possible_followers, random.randint(mean_edges + 2 * std_edges + 1, mean_edges + 2 * std_edges + 3))
            
            for follower in additional_followers:
                relationship = (anomaly_node, 'connected_to', follower)
                if relationship not in existing_relationships:
                    nodes[anomaly_node]['relations'].append({
                        'object': follower,
                        'name': 'connected_to'
                    })
                    connected_nodes.append(nodes[follower]['name'])
                    existing_relationships.add(relationship)

            nodes[anomaly_node]['anomaly_reason'] = f"Huge node with many edges since it is connected to the nodes: {', '.join(connected_nodes)}"
    
    elif context == 'transportation_network':
        station_nodes = [node_id for node_id, node in nodes.items() if 'Station' in node['attributes']]
        if station_nodes:
            anomaly_node = random.choice(station_nodes)
            nodes[anomaly_node]['anomaly_flag'] = 1
            connected_nodes = []
            possible_connections = [node_id for node_id, node in nodes.items() if 'Station' in node['attributes'] and node_id != anomaly_node]
            additional_connections = random.sample(possible_connections, random.randint(mean_edges + 2 * std_edges + 1, mean_edges + 2 * std_edges + 3))
            
            for connection in additional_connections:
                relationship = (anomaly_node, 'connects_to', connection)
                if relationship not in existing_relationships:
                    nodes[anomaly_node]['relations'].append({
                        'object': connection,
                        'name': 'connects_to'
                    })
                    connected_nodes.append(nodes[connection]['name'])
                    existing_relationships.add(relationship)

            nodes[anomaly_node]['anomaly_reason'] = f"Huge node with many edges since it is connected to the nodes: {', '.join(connected_nodes)}"
    
# Define the different contexts with normal and anomalous scenarios
contexts = {
    'developer_repos': {
        'node_set': {
            'Developer': developers,
            'Senior Developer': senior_developers,
            'Repository': repos,
            'Finance': finance_people
        },
        'rel_set': {
            'Developer': [('Developer', 'git_push', ['Repository'])],
            'Senior Developer': [('Senior Developer', 'git_push', ['Repository']), ('Senior Developer', 'manages', ['Developer'])],
            'Finance': [('Finance', 'approve_transaction', ['Developer', 'Finance'])]
        }
    },
    'credit_card_locations': {
        'node_set': {
            'Credit Card': credit_cards,
            'Location': locations
        },
        'rel_set': {
            'Credit Card': [('Credit Card', 'uses', ['Location'])]
        }
    },
    'person_subscriptions': {
        'node_set': {
            'streaming_service_person': finance_people + social_users + average_joe,
            'Streaming Service': streaming_services
        },
        'rel_set': {
            'streaming_service_person': [('streaming_service_person', 'subscribes_to', ['Streaming Service'])]
        }
    },
    'person_plane_tickets': {
        'node_set': {
            'plane_ticket_person': finance_people + average_joe,
            'Plane Ticket': plane_tickets,
            'Location': locations
        },
        'rel_set': {
            'plane_ticket_person': [('plane_ticket_person', 'purchases', ['Plane Ticket'])]
        }
    },
    'doctor_medications': {
        'node_set': {
            'Doctor': doctors,
            'Patient': patients,
            'Medication': medications
        },
        'rel_set': {
            'Patient': [('Patient', 'takes', ['Medication'])],
            'Doctor': [('Doctor', 'physician for', ['Patient'])]
        }
    },
    'species_food_chain': {
        'node_set': {
            'Species': species,
            'Food Chain': food_chain
        },
        'rel_set': {
            'Species': [('Species', 'eats', ['Species'])]
        }
    },
    'social_followers': {
        'node_set': {
            'social_user': social_users + average_joe
        },
        'rel_set': {
            'social_user':[('social_user', 'connected_to', ['social_user'])]
        }
    },
    'transportation_network': {
        'node_set': {
            'Station': ['Station 1', 'Station 2', 'Station 3', 'Station 4', 'Station 5', 'Station 6', 'Station 7', 'Station 8', 'Station 9'],
            'Train': ['Train 1', 'Train 2', 'Train 3', 'Train 4', 'Train 5', 'Train 6', 'Train 7', 'Train 8', 'Train 9']
        },
        'rel_set': {
            'Station': [('Station', 'connects_to', ['Station'])],
            'Train': [('Train', 'runs_on', ['Station'])]
        }
    }
}

# Generate dataset with both normal and anomalous graphs
dataset = {}
graph_id = 1
for context, data in contexts.items():
    # Create 50 normal graphs
    for i in range(1, 51):
        graph_id_str = f'graph_{graph_id}_normal'
        nodes = create_normal_graph(data['node_set'], data['rel_set'])
        dataset[graph_id_str] = {
            'objects': nodes
        }
        graph_id += 1
    
    # Create 50 anomalous graphs
    for i in range(1, 51):
        graph_id_str = f'graph_{graph_id}_anomalous'
        nodes = create_anomalous_graph(data['node_set'], data['rel_set'], context)
        dataset[graph_id_str] = {
            'objects': nodes
        }
        graph_id += 1

# Save to JSON file
with open('extended_graph_dataset.json', 'w') as f:
    json.dump(dataset, f, indent=4)

# Print sample output
print(json.dumps(dataset, indent=4))
