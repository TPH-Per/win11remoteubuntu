# Run as Administrator in PowerShell:
# Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
# .\scripts\setup-windows-network.ps1

$WindowsIP = "192.168.100.1"
$PrefixLength = 24
$UbuntuIP = "192.168.100.2"

Write-Host "[ThunderKVM] Detecting Thunderbolt/USB-C network adapter..."

# Find the Thunderbolt / RNDIS adapter
$adapter = Get-NetAdapter | Where-Object {
    $_.InterfaceDescription -match '(Thunderbolt|RNDIS|USB Ethernet|Apple|Gadget)' -and
    $_.Status -ne 'Disabled'
} | Select-Object -First 1

if (-not $adapter) {
    Write-Host "Could not auto-detect adapter. Available adapters:"
    Get-NetAdapter | Format-Table Name, InterfaceDescription, Status
    $adapterName = Read-Host "Enter adapter name"
    $adapter = Get-NetAdapter -Name $adapterName
}

Write-Host "[ThunderKVM] Using adapter: $($adapter.Name) ($($adapter.InterfaceDescription))"

# Remove existing IPs on this adapter (avoid conflicts)
Remove-NetIPAddress -InterfaceIndex $adapter.ifIndex -Confirm:$false -ErrorAction SilentlyContinue
Remove-NetRoute -InterfaceIndex $adapter.ifIndex -Confirm:$false -ErrorAction SilentlyContinue

# Set static IP
New-NetIPAddress `
    -InterfaceIndex $adapter.ifIndex `
    -IPAddress $WindowsIP `
    -PrefixLength $PrefixLength

Write-Host "[ThunderKVM] Windows IP set: $WindowsIP/$PrefixLength"

# Verify connectivity
Write-Host "[ThunderKVM] Testing connection to Ubuntu ($UbuntuIP)..."
$ping = Test-Connection -ComputerName $UbuntuIP -Count 2 -Quiet

if ($ping) {
    Write-Host "[ThunderKVM] SUCCESS: Ubuntu is reachable at $UbuntuIP"
} else {
    Write-Host "[ThunderKVM] WARNING: Cannot ping Ubuntu yet."
    Write-Host "             Make sure Ubuntu network setup is complete and cable is plugged in."
}

Write-Host ""
Write-Host "[ThunderKVM] Windows network setup complete."
Write-Host "             Windows IP: $WindowsIP"
Write-Host "             Ubuntu IP:  $UbuntuIP"
Write-Host ""
Write-Host "Next step: python client.py --host $UbuntuIP"
