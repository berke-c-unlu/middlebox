import math
from scapy.layers.inet import IP
from typing import List

class Detector:
    def __init__(self, suspicion_threshold: float):
        self.__packets: List[IP] = []
        self.__suspicion_threshold = suspicion_threshold
        self.common_types = [
            0, 1, 7, 10, 11, 12, 15, 25, 30, 68, 82, 94,
            130, 131, 133, 134, 136, 137, 142, 144, 145,
            147, 148, 149, 150, 151, 152, 158, 205, 222
        ]
        self.__suspicion_state = False

    def get_suspicion_threshold(self) -> float:
        return self.__suspicion_threshold

    def get_packets(self) -> List[IP]:
        return self.__packets
    
    def get_supicion_state(self) -> bool:
        return self.__suspicion_state
    
    def set_suspicion_state(self, state: bool):
        self.__suspicion_state = state
    
    def collect_packet(self, packet: IP):
        self.__packets.append(packet)
    
    def detect(self):        
        option_frequency = self.__option_frequency_analysis()
        option_type_frequency = self.__option_type_frequency_analysis()
        option_padding_entropy = self.__option_padding_entropy_analysis()
        print(f"Option Frequency: {option_frequency:.2f}")
        print(f"Option Type Frequency: {option_type_frequency:.2f}")
        print(f"Option Padding Entropy: {option_padding_entropy:.2f}")

        total_score = (option_frequency + option_type_frequency + option_padding_entropy) / 3.0
        print(f"Total Suspicion Score: {total_score:.2f}")

        if total_score >= self.__suspicion_threshold:
            print(f"Suspicious activity detected with {total_score:.2f} suspicion score.")
            self.__suspicion_state = True
        else:
            print("No suspicious activity detected.")
            self.__suspicion_state = False
        return total_score, self.__suspicion_state

    def __option_frequency_analysis(self) -> float:
        packet_count_with_options = sum(1 for pkt in self.__packets if pkt.getlayer('IP').options)
        total_count_of_packets = len(self.__packets)
        if total_count_of_packets == 0:
            return 0.0
        frequency = packet_count_with_options / total_count_of_packets

        if frequency == 0:
            print("No IP options found in any packets.")
            return 0.0
        if frequency < 0.2:
            print(f"Very low frequency of IP options: {frequency:.2f} (Threshold: 0.2)")
            return 0.25
        if frequency < 0.4:
            print(f"Low frequency of IP options: {frequency:.2f} (Threshold: 0.4)")
            return 0.5
        if frequency < 0.6:
            print(f"Moderate frequency of IP options: {frequency:.2f} (Threshold: 0.6)")
            return 0.75
        else:
            print(f"High frequency of IP options: {frequency:.2f} (Threshold: 0.8)")
            return 1.00

        
    def __option_type_frequency_analysis(self) -> float:
        options = [opt for pkt in self.__packets for opt in pkt.getlayer('IP').options]
        option_types = [bytes(opt)[0] for opt in options]
        if not option_types:
            return 0.0
        
        uncommon_option_type_count = sum(1 for typ in option_types if typ not in self.common_types)
        total = len(option_types)
        if total == 0:
            return 0.0
        frequency = uncommon_option_type_count / total
        if frequency == 0:
            print("No uncommon IP option types found.")
            return 0.0
        if frequency < 0.2:
            print(f"Low frequency of uncommon IP option types: {frequency:.2f} (Threshold: 0.2)")
            return 0.2
        if frequency < 0.4:
            print(f"Moderate frequency of uncommon IP option types: {frequency:.2f} (Threshold: 0.4)")
            return 0.4
        if frequency < 0.6:
            print(f"High frequency of uncommon IP option types: {frequency:.2f} (Threshold: 0.6)")
            return 0.6
        if frequency < 0.8:
            print(f"Very high frequency of uncommon IP option types: {frequency:.2f} (Threshold: 0.8)")
            return 0.8
        else:
            print(f"Extremely high frequency of uncommon IP option types: {frequency:.2f}")
            return 1.0
    
    
    def __option_padding_entropy_analysis(self) -> float:
        padding_lengths = [1,2,3,4]
        entropies = []
        for padding_length in padding_lengths:
            # filter packets with IP options
            filtered_packets = [bytes(pkt) for pkt in self.__packets if pkt.getlayer('IP').options]
            # get paddings from filtered packets
            paddings = [raw_pkt[-padding_length-1:-1] for raw_pkt in filtered_packets]
            if not paddings:
                continue
            entropy = self.__calculate_entropy(paddings)
            entropies.append(entropy)
        
        entropy_avg = sum(entropies) / len(entropies) if entropies else 0.0

        if entropy_avg < 3.5:
            print(f"Very Low average entropy of padding lengths: {entropy_avg:.2f} (Threshold: 3.5)")
            return 1.0
        if entropy_avg < 4.5:
            print(f"Low average entropy of padding lengths: {entropy_avg:.2f} (Threshold: 3.5)")
            return 0.75
        if entropy_avg < 5.5:
            print(f"Moderate average entropy of padding lengths: {entropy_avg:.2f} (Threshold: 5.5)")
            return 0.5
        if entropy_avg < 6.5:
            print(f"High average entropy of padding lengths: {entropy_avg:.2f} (Threshold: 6.5)")
            return 0.25
        else:
            print(f"Extremely high average entropy of padding lengths: {entropy_avg:.2f}")
            return 0.0
    
    def __calculate_entropy(self, data: bytes) -> float:
        if not data:
            return 0.0
        frequency = {}
        for byte in data:
            if byte not in frequency:
                frequency[byte] = 0
            frequency[byte] += 1
        
        total = len(data)
        entropy = -sum((count / total) * math.log2(count / total) for count in frequency.values())
        return entropy