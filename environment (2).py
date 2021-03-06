import random
import datetime
import os
import statistics
from tracemalloc import Statistic
import matplotlib.pyplot as plt
import random

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
NETWORK_TRACE = 'download'
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
upload_speed = []
all_download_speed = []

link_delay = [4 / 1000, 5 / 1000, 6 / 1000] #s
# read the data into a list
for cooked_file in cooked_files:
    # temporary lists
    file_path = network_trace_dir + cooked_file
    packet_arrival_time = []
    packet_size = []
    download_speed = []
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
                if not packet_arrival_time[-1] == packet_arrival_time[-2]:
                    
                    download_speed.append(float(parse[1])*8/(packet_arrival_time[-1]-packet_arrival_time[-2])/1000)  # kbps
            serial = serial+1
            packet_size.append(float(parse[1]))
            if packet_arrival_time[-1] > 2 * video_duration: break
        all_download_speed.append(download_speed)    
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
                if not packet_arrival_time[-1] == packet_arrival_time[-2]:
                    
                    upload_speed.append(float(parse[1])*8/(packet_arrival_time[-1]-packet_arrival_time[-2])/1000)  # kbps
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
        frameloss2u = 0
        frameloss2d = 0
        frameloss3u = 0
        frameloss3d = 0
        frameloss4u = 0
        frameloss4d = 0
        # during initial buffer, send out the original frame
        for i in range(int(total_frame_number)):
            # initial_frame
            # print(real_time, i * frame_time)
            if i < 10:
                next_frame_size = raw_frame_size
                next_frame_size2 = raw_frame_size
                next_frame_size3 = raw_frame_size
                next_frame_size4 = raw_frame_size
            else:
                next_frame_size = (1 * network_TP_history[-1]) * frame_time * 8 / 3300
                if real_time > frame_arrival_time2[-1]:
                    next_frame_size2 = min((network_TP_history[-1]) * frame_time * 8 / 3500,(network_TP_history2[-1]) * frame_time * 8 / 1500)
                elif real_time > frame_arrival_time2[-2]:
                    next_frame_size2 = min((network_TP_history[-1]) * frame_time * 8 / 3500,(network_TP_history2[-2]) * frame_time * 8 / 1500)
                else:
                    next_frame_size2 = min((network_TP_history[-1]) * frame_time * 8 / 3500,(network_TP_history2[-3]) * frame_time * 8 / 1500)
                if real_time > frame_arrival_time3[-1]:
                    next_frame_size3 = min((network_TP_history[-1]) * frame_time * 8 / 3500,(network_TP_history3[-1]) * frame_time * 8 / 1500)
                elif real_time > frame_arrival_time3[-2]:
                    next_frame_size3 = min((network_TP_history[-1]) * frame_time * 8 / 3500,(network_TP_history3[-2]) * frame_time * 8 / 1500)
                else:
                    next_frame_size3 = min((network_TP_history[-1]) * frame_time * 8 / 3500,(network_TP_history3[-3]) * frame_time * 8 / 1500)
                if real_time > frame_arrival_time4[-1]:
                    next_frame_size4 = min((network_TP_history[-1]) * frame_time * 8 / 3500,(network_TP_history4[-1]) * frame_time * 8 / 1500)
                elif real_time > frame_arrival_time4[-2]:
                    next_frame_size4 = min((network_TP_history[-1]) * frame_time * 8 / 3500,(network_TP_history4[-2]) * frame_time * 8 / 1500)
                else:
                    next_frame_size4 = min((network_TP_history[-1]) * frame_time * 8 / 3500,(network_TP_history4[-3]) * frame_time * 8 / 1500)
            if real_time > (i + 5) * frame_time:
                '''next_frame_size = 0
                next_frame_size2 = 0
                next_frame_size3 = 0
                next_frame_size4 = 0'''
                
                print("protection")
                next_frame_size = min(next_frame_size, 4000 - 400 * (real_time / frame_time - i))
                next_frame_size2 = min(next_frame_size2, 4000 - 400 * (real_time / frame_time - i))
                next_frame_size3 = min(next_frame_size3, 4000 - 400 * (real_time / frame_time - i))
                next_frame_size4 = min(next_frame_size4, 4000 - 400 * (real_time / frame_time - i))
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
            delay_accumulation = 0
            timeu2 = 0
            timeu3 = 0
            timeu4 = 0
            time2 = 0
            time3 = 0
            time4 = 0
            skipu2 = 0
            skipd2 = 0
            skipu3 = 0
            skipd3 = 0
            skipu4 = 0
            skipd4 = 0
            sum_size = 0
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
                timeu2 += upload_time[upload_serial] - upload_time[upload_serial - 1]
                if(timeu2 > frame_time / 2): 
                    temp_upload -= upload_packet_size[upload_serial - 1]
                    timeu2 -= upload_time[upload_serial] - upload_time[upload_serial - 1]
                    skipu2 = frame_time / 2 - timeu2
                    frameloss2u += 1
                    break
            sum_size += temp_upload
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
                if(time2 > frame_time): 
                    temp_size -= all_packet_size[0][packet_serial2 - 1]
                    time2 -= all_packet_arrival_time[0][packet_serial2] - all_packet_arrival_time[0][packet_serial2 - 1]
                    skipd2 = frame_time - time2
                    frameloss2d += 1
                    break
            #time2 = max(time2, timeu2)
            if time2 == 0:
                network_TP_history2.append(0)
            else:
                network_TP_history2.append((temp_size)/(time2))
            
            frame_arrival_time2.append(real_time + link_delay[0] + max(time2 + skipd2, timeu2 + skipu2))
            frame_send_time3.append(real_time + timeu2 + skipu2)
            temp_size = 0
            temp_upload = 0
            
                
            upload_serial = upload_serial + 1
            while True:
                # print(temp_size)
                if temp_upload * 8/1000 > next_frame_size3: # in kb
                    break
                # print(packet_serial, i)
                # print(len(all_packet_size[0]))
                # print(all_packet_size[packet_serial])
                temp_upload = temp_upload + upload_packet_size[upload_serial] # in bytes
                upload_serial = upload_serial + 1
                timeu3 += upload_time[upload_serial] - upload_time[upload_serial - 1]
                if(timeu3 > frame_time / 2): 
                    temp_upload -= upload_packet_size[upload_serial - 1]
                    timeu3 -= upload_time[upload_serial] - upload_time[upload_serial - 1]
                    skipu3 = frame_time / 2 - timeu3
                    frameloss3u += 1
                    break
            sum_size += temp_upload
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
                if(time3 > frame_time): 
                    
                    temp_size -= all_packet_size[1][packet_serial3 - 1]
                    time3 -= all_packet_arrival_time[1][packet_serial3] - all_packet_arrival_time[1][packet_serial3 - 1]
                    skipd3 = frame_time - time3
                    frameloss3d += 1
                    break
            #time3 = max(time3, timeu3)
            if time3 == 0:
                network_TP_history3.append(0)
            else:
                network_TP_history3.append((temp_size)/(time3))

            frame_arrival_time3.append(real_time + timeu2 + skipu2 + link_delay[1] + max(time3 + skipd3, timeu3 + skipu3))
            frame_send_time4.append(real_time + timeu2 + skipu2 + timeu3 + skipu3)
            temp_size = 0
            temp_upload = 0

            upload_serial = upload_serial + 1
            while True:
                # print(temp_size)
                if temp_upload * 8/1000 > next_frame_size4: # in kb
                    break
                # print(packet_serial, i)
                # print(len(all_packet_size[0]))
                # print(all_packet_size[packet_serial])
                temp_upload = temp_upload + upload_packet_size[upload_serial] # in bytes
                upload_serial = upload_serial + 1
                timeu4 += upload_time[upload_serial] - upload_time[upload_serial - 1]
                if(timeu4 > frame_time / 2): 
                    temp_upload -= upload_packet_size[upload_serial - 1]
                    timeu4 -= upload_time[upload_serial] - upload_time[upload_serial - 1]
                    skipu4 = frame_time / 2 - timeu4
                    frameloss4u += 1
                    break
            sum_size += temp_upload
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
                if(time4 > frame_time): 
                    temp_size -= all_packet_size[2][packet_serial4 - 1]
                    time4 -= all_packet_arrival_time[2][packet_serial4] - all_packet_arrival_time[2][packet_serial4 - 1]
                    skipd4 = frame_time - time4
                    frameloss4d += 1
                    break
            #time4 = max(time4, timeu4)
            if time4 == 0:
                network_TP_history4.append(0)
            else:
                network_TP_history4.append((temp_size)/(time4))
            network_TP_history.append((sum_size)/(timeu2 + timeu3 + timeu4))
            frame_arrival_time4.append(real_time + timeu2 + skipu2 + timeu3 + skipu3 + link_delay[2] + max(time4 + skipd4, timeu4 + skipu4))
            real_time += timeu2 + timeu3 + timeu4 + skipu2 + skipu3 + skipu4
            real_time1 += timeu2 + timeu3 + timeu4 + skipu2 + skipu3 + skipu4
            real_time2 += max(time2 + skipd2, timeu2 + skipu2)
            real_time3 += max(time3 + skipd3, timeu3 + skipu3)
            real_time4 += max(time4 + skipd4, timeu4 + skipu4)
                # record the throughput history for every frame (kbs)
            print(time2 + skipd2, timeu2 + skipu2, time3 + skipd3,timeu3 + skipu3,time4 + skipd4, timeu4 + skipu4)
            

            
        # print(len(frame_cdn_arrival_time))
        # print(frame_cdn_arrival_time)
        for i in range(int(total_frame_number)):
            print(frame_send_time2[i],frame_arrival_time2[i],frame_send_time3[i],frame_arrival_time3[i],frame_send_time4[i],frame_arrival_time4[i])
        # based on the packet arrival time and estimated frame size, calculate the exact arrival time of
        # each frame at the CDN server
        tptest = [upload_time[i + 1] -upload_time[i] for i in range(int(total_frame_number) - 1)]
        tptest.append(statistics.mean(tptest))
        network_TP_history_trans = [min(2000,i * frame_time * 8 / 3000) for i in network_TP_history]
        network_TP_history2_trans = [min(2000,i * frame_time * 8 / 1000) for i in network_TP_history2]
        network_TP_history3_trans = [min(2000,i * frame_time * 8 / 1000) for i in network_TP_history3]
        network_TP_history4_trans = [min(2000,i * frame_time * 8 / 1000) for i in network_TP_history4]
        difference = [abs(network_TP_history_trans[i] - estimated_frame_size[i]) for i in range(int(total_frame_number))]
        difference2 = [abs(network_TP_history2_trans[i] - estimated_frame_size2[i]) for i in range(int(total_frame_number))]
        difference3 = [abs(network_TP_history3_trans[i] - estimated_frame_size3[i]) for i in range(int(total_frame_number))]
        difference4 = [abs(network_TP_history4_trans[i] - estimated_frame_size4[i]) for i in range(int(total_frame_number))]
        delay2 = [frame_arrival_time2[i] - i * frame_time for i in range(int(total_frame_number))]
        delay3 = [frame_arrival_time3[i] - i * frame_time for i in range(int(total_frame_number))]
        delay4 = [frame_arrival_time4[i] - i * frame_time for i in range(int(total_frame_number))]
        fluctuation =  [abs(estimated_frame_size[i + 1] - estimated_frame_size[i]) for i in range(int(total_frame_number) - 1)]
        fluctuation2 = [abs(estimated_frame_size2[i + 1] - estimated_frame_size2[i]) for i in range(int(total_frame_number) - 1)]
        fluctuation3 = [abs(estimated_frame_size3[i + 1] - estimated_frame_size3[i]) for i in range(int(total_frame_number) - 1)]
        fluctuation4 = [abs(estimated_frame_size4[i + 1] - estimated_frame_size4[i]) for i in range(int(total_frame_number) - 1)]
        fluctuation.append(statistics.mean(fluctuation))
        fluctuation2.append(statistics.mean(fluctuation2))
        fluctuation3.append(statistics.mean(fluctuation3))
        fluctuation4.append(statistics.mean(fluctuation4))
        framenumber = range(int(total_frame_number))
        print("-----------------------------------summary-----------------------------------")
        print("mean frame size of peer2(kb):")
        print(statistics.mean(estimated_frame_size2))
        print("mean frame size of peer3(kb):")
        print(statistics.mean(estimated_frame_size3))
        print("mean frame size of peer4(kb):")
        print(statistics.mean(estimated_frame_size4))
        print("mean throughput of peer2(B/s):")
        print(statistics.mean(network_TP_history2))
        print("mean throughput of peer3(B/s):")
        print(statistics.mean(network_TP_history3))
        print("mean throughput of peer4(B/s):")
        print(statistics.mean(network_TP_history4))
        print("mean delay of peer2(s):")
        print(statistics.mean(delay2))
        print("mean delay of peer3(s):")
        print(statistics.mean(delay3))
        print("mean delay of peer4(s):")
        print(statistics.mean(delay4))
        print("mean fluctuation of peer2(kb):")
        print(statistics.mean(fluctuation2))
        print("mean fluctuation of peer3(kb):")
        print(statistics.mean(fluctuation3))
        print("mean fluctuation of peer4(kb):")
        print(statistics.mean(fluctuation4))
        print("frame loss:(2up, 2down, 3up, 3down, 4up, 4down)")
        print(frameloss2u,frameloss2d,frameloss3u,frameloss3d,frameloss4u,frameloss4d)
        #plt.plot(framenumber, tptest, '.-', label='tptest')
        #plt.plot(framenumber, estimated_frame_size, '.-', label='estimated frame size')
        plt.plot(framenumber, estimated_frame_size2, '.-', label='estimated frame size2')
        plt.plot(framenumber, estimated_frame_size3, '.-', label='estimated frame size3')
        plt.plot(framenumber, estimated_frame_size4, '.-', label='estimated frame size4')
        #plt.plot(framenumber, network_TP_history, '.-', label='network throughput history')
        #plt.plot(framenumber, network_TP_history2, '.-', label='network throughput history2')
        #plt.plot(framenumber, network_TP_history3, '.-', label='network throughput history3')
        #plt.plot(framenumber, network_TP_history4, '.-', label='network throughput history4')
        #plt.plot(framenumber, network_TP_history_trans, '.-', label='network throughput history')
        #plt.plot(framenumber, network_TP_history2_trans, '.-', label='network throughput history2')
        #plt.plot(framenumber, network_TP_history3_trans, '.-', label='network throughput history3')
        #plt.plot(framenumber, network_TP_history4_trans, '.-', label='network throughput history4')
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





