import random
import datetime
import os
import statistics
import matplotlib.pyplot as plt

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
video_duration = 20.0 # seconds

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
upload_dir =  './network_trace/upload/'
cooked_files = os.listdir(network_trace_dir)
cooked_upload_files = os.listdir(upload_dir)
upload_time = []
upload_packet_size = []
all_packet_arrival_time = []
all_packet_size = []
all_file_names = []
all_instant_speed = []
network_TP_history = []
network_TP_history2 = []
network_TP_history3 = []
network_TP_history4 = []
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

for i in cooked_upload_files:
     file_path = upload_dir + i
     with open(file_path, 'rb') as f:
         serial = 0
         relative_start = 0
         for line in f:
             parse = line.split()
             if serial == 0:
                 upload_time.append(0)
                 relative_start = float(parse[0])
             else:
                 upload_time.append(float(parse[0])-relative_start)
             serial = serial+1
             upload_packet_size.append(float(parse[1]))
         if upload_time[-1] > 2 * video_duration: break


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
        frame_send_time2 = []
        frame_send_time3 = []
        frame_send_time4 = []
        frame_arrival_time2 = []
        frame_arrival_time3 = []
        frame_arrival_time4 = []
        estimated_frame_size = []
        estimated_frame_size2 = []
        estimated_frame_size3 = []
        estimated_frame_size4 = []
        packet_serial2 = 0
        packet_serial3 = 0
        packet_serial4 = 0
        past_TP = 0
        real_time = 0
        real_time1 = 0
        real_time2 = 0
        real_time3 = 0
        real_time4 = 0
        frameloss = 0

        # during initial buffer, send out the original frame
        for i in range(int(total_frame_number)):
            # initial_frame
            if i < FPS-1:
                next_frame_size = raw_frame_size
                next_frame_size2 = raw_frame_size
                next_frame_size3 = raw_frame_size
                next_frame_size4 = raw_frame_size
            else:
                # todo: put estimation algorithm here
                # using the throughput history to predict the frame size
                # next_frame_size = 100
                if len(network_TP_history)>=4:
                    next_frame_size = (0.4 * network_TP_history[-1] + 0.3 * network_TP_history[-2] + 0.2 * network_TP_history[-3] + 0.1 * network_TP_history[-4]) * frame_time / 3
                    next_frame_size2 = (0.4 * network_TP_history2[-1] + 0.3 * network_TP_history2[-2] + 0.2 * network_TP_history2[-3] + 0.1 * network_TP_history2[-4]) * frame_time / 3
                    next_frame_size3 = (0.4 * network_TP_history3[-1] + 0.3 * network_TP_history3[-2] + 0.2 * network_TP_history3[-3] + 0.1 * network_TP_history3[-4]) * frame_time / 3
                    next_frame_size4 = (0.4 * network_TP_history4[-1] + 0.3 * network_TP_history4[-2] + 0.2 * network_TP_history4[-3] + 0.1 * network_TP_history4[-4]) * frame_time / 3
                else:
                    next_frame_size = statistics.mean(network_TP_history) * frame_time / 3
                    next_frame_size2 = statistics.mean(network_TP_history2) * frame_time / 3
                    next_frame_size3 = statistics.mean(network_TP_history3) * frame_time / 3
                    next_frame_size4 = statistics.mean(network_TP_history4) * frame_time / 3
            if real_time >= (i + 5) * frame_time:
                next_frame_size = min(next_frame_size, 2000 - 200 * (real_time / frame_time - i))
                next_frame_size2 = min(next_frame_size2, 2000 - 200 * (real_time / frame_time - i))
                next_frame_size3 = min(next_frame_size3, 2000 - 200 * (real_time / frame_time - i))
                next_frame_size4 = min(next_frame_size4, 2000 - 200 * (real_time / frame_time - i))
            if(next_frame_size < frame_size_min):next_frame_size = frame_size_min
            if(next_frame_size > frame_size_max):next_frame_size = frame_size_max
            if(next_frame_size2 < frame_size_min):next_frame_size2 = frame_size_min
            if(next_frame_size2 > frame_size_max):next_frame_size2 = frame_size_max
            if(next_frame_size3 < frame_size_min):next_frame_size3 = frame_size_min
            if(next_frame_size3 > frame_size_max):next_frame_size3 = frame_size_max
            if(next_frame_size4 < frame_size_min):next_frame_size4 = frame_size_min
            if(next_frame_size4 > frame_size_max):next_frame_size4 = frame_size_max
            estimated_frame_size.append(next_frame_size)
            estimated_frame_size2.append(next_frame_size2)
            estimated_frame_size3.append(next_frame_size3)
            estimated_frame_size4.append(next_frame_size4)
            # check whether at this time the frame is available to send
            if real_time >= i * frame_time:
                frame_send_time2.append(real_time)
            else:
                real_time = i * frame_time
                frame_send_time2.append(real_time)
            # calculate CDN arrival time, by using the packet trace
            # one ideal assumption: the utilization of network is still high because the packet is almost always full with needed info
            # round trip time has been already calculated in the packet data
            temp_size = 0 # sum value used to send the current frame
            temp_upload = 0
            # find the right initial that includes the frame data: the first packet after real time
            upload_serial = 0
            upload_size = 0
            packet_serial2 = 0
            packet_serial3 = 0
            packet_serial4 = 0
            timeu = 0
            time2 = 0
            time3 = 0
            time4 = 0
            while True:
                # print(all_packet_arrival_time[0][packet_serial], real_time)
                if real_time1 == 0:
                    upload_serial = 0
                    break
                elif upload_time[upload_serial] >= real_time1:
                    break
                upload_serial = upload_serial + 1
            upload_serial = upload_serial + 1
            while True:
                # print(temp_size)
                if temp_upload * 8/1000 > next_frame_size2: # in kb
                    break
                # print(packet_serial, i)
                # print(len(all_packet_size[0]))
                # print(all_packet_size[packet_serial])
                temp_upload = temp_upload + upload_packet_size[upload_serial] # in bytes
                upload_serial = upload_serial + 1
                timeu += upload_packet_size[upload_serial] - upload_packet_size[upload_serial - 1]
                if(timeu > frame_time / 2): 
                    frameloss += 1
                    break

            while True:
                # print(all_packet_arrival_time[0][packet_serial], real_time)
                if real_time2 == 0:
                    packet_serial2 = 0
                    break
                elif all_packet_arrival_time[0][packet_serial2] >= real_time2 and all_packet_arrival_time[0][packet_serial2-1] < real_time2:
                    break
                packet_serial2 = packet_serial2 + 1
            packet_serial2 = packet_serial2 + 1
            while True:
                # print(temp_size)
                if temp_size*8/1000 > next_frame_size2: # in kb
                    break
                # print(packet_serial, i)
                # print(len(all_packet_size[0]))
                # print(all_packet_size[packet_serial])
                temp_size = temp_size + all_packet_size[0][packet_serial2] # in bytes
                packet_serial2 = packet_serial2 + 1
                time2 += all_packet_arrival_time[0][packet_serial2] - all_packet_arrival_time[0][packet_serial2 - 1]
                if(time2 > frame_time / 2): 
                    frameloss += 1
                    break
                time2 = max(time2,timeu)
            frame_arrival_time2.append(real_time + time2)
            frame_send_time3.append(real_time + time2)
            temp_size = 0
            temp_upload = 0
            timeu = 0
            
                
            upload_serial = upload_serial + 1
            while True:
                # print(temp_size)
                if temp_upload * 8/1000 > next_frame_size2: # in kb
                    break
                # print(packet_serial, i)
                # print(len(all_packet_size[0]))
                # print(all_packet_size[packet_serial])
                temp_upload = temp_upload + upload_packet_size[upload_serial] # in bytes
                upload_serial = upload_serial + 1
                timeu += upload_packet_size[upload_serial] - upload_packet_size[upload_serial - 1]
                if(timeu > frame_time / 2): 
                    frameloss += 1
                    break

            while True:
                # print(all_packet_arrival_time[0][packet_serial], real_time)
                if real_time3 == 0:
                    packet_serial3 = 0
                    break
                elif all_packet_arrival_time[1][packet_serial3] >= real_time3 and all_packet_arrival_time[1][packet_serial3-1] < real_time3:
                    break
                packet_serial3 = packet_serial3 + 1
            packet_serial3 = packet_serial3 + 1
            while True:
                # print(temp_size)
                if temp_size*8/1000 > next_frame_size3: # in kb
                    break
                # print(packet_serial, i)
                # print(len(all_packet_size[0]))
                # print(all_packet_size[packet_serial])
                temp_size = temp_size + all_packet_size[1][packet_serial3] # in bytes
                packet_serial3 = packet_serial3 + 1
                time3 += all_packet_arrival_time[1][packet_serial3] - all_packet_arrival_time[1][packet_serial3 - 1]
                if(time3 > frame_time / 2): 
                    frameloss += 1
                    break
            frame_arrival_time3.append(real_time + time2 + time3)
            frame_send_time4.append(real_time + time2 + time3)
            temp_size = 0
            temp_upload = 0
            timeu = 0

            upload_serial = upload_serial + 1
            while True:
                # print(temp_size)
                if temp_upload * 8/1000 > next_frame_size2: # in kb
                    break
                # print(packet_serial, i)
                # print(len(all_packet_size[0]))
                # print(all_packet_size[packet_serial])
                temp_upload = temp_upload + upload_packet_size[upload_serial] # in bytes
                upload_serial = upload_serial + 1
                timeu += upload_packet_size[upload_serial] - upload_packet_size[upload_serial - 1]
                if(timeu > frame_time / 2): 
                    frameloss += 1
                    break
            while True:
                # print(all_packet_arrival_time[0][packet_serial], real_time)
                if real_time4 == 0:
                    packet_serial4 = 0
                    break
                elif all_packet_arrival_time[2][packet_serial4] >= real_time4 and all_packet_arrival_time[2][packet_serial4-1] < real_time4:
                    break
                packet_serial4 = packet_serial4 + 1
            packet_serial4 = packet_serial4 + 1
            while True:
                # print(temp_size)
                if temp_size*8/1000 > next_frame_size4: # in kb
                    break
                # print(packet_serial, i)
                # print(len(all_packet_size[0]))
                # print(all_packet_size[packet_serial])
                temp_size = temp_size + all_packet_size[2][packet_serial4] # in bytes
                packet_serial4 = packet_serial4 + 1
                time4 += all_packet_arrival_time[2][packet_serial4] - all_packet_arrival_time[2][packet_serial4 - 1]
                if(time4 > frame_time / 2): 
                    frameloss += 1
                    break
                
            frame_arrival_time4.append(real_time + time2 + time3 + time4)
            real_time += time2 + time3 + time4
            real_time1 += time2 + time3 + time4
            real_time2 += time2
            real_time3 += time3
            real_time4 += time4
                # record the throughput history for every frame (kbs)
            network_TP_history.append((next_frame_size2 + next_frame_size3 + next_frame_size4)/(time2 + time3 + time4))
            network_TP_history2.append((next_frame_size2/time2))
            network_TP_history3.append((next_frame_size3/time3))
            network_TP_history4.append((next_frame_size4/time4))

            
        # print(len(frame_cdn_arrival_time))
        # print(frame_cdn_arrival_time)
        for i in range(int(total_frame_number)):
            print(frame_send_time2[i],frame_arrival_time2[i],frame_send_time3[i],frame_arrival_time3[i],frame_send_time4[i],frame_arrival_time4[i])
        # based on the packet arrival time and estimated frame size, calculate the exact arrival time of
        # each frame at the CDN server
        print("-----------------------------------summary-----------------------------------")
        print("mean frame size of peer2(kb):")
        print(statistics.mean(estimated_frame_size2))
        print("mean frame size of peer3(kb):")
        print(statistics.mean(estimated_frame_size3))
        print("mean frame size of peer4(kb):")
        print(statistics.mean(estimated_frame_size4))
        print("mean throughput of peer2(kb/s):")
        print(statistics.mean(network_TP_history2))
        print("mean throughput of peer3(kb/s):")
        print(statistics.mean(network_TP_history3))
        print("mean throughput of peer4(kb/s):")
        print(statistics.mean(network_TP_history4))
        print("frame loss:")
        print(frameloss)
        network_TP_history2_trans = [min(2000,i * frame_time / 3) for i in network_TP_history2]
        network_TP_history3_trans = [min(2000,i * frame_time / 3) for i in network_TP_history3]
        network_TP_history4_trans = [min(2000,i * frame_time / 3) for i in network_TP_history4]
        difference2 = [abs(network_TP_history2_trans[i] - estimated_frame_size2[i]) for i in range(int(total_frame_number))]
        difference3 = [abs(network_TP_history3_trans[i] - estimated_frame_size3[i]) for i in range(int(total_frame_number))]
        difference4 = [abs(network_TP_history4_trans[i] - estimated_frame_size4[i]) for i in range(int(total_frame_number))]
        fluctuation2 = [abs(estimated_frame_size2[i + 1] - estimated_frame_size2[i]) for i in range(int(total_frame_number) - 1)]
        fluctuation3 = [abs(estimated_frame_size3[i + 1] - estimated_frame_size3[i]) for i in range(int(total_frame_number) - 1)]
        fluctuation4 = [abs(estimated_frame_size4[i + 1] - estimated_frame_size4[i]) for i in range(int(total_frame_number) - 1)]
        fluctuation2.append(statistics.mean(fluctuation2))
        fluctuation3.append(statistics.mean(fluctuation3))
        fluctuation4.append(statistics.mean(fluctuation4))
        framenumber = range(int(total_frame_number))
        plt.plot(framenumber, estimated_frame_size2, '.-', label='estimated frame size2')
        plt.plot(framenumber, estimated_frame_size3, '.-', label='estimated frame size3')
        plt.plot(framenumber, estimated_frame_size4, '.-', label='estimated frame size4')
        plt.plot(framenumber, network_TP_history2_trans, '.-', label='network throughput history2')
        plt.plot(framenumber, network_TP_history3_trans, '.-', label='network throughput history3')
        plt.plot(framenumber, network_TP_history4_trans, '.-', label='network throughput history4')
        #plt.plot(framenumber, difference2, '.-', label='difference2')
        #plt.plot(framenumber, difference3, '.-', label='difference3')
        #plt.plot(framenumber, difference4, '.-', label='difference4')
        #plt.plot(framenumber, fluctuation2, '.-', label='fluctuation2')
        #plt.plot(framenumber, fluctuation3, '.-', label='fluctuation3')
        #plt.plot(framenumber, fluctuation4, '.-', label='fluctuation4')
        plt.xticks(framenumber)  
        plt.xlabel('frame') 
        plt.legend() 
        plt.show() 
        # print(frameloss)
        # generate a CDN arrival time list with frame size
    '''else:
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
        print(statistics.mean(ideal_frame_size))'''

# Part two: downloading part
# for stage 1: downloading part is still all-i CBR where the bitrate and the frame size is fixed, if the frame size is smaller than the
# designed size at that bitrate, then use the smaller bitrate ones, otherwise just drop it
Bitrate_Ladder = [800, 1400, 2200] # kbps
target_frame_size = []  # kb
for bitrate in Bitrate_Ladder:
    target_frame_size.append(bitrate/FPS)


# how individual frame sizes impact the QoE and how to design the QoE to cope with it





