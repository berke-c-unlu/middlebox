import os
import socket
import time
from scapy.all import IP
from typing import Generator
from scapy.layers.inet import IPOption
import argparse

IP_OPTIONS_HEADER_SIZE = 40
IP_OPTIONS_HEADER_OCCUPIED = 2

class Sender:
    def __init__(self,secret_message: str, opt_type=0x99, pad_len=0, packet_rate=1.0):
        self.secret_message = secret_message
        self.opt_type = opt_type
        self.pad_len = pad_len
        self.packet_rate = packet_rate
        self.host = os.getenv('INSECURENET_HOST_IP')
        self.port = 8888
        self.delay = 1 / packet_rate

        # Calculate the available space in the packet
        # Since IP options header is maximum 40 bytes, we need to subtract the occupied space and the padding length
        # occupied space is 2 bytes (option type and length)
        self.available_space_in_packet = IP_OPTIONS_HEADER_SIZE - pad_len - IP_OPTIONS_HEADER_OCCUPIED
    
    def send_covert_packets(self):
        messages = self.__build_options_headers()

        total_sent_size = 0
        rtt_values = []

        try:
            # Create a UDP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print(f"Covert channel sender started on {self.host}:{self.port}")

            # Set the delay for packet sending
            print(f"Packet sending rate: {self.packet_rate} packets per second")

            for message in messages:
                start_time = time.time()

                pkt = IP(dst=self.host, options=[message])
                sock.sendto(bytes(pkt), (self.host, self.port))
                print(f"Covert message {bytes(pkt)} sent to {self.host}:{self.port}")

                # Wait for a response from the server
                response, server = sock.recvfrom(65535)
                print(f"Received response from {server}: {response}")
                time.sleep(self.delay)
                # Calculate the total sent size
                total_sent_size += len(bytes(pkt))
                # Calculate RTT in ms
                rtt_values.append((time.time() - start_time) * 1000)

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            sock.sendto(b"Finish", (self.host, self.port))
            print(f"Total bytes sent: {total_sent_size} bytes")
            print(f"Average RTT: {(sum(rtt_values) / len(messages)):.2f} ms")
            print(f"Throughput: {(total_sent_size / (sum(rtt_values)/1000)):.2f} bytes/s")
            sock.close()

    def __build_options_headers(self) -> list[IPOption]:
        messages = []
        for chunk in self.__split_message():
            # Pad the chunk
            option = self.__pad_chunk(chunk)

            # create the IP option
            covert_opt = IPOption(option)
            messages.append(covert_opt)
        return messages

    def __split_message(self) -> 'Generator[bytes, None, None]':
        covert_message = self.secret_message.encode()
        for i in range(0, len(covert_message), self.available_space_in_packet):
            chunk = covert_message[i:i + self.available_space_in_packet]
            yield chunk
    
    def __pad_chunk(self, chunk: bytes) -> bytes:
        padding = b'\xc8' * self.pad_len
        opt_len = len(chunk) + self.pad_len + IP_OPTIONS_HEADER_OCCUPIED
        return bytes([self.opt_type, opt_len]) + chunk + padding


def parse_args():
    parser = argparse.ArgumentParser(description="Covert Channel Sender")
    parser.add_argument(
        "--secret-message",
        type=str,
        required=True,
        help="The secret message to be sent covertly",
    )
    parser.add_argument(
        "--opt-type",
        type=int,
        default=0x99,
        help="The type of the IP option to be used",
    )
    parser.add_argument(
        "--pad-len",
        type=int,
        default=0,
        help="The length of padding to be added",
    )
    parser.add_argument(
        "--packet-rate",
        type=float,
        default=1.0,
        help="The rate at which packets are sent (packets per second)",
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    sender = Sender(
        secret_message=args.secret_message,
        opt_type=args.opt_type,
        pad_len=args.pad_len,
        packet_rate=args.packet_rate
    )
    sender.send_covert_packets()
