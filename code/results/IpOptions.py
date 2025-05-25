from scapy.all import IP
from scapy.layers.inet import IPOption


def create_random_ip_option():
    result = []
    for opt_type in range(141,253):
        try:
            option_data = bytes([opt_type, 5]) + bytes([0, 1, 2, 3])  # Example data
            option = IPOption(option_data)
        except Exception as e:
            print(f"Error creating IPOption with type {opt_type}: {e}")
            continue
        print(f"Successfully created IPOption with type {opt_type}: {option}")
        if isinstance(option, IPOption):
            result.append(option)
    return result

if __name__ == "__main__":
    option = create_random_ip_option()
    _ip_options_names = {0: "end_of_list",
                     1: "nop",
                     2: "security",
                     3: "loose_source_route",
                     4: "timestamp",
                     5: "extended_security",
                     6: "commercial_security",
                     7: "record_route",
                     8: "stream_id",
                     9: "strict_source_route",
                     10: "experimental_measurement",
                     11: "mtu_probe",
                     12: "mtu_reply",
                     13: "flow_control",
                     14: "access_control",
                     15: "encode",
                     16: "imi_traffic_descriptor",
                     17: "extended_IP",
                     18: "traceroute",
                     19: "address_extension",
                     20: "router_alert",
                     21: "selective_directed_broadcast_mode",
                     23: "dynamic_packet_state",
                     24: "upstream_multicast_packet",
                     25: "quick_start",
                     30: "rfc4727_experiment",
                     }

    start = 141
    end = 252

    missing_option_values = []

    for val in range(start, end + 1):
        option_val = val & 0x1F 
        if option_val not in _ip_options_names:
            missing_option_values.append(val)

    print(missing_option_values)
    