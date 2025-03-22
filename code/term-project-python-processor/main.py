import asyncio
from nats.aio.client import Client as NATS
import os, random
from scapy.all import Ether
from nats.aio.client import Msg
import queue
import argparse

class Processor:
    def __init__(self, delay_mean: float):
        self.nc = NATS()
        self.nats_url = os.getenv("NATS_SURVEYOR_SERVERS", "nats://nats:4222")
        self.INPKT_SEC = "inpktsec"
        self.INPKT_INSEC = "inpktinsec"
        self.OUTPKT_SEC = "outpktsec" 
        self.OUTPKT_INSEC = "outpktinsec"
        self.delay_mean = delay_mean
        self.delays = queue.Queue(maxsize=1000)

    async def connect(self):
        await self.nc.connect(self.nats_url)

    async def message_handler(self, msg: Msg):
        # subject is the topic
        subject = msg.subject
        data = msg.data
        packet = Ether(data)
        print(f"Received a message on '{subject}': {packet.show()}")

        if subject == self.INPKT_SEC:
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
            while True:
                await asyncio.sleep(1)
                self.__write_mean_delay()
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


def parse_args():
    parser = argparse.ArgumentParser(description="Processor")
    parser.add_argument(
        "--delay-mean",
        type=float,
        default=5,
        help="Mean delay in microseconds",
    )
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    processor = Processor(args.delay_mean)
    asyncio.run(processor.run())