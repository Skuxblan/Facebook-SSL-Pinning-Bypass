# Facebook SSL Pinning Bypass

This tool provides functionality to bypass SSL pinning on Android applications using Frida. It consists of two main components: a Frida server setup script and an injection script specifically designed to bypass SSL certificate verification.

## Latest Tested App Version
- Facebook version: **498.0.0.54.74**

## Prerequisites

- Python 3.x
- Android Debug Bridge (ADB)
- Frida (`pip install frida-tools`)
- Rooted Android device
- Man-in-the-middle tool

## Installation

1. Clone this repository

2. Install requirements:
```bash
pip install -r requirements.txt
```

## Initial Setup

### MITM Tool Setup (mitmproxy example)
1. Install mitmproxy:
   - **Linux**: `apt install mitmproxy`
   - **Windows**: Download from official site

2. Start tool:
   - Console: `mitmproxy`
   - Web UI: `mitmweb`

3. Android proxy setup:
   - Wi-Fi settings
   - Modify network
   - Manual proxy
   - Computer IP:8080

4. Certificate setup:
   - Visit mitm.it
   - Install certificate
   - Enable in settings

## Requirements

Required Python packages:
```
frida-tools
requests
```

## Usage

### 1. Set up MITM Tool
1. Start your MITM tool (e.g., mitmproxy, Burp Suite)
2. Configure Android proxy settings:
   - Wi-Fi settings → Modify network
   - Set Manual proxy
   - Enter computer's IP and port (default: 8080)
3. Install & enable MITM certificate on Android:
   - Visit tool's cert page (e.g., mitm.it)
   - Install & enable in Security settings

### 2. Start Frida Server
```bash
python start-frida-server.py
```
This will:
- Detect device architecture
- Download matching Frida server
- Install and run on device

### 3. Inject SSL Bypass
```bash
python inject.py
```
This will:
- Hook into Facebook app
- Bypass SSL certificate verification
- Allow MITM inspection

### 4. Monitor Traffic
- Watch intercepted traffic in MITM tool
- Analyze SSL/TLS communications

## Known Issues and Limitations

- Requires rooted Android device
- Facebook app specific
- Needs USB debugging enabled
- Custom SSL verification hook

## Troubleshooting

1. Frida server issues:
   - Check root access
   - Verify ADB connection
   - Match Frida versions

2. Injection problems:
   - Confirm Frida is running
   - Check Facebook app
   - Verify device connection
   - Test MITM configuration

## Disclaimer

This tool is for educational and research purposes only.
