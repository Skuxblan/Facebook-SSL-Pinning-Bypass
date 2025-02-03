import os
import sys
import requests
import subprocess
import lzma
import time

def get_latest_frida_version():
    """Get the latest Frida release version from GitHub."""
    try:
        response = requests.get("https://api.github.com/repos/frida/frida/releases/latest")
        response.raise_for_status()
        return response.json()["tag_name"]
    except Exception as e:
        print(f"[-] Error getting latest Frida version: {e}")
        sys.exit(1)

def get_frida_version():
    """Get the installed Frida version or latest available version."""
    try:
        result = subprocess.run(['frida', '--version'], capture_output=True, text=True)
        installed_version = result.stdout.strip()
        latest_version = get_latest_frida_version()
        
        print(f"[*] Installed Frida version: {installed_version}")
        print(f"[*] Latest Frida version: {latest_version}")
        
        return latest_version
    except FileNotFoundError:
        print("[-] Frida not found. Please install Frida first.")
        sys.exit(1)

def get_device_arch():
    """Get the Android device architecture."""
    try:
        result = subprocess.run(['adb', 'shell', 'getprop', 'ro.product.cpu.abi'], 
                              capture_output=True, text=True)
        arch = result.stdout.strip()
        
        # Map Android architectures to Frida naming
        arch_map = {
            'arm64-v8a': 'android-arm64',
            'armeabi-v7a': 'android-arm',
            'x86': 'android-x86',
            'x86_64': 'android-x86_64'
        }
        
        return arch_map.get(arch, arch)
    except subprocess.CalledProcessError:
        print("[-] Error: Unable to get device architecture. Is ADB connected?")
        sys.exit(1)

def download_frida_server(frida_version, arch):
    """Download Frida server for the specified architecture."""
    base_url = f"https://github.com/frida/frida/releases/download/{frida_version}"
    filename = f"frida-server-{frida_version}-{arch}"
    url = f"{base_url}/{filename}.xz"
    
    print(f"[*] Downloading Frida server from: {url}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Save the compressed content to a temporary file
        with open(f"{filename}.xz", "wb") as f:
            f.write(response.content)
            
        # Decompress using lzma
        with lzma.open(f"{filename}.xz", "rb") as compressed:
            with open("frida-server", "wb") as decompressed:
                decompressed.write(compressed.read())
                
        # Clean up the .xz file
        os.remove(f"{filename}.xz")
        if os.path.exists(filename):
            os.remove(filename)
        
        return "frida-server"
    except Exception as e:
        print(f"[-] Error downloading Frida server: {e}")
        sys.exit(1)

def check_existing_frida_server():
    """Check if frida-server already exists on device."""
    try:
        # Check if file exists
        result = subprocess.run(
            ['adb', 'shell', 'ls /data/local/tmp/frida-server'],
            capture_output=True, text=True, shell=True
        )
        return result.returncode == 0
    except:
        return False

def start_frida(filename=None):
    """Start Frida server on device. If filename is provided, push it first."""
    try:
        # Kill any existing Frida server process
        print("[*] Attempting to kill existing Frida server...")
        subprocess.run(['adb', 'shell', 'su -c "pkill -9 frida-server"'], 
                      capture_output=True, shell=True)
        time.sleep(1)
        
        # Push file if provided
        if filename:
            print("[*] Pushing Frida server to device...")
            result = subprocess.run(['adb', 'push', filename, '/data/local/tmp/frida-server'], 
                                  capture_output=True, text=True)
            if result.stderr and "pushed" in result.stderr:
                print(f"[+] {result.stderr.strip()}")
        
        print("[*] Setting permissions...")
        subprocess.run(['adb', 'shell', 'su -c "chmod 755 /data/local/tmp/frida-server"'], 
                      capture_output=True, shell=True)
        
        print("[*] Running Frida server...")
        subprocess.run(['adb', 'shell', 'su -c "/data/local/tmp/frida-server -D"'], 
                      capture_output=True, shell=True)
        print("[+] Frida server is running!")
        print("[+] You can now use Frida for injection")
        
    except subprocess.CalledProcessError as e:
        print(f"[-] Error: {e}")
        sys.exit(1)

def main():
    print("[*] Starting Frida server setup...")
    
    # Check if ADB is available
    try:
        subprocess.run(['adb', 'version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[-] Error: ADB not found. Please install Android SDK platform tools.")
        sys.exit(1)
    
    # Get device state
    result = subprocess.run(['adb', 'get-state'], capture_output=True, text=True)
    if 'device' not in result.stdout:
        print("[-] Error: No device connected. Please connect an Android device.")
        sys.exit(1)
    
    # Get latest Frida version and device architecture
    frida_version = get_latest_frida_version()
    device_arch = get_device_arch()
    
    print(f"[*] Using Frida version: {frida_version}")
    print(f"[*] Device architecture: {device_arch}")
    
    # Check if frida-server already exists
    if check_existing_frida_server():
        print("[*] Frida server already exists on device, starting server...")
        start_frida()
    else:
        print("[*] Downloading new frida-server...")
        # Download and setup Frida server
        filename = download_frida_server(frida_version, device_arch)
        start_frida(filename)
        # Clean up downloaded files
        if os.path.exists(filename):
            os.remove(filename)

if __name__ == "__main__":
    main()
