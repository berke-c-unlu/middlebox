#!/bin/bash

### Padding length test

# docker compose exec -d term-project-python-processor python3 main.py
# echo "Started main.pyin term-project-python-processor"

# docker compose exec -d insec python3 covert-channel-receiver.py --pad-len 5
# echo "Started covert-channel-receiver.py in insec"

# docker compose exec sec python3 covert-channel-sender.py --pad-len 5 --secret-message "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor."  > ./test-results/pad-len-sec-5.txt 2>&1 &
# echo "Started covert-channel-sender.py in sec"
# sec_pid=$!

# wait $sec_pid
# echo "sec container exited, logs are written"
# docker compose restart

# #######################################################################################

### Message length test

# "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean m"
# "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec qu" 
# "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec." 
# "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a" 

# docker compose exec -d term-project-python-processor python3 main.py
# echo "Started main.pyin term-project-python-processor"

# docker compose exec -d insec python3 covert-channel-receiver.py --pad-len 10
# echo "Started covert-channel-receiver.py in insec"

# docker compose exec sec python3 covert-channel-sender.py --pad-len 10 --secret-message "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a"   > ./test-results/secret-message-400.txt 2>&1 &
# echo "Started covert-channel-sender.py in sec"
# sec_pid=$!

# wait $sec_pid
# echo "sec container exited, logs are written"
# docker compose restart


# #######################################################################################

### Rate test

# docker compose exec -d term-project-python-processor python3 main.py
# echo "Started main.pyin term-project-python-processor"

# docker compose exec -d insec python3 covert-channel-receiver.py --pad-len 10
# echo "Started covert-channel-receiver.py in insec"

# docker compose exec sec python3 covert-channel-sender.py --pad-len 10 --packet-rate 5.0 --secret-message "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor."  > ./test-results/packet-rate-5,0.txt 2>&1 &
# echo "Started covert-channel-sender.py in sec"
# sec_pid=$!

# wait $sec_pid
# echo "sec container exited, logs are written"
# docker compose restart


# ########################################################################################