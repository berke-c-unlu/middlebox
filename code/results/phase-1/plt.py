import matplotlib.pyplot as plt
import numpy as np

#34.144 -- 10.50 --> 10 delay
#57.354 -- 21.68 --> 20 delay
#73.921 -- 31.00 --> 30 delay
#95.500 -- 40.58 --> 40 delay
#122.660 -- 54.21 --> 50 delay
#127.751 -- 56.68 --> 60 delay
#166.854 -- 76.40 --> 70 delay
#178.038 -- 81.38 --> 80 delay
#196.036 -- 91.42 --> 90 delay
#229.593 -- 107.95 --> 100 delay

# Create data
delay = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
mean_delay = [10.50, 21.68, 31.00, 40.58, 54.21, 56.68, 76.40, 81.38, 91.42, 107.95]
rtt_values = [34.144, 57.354, 73.921, 95.500, 122.660, 127.751, 166.854, 178.038, 196.036, 229.593]

# x axis is mean delay
# y axis is rtt values

# create a figure and axis
fig, ax = plt.subplots()

ax.plot(mean_delay, rtt_values, label='RTT values', marker='o', linestyle='-', color='b')
ax.set_xlabel('Mean Value for Random Delay (ms)')
ax.set_ylabel('Average RTT for Ping Packets (ms)')
ax.set_xticks(np.arange(10, 120, 10))  # X-axis ticks every 10 units
ax.set_yticks(np.arange(0, 251, 25))  # Y-axis ticks every 25 units

for x, y in zip(mean_delay, rtt_values):
    ax.text(x, y, f'({x}, {y})', fontsize=9, ha='right', va='bottom', color='black')


ax.legend()

plt.show()