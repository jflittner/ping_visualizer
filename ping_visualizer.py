# ping_visualizer.py
import argparse
import subprocess
import pingparsing
import matplotlib.pyplot as plt
import time
import requests
from datetime import datetime
import csv
import os
import sys
import re

def make_filename_safe(filename):
    """
    Remove or replace unsafe characters from filename.
    """
    # Remove any characters that are not allowed in file names
    filename = re.sub(r'[^\w\-_. ]', '', filename)
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    return filename

def ping(host, count=2):
    try:
        rtt_avg = None
        while not isinstance(rtt_avg, float):
            cmd = ['ping', '-c', str(count), host]
            output = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
            ping_parser = pingparsing.PingParsing()
            result = ping_parser.parse(output.stdout)
            rtt_avg = result.rtt_avg
            if not isinstance(rtt_avg, float):
                print("Error during ping. Retrying...")
                time.sleep(1)
        return rtt_avg
    except Exception as e:
        print(f"Error fetching IP information: {e}. Exiting...")
        sys.exit(0)

def get_ip_info():
    try:
        response = requests.get('https://ipinfo.io/json')
        data = response.json()

        ip = data.get('ip', None)
        hostname = data.get('org', None) or data.get('hostname', ip)

        if ip and hostname:
            return ip, hostname
        else:
            print("Error fetching IP information: IP or hostname not found")
            return None, None
    except Exception as e:
        print(f"Error fetching IP information: {e}")
        return None, None


def append_to_csv(time, latency, filename):
    file_exists = os.path.isfile(filename)
    with open(filename, 'a', newline='') as csvfile:
        fieldnames = ['time', 'latency']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()
        writer.writerow({'time': time, 'latency': latency})

def set_dark_mode():
    plt.style.use('dark_background')
    plt.rcParams['axes.edgecolor'] = 'gray'
    plt.rcParams['xtick.color'] = 'white'
    plt.rcParams['ytick.color'] = 'white'
    plt.rcParams['grid.color'] = 'gray'
    plt.rcParams['figure.facecolor'] = 'black'

def on_close(event):
    print("Plot window closed. Exiting")
    sys.exit(0)

def visualize_ping(host, interval=1, duration=60, dark_mode=False, fig_width=8, fig_height=6):
    
    print(f"Running, use Ctrl-c or close the plot to exit the program")
    
    if dark_mode:
        set_dark_mode()

    latencies = []
    times = []
    last_latency = None

    start_time = time.time()
    current_time = start_time

    plt.ion()
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    fig.canvas.mpl_connect('close_event', on_close)

    ip, hostname = get_ip_info()

    # Make hostname safe for use in file names
    safe_hostname = make_filename_safe(hostname)

    # Set the CSV and image file names
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f"output/ping_data_{safe_hostname}_{timestamp}.csv"
    img_filename = f"output/ping_plot_{safe_hostname}_{timestamp}.png"

    # Create the output directory if it doesn't exist
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    try:
        while current_time - start_time < duration:
            
            latency = ping(host)
            latencies.append(latency)
            times.append(current_time - start_time)

            last_latency = latency if latency is not None else last_latency  # Update the last latency

            current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            title = f"Ping Latency: {host} - {current_datetime}"
            title += f"\nISP: {hostname}"

            ax.clear()
            ax.plot(times, latencies)
            ax.set_xlabel('Time (s)')
            ax.set_ylabel('Latency (ms)')

            min_latency = min(latencies)
            max_latency = max(latencies)
            avg_latency = sum(latencies) / len(latencies)
            jitter = sum([abs(latencies[i] - latencies[i - 1]) for i in range(1, len(latencies))]) / (len(latencies) - 1) if len(latencies) > 1 else 0
            title += f"\nMin: {min_latency:.2f}, Max: {max_latency:.2f}, Avg: {avg_latency:.2f}, Jitter: {jitter:.2f}, Last: {last_latency:.2f}"

            ax.set_title(title)
            plt.pause(interval)
            current_time = time.time()
            
            # Append data to the CSV file
            append_to_csv(times[-1], latencies[-1], csv_filename)

            # Save the plot as a PNG image
            plt.savefig(img_filename)

        print(f"Close the plot window to exit the program")
        plt.ioff()
        plt.show()

    except KeyboardInterrupt:
        print("Program interrupted by user. Exiting...")
        sys.exit(0)

    except Exception as e:
        # handle the exception
        print("An exception occurred:", e)

    finally:
        print(f"Finished! Plot saved to {img_filename} and data saved to {csv_filename}")
        sys.exit(0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Visualize ping latency over time.')
    parser.add_argument('host', help='Target host (e.g., google.com)')
    parser.add_argument('-i', '--interval', type=int, default=1, help='Interval between pings in seconds (default: 1)')
    parser.add_argument('-d', '--duration', type=int, default=60, help='Duration of the test in seconds (default: 60)')
    parser.add_argument('-m', '--dark_mode', action='store_true', help='Enable dark mode')
    parser.add_argument('-w', '--width', type=int, default=8, help='Width of the plot in inches (default: 8)')
    parser.add_argument('-ht', '--height', type=int, default=6, help='Height of the plot in inches (default: 6)')

    args = parser.parse_args()

    visualize_ping(args.host, args.interval, args.duration, args.dark_mode)
