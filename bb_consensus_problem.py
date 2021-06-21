from math import dist
from Message import Message
from Node import Node, generate_hash
import random

def run_bb_problem(number_of_generals:int, number_of_traitors:int = 0, force_traitor_leader = False):
    network = build_network(number_of_generals, number_of_traitors , force_traitor_leader)
    public_keys = {id:node.public_key for (id,node) in network.items()}
    get_consensus(number_of_traitors + 1, network, public_keys)

def build_network(general_num, traitor_num, froce_traitor_leader, node_defult = 1):
    nodes = {}
    
    leader = Node(0, node_defult ,True)
    nodes[leader.id] = leader
    
    for x in range(1 , general_num):
      general = Node(x, node_defult)
      nodes[general.id] = general

    return nodes

def get_consensus(rounds, network: dict[int:Node], public_keys):
    leader_node = network[0]
    general_nodes:list[Node] = [node for (id,node) in network.items() if id != 0]

    message_payload = random.randint(0,1)
    message = Message(message_payload, leader_node.id, 1, [leader_node.sign(message_payload)])
    broadcast(message, general_nodes)

    for i in range(0,rounds):
        process_unseen_messages(general_nodes, i + 1, public_keys)

    for node in general_nodes:
        node.make_decision()

def broadcast(message: Message, receiving_nodes: list[Node]):
    for node in receiving_nodes:
        node.unseen_messages.append(message)

def process_unseen_messages(nodes: list[Node], round_num, public_keys):
    for node in nodes:
        other_general_nodes = [x for x in nodes if x.id != node.id]
        for message in node.unseen_messages:
            if(node.validate_message(message, public_keys)):
              broadcast(Message(message.payload, node.id, round_num, message.signatures + [node.sign(message.payload)]), other_general_nodes)
        
        node.unseen_messages = []
        
run_bb_problem(4)