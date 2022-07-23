import random
import datetime
import os
import statistics

MILLISECONDS_IN_SECOND = 1000.0
B_IN_MB = 1000000.0
BITS_IN_BYTE = 8.0

# at stage 1: we assume the uploading and downloading processes are both all-i encoding so all frames are
# independent from each other
# value of ideal condition will impact on whether uploading part is ideal or not
ideal_condition = False
RTT = 0 # round trip time

# video configurations
FPS = 25.0
frame_time = 1/FPS
video_duration = 300.0 # seconds

# at stage 1: no need for video trace data since the packet network trace data is the most important, we could simply
# use a CBR all-i video (constant frame size for all frames)

# set the constant frame size (maximum value)
frame_size_max = 2000 #kb (all-i 50 mbps CBR, the best possible images from the sensors)
frame_size_min = 25 #kb (minimum value for a frame that is worth transferring, lower than that would be pointless for poor quality)

# playback settings
initial_buffers = 1 # seconds
target_buffers = 1 # seconds

# Network information
data_segment_size = 1472 # bytes/from Showing Data

# Part one: uploading part

# read the network packet trace data
NETWORK_TRACE = '3HK'
network_trace_dir = './network_trace/' + NETWORK_TRACE + '/'
cooked_files = os.listdir(network_trace_dir)
all_packet_arrival_time = []
all_packet_size = []
all_file_names = []
all_instant_speed = []
network_TP_history = []
# read the data into a list
for cooked_file in cooked_files:
    # temporary lists
    file_path = network_trace_dir + cooked_file
    packet_arrival_time = []
    packet_size = []
    with open(file_path, 'rb') as f:
        serial = 0
        relative_start = 0
        for line in f:
            parse = line.split()
            if serial == 0:
                packet_arrival_time.append(0)
                relative_start = float(parse[0])
            else:
                packet_arrival_time.append(float(parse[0])-relative_start)
                if packet_arrival_time[-1] == packet_arrival_time[-2]:
                    # check if there are duplicates in timecodes
                    print(float(parse[0]))
            serial = serial+1
            packet_size.append(float(parse[1]))

        all_packet_arrival_time.append(packet_arrival_time)
        all_packet_size.append(packet_size)
        all_file_names.append(cooked_file)

# place = 0
# for i in range(len(all_packet_arrival_time[0])):
#     if all_packet_arrival_time[0][i]>386.826:
#         place = i
#         break
# print(sum(all_packet_size[0][0:place])/all_packet_arrival_time[0][place]*8/1000000)


# check if the network trace data is long enough for current video playback
if all_packet_arrival_time[0][-1] >= video_duration + initial_buffers:
    total_frame_number = FPS * video_duration
    # check whether the test will be run in ideal condition or not
    if ideal_condition == False:
        # A(realistic): an estimation algorithm that estimates the current throughput for optimal frame size based on the trace data
        # this part can be modified to test different estimation algorithms
        video_raw_rate = 2 # mbps, ALL-I CBR
        raw_frame_size = video_raw_rate * 1000 / FPS # kb
        next_frame_size = 0
        frame_send_time = []
        frame_cdn_arrival_time = []
        estimated_frame_size = []
        packet_serial = 0
        flag = 0
        past_TP = 0
        real_time = 0
        # during initial buffer, send out the original frame
        for i in range(int(total_frame_number)):
            # initial_frame
            if i < FPS-1:
                next_frame_size = raw_frame_size
            else:
                # todo: put estimation algorithm here
                # using the throughput history to predict the frame size
                # next_frame_size = 100
                if len(network_TP_history)>=24:
                    next_frame_size = statistics.mean(network_TP_history[-24:-1]) * frame_time
                else:
                    next_frame_size = statistics.mean(network_TP_history)*frame_time
            estimated_frame_size.append(next_frame_size)
            # check whether at this time the frame is available to send
            if real_time >= i * frame_time:
                frame_send_time.append(real_time)
            else:
                # the frame hasn't been generated yet, wait till it is ready to send it
                real_time = i * frame_time
                frame_send_time.append(real_time)
            # calculate CDN arrival time, by using the packet trace
            # one ideal assumption: the utilization of network is still high because the packet is almost always full with needed info
            # round trip time has been already calculated in the packet data
            temp_size = 0 # sum value used to send the current frame
            # find the right initial that includes the frame data: the first packet after real time
            packet_serial = 0
            while flag == 0:
                # print(all_packet_arrival_time[0][packet_serial], real_time)
                if real_time == 0:
                    packet_serial = 0
                    break
                elif all_packet_arrival_time[0][packet_serial] >= real_time and all_packet_arrival_time[0][packet_serial-1] < real_time:
                    break
                packet_serial = packet_serial + 1
            packet_serial = packet_serial+1
            # print(next_frame_size)
            while flag == 0:
                # print(temp_size)
                if temp_size*8/1000 > next_frame_size: # in kb
                    break
                # print(packet_serial, i)
                # print(len(all_packet_size[0]))
                # print(all_packet_size[packet_serial])
                temp_size = temp_size + all_packet_size[0][packet_serial] # in bytes
                packet_serial = packet_serial + 1
            if all_packet_arrival_time[0][packet_serial-1] > real_time:
                frame_cdn_arrival_time.append(all_packet_arrival_time[0][packet_serial-1])
                # record the throughput history for every frame (kbs)
                network_TP_history.append(next_frame_size/(frame_cdn_arrival_time[-1]-frame_send_time[-1]))
                real_time = all_packet_arrival_time[0][packet_serial-1]
            else:
                print("A bug occurred, a frame has arrived before it is generated")
        # print(len(frame_cdn_arrival_time))
        # print(frame_cdn_arrival_time)
        for i in range(int(total_frame_number)):
            print(frame_send_time[i],frame_cdn_arrival_time[i])
        # based on the packet arrival time and estimated frame size, calculate the exact arrival time of
        # each frame at the CDN server
        print(statistics.mean(estimated_frame_size))
        print(statistics.mean(network_TP_history))


    







