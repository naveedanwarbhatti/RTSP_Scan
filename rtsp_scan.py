import socket
import argparse
import base64
import json
from colorama import Fore, Style, init
import ipaddress
import os

# Initialize colorama for cross-platform support
init()

# Function to load IP addresses from a file
def load_ips_from_file(ips_file):
    try:
        with open(ips_file, 'r') as file:
            ips = [line.strip() for line in file.readlines()]
        print(f"Loaded {len(ips)} IP addresses from {ips_file}")
        return ips
    except Exception as e:
        print(f"Error loading IP addresses file: {e}")
        return []

# Function to parse a range of IP addresses (e.g., 192.168.1.1-192.168.1.10)
def parse_ip_range(ip_range):
    try:
        start_ip, end_ip = ip_range.split('-')
        start = ipaddress.IPv4Address(start_ip)
        end = ipaddress.IPv4Address(end_ip)
        return [str(ip) for ip in ipaddress.summarize_address_range(start, end)]
    except Exception as e:
        print(f"Error parsing IP range: {e}")
        return []

# Function to load credentials from a JSON file
def load_credentials(credentials_file):
    try:
        with open(credentials_file, 'r') as file:
            credentials_data = json.load(file)
        usernames = credentials_data.get('usernames', [])
        passwords = credentials_data.get('passwords', [])
        credentials = [(user, pwd) for user in usernames for pwd in passwords]
        print(f"Loaded {len(usernames)} usernames and {len(passwords)} passwords from {credentials_file}")
        return credentials
    except Exception as e:
        print(f"Error loading credentials file: {e}")
        return []

# Function to send an RTSP DESCRIBE request to a specific IP, port, and route with optional credentials
def send_describe_request(ip, port, route, timeout, username=None, password=None):
    request = f"DESCRIBE rtsp://{ip}:{port}/{route} RTSP/1.0\r\nCSeq: 1\r\n"
    
    # Add Basic Authentication header if username and password are provided
    if username and password:
        credentials = f"{username}:{password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode("utf-8")
        request += f"Authorization: Basic {encoded_credentials}\r\n"
    
    request += "\r\n"
    
    try:
        # Create a socket connection to the RTSP server with a custom timeout
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)  # Set the custom timeout
        sock.connect((ip, port))
        sock.send(request.encode())
        
        # Get the response from the server
        response = sock.recv(4096)
        sock.close()
        return response.decode('utf-8')
    except Exception as e:
        return None

# Function to search for RTSP routes and optionally try credentials
def attack_rtsp(ip, port, routes_file, credentials_file, timeout, mode, debug=False):
    routes = load_routes(routes_file)
    if not routes:
        print(f"{ip} [Failed]: No routes found or failed to load the routes file.")
        return
    
    credentials = []
    if mode == 'credentials':
        credentials = load_credentials(credentials_file)
    
    # Loop over each route
    for route in routes:
        if debug:
            print(Fore.GREEN + f"Trying route: {route}" + Style.RESET_ALL)
        
        # Step 1: Try the route without credentials
        response = send_describe_request(ip, port, route, timeout)
        
        if response:
            if debug:
                print(Fore.GREEN + f"Response for route {route}:\n{response}" + Style.RESET_ALL)
                
            # If the stream is accessible (200 OK), report success
            if "RTSP/1.0 200 OK" in response:
                rtsp_url = f"rtsp://{ip}:{port}/{route}"
                print(f"Stream found: {rtsp_url}")
                return  # Exit after finding the stream
            
            # If the server requires authentication (401 Unauthorized) and the mode is "credentials", try with credentials
            elif "RTSP/1.0 401 Unauthorized" in response and mode == 'credentials':
                print(f"Authorization required for route: {route}. Trying with credentials...")
                
                for username, password in credentials:
                    if debug:
                        print(Fore.GREEN + f"Trying with credentials: {username}/{password}" + Style.RESET_ALL)
                    
                    # Step 2: Retry the route with each credential combination
                    auth_response = send_describe_request(ip, port, route, timeout, username=username, password=password)
                    
                    if auth_response and "RTSP/1.0 200 OK" in auth_response:
                        rtsp_url = f"rtsp://{username}:{password}@{ip}:{port}/{route}"
                        print(f"Stream found with credentials: {rtsp_url}")
                        return  # Exit after finding the stream with credentials
    
    # If no successful stream was found
    print(f"{ip} [Failed]")

# Function to load RTSP routes from a file
def load_routes(routes_file):
    try:
        with open(routes_file, 'r') as file:
            routes = [line.strip() for line in file.readlines()]
        print(f"Loaded {len(routes)} routes from {routes_file}")
        return routes
    except Exception as e:
        print(f"Error loading routes file: {e}")
        return []

# Main function to handle input arguments
def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="RTSP scanner for multiple IPs and routes with or without credentials.")
    parser.add_argument('-i', '--ip', required=True, help='Single IP, comma-separated IPs, IP range, or file path containing IPs')
    parser.add_argument('--routes', '-R', default="dictionaries/routes.txt", help='Path to the file containing list of RTSP routes (default: dictionaries/routes.txt)')
    parser.add_argument('--credentials', '-C', default="dictionaries/credentials.json", help='Path to the JSON file containing credentials (default: dictionaries/credentials.json)')
    parser.add_argument('--port', '-P', type=int, default=554, help='RTSP port to use (default: 554)')
    parser.add_argument('--timeout', '-T', type=float, default=1.0, help='Set custom timeout for each RTSP request (default: 1 second)')
    parser.add_argument('--mode', '-M', choices=['routes', 'credentials'], default='routes', help='Mode of operation: "routes" (find routes only) or "credentials" (apply credentials if required)')
    parser.add_argument('--debug', '-d', action='store_true', help='Enable debug mode to print tried routes and responses')
    
    args = parser.parse_args()

    # Detect input format for IP addresses
    ips = []
    if os.path.isfile(args.ip):
        # IPs are in a file
        ips = load_ips_from_file(args.ip)
    elif ',' in args.ip:
        # Multiple comma-separated IPs
        ips = args.ip.split(',')
    elif '-' in args.ip:
        # IP range
        ips = parse_ip_range(args.ip)
    else:
        # Single IP
        ips = [args.ip]
    
    if not ips:
        print("No valid IP addresses found.")
        return
    
    # Loop through each IP address and try the routes
    for ip in ips:
        print(f"Scanning IP: {ip}")
        attack_rtsp(ip, args.port, args.routes, args.credentials, timeout=args.timeout, mode=args.mode, debug=args.debug)

# Entry point of the script
if __name__ == "__main__":
    main()
