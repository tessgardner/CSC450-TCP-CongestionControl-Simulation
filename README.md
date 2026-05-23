# CSC450-TCP-CongestionControl-Simulation

A Python-based simulation of TCP Tahoe and TCP Reno congestion control algorithms using packet trace data exported from Wireshark.

This project analyzes TCP traffic, detects congestion events through triple duplicate ACKs, and simulates how Tahoe and Reno adjust the congestion window (```cwnd```) and slow start threshold (```ssthresh```) over time.

### Features:
* Simulates TCP Tahoe and TCP Reno
* Detects Duplicate ACKS, Triple Duplicate ACKS, and congestion events
* Tracks the congestion window, slow start threshold, and congestion control state
* Exports simulation results to CSV files
* Uses real Wireshark-exported TCP trace data

### Technologies Used:
* Python 3
* Pandas
* Wireshark CSV exports

### Expected CSV Format
The input CSV file should contain at least the following columns:
* ```No.```- Packet number
* ```Protocol```- Packet protocol
* ```Source_IP```- Source IP address
* ```Destination_IP```- Destination IP address
* ```ACK```- TCP acknowledgement number

### Installation:
Clone the repository:  
```git clone https://github.com/YOUR_USERNAME/tcp-congestion-control.git```  
```cd tcp-congestion-control```  

Install dependencies:  
```pip install pandas```  

### Usage:
Run the script from the command line:  
```python congestion_control.py <csv_file> <destination_ip> <source_ip>```

### Output Files:
The program generates two CSC files:
1. ```TCP_tahoe_output.csv```
2. ```TCP_reno_output.csc```

These files contain:
* Congestion window values
* Slow start thresholds
* Congestion states
* Detected congestion events  

Note: existing output files will be overwritten if they already exist
