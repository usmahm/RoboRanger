# Raspberry Pi Ubuntu 22.04 Remote Development Setup Guide

This guide explains how to set up:

- SSH access
- Headless VNC remote desktop access
- XFCE desktop environment
- Automatic VNC startup on boot

for a Raspberry Pi running Ubuntu Desktop 22.04.

This setup was tested on a headless Raspberry Pi (without HDMI connected).

---

# Why This Setup Was Used

Initially, the setup used:

- Ubuntu GNOME Desktop
- GDM3
- x11vnc

However, Ubuntu GNOME on Raspberry Pi caused multiple issues in headless mode:

- Black screens over VNC
- Wayland incompatibility
- GPU/compositor rendering issues
- Unstable remote desktop sessions

To solve this, the final setup used:

| Component | Reason                                               |
| --------- | ---------------------------------------------------- |
| XFCE      | Lightweight and stable desktop environment           |
| LightDM   | Simpler display manager that works better headlessly |
| x11vnc    | Allows sharing the actual desktop display            |
| X11       | Required for x11vnc compatibility                    |

This combination is commonly used for:

- Robotics development
- ROS2 development
- Remote Raspberry Pi development
- Headless systems

It is more stable and lighter than GNOME on Raspberry Pi.

---

# 1. Update System

```bash
sudo apt update
sudo apt upgrade -y
```

---

# 2. Install SSH Server

```bash
sudo apt install openssh-server -y
sudo systemctl enable ssh
sudo systemctl start ssh
sudo systemctl status ssh
```

---

# 3. Find Raspberry Pi IP Address

```bash
hostname -I
```

---

# 4. Connect via SSH

```bash
ssh username@192.168.x.x
```

---

# 5. Install XFCE Desktop and LightDM

```bash
sudo apt install xfce4 xfce4-goodies lightdm -y
```

During installation select:

```text
lightdm
```

---

# 6. Configure LightDM as Default Display Manager

```bash
cat /etc/X11/default-display-manager
```

Expected:

```text
/usr/sbin/lightdm
```

If not:

```bash
sudo dpkg-reconfigure lightdm
```

---

# 7. Configure Headless HDMI Display

Edit:

```bash
sudo nano /boot/firmware/config.txt
```

Add:

```ini
dtoverlay=vc4-kms-v3d

hdmi_force_hotplug=1
hdmi_group=2
hdmi_mode=82
```

---

# 8. Enable Automatic Login

Edit:

```bash
sudo nano /etc/lightdm/lightdm.conf
```

Add:

```ini
[Seat:*]
autologin-user=YOUR_USERNAME
autologin-session=xfce
```

---

# 9. Install x11vnc

```bash
sudo apt install x11vnc -y
```

---

# 10. Create VNC Password

```bash
mkdir -p ~/.vnc
x11vnc -storepasswd
```

---

# 11. Find X11 Authentication File

```bash
ps aux | grep Xorg
```

Look for something like:

```text
-auth /var/run/lightdm/root/:0
```

---

# 12. Test x11vnc Manually

```bash
sudo x11vnc \
-display :0 \
-auth /var/run/lightdm/root/:0 \
-forever \
-shared \
-noxdamage \
-repeat \
-xkb \
-usepw
```

Expected:

```text
PORT=5900
```

---

# 13. Connect Using VNC Viewer

Connect using:

```text
192.168.x.x:5900
```

---

# 14. Configure x11vnc to Start Automatically

Create service:

```bash
sudo nano /etc/systemd/system/x11vnc.service
```

Paste:

```ini
[Unit]
Description=x11vnc remote desktop service
After=display-manager.service network.target

[Service]
Type=simple

ExecStart=/usr/bin/x11vnc \
-display :0 \
-auth /var/run/lightdm/root/:0 \
-forever \
-shared \
-noxdamage \
-repeat \
-xkb \
-rfbauth /home/YOUR_USERNAME/.vnc/passwd \
-rfbport 5900

Restart=on-failure
RestartSec=5

[Install]
WantedBy=graphical.target
```

---

# 15. Enable the Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable x11vnc.service
sudo systemctl restart x11vnc.service
systemctl status x11vnc.service
```

Expected:

```text
active (running)
```

---

# 16. Reboot Test

```bash
sudo reboot
```

After reboot:

- do NOT connect HDMI
- directly connect through VNC

---

# Troubleshooting Guide

## Black Screen After Connecting

Usually caused by:

- GNOME compositor issues
- Wayland
- No active desktop session

Solution:
Use XFCE + LightDM + X11 instead of GNOME/GDM3.

---

## Wayland Error

Error:

```text
wayland sessions are only supported via -rawfb
```

Solution:

```bash
sudo nano /etc/gdm3/custom.conf
```

Enable:

```ini
WaylandEnable=false
```

---

## x11vnc Cannot Find Xauthority

Error:

```text
-auth guess failed
```

Solution:

```bash
ps aux | grep Xorg
```

Find the auth path after `-auth`.

Example:

```text
/var/run/lightdm/root/:0
```

Then use:

```bash
x11vnc -auth /var/run/lightdm/root/:0
```

---

## Black Screen With Only Wallpaper

Solution:

```bash
echo "startxfce4" > ~/.xsession
chmod +x ~/.xsession
```

---

## VNC Does Not Work Headlessly

Ensure these exist:

```ini
hdmi_force_hotplug=1
hdmi_group=2
hdmi_mode=82
```

inside:

```text
/boot/firmware/config.txt
```

---

# Recommended Development Workflow

| Task             | Recommended Tool   |
| ---------------- | ------------------ |
| Terminal access  | SSH                |
| Coding           | VS Code Remote SSH |
| GUI applications | VNC                |
| ROS2 nodes       | Raspberry Pi       |
| RViz             | Local computer     |
| File access      | SFTP / VS Code     |

---

# File Access from Mac

You already have SSH.

That means you automatically have:

- SFTP
- SCP
- Remote editing

**Best Option: VS Code Remote SSH**

Install:

- VS Code
- Remote SSH Extension

Then:

1. Open VS Code
2. Install the extension
3. Press `Cmd + Shift + P`
4. Select **Remote-SSH: Connect to Host**
5. Enter: `ssh username@192.168.1.45`

This gives you:

- Full filesystem access
- Terminal
- Code editing
- Git
- ROS development
- Backend/frontend work

This is the best workflow for your RoboRanger setup.

---

# Notes on ROS2 and RViz

This setup works well with:

- ROS2
- rqt
- OpenCV GUIs
- Robotics dashboards

For heavy 3D rendering:

- RViz is better run on a more powerful computer
- Raspberry Pi should run ROS2 nodes only

Recommended architecture:

| Device       | Responsibility                |
| ------------ | ----------------------------- |
| Raspberry Pi | Sensors, ROS2 nodes, backend  |
| Mac/Linux PC | RViz, Foxglove, visualization |

---

# Optional Improvements

Future improvements may include:

- VS Code Remote SSH
- Tailscale remote access
- NoMachine instead of VNC
- Docker development environment
- ROS2 Cyclone DDS setup
- Static IP configuration
