import socket
from scapy.layers.inet import IP, IPOption, UDP

class Receiver:
    def __init__(self):
        self.opt_types = [182, 186, 187, 188, 189, 191, 214, 218, 219, 220, 221, 223, 246, 250, 251, 252]
        self.received_messages = []
        self.port = 8888

    def start(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', self.port))
        print(f"Listening for UDP packets on port {self.port}")

        try:
            while True:
                data, addr = sock.recvfrom(65535)
                print(f"Received {len(data)} bytes from {addr}")
                try:
                    ip_pkt = IP(data)
                    # if UDP and message is Finish
                    if UDP in ip_pkt and ip_pkt[UDP].dport == self.port and b'Finish' in bytes(ip_pkt[UDP].payload):
                        print("Received Finish message, clearingg received_messages.")
                        print("".join(self.received_messages))
                        print("Clearing received messages...")
                        self.received_messages.clear()
                        sock.sendto("Finish".encode(), addr)
                        continue

                    if IP not in ip_pkt:
                        print("No IP layer found, skipping...")
                        sock.sendto("".encode(), addr)  
                        continue

                    if IP in ip_pkt and not ip_pkt.options:
                        print("No IP options found, skipping...")
                        sock.sendto("".encode(), addr)  
                        continue

                    for opt in ip_pkt.options:
                        if isinstance(opt, IPOption):
                            option_type = bytes(opt)[0]
                            print(option_type)
                            if option_type not in self.opt_types:
                                print(f"Unknown option type: {option_type}, skipping...")
                                sock.sendto("".encode(), addr)
                                continue

                            payload = bytes(opt)[2:]
                            print(f"Received message: {payload}")

                            padding_length = self.__find_pad_len(payload) + 1  # +1 for the padding length byte
                            if padding_length == 0:
                                print("No padding found, skipping...")
                                sock.sendto("".encode(), addr)  
                                continue

                            covert_message = payload[:len(payload) - padding_length]
                            print(f"Covert message: {covert_message}")

                            self.received_messages.append(covert_message.decode())
                            print("".join(self.received_messages))

                            sock.sendto(bytes("".join(self.received_messages).encode()), addr)            
                except Exception as e:
                    print(f"Error processing packet: {e}")

        except KeyboardInterrupt:
            sock.close()
            print("All received messages:")
            print("".join(self.received_messages))

    def __find_pad_len(self, message: bytes) -> int:
        # last byte of this message is reserved for the length of the padding
        if not message or len(message) < 1:
            return -1
        if message[-1] == 0:
            return -1
        return message[-1]
        
    
if __name__ == "__main__":
    receiver = Receiver()
    receiver.start()