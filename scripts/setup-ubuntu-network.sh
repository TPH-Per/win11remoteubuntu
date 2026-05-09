#!/usr/bin/env bash
# Run once: sudo ./scripts/setup-ubuntu-network.sh
# Configures static IP 192.168.100.2 on the Thunderbolt interface
# and makes it persistent across reboots via NetworkManager or netplan.

set -e

echo "[ThunderKVM] Detecting Thunderbolt/USB-C network interface..."

# Plug in the cable BEFORE running this script
# List all interfaces, find the one that appeared after plugging cable
IFACE=""
for iface in $(ls /sys/class/net/); do
    driver=$(readlink /sys/class/net/$iface/device/driver 2>/dev/null || true)
    if echo "$driver" | grep -qiE '(thunderbolt|apple_mfi_fastcharge|cdc_ncm|cdc_ether|rndis)'; then
        IFACE=$iface
        break
    fi
done

if [ -z "$IFACE" ]; then
    echo "Could not auto-detect interface. Available interfaces:"
    ip link show | grep -v 'lo:' | grep 'state'
    read -p "Enter interface name manually: " IFACE
fi

echo "[ThunderKVM] Using interface: $IFACE"

UBUNTU_IP="192.168.100.2"
NETMASK="24"

# Method 1: NetworkManager (desktop Ubuntu, most common)
if command -v nmcli &>/dev/null; then
    echo "[ThunderKVM] Configuring via NetworkManager..."
    nmcli con add type ethernet ifname "$IFACE" con-name "thunder-kvm" \
        ip4 "$UBUNTU_IP/$NETMASK" ipv4.method manual \
        ipv6.method disabled
    nmcli con up "thunder-kvm"
    echo "[ThunderKVM] NetworkManager connection 'thunder-kvm' created and active."

# Method 2: Netplan (Ubuntu server/headless)
elif [ -d /etc/netplan ]; then
    echo "[ThunderKVM] Configuring via Netplan..."
    cat > /etc/netplan/99-thunder-kvm.yaml << EOF
network:
  version: 2
  ethernets:
    $IFACE:
      dhcp4: no
      addresses: [$UBUNTU_IP/$NETMASK]
EOF
    netplan apply
    echo "[ThunderKVM] Netplan config written and applied."
fi

# Verify
sleep 1
if ip addr show "$IFACE" | grep -q "$UBUNTU_IP"; then
    echo "[ThunderKVM] SUCCESS: $IFACE → $UBUNTU_IP/$NETMASK"
else
    echo "[ThunderKVM] WARNING: IP not yet visible. Try: ip addr show $IFACE"
fi

echo ""
echo "[ThunderKVM] Ubuntu network setup complete."
echo "             Ubuntu IP: $UBUNTU_IP"
echo "             Now run setup-windows-network.ps1 on the Windows machine."
