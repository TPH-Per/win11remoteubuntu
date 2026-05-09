# ThunderKVM

A Software KVM over Thunderbolt/USB-C Cable.

Control an Ubuntu laptop from a Windows laptop using a direct USB-C / Thunderbolt cable — no internet, no relay server, no KVM switch hardware needed.

## Setup Instructions (3 Steps)

**Step 1: Connect the Cable**
Plug a Thunderbolt or USB-C data cable directly between the Windows and Ubuntu laptops. Wait a few seconds for the OS to detect the new network interface.

**Step 2: Configure Static IPs**
- **On Ubuntu:** Run `sudo ./scripts/setup-ubuntu-network.sh` to set the IP to `192.168.100.2`.
- **On Windows:** Open PowerShell as Administrator and run `.\scripts\setup-windows-network.ps1` to set the IP to `192.168.100.1`.

**Step 3: Run the Server and Client**
- **On Ubuntu (Server):** 
  ```bash
  cd ubuntu-server
  python server.py
  ```
  *(Note: If you are using Ubuntu 22.04+ with Wayland, you must log out and select "Ubuntu on Xorg", or follow the instructions printed by the server).*
  
- **On Windows (Client):**
  ```cmd
  cd windows-client
  python client.py --host 192.168.100.2
  ```

## Usage
Once connected, the Windows client will open a window showing the Ubuntu screen. 
Press **Scroll Lock** to toggle KVM focus:
- **LOCAL Mode (Red Indicator):** Your mouse and keyboard inputs go to Windows normally.
- **REMOTE Mode (Green Indicator):** Your mouse and keyboard inputs are captured and sent to Ubuntu. The cursor is warped to the center of the viewer window.
