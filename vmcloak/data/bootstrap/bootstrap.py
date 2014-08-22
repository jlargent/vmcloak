from ctypes import c_char, c_ushort, c_uint, c_char_p
from ctypes import windll, Structure, POINTER, sizeof
import shutil
import socket
import subprocess
import tempfile
import random
from _winreg import CreateKeyEx, SetValueEx
from _winreg import HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE
from _winreg import KEY_SET_VALUE, REG_DWORD, REG_SZ, REG_MULTI_SZ

from settings import HOST_IP, HOST_PORT, RESOLUTION
import logging


# http://blogs.technet.com/b/heyscriptingguy/archive/2010/07/07/hey-scripting-guy-how-can-i-change-my-desktop-monitor-resolution-via-windows-powershell.aspx
# http://msdn.microsoft.com/en-us/library/windows/desktop/dd183565(v=vs.85).aspx
class _DevMode(Structure):
    _fields_ = [
        ('dmDeviceName', c_char * 32),
        ('unused1', c_ushort * 2),
        ('dmSize', c_ushort),
        ('unused2', c_ushort),
        ('unused3', c_uint * 8),
        ('dmFormName', c_char * 32),
        ('dmLogPixels', c_ushort),
        ('dmBitsPerPel', c_ushort),
        ('dmPelsWidth', c_uint),
        ('dmPelsHeight', c_uint),
        ('unused2', c_uint * 10),
    ]

EnumDisplaySettings = windll.user32.EnumDisplaySettingsA
EnumDisplaySettings.argtypes = c_char_p, c_uint, POINTER(_DevMode)

ChangeDisplaySettings = windll.user32.ChangeDisplaySettingsA
ChangeDisplaySettings.argtypes = POINTER(_DevMode), c_uint

ENUM_CURRENT_SETTINGS = -1
CDS_UPDATEREGISTRY = 1
DISP_CHANGE_SUCCESSFUL = 0


def generate_hd():
    """ Generates random HD names
    :return: a string with a  registry hd description
    """
    return " ".join(random.sample(["HD", "HARDDISK", "IBM", "WD", "Western Digital", "Seagate", "HGST", "Samsung",
                                   "Harddisk", "Drive", "TB", "GB", "Desk", "IDE", "SATA", "USB", "Desktop"], 3))

def generate_cd():
    """ Generates random CD names
    :return: a string with a  registry hd description
    """
    return " ".join(random.sample(["CD", "CDROM", "IBM", "WD", "Western Digital", "Seagate", "HGST", "Samsung",
                                   "CD-ROM", "Drive", "TB", "GB", "Desk", "IDE", "SATA", "USB",
                                   "BlueRay", "Blue-Ray", "DVD", "DVD-ROM", "DVD ROM", "RW"], 3))

def generate_bios():
    """ Generates random BIOS names
    :return: a string with a  registry hd description
    """
    return " ".join(random.sample(["BIOS", "3.6", "5.4", "System", "Version", "Award", "AMI", "EFI", "UEFI",
                                   "Insyde", "SeaBIOS"], 3))

def generate_vga_bios():
    """ Generates random VGA BIOS names
    :return: a string with a  registry hd description
    """
    return " ".join(random.sample(["BIOS", "3.6", "5.24", "VGA", "Version", "Gigabyte", "Dell", "Sapphire", "Alienware",
                                   "Gainward", "Asus"], 3))

REGISTRY = [
    # Disable "Windows XP Tour" prompt.
    # http://www.techrepublic.com/article/tech-tip-disable-the-windows-xp-tour-prompt/
    (HKEY_CURRENT_USER, 'Software\\Microsoft\\Windows\\CurrentVersion\\Applets\\Tour', 'RunCount', REG_DWORD, 0),

    # Disable the Windows Indexation service.
    # http://www.wikihow.com/Turn-Off-Windows-XP%E2%80%99s-Indexing-Service
    (HKEY_LOCAL_MACHINE, 'System\\CurrentControlSet\\Services\\CiSvc', 'Start', REG_DWORD, 4),

    # Hide HD device identifier (pafish 1)
    (HKEY_LOCAL_MACHINE, "HARDWARE\\DEVICEMAP\\Scsi\\Scsi Port 0\\Scsi Bus 0\\Target Id 0\\Logical Unit Id 0", 'Identifier', REG_SZ, generate_hd()),

    # Hide CDROM (pafish 1+)
    (HKEY_LOCAL_MACHINE, "HARDWARE\\DEVICEMAP\\Scsi\\Scsi Port 1\\Scsi Bus 0\\Target Id 0\\Logical Unit Id 0", 'Identifier', REG_SZ, generate_cd()),

    # Hide SystemBios Version (pafish 2)
    (HKEY_LOCAL_MACHINE, "HARDWARE\\Description\\System", "SystemBiosVersion", REG_MULTI_SZ, [generate_bios()]),

    # Hide SystemBios Version (pafish 4)
    (HKEY_LOCAL_MACHINE, "HARDWARE\\Description\\System", "VideoBiosVersion", REG_MULTI_SZ,
     [generate_vga_bios(), generate_vga_bios()])
    ]


class SetupWindows():

    def __init__(self):
        pass

    def set_resolution(self, width, height):
        """ Set the screen resolution

        :param width: width
        :param height: height
        :return:
        """
        dm = _DevMode()
        dm.dmSize = sizeof(dm)
        if not EnumDisplaySettings(None, ENUM_CURRENT_SETTINGS, dm):
            return False

        dm.dmPelsWidth = width
        dm.dmPelsHeight = height

        ret = ChangeDisplaySettings(dm, CDS_UPDATEREGISTRY)
        return ret == DISP_CHANGE_SUCCESSFUL


    def set_regkey(self, key, subkey, name, typ, value):
        """ Set a specified registry key

        :param key: Main key
        :param subkey: Sub key
        :param name: key
        :param typ: Type of key
        :param value: Value to set
        :return:
        """
        parts = subkey.split('\\')
        for off in xrange(1, len(parts)):
            CreateKeyEx(key, '\\'.join(parts[:off]), 0, KEY_SET_VALUE).Close()

        with CreateKeyEx(key, subkey, 0, KEY_SET_VALUE) as handle:
            SetValueEx(handle, name, 0, typ, value)

    def run(self):
        """ Modify the system settings

        :return:
        """
        # Read the agent.py file so we can drop it again later on.
        agent = open('C:\\vmcloak\\agent.py', 'rb').read()

        try:
            s = socket.create_connection((HOST_IP, HOST_PORT))

            width, height = [int(x) for x in RESOLUTION.split('x')]
            s.send('\x01' if self.set_resolution(width, height) else '\x00')
        except socket.error:
            print("Socket error")

        for key, subkey, name, typ, value in REGISTRY:
            self.set_regkey(key, subkey, name, typ, value)

        # Drop the agent and execute it.
        _, path = tempfile.mkstemp(suffix='.py')
        open(path, 'wb').write(agent)

        # Don't wait for this process to end. Also, the agent will remove the
        # temporary agent file itself.
        subprocess.Popen(['C:\\Python27\\pythonw.exe', path])

        # Remove all vmcloak files that are directly related. This does not
        # include the auxiliary directory or any of its contents.
        shutil.rmtree('C:\\vmcloak')


if __name__ == '__main__':
    sw = SetupWindows()
    sw.run()