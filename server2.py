#server2.py
import socket
import pickle
import sys
import csv
import argparse
import time


class Packet():


    def __init__(self,sequence_number,message, checksum, ackOrNak, length, dotFlag):
        self.sequence_number = sequence_number
        self.message = message
        self.checksum = checksum
        self.ackOrNak = ackOrNak  # 1 for ACK, 0 for NAK, 2 for message
        self.length = length
        self.dotFlag = dotFlag
        
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
        return value % 2 == 0
    
            
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

def split_message(message, mss):
    """Split the message into chunks of size mss."""
    return [message[i:i + mss] for i in range(0, len(message), mss)]


def main():
    parser = argparse.ArgumentParser(description='Client for sending packets to the server.')
    parser.add_argument('port', type=int, help='Port number to connect to the server.')
    parser.add_argument('MSS', type=int, help='Maximum Segment Size.')
    parser.add_argument('corrupt', type=float, help='Corruption percentage of the packets.')
    
    args = parser.parse_args()
    
    port = args.port
    MSS = args.MSS
    corrupt_percent = args.corrupt


    port = 8008
    host = socket.gethostname()
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind( ('',port) )
    
    print("Server is listening")

    serverSocket.listen(1)

    connection,addr = serverSocket.accept()
    print("client connected")
    received_messages = []
    while True:
        print("got packet")
        data = connection.recv(1024)
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
                print("Packet is valid!")
                ack_packet = Packet(ob.sequence_number,"", True, 1, 0, False)
                #send_packet(connection, ack_packet)
                picAk = pickle.dumps(ack_packet)
                received_messages.append(ob.get_message())  
                connection.send(picAk)
                print("Sent ACK for packet:", ob.sequence_number)
                
            
                if ob.get_message() and ob.get_message()[-1] in ".!?":
                    print("Punctuation encountered. Stopping packet acceptance.")
                    #received_messages.append(ob.get_message())
                    pirate_dict = load_pirate_dictionary('pirate.csv')
                    translated_sentence = translate_to_pirate(received_messages, pirate_dict)
                    print(translated_sentence)
                    message_chunks = split_message(translated_sentence, MSS)
                    packet_list = []
                    #serverSocket.connect( (host,port) )
                    for i, chunk in enumerate(message_chunks):
                        ob = Packet(i + 1,chunk, 0, 2, len(chunk),False)
                        ob.set_checksum(ob.calculate_checksum()) #come back to later
                        packet_list.append(ob)
                        
                    for each_packet in packet_list:
                        print(each_packet)
                        data = pickle.dumps(each_packet) #turn into byte
                        print("Sending",each_packet.get_sequence())
                        connection.send(data)
                        time.sleep(1)   
                    print("Translated to pirate:", translated_sentence)
                    break
                   # translated_packet= Packet(ob.sequence_number,translated_sentence,True,1,len(translated_sentence),True)
                    #translated_byte= pickle.dumps(translated_packet)
                    #connection.send(translated_byte)
                    print("Server done")
                      # Stop accepting more packets
                
                # Check if the last character of the message is punctuation
            else :
                print("Packet is not valid, retransmitting.")
                nak_packet = Packet(ob.sequence_number,"",False,0,0,False)
                #send_packet(connection, nak_packet)
                picNak = pickle.dumps(nak_packet)
                connection.send(picNak)
                print("Sent NAK for packet:", ob.sequence_number)
                
    #serverSocket.close()
    #connection,addr = serverSocket.accept()       
    #pirate_dict = load_pirate_dictionary('pirate.csv')
    #translated_sentence = translate_to_pirate(received_messages, pirate_dict)
    #print("Translated to pirate:", translated_sentence)
    #translated_packet= Packet(1,translated_sentence,True,2,len(translated_sentence))
    #translated_byte= pickle.dumps(translated_sentence)
    #connection.send(translated_byte)
       # print(ob.get_message())
        #print(ob.get_sequence())
        #print("")
        #if ob.get_message() == "FIN":
         #   break
    
    #make recieved messages a byte
    #codeToSend= pickle.dumps(received_messages)
    #send to client
    #connection.send(codeToSend)
    #print("Server done")







if __name__ == "__main__":
    main()