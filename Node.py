from Signature import Signature
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Message import Message

class Node:
    def __init__(self, id, defult_value, is_leader = False, is_traitor = False):
        self.id = id
        self.defult_value = defult_value
        self.is_leader = is_leader
        self.is_traitor = is_traitor

        rsakey = RSA.generate(1024)

        self.private_key = rsakey.export_key()
        self.public_key = rsakey.public_key().export_key()
        self.to_be_received_messages: list[Message] = []
        self.unseen_messages: list[Message] = []
        self.valid_messages: list[Message] = []
        self.all_messages: list[Message] = []
        self.valid_message_payloads: set[int] = set()
        self.consensus_decision = None

    def sign(self, payload):
        hash = generate_hash(payload)
        signature_value = PKCS1_v1_5.new(RSA.import_key(self.private_key)).sign(hash)
        return Signature(signature_value , self.id)

    def validate_message(self, message: Message, public_keys: dict[int:bytes], current_round):
        self.all_messages.append(message)

        if(message.payload == None or message.signatures == None):
            return False

        if(message.signatures[0].signer_id != 0):
            return False   

        if({x.signer_id for x in message.signatures}.__contains__(self.id)):
            return False

        if(len(message.signatures) != current_round):
            return False

        if(len({x.value for x in message.signatures}) != len(message.signatures)):
            return False

        for signature in message.signatures:
            if(PKCS1_v1_5.new(RSA.import_key(public_keys[signature.signer_id])).verify(generate_hash(message.payload),signature.value) != True):
                return False 

        self.valid_messages.append(message)
        self.valid_message_payloads.add(message.payload)
        return True
    
    def make_decision(self):
        if(len(self.valid_message_payloads) != 1):
            self.consensus_decision = self.defult_value
            
            if(self.is_traitor != True):
                print(f'I am general node {self.id}, my valid payload set is {self.valid_message_payloads} and we have to defult to {self.consensus_decision}')
        else:
            self.consensus_decision = self.valid_message_payloads.pop()
            self.valid_message_payloads.add(self.consensus_decision)
            if(self.is_traitor != True):
                print(f'I am general node {self.id}, my valid payload set is {self.valid_message_payloads} and I say we {self.consensus_decision}')

def generate_hash(value):
    return SHA256.new(bytes(value))