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
video_duration = 50.0 # seconds

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
    instant_speed = []
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
                    print("there are duplicates")
                else:
                    instant_speed.append(float(parse[1])*8/(packet_arrival_time[-1]-packet_arrival_time[-2])/1000)  # kbps
            serial = serial+1
            packet_size.append(float(parse[1]))

        all_instant_speed.append(instant_speed)
        all_packet_arrival_time.append(packet_arrival_time)
        all_packet_size.append(packet_size)
        all_file_names.append(cooked_file)

# all_instant_speed is not usable since the time gap is not fixed, the result is far from reality
# use a fixed time gap to do the calculation:

# time_interval = 0.2
# # total_number = (all_packet_arrival_time[0][-1])/time_interval
# total_number = (4*video_duration)/time_interval
# timed_throughput = []
# for i in range(int(total_number)):
#     start = i*time_interval
#     end = (i+1)*time_interval
#     serial_start = 0
#     serial_end = 0
#     for j in range(len(all_packet_arrival_time[0])):
#         if all_packet_arrival_time[0][j]<start and all_packet_arrival_time[0][j+1]>start:
#             serial_start = j
#         if all_packet_arrival_time[0][j]<end and all_packet_arrival_time[0][j+1]>end:
#             serial_end = j
#             break
#     temp_tp = (serial_end - serial_start + 1) * data_segment_size * 8 / time_interval / 1000 #kbps
#     timed_throughput.append(temp_tp)
    # print(temp_tp)

# for i in range(10):
#     print(all_instant_speed[0][i])
# print(statistics.mean(timed_throughput))
print(statistics.mean(all_instant_speed[0]))


# print(sum(all_packet_size[0][0:len(all_packet_arrival_time[0])-1])*8/
#       (all_packet_arrival_time[0][-1]-all_packet_arrival_time[0][0])/1000000)
# print(data_segment_size*len(all_packet_arrival_time[0])*8/all_packet_arrival_time[0][-1]/1000)
#
# print(sum(all_instant_speed[0][0:100]))
# print(data_segment_size*100*8/all_packet_arrival_time[0][99]/1000)
# print(all_instant_speed[0])




# check if the network trace data is long enough for current video playback
if all_packet_arrival_time[0][-1] >= video_duration + initial_buffers:
    total_frame_number = FPS * video_duration
    # check whether the test will be run in ideal condition or not
    if ideal_condition == False:
        # A(realistic): an estimation algorithm that estimates the current throughput for optimal frame size based on the trace data
        # this part can be modified to test different estimation algorithms
        video_raw_rate = 10 # mbps, ALL-I CBR
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
                # todo: put uploading ABR algorithms here, including live streaming, on demand streaming ABR algorithms
                # no.1: simple mean estimation algorithm for frame size
                # using the throughput history to predict the frame size
                # because now the throughput is calculated by the instant moment, it is easy to overestimate, so divided by 40

                next_frame_size = 100
                if len(network_TP_history) >= 24:
                    next_frame_size = statistics.mean(network_TP_history[-24:-1]) * frame_time/40
                else:
                    next_frame_size = statistics.mean(network_TP_history)*frame_time/40

                # no.2: Buffer-based algorithm
                # check with the buffer occupancy, but the experiment proved that BB can't be used in uploading

                # reservoir = 5
                # cushion = 10
                # print(i-len(frame_cdn_arrival_time))
                # if i-len(frame_cdn_arrival_time)>reservoir+cushion:
                #     next_frame_size = frame_size_min
                #     print("scenario 3")
                # elif i-len(frame_cdn_arrival_time)<reservoir:
                #     next_frame_size = raw_frame_size
                #     print("scenario 1")
                # else:
                #     next_frame_size = raw_frame_size * (i-len(frame_cdn_arrival_time))/(reservoir+cushion)
                #     print("scenario 2")

                # no.3: for test only, fixed estimated frame size
                # next_frame_size = 1000

            estimated_frame_size.append(next_frame_size)
            # check whether at this time the frame is available to send
            if real_time >= i * frame_time:
                frame_send_time.append(real_time)
            else:
                # the frame hasn't been generated yet, wait till it is ready to send it
                real_time = i * frame_time
                frame_send_time.append(real_time)
            # calculate CDN arrival time, by using the packet trace
            # instead of using the precise arrival time of each packet, we use linear interpolation to estimate the
            # throughput using the packets every given interval (e.g. 0.1s) so that we could calculate the arrival time of each
            # frame more easily

            current_tp = 0
            for j in range(len(all_packet_arrival_time[0])):
                if all_packet_arrival_time[0][j]<=real_time and all_packet_arrival_time[0][j+1]>real_time:
                    print(i)
                    current_tp = all_instant_speed[0][j]+(real_time-all_packet_arrival_time[0][j])* \
                                 (all_instant_speed[0][j+1]-all_instant_speed[0][j])\
                                 /(all_packet_arrival_time[0][j+1]-all_packet_arrival_time[0][j])
                    print(current_tp)
                    break
            transmission_time = next_frame_size/current_tp
            real_time = real_time+transmission_time
            frame_cdn_arrival_time.append(real_time)
            network_TP_history.append(current_tp)

        # print(len(frame_cdn_arrival_time))
        # print(frame_cdn_arrival_time)
        for i in range(int(total_frame_number)):
            print(frame_send_time[i],frame_cdn_arrival_time[i])
        # based on the packet arrival time and estimated frame size, calculate the exact arrival time of
        # each frame at the CDN server
        print(statistics.mean(estimated_frame_size))
        print(statistics.mean(network_TP_history))
        place = 0
        for i in range(len(all_packet_arrival_time[0])):
            if all_packet_arrival_time[0][i] > frame_cdn_arrival_time[-1]:
                place = i
                break
        # show the most precise throughput during transmission
        print(sum(all_packet_size[0][0:place]) / all_packet_arrival_time[0][place] * 8 / 1000)

        # generate a CDN arrival time list with frame size
    else:
        # B(ideal): knowing the current network in advance and assign the theoretically perfect frame size for transmission
        # in this case, zero initial delay and zero playback buffer since we can perfectly transfer the frame in 1/fps time

        ideal_frame_size = []
        last_packet_serial = 0
        for i in range(int(total_frame_number)):
            # by introducing target buffers and initial buffers, initial preparing time for the first frames will be increased
            if i < FPS-1:
                frame_time = (initial_buffers+target_buffers)/FPS
            else:
                frame_time = target_buffers/FPS
            frame_start = i * frame_time
            frame_end = frame_start + frame_time
            temp_packet_serial = last_packet_serial
            flag = 0
            while flag == 0:
                last_packet_serial = last_packet_serial + 1
                if all_packet_arrival_time[0][last_packet_serial] > frame_end:
                    break
            # calculate the frame size by assuming it could be split into every packet seamlessly
            frame_size = (last_packet_serial-temp_packet_serial) * data_segment_size
            - data_segment_size * (frame_start-all_packet_arrival_time[0][temp_packet_serial]) / (all_packet_arrival_time[0][temp_packet_serial+1]-all_packet_arrival_time[0][temp_packet_serial])
            - data_segment_size * (all_packet_arrival_time[0][last_packet_serial] - frame_end) / (all_packet_arrival_time[0][last_packet_serial]-all_packet_arrival_time[0][last_packet_serial-1])
            # convert the units: frame size is now in bytes
            frame_size_kb = frame_size * BITS_IN_BYTE/1000
            if frame_size_kb > frame_size_max:
                frame_size_kb = frame_size_max
            if frame_size_kb < frame_size_min:
                frame_size_kb = 0
            # skip the frame when too small
            ideal_frame_size.append(frame_size_kb)
        # CDN arrival time is exactly the play back time for each frame
        print(statistics.mean(ideal_frame_size))
        place = 0
        for i in range(len(all_packet_arrival_time[0])):
            if all_packet_arrival_time[0][i] > video_duration:
                place = i
                break
        # show the most precise throughput during transmission
        print(sum(all_packet_size[0][0:place]) / all_packet_arrival_time[0][place] * 8 / 1000)
# Part two: downloading part
# for stage 1: downloading part is still all-i CBR where the bitrate and the frame size is fixed, if the frame size is smaller than the
# designed size at that bitrate, then use the smaller bitrate ones, otherwise just drop it
Bitrate_Ladder = [800, 1400, 2200] # kbps
target_frame_size = []  # kb
for bitrate in Bitrate_Ladder:
    target_frame_size.append(bitrate/FPS)

# how individual frame sizes impact the QoE and how to design the QoE to cope with it





