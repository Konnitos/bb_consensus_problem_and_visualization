from math import dist
from Message import Message
from Node import Node, generate_hash
import random

def run_bb_problem(number_of_generals:int, number_of_traitors:int = 0, force_traitor_leader = False):
    network = build_network(number_of_generals, number_of_traitors, force_traitor_leader)
    public_keys = {id:node.public_key for (id,node) in network.items()}
    get_consensus(number_of_traitors + 1, network, public_keys)
    
def build_network(general_num, traitor_num, force_traitor_leader, node_defult = 1):
    nodes = {}

    leader = Node(0, node_defult ,True)
    
    if(traitor_num == general_num):
        leader.is_traitor = True
        traitor_num -= 1
    elif(force_traitor_leader == True):
        leader.is_traitor = True
        traitor_num -= 1
    elif(random.randint(0,1) == 1 and traitor_num > 0):
        leader.is_traitor = True
        traitor_num -= 1

    nodes[leader.id] = leader
    
    for x in range(1 , general_num):
      general = Node(x, node_defult)

      if(traitor_num > 0):
          general.is_traitor = True
          traitor_num -= 1  

      nodes[general.id] = general

    return nodes

def get_consensus(rounds, network: dict[int:Node], public_keys):
    leader_node = network[0]
    general_nodes:list[Node] = [node for (id,node) in network.items() if id != 0]

    if(leader_node.is_traitor):
        traitor_leader_activity(leader_node, general_nodes)
    else:
        message_payload = random.randint(0,1)
        message = Message(message_payload, leader_node.id, 1, [leader_node.sign(message_payload)])
        broadcast(message, general_nodes)

    for i in range(0,rounds):
        receive_messages_from_broadcast(general_nodes)
        process_unseen_messages(general_nodes, leader_node, i + 1, public_keys)

    for node in general_nodes:
        node.make_decision()

def broadcast(message: Message, receiving_nodes: list[Node]):
    for node in receiving_nodes:
        if(node.id != message.sender_id):
            node.to_be_received_messages.append(message)

def receive_messages_from_broadcast(nodes: list[Node]):
    for node in nodes:
        node.unseen_messages = node.to_be_received_messages
        node.to_be_received_messages = []

def process_unseen_messages(nodes: list[Node], leader_node, round_num, public_keys):
    for node in nodes:
        for message in node.unseen_messages:
            if(node.validate_message(message, public_keys, round_num)):
                if(node.is_traitor):
                    traitor_general_activity(node, leader_node, message, nodes, round_num)
                else:
                    broadcast(Message(message.payload, node.id, round_num, message.signatures + [node.sign(message.payload)]), nodes)
        
        node.unseen_messages = []

def traitor_leader_activity(leader_node: Node, general_nodes: list[Node]):
    payload = random.randint(0,1)
    for node in general_nodes:
        if(random.randint(0,1) == 1):
            payload = 1 if payload == 0 else 0
            message = Message(payload, leader_node.id, 1, [leader_node.sign(payload)])
            node.to_be_received_messages.append(message)
        else:
            message = Message(None, leader_node.id, 1, None)
            node.to_be_received_messages.append(message)
            
def traitor_general_activity(traitor_general_node: Node, leader_node: Node, message, nodes: list[Node], round_num):
    for node in nodes:
        if(node.id != traitor_general_node.id):
            traitor_action = random.randint(0,2)
            if(traitor_action == 0):
                traitor_payload = 1 if message.payload == 0 else 1

                if(leader_node.is_traitor and len(message.signatures) == 1):    
                    next_message = Message(traitor_payload, traitor_general_node.id, round_num, [leader_node.sign(traitor_payload) , traitor_general_node.sign(traitor_payload)])
                    node.to_be_received_messages.append(next_message)

                else: 
                    next_message = Message(traitor_payload, traitor_general_node.id, round_num, message.signatures + [traitor_general_node.sign(message.payload)])    
                    node.to_be_received_messages.append(next_message)

            elif(traitor_action == 1):
                next_message = Message(message.payload, traitor_general_node.id, round_num, message.signatures + [traitor_general_node.sign(message.payload)])
                node.to_be_received_messages.append(next_message)

            elif(traitor_action == 2):
                next_message = Message(None, traitor_general_node.id, round_num, [None])
                node.to_be_received_messages.append(next_message)
            
run_bb_problem(4, 3, True)