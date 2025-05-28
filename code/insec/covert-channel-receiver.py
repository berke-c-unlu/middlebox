import socket
from scapy.layers.inet import IP, UDP
import argparse

class Receiver:
    def __init__(self, pad_len=4):
        self.opt_types = [182, 186, 187, 188, 189, 191, 214, 218, 219, 220, 221, 223, 246, 250, 251, 252]
        self.received_messages = []
        self.port = 8888
        self.pad_len = pad_len
        self.received_pkt_count = 0
        self.received_byte_count = 0

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

                    if IP in ip_pkt and not ip_pkt.options:
                        print("No IP options found, skipping...")
                        sock.sendto("".encode(), addr)  
                        continue

                    options_len = sum(len(opt) for opt in ip_pkt.options)

                    raw = bytes(ip_pkt)
                    start = 20 + options_len
                    self.received_messages.append(raw[start:start+self.pad_len].rstrip(b'\x00').decode())
                    print(f"raw packet: {raw}")
                    print(f"Received covert message: {self.received_messages[-1]}")
                            
                    sock.sendto(bytes("".join(self.received_messages).encode()), addr)            
                except Exception as e:
                    print(f"Error processing packet: {e}")

        except KeyboardInterrupt:
            sock.close()
            print("All received messages:")
            print("".join(self.received_messages))

def parse_args():
    parser = argparse.ArgumentParser(description="Covert Channel Sender")
    parser.add_argument(
        "--pad-len",
        type=int,
        default=4,
        help="The length of padding for covert messages",
    )
    return parser.parse_args()
    
if __name__ == "__main__":
    args = parse_args()
    receiver = Receiver(args.pad_len)
    receiver.start()