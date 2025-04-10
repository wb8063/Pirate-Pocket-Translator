import pickle
import random

class Packet:
    def __init__(self, sequence_number, checksum, ack_or_nak, length, message):
        self.sequence_number = sequence_number
        self.checksum = checksum
        self.ack_or_nak = ack_or_nak
        self.length = length
        self.message = message

    def calculate_checksum(self):
        return sum(ord(c) for c in self.message) % 256

    def is_valid(self):
        return self.checksum == self.calculate_checksum()
