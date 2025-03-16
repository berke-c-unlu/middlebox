import asyncio
from nats.aio.client import Client as NATS
import os, random
from scapy.all import Ether
from nats.aio.client import Msg

class Processor:
    def __init__(self):
        self.nc = NATS()
        self.nats_url = os.getenv("NATS_SURVEYOR_SERVERS", "nats://nats:4222")
        self.INPKT_SEC = "inpktsec"
        self.INPKT_INSEC = "inpktinsec"
        self.OUTPKT_SEC = "outpktsec" 
        self.OUTPKT_INSEC = "outpktinsec"

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
        delay = self.create_random_delay()
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
        except KeyboardInterrupt:
            print("Disconnecting...")
            await self.nc.close()

    def create_random_delay(self):
        return random.expovariate(1 / 5e-6)

    

if __name__ == '__main__':
    processor = Processor()
    asyncio.run(processor.run())