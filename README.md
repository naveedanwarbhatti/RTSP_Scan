
# RTSP Route and Credential Scanner

This tool scans RTSP streams on IP cameras to find valid RTSP routes and optionally applies credentials if the server requires authentication. You can use this tool to find accessible RTSP routes and, if needed, authenticate with provided credentials.

## Features

- **Find RTSP Routes**: Scan for accessible RTSP routes on specified IP addresses.
- **Apply Credentials (Optional)**: If a server requires credentials (`401 Unauthorized`), the tool can attempt to authenticate using provided usernames and passwords.
- **Modes**: Choose between "routes" mode (to just find RTSP routes) and "credentials" mode (to apply credentials if necessary).
- **Support for Single IP, IP Ranges, and IP Files**: Accepts a single IP, a range of IP addresses, or a file containing IPs.
- **Customizable Timeout**: Set custom timeouts for each RTSP request.
- **Debug Mode**: Enable debug mode to get detailed output of each request and response.

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/rtsp-route-scanner.git
    ```

2. Install the required dependencies (if needed, e.g., `colorama`):

    ```bash
    pip install colorama
    ```

## Usage

You can run the script with different options depending on your needs. Here's how you can use the tool:

### Basic Usage (Finding Routes Only)

```bash
python rtsp_scan.py -i 192.168.1.100 --mode routes
```

This will attempt to find accessible RTSP routes on the specified IP without applying credentials, even if authentication is required.

### Finding Routes and Applying Credentials

```bash
python rtsp_scan.py -i 192.168.1.100 --mode credentials
```

This will scan for accessible RTSP routes and apply credentials if the server responds with `401 Unauthorized`.

### IP Input Options

You can specify IP addresses in several ways:

1. **Single IP**:
    ```bash
    python rtsp_scan.py -i 192.168.1.100
    ```

2. **Multiple Comma-Separated IPs**:
    ```bash
    python rtsp_scan.py -i 192.168.1.100,192.168.1.101,192.168.1.102
    ```

3. **IP Range**:
    ```bash
    python rtsp_scan.py -i 192.168.1.100-192.168.1.110
    ```

4. **File Containing IPs**:
    ```bash
    python rtsp_scan.py -i /path/to/ips.txt
    ```

### Example Commands

1. **Find Routes (No Credentials)**:
    ```bash
    python rtsp_scan.py -i 192.168.1.100 --mode routes
    ```

2. **Find Routes and Apply Credentials**:
    ```bash
    python rtsp_scan.py -i 192.168.1.100 --mode credentials
    ```

3. **Multiple IPs with Credentials**:
    ```bash
    python rtsp_scan.py -i 192.168.1.100,192.168.1.101 --mode credentials
    ```

### Other Options

- **Set RTSP Port** (default: 554):
    ```bash
    python rtsp_scan.py -i 192.168.1.100 --port 8554
    ```

- **Set Timeout** (default: 1 second):
    ```bash
    python rtsp_scan.py -i 192.168.1.100 --timeout 5
    ```

- **Enable Debug Mode** (prints detailed request/response info):
    ```bash
    python rtsp_scan.py -i 192.168.1.100 --debug
    ```

### Default Values

- **Default Routes File**: `dictionaries/routes.txt`
- **Default Credentials File**: `dictionaries/credentials.json`

You can replace these with custom files using the `--routes` or `--credentials` flags.

### Example Output

#### If RTSP Route Doesn't Require Credentials

```bash
Scanning IP: 192.168.1.100
Trying route: /live/ch01_0
Response for route /live/ch01_0:
RTSP/1.0 200 OK
Stream found: rtsp://192.168.1.100:554/live/ch01_0
```

#### If RTSP Route Requires Credentials

```bash
Scanning IP: 192.168.1.100
Trying route: /live/ch01_0
Response for route /live/ch01_0:
RTSP/1.0 401 Unauthorized
Authorization required for route: /live/ch01_0. Trying with credentials...
Trying with credentials: admin/admin
Stream found with credentials: rtsp://admin:admin@192.168.1.100:554/live/ch01_0
```

#### If Route Fails (No Credentials in "routes" mode)

```bash
Scanning IP: 192.168.1.100
Trying route: /live/ch01_0
Response for route /live/ch01_0:
RTSP/1.0 401 Unauthorized
192.168.1.100 [Failed]
```

### Flags and Options

| Flag | Description | Example |
|------|-------------|---------|
| `-i, --ip` | Specify the IP, range, or file | `-i 192.168.1.100`, `-i 192.168.1.100-192.168.1.110`, `-i ips.txt` |
| `-R, --routes` | Path to routes file (default: `dictionaries/routes.txt`) | `--routes /custom/routes.txt` |
| `-C, --credentials` | Path to credentials file (default: `dictionaries/credentials.json`) | `--credentials /custom/credentials.json` |
| `-P, --port` | RTSP port (default: 554) | `--port 8554` |
| `-T, --timeout` | Timeout for RTSP requests (default: 1 second) | `--timeout 5` |
| `-M, --mode` | Operation mode: `routes` (default) or `credentials` (apply credentials if required) | `--mode credentials` |
| `-d, --debug` | Enable debug mode | `--debug` |

---

## License

This project is licensed under the MIT License.

## Contributing

Feel free to open issues and pull requests if you'd like to contribute to this project.
