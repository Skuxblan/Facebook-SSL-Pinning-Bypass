import frida
import sys

def hook_proxygen_SSLVerification():
    # Connect to the device
    device = frida.get_usb_device()

    # Spawn the Facebook app
    try:
        print("[*] Spawning com.facebook.katana...")
        pid = device.spawn(["com.facebook.katana"])
        session = device.attach(pid)
        device.resume(pid)  # Resume the app after attaching
    except Exception as e:
        print(f"[-] Failed to spawn or attach to the app: {e}")
        return

    # JavaScript code to inject into the app
    script = session.create_script("""
    const functionName = "_ZN8proxygen15SSLVerification17verifyWithMetricsEbP17x509_store_ctx_stRKNSt6__ndk212basic_stringIcNS3_11char_traitsIcEENS3_9allocatorIcEEEEPNS0_31SSLFailureVerificationCallbacksEPNS0_31SSLSuccessVerificationCallbacksERKNS_15TimeUtilGenericINS3_6chrono12steady_clockEEERNS_10TraceEventE";
    
    // Function to hook the target function
    function hookFunction() {
        try {
            // Find the module containing the function
            const module = Process.findModuleByName("libcoldstart.so");
            if (!module) {
                console.log("[-] libcoldstart.so module not found!");
                return; // Exit the function if the module is not found
            }

            // Find the function by name
            const f = Module.getExportByName(module.name, functionName);
            if (f) {
                console.log(`[*] Function base address: ${module.base}`);
                console.log(`[*] Function offset: 0x${f.sub(module.base).toString(16)}`);
                
                // Display 16 bytes before and after the return instruction
                const returnInstruction = f.add(0x8c7e28 - 0x8c7b44); // offset where mov w19, wzr is located
                console.log('[*] Instructions at return:');
                console.log(hexdump(returnInstruction.sub(16), { length: 32 }));

                // Hook the function
                Interceptor.attach(f, {
                    onLeave: function (retvalue) {
                        console.log(`[*] Original return value: ${retvalue}`);
                        retvalue.replace(1); // Change the return value to 1
                        console.log('[*] Return value changed to 1');
                    }
                });
                console.log(`[*][+] Hooked function in ${module.name}`);
            } else {
                console.log(`[*][-] Function ${functionName} not found`);
            }
        } catch (err) {
            console.log(`[*][-] Failed to hook function: ${err}`);
        }
    }

    // Function to wait for the module to be loaded
    function waitForModule(moduleName) {
        return new Promise((resolve, reject) => {
            const interval = setInterval(() => {
                const module = Process.findModuleByName(moduleName);
                if (module) {
                    clearInterval(interval);
                    resolve(module);
                }
            }, 200);
        });
    }

    // Wait for the module to be loaded, then hook the function
    waitForModule("libcoldstart.so").then(hookFunction).catch(err => {
        console.log(`[*][-] Error waiting for module: ${err}`);
    });
    """)

    # Handle messages from the injected JavaScript
    def on_message(message, data):
        print(message)

    script.on('message', on_message)
    script.load()
    print("[*] Script loaded. Press Ctrl+C to exit.")
    sys.stdin.read()

if __name__ == "__main__":
    # Hook the SSL verification function
    hook_proxygen_SSLVerification()