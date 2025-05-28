import asyncio
from nats.aio.client import Client as NATS
import os, random
from scapy.layers.inet import IP, Ether
from nats.aio.client import Msg
import queue
import argparse
from detector import Detector
from mitigator import Mitigator

class Processor:
    def __init__(self, delay_mean: float, suspicion_threshold: float | None = None, mitigation_strategy: str | None = None):
        self.nc = NATS()
        self.nats_url = os.getenv("NATS_SURVEYOR_SERVERS", "nats://nats:4222")
        self.INPKT_SEC = "inpktsec"
        self.INPKT_INSEC = "inpktinsec"
        self.OUTPKT_SEC = "outpktsec" 
        self.OUTPKT_INSEC = "outpktinsec"
        self.delay_mean = delay_mean
        self.delays = queue.Queue(maxsize=1000)

        self.detector = Detector(suspicion_threshold)
        self.mitigator = Mitigator(mitigation_strategy)

    async def connect(self):
        await self.nc.connect(self.nats_url)

    async def message_handler(self, msg: Msg):
        # subject is the topic
        subject = msg.subject
        data = msg.data
        packet = Ether(data)

        if subject == self.INPKT_SEC:
            ip_packet = IP(data)
            if ip_packet != None and packet.haslayer(IP):
                self.detector.collect_packet(ip_packet)
                if self.mitigator.should_mitigate() and self.mitigator.get_mitigation_strategy() == "modify_and_send":
                    new_bytes = self.mitigator.mitigate(data)
                    await self.publish(self.OUTPKT_INSEC, new_bytes)
                else:
                    await self.publish(self.OUTPKT_INSEC, data)
            else:
                await self.publish(self.OUTPKT_INSEC, data)
        else:
            await self.publish(self.OUTPKT_SEC, data)
        
    async def subscribe(self, topic: str):
        await self.nc.subscribe(topic, cb=self.message_handler)

    async def publish(self, topic: str, data: bytes):
        delay = self.__create_random_delay()
        print(f"Publishing to {topic} with delay {delay}")
        await asyncio.sleep(delay)
        await self.nc.publish(topic, data)

    async def run(self):
        await self.connect()
        print(f"Connected to {self.nats_url}")

        await self.subscribe(self.INPKT_SEC)
        await self.subscribe(self.INPKT_INSEC)
        print(f"Subscribed to {self.INPKT_SEC} and {self.INPKT_INSEC} topics")
        try:
            async def periodic_write_mean_delay():
                while True:
                    await asyncio.sleep(1)
                    self.__write_mean_delay()

            async def periodic_detection():
                if self.detector.get_suspicion_threshold() is None:
                    print("No suspicion threshold set, skipping periodic detection.")
                    return
                while True:
                    await asyncio.sleep(5)
                    self.__detection()

            await asyncio.gather(
                periodic_write_mean_delay(),
                periodic_detection()
            )
        except KeyboardInterrupt:
            print("Disconnecting...")
            await self.nc.close()

    def __create_random_delay(self):
        delay = random.expovariate(1 / (self.delay_mean * 1e-3))
        self.__push_delay(delay * 1000)
        return delay
    
    def __push_delay(self, delay):
        if self.delays.full():
            self.delays.get()
        self.delays.put(delay)

    def __write_mean_delay(self):
        if len(self.delays.queue) == 0:
            return
        average_delay = sum(self.delays.queue) / len(self.delays.queue)
        print(f"{average_delay} with --delay-mean {self.delay_mean}\n")

    def __detection(self):
        if len(self.detector.get_packets()) == 0:
            print("No packets collected for detection.")
            return
        if len(self.detector.get_packets()) < 50:
            print("Not enough suspicious packets collected for detection. At least 50 packets are required.")
            return
        
        suspicion_score, is_suspicious = self.detector.detect()
        if is_suspicious:
            print(f"Suspicious activity detected with score: {suspicion_score:.2f}")
        else:
            print("No suspicious activity detected.")
        self.detector.set_suspicion_state(is_suspicious)
        self.mitigator.update_mitigation_state(is_suspicious)


def parse_args():
    parser = argparse.ArgumentParser(description="Processor")
    parser.add_argument(
        "--delay-mean",
        type=float,
        default=5,
        help="Mean delay in microseconds",
    )
    parser.add_argument(
        "--suspicion-threshold",
        type=float,
        default=0.5,
        help="Suspicion threshold for the detector",
    )
    parser.add_argument(
        "--mitigation-strategy",
        type=str,
        choices=["modify_and_send"],
        default=None,
        help="Mitigation strategy to apply on suspicious packets",
    )
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    processor = Processor(args.delay_mean, args.suspicion_threshold, args.mitigation_strategy)
    asyncio.run(processor.run())