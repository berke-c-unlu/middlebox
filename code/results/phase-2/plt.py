import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats

def build_padding_length_chart():
    padding_length = [5, 10, 15, 20]
    total_bytes_sent = [172, 220, 240, 344]
    average_rtt = [1037, 1022, 1021, 1026]
    throughput = [55.29, 53.78, 58.72, 55.87]
    
    create_chart(padding_length, average_rtt, 'Padding Length (bytes)', 'Average RTT (ms)', 'Average RTT vs Padding Length')
    create_chart(padding_length, total_bytes_sent, 'Padding Length (bytes)', 'Total Bytes Sent (bytes)', 'Total Bytes Sent vs Padding Length')
    create_chart(padding_length, throughput, 'Padding Length (bytes)', 'Throughput (Bits/s)', 'Throughput vs Padding Length')

    print("Padding Length Test Confidence Interval for Average RTT:", calculate_confidence_interval(average_rtt))
    print("Padding Length Test Confidence Interval for Total Bytes Sent:", calculate_confidence_interval(total_bytes_sent))
    print("Padding Length Test Confidence Interval for Throughput:", calculate_confidence_interval(throughput))
    print("Padding Length Test Mean for Average RTT:", calculate_mean(average_rtt))
    print("Padding Length Test Mean for Total Bytes Sent:", calculate_mean(total_bytes_sent))
    print("Padding Length Test Mean for Throughput:", calculate_mean(throughput))

def build_message_length_chart():
    message_length = [100, 200, 300, 400]
    total_bytes_sent = [228, 456, 652, 880]
    average_rtt = [1023, 1021, 1024, 1031]
    throughput = [55.71, 55.82, 57.84, 56.89]

    create_chart(message_length, average_rtt, 'Message Length (bytes)', 'Average RTT (ms)', 'Average RTT vs Message Length')
    create_chart(message_length, total_bytes_sent, 'Message Length (bytes)', 'Total Bytes Sent (bytes)', 'Total Bytes Sent vs Message Length')
    create_chart(message_length, throughput, 'Message Length (bytes)', 'Throughput (Bits/s)', 'Throughput vs Message Length')

    print("Message Length Test Confidence Interval for Average RTT:", calculate_confidence_interval(average_rtt))
    print("Message Length Test Confidence Interval for Total Bytes Sent:", calculate_confidence_interval(total_bytes_sent))
    print("Message Length Test Confidence Interval for Throughput:", calculate_confidence_interval(throughput))
    print("Message Length Test Mean for Average RTT:", calculate_mean(average_rtt))
    print("Message Length Test Mean for Total Bytes Sent:", calculate_mean(total_bytes_sent))
    print("Message Length Test Mean for Throughput:", calculate_mean(throughput))


def build_packet_rate_chart():
    packet_rate = [0.5, 1.0, 2.0, 5.0]
    total_bytes_sent = [220, 220, 220, 220]
    average_rtt = [2021, 1020, 520, 222]
    throughput = [27.21, 53.90, 105.67, 247.70]

    create_chart(packet_rate, average_rtt, 'Packet Rate (packets/s)', 'Average RTT (ms)', 'Average RTT vs Packet Rate')
    create_chart(packet_rate, total_bytes_sent, 'Packet Rate (packets/s)', 'Total Bytes Sent (bytes)', 'Total Bytes Sent vs Packet Rate')
    create_chart(packet_rate, throughput, 'Packet Rate (packets/s)', 'Throughput (Bits/s)', 'Throughput vs Packet Rate')

    print("Packet Rate Test Confidence Interval for Average RTT:", calculate_confidence_interval(average_rtt))
    print("Packet Rate Length Test Confidence Interval for Throughput:", calculate_confidence_interval(throughput))

    print("Packet Rate Test Mean for Average RTT:", calculate_mean(average_rtt))
    print("Packet Rate Test Mean for Total Bytes Sent:", calculate_mean(total_bytes_sent))
    print("Packet Rate Test Mean for Throughput:", calculate_mean(throughput))
    

def calculate_confidence_interval(data, confidence=0.95):
    mean_value = np.mean(data)
    std_error = np.std(data) / np.sqrt(len(data))

    conf_interval = stats.t.interval(confidence, len(data)-1, loc=mean_value, scale=std_error)
    return conf_interval

def calculate_mean(data):
    return np.mean(data)

def create_chart(x, y, label_x, label_y, title):
    fig, ax = plt.subplots()
    ax.plot(x, y, label=title, marker='o', linestyle='-', color='b')
    ax.set_xlabel(label_x)
    ax.set_ylabel(label_y)
    ax.set_title(title)

    ax.set_xticks(np.arange(0, max(x)*2, max(x) / 10))  # X-axis ticks every 1 unit
    ax.set_yticks(np.arange(0, max(y)*2, max(y) / 10))  # Y-axis ticks every 10 units

    # add text as x and y and corresponding throughput
    for x, y in zip(x, y):
        ax.text(x, y, f'({x}, {y})', fontsize=9, ha='right', va='bottom', color='black')

    ax.legend()
    plt.show()

if __name__ == "__main__":
    build_padding_length_chart()
    build_message_length_chart()
    build_packet_rate_chart()