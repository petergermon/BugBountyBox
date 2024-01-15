import subprocess

# Set hostname and username
hostname = "BugBountyBox"
username = "bbb"

# Set Disk Device
try:
    output = subprocess.check_output(['fdisk', '-l'])       # Run fdisk -l command and capture the output
    print(output)                                           # Print the output for the user to select the disk device
    disk_device = input("Enter the disk device: ")          # Ask the user to enter the disk device
    selected_disk = disk_device.strip()                     # Store the disk device into a variable
    
    # Check if the selected disk is valid
    if selected_disk not in output.decode():
        raise ValueError("Invalid disk device selected.")  
except subprocess.CalledProcessError as e:
    print(f"Error: {e}")
except ValueError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")

# Ask user to specify the swap and root partition size
while True:
    swap_size = input("Enter the swap partition size (e.g. 1G): ")
    root_size = input("Enter the root partition size (e.g. 10G): ")
    if swap_size and swap_size.strip() != "" and root_size and root_size.strip() != "":
        break
    else:
        print("Invalid partition size. Please try again.")

# Ask user if this is being installed on a SSD and store the answer in a variable
while True:
    ssd = input("Is this being installed on a SSD? (y/n): ")
    if ssd and ssd.strip() != "":
        if ssd.lower() == "y" or ssd.lower() == "n":
            break
        else:
            print("Invalid input. Please try again.")
    else:
        print("Invalid input. Please try again.")
        

# Ask user to set password for user account
while True:
    user_password = input("Set password for user account: ")
    confirm_password = input("Confirm password for user account: ")
    if user_password == confirm_password:
        break
    else:
        print("Passwords do not match. Please try again.")

# Ask user to set password for root account
while True:
    root_password = input("Set password for root account: ")
    confirm_password = input("Confirm password for root account: ")
    if root_password == confirm_password:
        break
    else:
        print("Passwords do not match. Please try again.")

# Ask user to set timezone
while True:
    timezone = input("Set timezone (e.g. America/Los_Angeles): ")
    if timezone and timezone.strip() != "":
        break
    else:
        print("Invalid timezone. Please try again.")

# Ask user to set locale
while True:
    locale = input("Set locale (e.g. en_US.UTF-8): ")
    if locale and locale.strip() != "":
        break
    else:
        print("Invalid locale. Please try again.")

# Ask user to set keyboard layout
while True:
    keyboard_layout = input("Set keyboard layout (e.g. us): ")
    if keyboard_layout and keyboard_layout.strip() != "":
        break
    else:
        print("Invalid keyboard layout. Please try again.")

# Zap the disk
try:
    print("Zapping disk...")
    subprocess.run(['sgdisk', '-Z', selected_disk])          # Run sgdisk -Z command to zap the disk
except subprocess.CalledProcessError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")

# Create partitions
try:
    print("Creating partitions...")
    subprocess.run(['sgdisk', '-n', '1:0:+1G', '-t', '1:ef00', selected_disk])      # Run sgdisk -n command to create EFI partition
    subprocess.run(['sgdisk', '-n', f'2:0:+{swap_size}', '-t', '2:8200', selected_disk])      # Run sgdisk -n command to create swap partition
    subprocess.run(['sgdisk', '-n', f'3:0:+{root_size}', '-t', '3:8300', selected_disk])      # Run sgdisk -n command to create root partition
    subprocess.run(['sgdisk', '-n', '4:0:0', '-t', '4:8300', selected_disk])        # Run sgdisk -n command to create home partition
except subprocess.CalledProcessError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")

# Format partitions
try:
    print("Formatting partitions...")
    subprocess.run(['mkfs.fat', '-F32', f'{selected_disk}1'])      # Run mkfs.fat command to format EFI partition
    subprocess.run(['mkswap', f'{selected_disk}2'])                # Run mkswap command to format swap partition
    subprocess.run(['mkfs.ext4', f'{selected_disk}3'])             # Run mkfs.ext4 command to format root partition
    subprocess.run(['mkfs.ext4', f'{selected_disk}4'])             # Run mkfs.ext4 command to format home partition
except subprocess.CalledProcessError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")

# Mount partitions
try:
    print("Mounting partitions...")
    subprocess.run(['mount', f'{selected_disk}3', '/mnt'])         # Run mount command to mount root partition
    subprocess.run(['mkdir', '/mnt/boot'])                         # Run mkdir command to create boot directory
    subprocess.run(['mount', f'{selected_disk}1', '/mnt/boot'])    # Run mount command to mount EFI partition
    subprocess.run(['mkdir', '/mnt/home'])                         # Run mkdir command to create home directory
    subprocess.run(['mount', f'{selected_disk}4', '/mnt/home'])    # Run mount command to mount home partition
    subprocess.run(['swapon', f'{selected_disk}2'])                # Run swapon command to mount swap partition
except subprocess.CalledProcessError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")

# Update mirrorlist
try:
    print("Updating mirrorlist...")
    subprocess.run(['pacman', '-Sy', '--noconfirm', 'reflector'])     # Run pacman command to install reflector
    subprocess.run(['reflector', '-c', 'US', '-a', '6', '-f', '10', '-l', '8', '--sort', 'rate', '--save', '/etc/pacman.d/mirrorlist'])      # Run reflector command to update mirrorlist
except subprocess.CalledProcessError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")

# Install base system
try:
    print("Installing base system...")
    subprocess.run(['pacstrap', '/mnt', 'base', 'base-devel', 'linux', 'linux-firmware', 'linux-headers', 'networkmanager', 'iproute2', 'iwd', 'dhcpcd', 'git', 'nano', 'sudo', 'htop', 'bash', 'bash-completion', 'xorg', 'plasma', 'plasma-wayland-session', 'kde-applications'])      # Run pacstrap command to install base system
except subprocess.CalledProcessError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")

# Generate fstab
try:
    print("Generating fstab...")
    subprocess.run(['genfstab', '-U', '/mnt', '>>', '/mnt/etc/fstab'])      # Run genfstab command to generate fstab
except subprocess.CalledProcessError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")

# Set locale
try:
    print("Setting locale...")
    subprocess.run(['echo', f'LANG={locale}', '>>', '/mnt/etc/locale.conf'])     # Run echo command to set locale
    subprocess.run(['echo', f'{locale} UTF-8', '>>', '/mnt/etc/locale.gen'])     # Run echo command to set locale
    subprocess.run(['arch-chroot', '/mnt', 'locale-gen'])                        # Run arch-chroot command to generate locale
except subprocess.CalledProcessError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")

# Set timezone
try:
    print("Setting timezone...")
    subprocess.run(['arch-chroot', '/mnt', 'ln', '-sf', f'/usr/share/zoneinfo/{timezone}', '/etc/localtime'])              # Run arch-chroot command to set timezone
    subprocess.run(['arch-chroot', '/mnt', 'hwclock', '--systohc', '--utc'])                                               # Run arch-chroot command to set hardware clock
except subprocess.CalledProcessError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")

# Enable trim for SSD if user selected SSD
if ssd.lower() == "y":
    try:
        print("Enabling trim for SSD...")
        subprocess.run(['arch-chroot', '/mnt', 'systemctl', 'enable', 'fstrim.timer'])     # Run arch-chroot command to enable trim
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Enable multilib repository
try:
    print("Enabling multilib repository...")
    subprocess.run(['echo', '[multilib]', '>>', '/mnt/etc/pacman.conf'])                             # Run echo command to enable multilib repository
    subprocess.run(['echo', 'Include = /etc/pacman.d/mirrorlist', '>>', '/mnt/etc/pacman.conf'])     # Run echo command to enable multilib repository
    subprocess.run(['arch-chroot', '/mnt', 'pacman', '-Sy', '--noconfirm'])                          # Run arch-chroot command to update package database
except subprocess.CalledProcessError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")

# Create user account
try:
    print("Creating user account...")
    subprocess.run(['arch-chroot', '/mnt', 'useradd', '-m', '-g', 'users' '-G', 'wheel', '-s', '/bin/bash', username])      # Run arch-chroot command to create user account
    subprocess.run(['arch-chroot', '/mnt', 'passwd', username, f'<<< {user_password}'])                                     # Run arch-chroot command to set password for user account
    subprocess.run(['arch-chroot', '/mnt', 'passwd', '-l', 'root', f'<<< {root_password}'])                                 # Run arch-chroot command to set password for root account
    subprocess.run(['arch-chroot', '/mnt', 'echo', f'{username} ALL=(ALL) ALL', '>>', '/etc/sudoers'])                      # Run arch-chroot command to add user to sudoers
    subprocess.run(['echo "# bbb configuration" >> /mnt/etc/sudoers'])                                                      # Run echo command to add comment to sudoers
    subprocess.run(['echo "%wheel ALL=(ALL) ALL" >> /mnt/etc/sudoers'])                                                     # Run echo command to add wheel group to sudoers
    subprocess.run(['echo "Defaults rootpw" >> /mnt/etc/sudoers'])                                                          # Run echo command to add rootpw to sudoers
except subprocess.CalledProcessError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")

# Install bootloader
try:
    print("Installing bootloader...")
    subprocess.run(['arch-chroot', '/mnt', 'bootctl', '--path=/boot', 'install'])                                                                           # Run arch-chroot command to install bootloader
    subprocess.run(['echo', 'default arch', '>>', '/mnt/boot/loader/loader.conf'])                                                                          # Run echo command to set default boot entry
    subprocess.run(['echo', 'editor 0', '>>', '/mnt/boot/loader/loader.conf'])                                                                              # Run echo command to disable editor
    subprocess.run(['echo', 'title Arch Linux', '>>', '/mnt/boot/loader/entries/arch.conf'])                                                                # Run echo command to set title for Arch Linux
    subprocess.run(['echo', f'linux /vmlinuz-linux', '>>', '/mnt/boot/loader/entries/arch.conf'])                                                           # Run echo command to set kernel image
    subprocess.run(['echo', f'initrd /intel-ucode.img', '>>', '/mnt/boot/loader/entries/arch.conf'])                                                        # Run echo command to set microcode
    subprocess.run(['echo', f'initrd /initramfs-linux.img', '>>', '/mnt/boot/loader/entries/arch.conf'])                                                    # Run echo command to set initramfs
    subprocess.run(['echo', f'options root=PARTUUID=$(blkid -s PARTUUID -o value {selected_disk}3) rw', '>>', '/mnt/boot/loader/entries/arch.conf'])        # Run echo command to set kernel parameters
except subprocess.CalledProcessError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")

# Enable DHCP
try:
    print("Enabling DHCP...")
    subprocess.run(['arch-chroot', '/mnt', 'systemctl', 'enable', 'dhcpcd.service'])      # Run arch-chroot command to enable DHCP
except subprocess.CalledProcessError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")

# Enable SDDM
try:
    print("Enabling SDDM...")
    subprocess.run(['arch-chroot', '/mnt', 'systemctl', 'enable', 'sddm.service'])        # Run arch-chroot command to enable SDDM
except subprocess.CalledProcessError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")

# Enable NetworkManager
try:
    print("Enabling NetworkManager...")
    subprocess.run(['arch-chroot', '/mnt', 'systemctl', 'enable', 'NetworkManager.service'])      # Run arch-chroot command to enable NetworkManager
except subprocess.CalledProcessError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")

# Unmount filesystem and reboot
try:
    print("Unmounting filesystem...")
    subprocess.run(['umount', '-R', '/mnt'])      # Run umount command to unmount filesystem
    subprocess.run(['reboot'])                    # Run reboot command to reboot system
except subprocess.CalledProcessError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
