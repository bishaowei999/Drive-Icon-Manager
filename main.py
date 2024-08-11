"""
https://github.com/Return-Log/Drive-Icon-Manager
GPL-3.0 license
coding: UTF-8
"""

import winreg
from colorama import init, Fore
import ctypes
import sys

# 初始化colorama以支持Windows上的终端颜色显示
init(autoreset=True)

# 定义版本号和GitHub链接
VERSION = "v1.1"
GITHUB_LINK = "https://github.com/Return-Log/Drive-Icon-Manager"


def print_welcome():
    """打印欢迎信息和版本号"""
    print(f"{Fore.GREEN}欢迎使用 Drive Icon Manager 版本 {VERSION}")
    print(f"{Fore.YELLOW}此工具可以帮助你删除 '此电脑' 和 '资源管理器侧边栏' 中的第三方软件图标")
    print(f"{Fore.CYAN}访问 GitHub 仓库: {Fore.BLUE}{GITHUB_LINK}\n")


def is_admin():
    """检查是否具有管理员权限"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin():
    """以管理员权限重新运行"""
    if not is_admin():
        print(f"{Fore.RED}本工具需要管理员权限，请重新运行并获取管理员权限")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, ' '.join(sys.argv), None, 1)
        sys.exit()


def get_current_user_sid():
    """通过注册表获取当前用户的SID"""
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                             r"SOFTWARE\Microsoft\Windows\CurrentVersion\Authentication\LogonUI")
        sid, _ = winreg.QueryValueEx(key, "LastLoggedOnUserSid")
        winreg.CloseKey(key)
        return sid
    except Exception as e:
        print(f"无法获取当前用户的SID: {e}")
        return None


def list_drive_icons(base_key, path, source):
    """列出指定路径下的驱动器图标及其注册表项名称和显示名称"""
    icons = []
    try:
        key = winreg.OpenKey(base_key, path, 0, winreg.KEY_READ)
        i = 0
        while True:
            try:
                # 枚举子项
                subkey_name = winreg.EnumKey(key, i)
                subkey_path = f"{path}\\{subkey_name}"
                subkey = winreg.OpenKey(base_key, subkey_path, 0, winreg.KEY_READ)
                try:
                    # 获取默认值（显示名称）
                    display_name, _ = winreg.QueryValueEx(subkey, None)
                except FileNotFoundError:
                    display_name = "无显示名称"
                icons.append((subkey_name, display_name, source))
                winreg.CloseKey(subkey)
                i += 1
            except OSError:
                break
        winreg.CloseKey(key)
    except Exception as e:
        print(f"{Fore.RED}无法列出驱动器图标: {e}")
    return icons


def delete_drive_icon(index):
    """删除指定索引的驱动器图标"""
    subkey_name, _, source = icons[index]
    if source == '此电脑':
        key_path = r'Software\Microsoft\Windows\CurrentVersion\Explorer\MyComputer\NameSpace'
    else:
        current_user_sid = get_current_user_sid()
        key_path = fr'{current_user_sid}\Software\Microsoft\Windows\CurrentVersion\Explorer\Desktop\NameSpace'

    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER if source == '此电脑' else winreg.HKEY_USERS, key_path, 0,
                             winreg.KEY_ALL_ACCESS)
        winreg.DeleteKey(key, subkey_name)
        winreg.CloseKey(key)
        print(f"{Fore.GREEN}已删除驱动器图标: {subkey_name}")
    except Exception as e:
        print(f"{Fore.RED}无法删除驱动器图标: {e}")


def display_icons():
    """显示所有驱动器图标"""
    global icons
    icons = []

    # 列出“此电脑”中的图标
    icons += list_drive_icons(winreg.HKEY_CURRENT_USER,
                              r'Software\Microsoft\Windows\CurrentVersion\Explorer\MyComputer\NameSpace', '此电脑')

    # 列出“资源管理器侧边栏”中的图标
    current_user_sid = get_current_user_sid()
    icons += list_drive_icons(winreg.HKEY_USERS,
                              fr'{current_user_sid}\Software\Microsoft\Windows\CurrentVersion\Explorer\Desktop\NameSpace',
                              '资源管理器侧边栏')

    if icons:
        for index, (subkey_name, display_name, source) in enumerate(icons, start=1):
            color = Fore.CYAN if source == '此电脑' else Fore.MAGENTA
            print(f"{color}{index}: {Fore.YELLOW}{subkey_name} - {Fore.WHITE}{display_name} ({source})")
    else:
        print(f"{Fore.RED}未找到驱动器图标")


def main():
    """主函数整体流程"""
    run_as_admin()
    print_welcome()
    while True:
        display_icons()
        try:
            index_to_delete = int(input(f"{Fore.BLUE}\n输入要删除的驱动器图标索引 (输入0退出): "))
            if index_to_delete == 0:
                print(f"{Fore.GREEN}退出程序")
                break
            elif 1 <= index_to_delete <= len(icons):
                delete_drive_icon(index_to_delete - 1)
            else:
                print(f"{Fore.RED}无效的索引")
        except ValueError:
            print(f"{Fore.RED}无效输入，请输入一个数字")


if __name__ == "__main__":
    main()
