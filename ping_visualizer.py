# ping_visualizer.py
import argparse
import subprocess
import pingparsing
import matplotlib.pyplot as plt
import time
import requests
from ipwhois import IPWhois
from datetime import datetime
import csv
import os


def ping(host, count=1):
    cmd = ['ping', '-c', str(count), host]
    output = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
    ping_parser = pingparsing.PingParsing()
    result = ping_parser.parse(output.stdout)
    return result.rtt_avg


def get_ip_info():
    try:
        ip = requests.get('https://api.ipify.org').text
        ipwhois = IPWhois(ip)
        lookup = ipwhois.lookup_rdap()
        hostname = lookup.get('asn_description')
        return ip, hostname
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


def visualize_ping(host, interval=1, duration=60, dark_mode=False, fig_width=8, fig_height=6):
    if dark_mode:
        set_dark_mode()

    latencies = []
    times = []

    start_time = time.time()
    current_time = start_time

    plt.ion()
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    ip, hostname = get_ip_info()

    # Set the CSV and image file names
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f"ping_data_{timestamp}.csv"
    img_filename = f"ping_plot_{timestamp}.png"

    while current_time - start_time < duration:
        latency = ping(host)
        latencies.append(latency)
        times.append(current_time - start_time)

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
        title += f"\nMin: {min_latency:.2f} ms, Max: {max_latency:.2f} ms, Avg: {avg_latency:.2f} ms, Jitter: {jitter:.2f} ms"

        ax.set_title(title)
        plt.pause(interval)
        current_time = time.time()
        
        # Append data to the CSV file
        append_to_csv(times[-1], latencies[-1], csv_filename)

        # Save the plot as a PNG image
        plt.savefig(img_filename)

    plt.ioff()
    plt.show()

    print(f"Data saved to {csv_filename}")

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
