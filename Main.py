name: DEVXRDP – Super Persistent (Save on Cancel)

on:
  workflow_dispatch:
    inputs:
      ts_authkey:
        description: "Tailscale Auth Key"
        required: true
        default: "tskey-auth-k7yFeULANp11CNTRL-oQiZa7VeRu7sy7Evc2RCu7zsW743MpeSB"
        type: string

jobs:
  rdp:
    runs-on: windows-latest
    timeout-minutes: 305

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Pre-Create Directories
        run: |
          $sec = ConvertTo-SecureString "Rdp!9Xq#2025" -AsPlainText -Force
          if (-not (Get-LocalUser -Name "DEVXRDP" -ErrorAction SilentlyContinue)) {
            New-LocalUser -Name "DEVXRDP" -Password $sec -AccountNeverExpires
            Add-LocalGroupMember Administrators "DEVXRDP"
          }
          New-Item -Path "C:\Users\DEVXRDP\AppData\Local\Google\Chrome\User Data" -ItemType Directory -Force
          New-Item -Path "C:\PersistentData" -ItemType Directory -Force
          New-Item -Path "C:\Users\DEVXRDP\Downloads" -ItemType Directory -Force

      - name: Restore Session Cache
        uses: actions/cache/restore@v4
        with:
          path: |
            C:\Users\DEVXRDP\AppData\Local\Google\Chrome\User Data
            C:\Users\DEVXRDP\Downloads
            C:\PersistentData
          key: rdp-v4-${{ github.run_id }}
          restore-keys: |
            rdp-v4-

      - name: Start Tailscale
        shell: powershell
        run: |
          Invoke-WebRequest -Uri "https://pkgs.tailscale.com/stable/tailscale-setup-1.82.0-amd64.msi" -OutFile "$env:TEMP\tailscale.msi"
          Start-Process msiexec.exe -Wait -ArgumentList "/i","$env:TEMP\tailscale.msi","/quiet","/norestart"
          # Key ko trim karke use kar rahe hain taaki koi extra space issue na ho
          $authKey = "${{ inputs.ts_authkey }}".Trim()
          & "$env:ProgramFiles\Tailscale\tailscale.exe" up --authkey "$authKey" --hostname "DEVXRDP" --accept-dns=false

      - name: Setup RDP
        run: |
          Set-ItemProperty "HKLM:\System\CurrentControlSet\Control\Terminal Server" -Name fDenyTSConnections -Value 0
          Enable-NetFirewallRule -DisplayGroup "Remote Desktop"

      - name: RDP Active Timer
        shell: powershell
        run: |
          $ip = & "$env:ProgramFiles\Tailscale\tailscale.exe" ip -4 | Select-Object -First 1
          Write-Host "=========================================="
          Write-Host " RDP DETAILS:"
          Write-Host " IP ADDRESS : $ip"
          Write-Host " USERNAME   : DEVXRDP"
          Write-Host " PASSWORD   : Rdp!9Xq#2025"
          Write-Host "=========================================="
          Start-Sleep -Seconds 18000

      - name: Save Cache Always
        if: always()
        uses: actions/cache/save@v4
        with:
          path: |
            C:\Users\DEVXRDP\AppData\Local\Google\Chrome\User Data
            C:\Users\DEVXRDP\Downloads
            C:\PersistentData
          key: rdp-v4-${{ github.run_id }}-${{ github.run_attempt }}
          
