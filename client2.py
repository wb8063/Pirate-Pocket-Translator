#client2.py
import socket
import pickle
import sys
import time
import argparse

class Packet():

    
    def __init__(self,sequence_number,message, checksum, ackOrNak, length, flagStatus):
        self.sequence_number = sequence_number
        self.message = message
        self.checksum = checksum
        self.ackOrNak = ackOrNak  # 1 for ACK, 0 for NAK, 2 for message
        self.length = length
        self.dotFlag = flagStatus
        
    def set_dotFlag(self, flagStatus):
        self.dotFlag = flagStatus
        
    def set_message(self,new_message):
        self.message = new_message
    
    def get_message(self):
        return self.message

    def get_sequence(self):
        return self.sequence_number
    
    def get_checksum(self):
        return self.checksum
    
    def set_checksum(self, newCheksum):
        self.checksum = newCheksum
        
    def get_ackOrNak(self):
        return self.ackOrNak
    
    def get_length(self):
        return self.length
    
    def is_valid(self):
        return self.checksum == self.calculate_checksum()
    
    def calculate_checksum(self):
        value= sum(ord(c) for c in self.message) %256
        return (value % 2) == 0
    
def split_message(message, mss):
    """Split the message into chunks of size mss."""
    return [message[i:i + mss] for i in range(0, len(message), mss)]

            
def load_pirate_dictionary(filename):
    pirate_dict = {}
    with open('pirate.csv', mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) == 2:
                english_word, pirate_word = row
                pirate_dict[english_word.strip().lower()] = pirate_word.strip()
    return pirate_dict

# Translate a sentence into pirate
def translate_to_pirate(received_message, pirate_dict):
    # Join the array into a single string
    sentence = ''.join(received_message)  # No spaces in between segments
    words = []
    
    # Split by space or punctuation while keeping them
    temp_word = ""
    for char in sentence:
        if char.isalnum() or char in "'":
            temp_word += char  # Build the current word
        else:
            if temp_word:
                words.append(temp_word)  # Add the completed word
                temp_word = ""  # Reset for next word
            words.append(char)  # Add punctuation

    # If there's a leftover word, add it
    if temp_word:
        words.append(temp_word)

    translated_words = []
    
    for word in words:
        # Check if the word is in the dictionary
        clean_word = ''.join(filter(str.isalpha, word)).lower()  # Remove punctuation for matching
        if clean_word in pirate_dict:
            translated_word = pirate_dict[clean_word]
        else:
            translated_word = word  # Keep original if no translation found
        
        # Append the translated word, maintaining original punctuation
        translated_words.append(translated_word + word[len(clean_word):])  # Keep punctuation
    
    return ''.join(translated_words)
            
def main():
    parser = argparse.ArgumentParser(description='Client for sending packets to the server.')
    parser.add_argument('port', type=int, help='Port number to connect to the server.')
    parser.add_argument('MSS', type=int, help='Maximum Segment Size.')
    parser.add_argument('corrupt', type=float, help='Corruption percentage of the packets.')
    
    args = parser.parse_args()
    
    port = args.port
    MSS = args.MSS
    corrupt_percent = args.corrupt

    user_message = input("Enter the message to send: ")
    message_chunks = split_message(user_message, MSS)

    recieved_message = []
    packet_list = []
    for i, chunk in enumerate(message_chunks):
        ob = Packet(i + 1,chunk, 0, 2, len(chunk),False)
        ob.set_checksum(ob.calculate_checksum()) #come back to later
        packet_list.append(ob)
 
    #packet_list.append(Packet(len(packet_list) + 1, "FIN",0,2,3))
    


    port = 8008
    host = socket.gethostname()
    clientSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    clientSocket.connect( (host,port) )
    for each_packet in packet_list:
        #if(ob.dotFlag == True):
        #    break
        data = pickle.dumps(each_packet)
        print("Sending",each_packet.get_sequence())
        clientSocket.send(data)
        time.sleep(1)   
        AONdata = clientSocket.recv(1024)
        #print(AONdata)
        ob= pickle.loads(AONdata)
        if ob.get_ackOrNak() == 1:  # If it's an ACK
            print(f"ACK received for sequence number: {ob.sequence_number}")
            ob.sequence_number += 1
        elif ob.get_ackOrNak() == 0:  # If it's a NAK
            print(f"NAK received for sequence number: {ob.sequence_number}. Resending...")
            #send_packet(clientSocket, data)  # Resend the original packet  
            clientSocket.send(data)  
        elif ob.get_ackOrNak() == 2: #its a regualr old message
            print("translated message recieved")
           # recieved_message.append(ob.get_message())
        print("")
    
    #while ob.dotFlag == True:
        #translated_data = clientSocket.recv(1024)
        #recieved_message = Packet
        #print(translated_data)
        #if translated_data != False:
        #    recieved_message = pickle.loads(translated_data)
        #else:
        #    print("no data")
        #recieved_message = pickle.loads(translated_data)    #trandlated data is in packet form i need it in arrya form
        
    while True:
        
        print("got packet")
        data = clientSocket.recv(1024)
        if not data:
            print("No data received, closing connection.")
            break  # Exit if no data is received
        try:
            ob = pickle.loads(data)  # Deserialize the data
        except Exception as e:
            print(f"Error deserializing data: {e}")
            continue  # Skip to the next iteration if there's an error
        if isinstance(ob, Packet):
            if ob.is_valid():
               # for eachPacket in recieved_message:
                #ob = pickle.loads(eachPacket)
                recieved_message.append(ob.get_message())
            
    print("Translated to pirate:", recieved_message)
 
                         
    
    
        
    





if __name__ == "__main__":
    main()