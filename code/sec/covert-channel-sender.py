import os
import random
import socket
import time
from scapy.layers.inet import IP, IPOption, UDP, IPOption_NOP, IPOption_Security, IPOption_LSRR, IPOption_SSRR, IPOption_RR, IPOption_Timestamp, IPOption_Traceroute
from typing import Generator
import argparse

IP_OPTIONS_HEADER_SIZE = 40
IP_OPTIONS_HEADER_OCCUPIED = 2

class Sender:
    def __init__(self, secret_message: str, noise_rate=0.3, pad_len=4, no_covert_pkt_count=50):
        self.noise_rate = noise_rate
        self.secret_message = secret_message
        self.pad_len = pad_len
        self.opt_types = [182, 186, 187, 188, 189, 191, 214, 218, 219, 220, 221, 223, 246, 250, 251, 252]
        self.host = os.getenv('INSECURENET_HOST_IP')
        self.port = 8888
        self.sent_pkt_count = 0
        self.sent_byte_count = 0
        self.no_covert_pkt_count = no_covert_pkt_count
    
    def send_covert_packets(self):
        total_sent_size = 0
        rtt_values = []

        try:
            # Create a UDP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print(f"Covert channel sender started on {self.host}:{self.port}")
            print("----------------------------------------------")
            
            if self.secret_message is None:
                print("No secret message provided, only sending noise packets.")
                index = 0
                while index < self.no_covert_pkt_count:
                    start_time = time.time()
                    sent_pkt = self.__send_noise(sock)
                    
                    # Wait for a response from the server
                    response, server = sock.recvfrom(65535)
                    print(f"Received response from {server}: {response}")
                    time.sleep(1)

                    # Calculate the total sent size
                    total_sent_size += len(bytes(sent_pkt))

                    # Calculate RTT in ms
                    rtt_values.append((time.time() - start_time) * 1000)
                    index += 1
                    print("---- END ----")
            else:
                options = self.__build_options_headers()
                print(f"Secret message: {self.secret_message}")
                index = 0
                while True:
                    if index >= len(options):
                        print("All packets sent, exiting...")
                        break

                    start_time = time.time()
                    sent_pkt = None

                    if random.random() < self.noise_rate:
                        sent_pkt = self.__send_noise(sock)
                    elif index < len(options):
                        sent_pkt = self.__send_covert_packet(sock, options[index])
                        index += 1

                    # Wait for a response from the server
                    response, server = sock.recvfrom(65535)
                    print(f"Received response from {server}: {response}")
                    time.sleep(1)

                    # Calculate the total sent size
                    total_sent_size += len(bytes(sent_pkt))

                    # Calculate RTT in ms
                    rtt_values.append((time.time() - start_time) * 1000)
                    print("---- END ----")
                    
            self.__send_finish(sock)
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            print(f"Total bytes sent: {total_sent_size} bytes")
            print(f"Average RTT: {(sum(rtt_values) / len(options)):.2f} ms")
            print(f"Throughput: {(total_sent_size / (sum(rtt_values)/1000)):.2f} bytes/s")
            sock.close()

    def __send_finish(self, sock: socket.socket) -> None:
        time.sleep(1)
        finish_pkt = IP(dst=self.host) / UDP(sport=random.randint(1024, 65535), dport=self.port) / b"Finish"
        sock.sendto(bytes(finish_pkt), (self.host, self.port))
        print("Finish packet sent.")
        # receive response from the server
        response, server = sock.recvfrom(65535)
        print(f"Received response from {server}: {response}")
        print(f"Sent {len(response)} covert bytes")
        print("Covert channel sender finished.")
        print("----------------------------------------------")
        return finish_pkt

    def __send_covert_packet(self, sock: socket.socket, option: tuple[IPOption, bytes]) -> IP:
        opt, chunk = option
        pkt = IP(dst=self.host, options=opt)

        # Inject padding
        raw_bytes = bytearray(bytes(pkt))
        header_length = (bytes(pkt)[0] & 0x0F) * 4   # Convert header length from words to bytes
        options_length = header_length - 20
        padding_length = len(chunk)
        padding_start = 20 + options_length
        raw_bytes[padding_start:padding_start+padding_length] = chunk.ljust(padding_length, b'\x00')


        sock.sendto(bytes(IP(raw_bytes)), (self.host, self.port))
        print(f"Covert message {bytes(IP(raw_bytes))} sent to {self.host}:{self.port}")

        self.sent_pkt_count += 1
        self.sent_byte_count += len(bytes(pkt))

        return pkt

    def __send_noise(self, sock: socket.socket) -> IP:
        noise_pkt = None
        print("Sending noise packet...")
        rand = random.random()
        if rand < 0.5:
            random_opt = random.choice([
                IPOption_NOP(),
                IPOption_Security(),
                IPOption_LSRR(),
                IPOption_SSRR(),
                IPOption_RR(),
                IPOption_Timestamp(),
                IPOption_Traceroute(),
            ])
            noise_pkt = IP(dst=self.host, options=[random_opt])
            print(f"Noise packet: {random_opt.__class__.__name__} option added")
        else:
            # Standard IP packet without options
            noise_pkt = IP(dst=self.host)
            print("Noise packet: plain IP")
        sock.sendto(bytes(noise_pkt), (self.host, self.port))
        self.sent_pkt_count += 1
        self.sent_byte_count += len(bytes(noise_pkt))
        return noise_pkt

    def __build_options_headers(self) -> list[(IPOption, bytes)]:
        options: list[(IPOption, bytes)] = []
        for chunk in self.__split_message():
            opt, padding = self.__create_options_header(chunk)
            options.append((opt, padding))
        return options

    def __split_message(self) -> 'Generator[bytes, None, None]':
        covert_message = self.secret_message.encode()

        i = 0
        while i < len(covert_message):
            chunk = covert_message[i:i + self.pad_len]
            i += len(chunk)
            yield chunk
    
    def __create_options_header(self, padding: bytes) -> tuple[IPOption, bytes]:
        dummy_opt_length = random.choice([6, 10, 14, 18, 22, 26, 30, 34, 38]) - self.pad_len - IP_OPTIONS_HEADER_OCCUPIED
        random_data = bytes(random.getrandbits(8) for _ in range(dummy_opt_length))
        dummy_opt_bytes = bytes([self.__select_opt_type()]) + bytes([dummy_opt_length]) + random_data

        return IPOption(dummy_opt_bytes), padding

    def __select_opt_type(self) -> int:
        return random.choice(self.opt_types)

def parse_args():
    parser = argparse.ArgumentParser(description="Covert Channel Sender")
    parser.add_argument(
        "--secret-message",
        type=str,
        help="The secret message to be sent covertly",
    )
    parser.add_argument(
        "--noise-rate",
        type=float,
        default=0.5,
        help="The rate at which noise packets are sent (0.0 to 1.0)",
    )
    parser.add_argument(
        "--pad-len",
        type=int,
        default=4,
        help="The length of padding for covert messages",
    )
    parser.add_argument(
        "--no-covert-pkt-count",
        type=int,
        default=50,
        help="The number of noise packets to send when no secret message is provided",
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    sender = Sender(
        secret_message=args.secret_message,
        noise_rate=args.noise_rate,
        pad_len=args.pad_len,
        no_covert_pkt_count=args.no_covert_pkt_count
    )
    sender.send_covert_packets()
