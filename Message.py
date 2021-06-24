from Signature import Signature

class Message:
    def __init__(self, payload, sender_id, round_sent, signatures: list[Signature] = [], reciver_id = None, is_valid = None):
        self.payload = payload
        self.sender_id = sender_id
        self.round_sent = round_sent
        self.signatures = signatures
        self.reciver_id = reciver_id
        self.is_valid = is_valid
