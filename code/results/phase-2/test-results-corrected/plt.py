import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats

def build_padding_length_chart():
    padding_length = [1, 2, 3, 4]
    total_bytes_sent = [6844, 3096, 2544, 1644]
    average_rtt = [2014, 2023, 2555, 2292]
    throughput = [27.06, 33.97, 30.6, 28.68]
    covert_throughput = [float(f"{(t / b) * 100:.2f}") for t, b in zip(throughput, total_bytes_sent)]
    
    create_chart(padding_length, average_rtt, 'Padding Length (bytes)', 'Average RTT (ms)', 'Average RTT vs Padding Length')
    create_chart(padding_length, total_bytes_sent, 'Padding Length (bytes)', 'Total Bytes Sent (bytes)', 'Total Bytes Sent vs Padding Length')
    create_chart(padding_length, throughput, 'Padding Length (bytes)', 'Throughput (Bytes/s)', 'Throughput vs Padding Length')
    create_chart(padding_length, covert_throughput, 'Padding Length (bytes)', 'Covert Throughput (Bytes/s)', 'Covert Throughput vs Padding Length')

    print("Padding Length Test Confidence Interval for Average RTT:", calculate_confidence_interval(average_rtt))
    print("Padding Length Test Confidence Interval for Total Bytes Sent:", calculate_confidence_interval(total_bytes_sent))
    print("Padding Length Test Confidence Interval for Throughput:", calculate_confidence_interval(throughput))
    print("Padding Length Test Confidence Interval for Covert Throughput:", calculate_confidence_interval(covert_throughput))
    print("Padding Length Test Mean for Average RTT:", calculate_mean(average_rtt))
    print("Padding Length Test Mean for Total Bytes Sent:", calculate_mean(total_bytes_sent))
    print("Padding Length Test Mean for Throughput:", calculate_mean(throughput))
    print("Padding Length Test Mean for Covert Throughput:", calculate_mean(covert_throughput))

def build_message_length_chart():
    message_length = [50, 100, 150, 200]
    total_bytes_sent = [928, 1548, 2540, 3148]
    average_rtt = [2205, 2052, 2022, 2046]
    throughput = [32.36, 30.17, 33.05, 30.77]
    covert_throughput = [float(f"{(t / b) * 100:.2f}") for t, b in zip(throughput, total_bytes_sent)]

    create_chart(message_length, average_rtt, 'Message Length (bytes)', 'Average RTT (ms)', 'Average RTT vs Message Length')
    create_chart(message_length, total_bytes_sent, 'Message Length (bytes)', 'Total Bytes Sent (bytes)', 'Total Bytes Sent vs Message Length')
    create_chart(message_length, throughput, 'Message Length (bytes)', 'Throughput (Bytes/s)', 'Throughput vs Message Length')
    create_chart(message_length, covert_throughput, 'Message Length (bytes)', 'Covert Throughput (Bytes/s)', 'Covert Throughput vs Message Length')

    print("Message Length Test Confidence Interval for Average RTT:", calculate_confidence_interval(average_rtt))
    print("Message Length Test Confidence Interval for Total Bytes Sent:", calculate_confidence_interval(total_bytes_sent))
    print("Message Length Test Confidence Interval for Throughput:", calculate_confidence_interval(throughput))
    print("Message Length Test Confidence Interval for Covert Throughput:", calculate_confidence_interval(covert_throughput))
    print("Message Length Test Mean for Average RTT:", calculate_mean(average_rtt))
    print("Message Length Test Mean for Total Bytes Sent:", calculate_mean(total_bytes_sent))
    print("Message Length Test Mean for Throughput:", calculate_mean(throughput))
    print("Message Length Test Mean for Covert Throughput:", calculate_mean(covert_throughput))
    
def build_noise_rate_chart():
    noise_rate = [0, 0.25, 0.5, 0.75]
    total_bytes_sent = [1052, 1288, 1932, 3432]
    average_rtt = [1029, 1514, 2495, 5073]
    throughput = [40.07, 34.02, 30.97, 27.06]
    covert_throughput = [float(f"{(t / b) * 100:.2f}") for t, b in zip(throughput, total_bytes_sent)]

    create_chart(noise_rate, average_rtt, 'Noise Rate', 'Average RTT (ms)', 'Average RTT vs Noise Rate')
    create_chart(noise_rate, total_bytes_sent, 'Noise Rate', 'Total Bytes Sent (bytes)', 'Total Bytes Sent vs Noise Rate')
    create_chart(noise_rate, throughput, 'Noise Rate', 'Throughput (Bytes/s)', 'Throughput vs Noise Rate')
    create_chart(noise_rate, covert_throughput, 'Noise Rate', 'Covert Throughput (Bytes/s)', 'Covert Throughput vs Noise Rate')

    print("Noise Rate Test Confidence Interval for Average RTT:", calculate_confidence_interval(average_rtt))
    print("Noise Rate Test Confidence Interval for Total Bytes Sent:", calculate_confidence_interval(total_bytes_sent))
    print("Noise Rate Test Confidence Interval for Throughput:", calculate_confidence_interval(throughput))
    print("Noise Rate Test Confidence Interval for Covert Throughput:", calculate_confidence_interval(covert_throughput))
    print("Noise Rate Test Mean for Average RTT:", calculate_mean(average_rtt))
    print("Noise Rate Test Mean for Total Bytes Sent:", calculate_mean(total_bytes_sent))
    print("Noise Rate Test Mean for Throughput:", calculate_mean(throughput))
    print("Noise Rate Test Mean for Covert Throughput:", calculate_mean(covert_throughput))


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
    build_noise_rate_chart()