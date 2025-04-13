import socket
from scapy.all import IP
from scapy.layers.inet import IPOption
import argparse

class Receiver:
    def __init__(self, opt_type=0x99, pad_len=0):
        self.opt_type = opt_type
        self.pad_len = pad_len
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
                    if IP in ip_pkt:
                        if ip_pkt.options:
                            for opt in ip_pkt.options:
                                if isinstance(opt, IPOption):
                                    option_type = bytes(opt)[0]
                                    if option_type != self.opt_type:
                                        continue
                                    payload = bytes(opt)[2:]
                                    print(f"Received covert message: {payload}")
                                    covert_message = payload[:len(payload) - self.pad_len]
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

def parse_args():
    parser = argparse.ArgumentParser(description="Covert Channel Receiver")
    parser.add_argument(
        "--opt-type",
        type=int,
        default=0x99,
        help="The type of the IP option to be used in hexadecimal",
    )
    parser.add_argument(
        "--pad-len",
        type=int,
        default=0,
        help="The length of padding to be added",
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    receiver = Receiver(opt_type=args.opt_type, pad_len=args.pad_len)
    receiver.start()