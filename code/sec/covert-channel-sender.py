import os
import random
import socket
import time
from scapy.layers.inet import IP, IPOption, UDP, ICMP
from typing import Generator
import argparse

IP_OPTIONS_HEADER_SIZE = 40
IP_OPTIONS_HEADER_OCCUPIED = 2
IP_OPTIONS_PADDING_LENGTH = 1

class Sender:
    def __init__(self,secret_message: str, packet_rate=1.0, noise_rate=0.3):
        self.noise_rate = noise_rate
        self.secret_message = secret_message
        self.opt_types = [182, 186, 187, 188, 189, 191, 214, 218, 219, 220, 221, 223, 246, 250, 251, 252]
        self.pad_chars = [i for i in range(256)]
        self.packet_rate = packet_rate
        self.host = os.getenv('INSECURENET_HOST_IP')
        self.port = 8888
        self.delay = 1 / packet_rate

        # Max ip options header size is 40 bytes, and the first 2 bytes are occupied by the option type and length
        # 1 byte is reserved for the padding length
        self.available_space_in_packet = IP_OPTIONS_HEADER_SIZE - IP_OPTIONS_HEADER_OCCUPIED - IP_OPTIONS_PADDING_LENGTH
    
    def send_covert_packets(self):
        pkts = self.__build_options_headers()

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
                while index < random.randint(5, 750):
                    start_time = time.time()
                    sent_pkt = self.__send_noise(sock)
                    
                    # Wait for a response from the server
                    response, server = sock.recvfrom(65535)
                    print(f"Received response from {server}: {response}")
                    time.sleep(self.delay)

                    # Calculate the total sent size
                    total_sent_size += len(bytes(sent_pkt))

                    # Calculate RTT in ms
                    rtt_values.append((time.time() - start_time) * 1000)
                    print("---- END ----")
            else:
                print(f"Secret message: {self.secret_message}")
                index = 0
                while True:
                    if index >= len(pkts):
                        print("All packets sent, exiting...")
                        break

                    start_time = time.time()
                    sent_pkt = None

                    if random.random() < self.noise_rate:
                        sent_pkt = self.__send_noise(sock)
                    elif index < len(pkts):
                        sent_pkt = self.__send_covert_packet(sock, IP(dst=self.host, options=pkts[index]))
                        index += 1

                    # Wait for a response from the server
                    response, server = sock.recvfrom(65535)
                    print(f"Received response from {server}: {response}")
                    time.sleep(self.delay)

                    # Calculate the total sent size
                    total_sent_size += len(bytes(sent_pkt))

                    # Calculate RTT in ms
                    rtt_values.append((time.time() - start_time) * 1000)
                    print("---- END ----")
                    
            self.__send_finish(sock)
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            sock.sendto(b"Finish", (self.host, self.port))
            print(f"Total bytes sent: {total_sent_size} bytes")
            print(f"Average RTT: {(sum(rtt_values) / len(pkts)):.2f} ms")
            print(f"Throughput: {(total_sent_size / (sum(rtt_values)/1000)):.2f} bytes/s")
            sock.close()

    def __send_finish(self, sock: socket.socket) -> None:
        time.sleep(self.delay)  # Ensure the last packet is sent after the delay
        finish_pkt = IP(dst=self.host) / UDP(sport=random.randint(1024, 65535), dport=self.port) / b"Finish"
        sock.sendto(bytes(finish_pkt), (self.host, self.port))
        print("Finish packet sent.")
        # receive response from the server
        response, server = sock.recvfrom(65535)
        print(f"Received response from {server}: {response}")
        print("Covert channel sender finished.")
        print("----------------------------------------------")
        return finish_pkt

    def __send_covert_packet(self, sock: socket.socket, pkt: IP) -> IP:
        sock.sendto(bytes(pkt), (self.host, self.port))
        print(f"Covert message {bytes(pkt)} sent to {self.host}:{self.port}")
        return pkt

    def __send_noise(self, sock: socket.socket) -> IP:
        noise_pkt = None
        print("Sending noise packet...")
        rand = random.random()
        if rand < 0.15:
            # Standard IP packet with options
            opt_type = random.choice(self.opt_types + [1]) # 1 is NOP option type 
            opt_data_len = random.randint(5, self.available_space_in_packet)

            random_data = bytes(random.getrandbits(8) for _ in range(opt_data_len))
            option_bytes = bytes([opt_type, opt_data_len + IP_OPTIONS_HEADER_OCCUPIED + IP_OPTIONS_PADDING_LENGTH]) + random_data + bytes(b'\x00')
            
            option = IPOption(option_bytes)
            noise_pkt = IP(dst=self.host, options=[option])

            print(f"Noise packet {bytes(noise_pkt)} with option type {opt_type} and length {opt_data_len + IP_OPTIONS_HEADER_OCCUPIED + IP_OPTIONS_PADDING_LENGTH} sent to {self.host}:{self.port}")
        elif rand < 0.5:
            # Standard IP packet without options
            noise_pkt = IP(dst=self.host)
            print("Noise packet: plain IP")
        elif rand < 0.75:
            # IP + UDP packet with random payload
            payload = bytes(random.getrandbits(8) for _ in range(20))
            noise_pkt = IP(dst=self.host) / UDP(sport=random.randint(1024, 65535), dport=self.port) / payload
            print("Noise packet: IP/UDP with random payload")
        else:
            # IP + ICMP packet with random payload
            payload = bytes(random.getrandbits(8) for _ in range(20))
            noise_pkt = IP(dst=self.host) / ICMP(type=random.randint(0, 255), code=random.randint(0, 255)) / payload
            print("Noise packet: IP/ICMP with random payload")

        sock.sendto(bytes(noise_pkt), (self.host, self.port))

        return noise_pkt

    def __build_options_headers(self) -> list[IPOption]:
        pkts = []
        for chunk in self.__split_message():
            opt = self.__create_options_header(chunk)
            pkts.append(opt)
        return pkts

    def __split_message(self) -> 'Generator[bytes, None, None]':
        covert_message = self.secret_message.encode()

        i = 0
        while i < len(covert_message):
            padding_len = self.__calculate_pad_len()
            chunk_size = self.__calculate_current_ip_options_header_size(padding_len)
            chunk = covert_message[i:i + chunk_size]
            padding = bytes([self.__select_pad_char() for _ in range(padding_len)])

            chunk_with_padding = chunk + padding + bytes([padding_len])
            print(f"Chunk with padding: {chunk_with_padding} with length {len(chunk_with_padding)}")
            i += len(chunk)
            yield chunk_with_padding
    
    def __calculate_pad_len(self) -> int:
        return random.randint(1, 10)
    
    def __calculate_current_ip_options_header_size(self, pad_len: int) -> int:
        return random.randint(10, self.available_space_in_packet - pad_len)
    
    def __create_options_header(self, chunk: bytes) -> IPOption:
        opt_len = len(chunk) + IP_OPTIONS_HEADER_OCCUPIED
        options_in_bytes = bytes([self.__select_opt_type(), opt_len]) + chunk

        print(f"Creating options header with type {options_in_bytes[0]} and length {opt_len} with options_in_bytes: {options_in_bytes}")

        return IPOption(options_in_bytes)

    def __select_opt_type(self) -> int:
        return random.choice(self.opt_types)
    
    def __select_pad_char(self) -> int:
        return random.choice(self.pad_chars)

def parse_args():
    parser = argparse.ArgumentParser(description="Covert Channel Sender")
    parser.add_argument(
        "--secret-message",
        type=str,
        help="The secret message to be sent covertly",
    )
    parser.add_argument(
        "--packet-rate",
        type=float,
        default=1.0,
        help="The rate at which packets are sent (packets per second)",
    )
    parser.add_argument(
        "--noise-rate",
        type=float,
        default=0.5,
        help="The rate at which noise packets are sent (0.0 to 1.0)",
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    sender = Sender(
        secret_message=args.secret_message,
        packet_rate=args.packet_rate,
        noise_rate=args.noise_rate
    )
    sender.send_covert_packets()
