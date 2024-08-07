import psutil
import time
import csv
import sys
import signal

# Global variable to track whether the script should continue running
running = True

# Signal handler to gracefully handle termination
def signal_handler(sig, frame):
    global running
    running = False

def get_total_resources():
    total_ram = psutil.virtual_memory().total  # Total RAM in bytes
    total_cores = psutil.cpu_count()           # Total CPU cores
    return total_ram, total_cores

def collect_metrics(output_file):
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['timestamp', 'cpu_percent', 'rss']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        while running:
            timestamp = time.time()
            cpu_percent = psutil.cpu_percent(interval=None)
            memory_info = psutil.virtual_memory()
            rss = memory_info.used
            
            writer.writerow({
                'timestamp': timestamp,
                'cpu_percent': cpu_percent,
                'rss': rss
            })
            csvfile.flush()
            time.sleep(1)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 system_monitor.py <output_file>")
        sys.exit(1)
    
    output_file = sys.argv[1]
    
    # Register signal handler for SIGINT (Ctrl+C)
    signal.signal(signal.SIGINT, signal_handler)
    
    total_ram, total_cores = get_total_resources()
    print(f"Total RAM: {total_ram} bytes")
    print(f"Total CPU Cores: {total_cores}")
    
    collect_metrics(output_file)
    
    print("Monitoring script terminated.")
