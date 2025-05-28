from typing import Literal, Optional
from scapy.layers.inet import IPOption_NOP, IP, Ether
from scapy.all import Raw, raw
class Mitigator:
    def __init__(self, mitigation_strategy: Optional[Literal["modify_and_send"]]):
        self.mitigation_strategy = mitigation_strategy
        self.mitigation_state = False

    def update_mitigation_state(self, state: bool):
        if state and not self.mitigation_state:
            print("Mitigation activated.")
            self.mitigation_state = True
        elif not state and self.mitigation_state:
            print("Mitigation deactivated.")
            self.mitigation_state = False
    
    def should_mitigate(self) -> bool:
        if self.mitigation_state:
            if self.mitigation_strategy == "modify_and_send":
                return True
        return False
    
    def get_mitigation_strategy(self) -> str:
        return self.mitigation_strategy
    
    def get_mitigation_state(self) -> bool:
        return self.mitigation_state
    
    def mitigate(self, packet):
        if self.mitigation_strategy == "modify_and_send":
            print(f"Mitigation strategy: {self.mitigation_strategy}")
            return self.__modify_packet(packet)
        else:
            print("No mitigation strategy provided, returning original packet...")
            return packet
    
    def __modify_packet(self, data: bytes) -> bytes:
        eth = Ether(data)
        if eth.type == 0x0800 and IP in eth:
            ip = eth[IP]
            ip.options = ip.options[:-4] + [IPOption_NOP()] * 4
            del ip.ihl
            del ip.len
            del ip.chksum
            old_payload = raw(ip.payload)
            ip.remove_payload()
            ip.payload = Raw(load= old_payload[:-4] + b'\x00\x00\x00\x00')
            eth = Ether(src=eth.src, dst=eth.dst, type=eth.type) / ip / Raw(load=b'\x00\x00\x00\x00')
            eth.show2(dump=False)
            return bytes(eth)
        print("No IP options found, skipping modification...")
        return data


