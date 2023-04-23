# Ping Visualizer

Ping Visualizer is a simple Python script that displays ping latency over time in a graphical format. It also saves the ping data to a CSV file and generates a PNG image of the plot.

## Installation

1. Clone the repository to your local machine:

```
git clone https://github.com/your_username/ping_visualizer.git
```

2. Navigate to the project directory and create a virtual environment (optional):

```
cd ping_visualizer
python3 -m venv venv
```

3. Activate the virtual environment (optional):

```
source venv/bin/activate # For Linux and macOS
venv\Scripts\activate.bat # For Windows
```

4. Install the required dependencies:

```
pip install -r requirements.txt
```

## Usage

Run the script with the following command:

```
python ping_visualizer.py --dark_mode <host>
```

## Optional Arguments

| Flag | Description |
| --- | --- |
| `-i`, `--interval` | Interval between pings in seconds (default: 1) |
| `-d`, `--duration` | Duration of the test in seconds (default: 60) |
| `-m`, `--dark_mode` | Enable dark mode |
| `-w`, `--width` | Width of the plot in inches (default: 8) |
| `-ht`, `--height` | Height of the plot in inches (default: 6) |

Example:

```
python ping_visualizer.py google.com -i 2 -d 120 -w 7 -ht 5 --dark_mode
```

This command will visualize the ping latency to `google.com` with a 2-second interval between pings, a total duration of 120 seconds, and dark mode enabled.

## Output

The script will save the ping data to a CSV file (`ping_data_<timestamp>.csv`) and generate a PNG image of the plot (`ping_plot_<timestamp>.png`) in the current directory.

## Dependencies

- Python 3.x
- matplotlib
- pingparsing
- requests
- ipwhois