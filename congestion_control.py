"""
Project 1 For CSC 450 (Computer Networks):
Simulates TCP Tahoe and TCP Reno congestion control behavior
using Wireshark-exported TCP trace data.
"""

import pandas as pd 
import math
import sys
import os

# TAHOE IMPLEMENTATION FUNCTION
def tcp_tahoe(cwnd, ssthresh, cwnd_array, ssthresh_array, state_array, congestion_state, PT_filtered, ProjectTrace, mss):

    # Iterating over each row of the filtered data (only TCP segments)
    for row in PT_filtered.itertuples():
        # If a triple duplicate ACK has been detected:
        if (row.triple_dup_ack == True):
            congestion_state = "Triple Duplicate Detected"
            ssthresh = cwnd / 2
            cwnd = mss
        # If the ACK is advancing as normal:
        elif (row.has_advanced == True):
            # Slow start state
            if (cwnd < ssthresh):
                congestion_state = "Slow Start"
                cwnd = cwnd + mss
            # Congestion avoidance state
            else:
                congestion_state = "Congestion Avoidance"
                cwnd += (mss * mss) / cwnd
        # If a duplicate ACK has been found but it's not a triple duplicate
        else:
            congestion_state = "Duplicate ACK"
        
        # Adding current cwnd, ssthresh, and congestion state values to an array for each iteration
        state_array.append(congestion_state)
        cwnd_array.append(cwnd)
        if (ssthresh == math.inf):
            ssthresh_array.append("")
        else:
            ssthresh_array.append(ssthresh)

    # Inserting the arrays for the entire iteration into the dataframe 
    PT_filtered['cwnd'] = cwnd_array
    PT_filtered['ssthresh'] = ssthresh_array
    PT_filtered['congestion state'] = state_array

    # Merging and returning the changes based on detected into the original csv 
    return pd.merge(ProjectTrace, PT_filtered[["No.", "has_advanced", "dup_count", "triple_dup_ack", "cwnd", "ssthresh", "congestion state"]], on="No.", how="left")

# RENO IMPLEMENTATION FUNCTION
def tcp_reno(cwnd, ssthresh, cwnd_array, ssthresh_array, state_array, congestion_state, PT_filtered, ProjectTrace, mss):
    
    congestion_found = False # tracks if congestion has been detected

    # Iterating over each row of the filtered data (only TCP segments)
    for row in PT_filtered.itertuples():
        # If a triple duplicate ACK has been detected:
        if (row.triple_dup_ack == True):
            congestion_state = "Fast Retransmit"
            congestion_found = True
            ssthresh = cwnd/2
            cwnd = ssthresh +(3 * mss)
        # Exiting fast recovery if we have gotten past the duplicates:
        elif (row.has_advanced == True) and (congestion_found == True):
            congestion_state = "Recovery is complete."
            cwnd = ssthresh
            congestion_found = False
        # Fast Recovery state
        elif (congestion_found == True) and (row.has_advanced == False):
            congestion_state = "Fast Recovery"
            cwnd = cwnd + mss
        elif (row.has_advanced == True) and (congestion_found == False):
            # Slow start state
            if (cwnd < ssthresh):
                congestion_state = "Slow Start"
                cwnd = cwnd + mss
            # Congestion avoidance state
            else:
                congestion_state = "Congestion Avoidance"
                cwnd += (mss * mss) / cwnd
    
        # Adding current cwnd, ssthresh, and congestion state values to an array for each iteration
        state_array.append(congestion_state)
        cwnd_array.append(cwnd)
        if (ssthresh == math.inf):
            ssthresh_array.append("")
        else:
            ssthresh_array.append(ssthresh)        
        
    # Inserting the arrays for the entire iteration into the dataframe 
    PT_filtered['cwnd'] = cwnd_array
    PT_filtered['ssthresh'] = ssthresh_array
    PT_filtered['congestion state'] = state_array

    # Merging and returning the changes based on detected into the original csv 
    return pd.merge(ProjectTrace, PT_filtered[["No.", "has_advanced", "dup_count", "triple_dup_ack", "cwnd", "ssthresh", "congestion state"]], on="No.", how="left")

# checking command line arguments
if len(sys.argv) != 4:
    print("Usage:python congestion_control.py <csv_file> <dest_ip> <src_ip>")
    sys.exit(1)

# INITIAL VALUES:
file_name = sys.argv[1]
dest_ip = sys.argv[2]
src_ip = sys.argv[3]

# verifying file
if not file_name.endswith(".csv"):
    print("Error: input file must be a .csv file")
    sys.exit(1)
if not os.path.exists(file_name):
    print(f"Error: file '{file_name}' not found")
    sys.exit(1)

mss = 1460 # max segment size
cwnd = mss # initialize congestion window to 1 mss
ssthresh = math.inf # slow start threshold, initialized to an extremely large number

is_tcp = "TCP" # Used to check if a segment is TCP protocol
congestion_state = "" # reflects the state of every tcp segment (slow start, congestion avoidance, fast recovery, etc)

cwnd_array = [] # array of cwnd values for each TCP segment
ssthresh_array = [] # array of ssthresh values for each TCP segment
state_array = [] # array of congestion states for each TCP segment

# Reading from .csv exported from wireshark
ProjectTrace = pd.read_csv(file_name)

# Filtering .csv so only TCP protocol segments with the correct src and dest ips are returned for us to work with
PT_filtered = ProjectTrace.loc[
    (ProjectTrace["Protocol"] == is_tcp) & 
    (ProjectTrace["Destination_IP"] == dest_ip) & 
    (ProjectTrace["Source_IP"] == src_ip)].copy()

# Logic to track when a triple ACK is identified and reflecting it in dataframe
PT_filtered = PT_filtered.sort_values("No.").reset_index(drop = True) # Sorting by packet number as a safety guard
PT_filtered["has_advanced"] = PT_filtered["ACK"].gt(PT_filtered["ACK"].shift()) # Tracking if current ACK is greater than last ACK
PT_filtered["groups"] = PT_filtered["has_advanced"].cumsum() # Grouping ACKs based on whether they've advanced or not
PT_filtered["dup_count"] = PT_filtered.groupby(["groups", "ACK"]).cumcount() # Counting number of duplicates of each ACK
PT_filtered["triple_dup_ack"] = PT_filtered["dup_count"] == 3 # Returns true for the packet with a triple duplicate ACK

# Returning segment that has the triple ACK
found_triple = PT_filtered.loc[PT_filtered['triple_dup_ack'] == True]
print(f"\nCONGESTION FOUND:\n{found_triple}\n")

print("Note: TCP_tahoe_output.csv and TCP_reno_output.csv will be overwritten if they already exist.")

# TCP TAHOE
print("Simulating TCP Tahoe...")
tahoe_output = tcp_tahoe(cwnd, ssthresh, cwnd_array, ssthresh_array, state_array, congestion_state, PT_filtered, ProjectTrace, mss)
tahoe_output.to_csv('TCP_tahoe_output.csv', index=False)
print("Simulation Complete. View output in TCP_tahoe_output.csv.")
print("\n")

# Clearing out variables before implementing Reno
cwnd_array = [] 
ssthresh_array = [] 
state_array = [] 
cwnd = mss
ssthresh = math.inf

#TCP RENO
print("Simulating TCP Reno...")
reno_output = tcp_reno(cwnd, ssthresh, cwnd_array, ssthresh_array, state_array, congestion_state, PT_filtered, ProjectTrace, mss)
reno_output.to_csv('TCP_reno_output.csv', index=False)
print("Simulation complete. View Output in TCP_reno_output.csv.")
print("\n")