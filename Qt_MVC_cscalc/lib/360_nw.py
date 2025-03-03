
import ctypes
from ctypes import wintypes
import win32gui
import win32con

# ListView 常量
LVM_FIRST = 0x1000
LVM_GETITEMCOUNT = LVM_FIRST + 4          # 获取行数
LVM_GETITEMTEXTW = LVM_FIRST + 115        # Unicode 版本，获取项文本

# LVITEMW 结构定义（简化版，只用到文本相关字段）
class LVITEMW(ctypes.Structure):
    _fields_ = [
        ("mask", wintypes.UINT),          # 指定哪些成员有效，设置为 LVIF_TEXT（1）
        ("iItem", ctypes.c_int),          # 项的索引
        ("iSubItem", ctypes.c_int),       # 子项的索引（通常 0 表示第一列）
        ("state", wintypes.UINT),
        ("stateMask", wintypes.UINT),
        ("pszText", wintypes.LPWSTR),     # 指向文本缓冲区的指针
        ("cchTextMax", ctypes.c_int),     # 缓冲区的大小
        ("iImage", ctypes.c_int),
        ("lParam", wintypes.LPARAM)
    ]
    
def find_window_by_title(title):
    """通过窗口标题查找窗口句柄"""
    hwnd = win32gui.FindWindow(None, title)
    if hwnd == 0:
        raise Exception(f"未找到标题为 '{title}' 的窗口")
    return hwnd

def find_child_window_by_class(parent_hwnd, class_name):
    """通过类名查找子窗口"""
    def callback(hwnd, extra):
        if win32gui.GetClassName(hwnd) == class_name:
            extra.append(hwnd)
        return True

    child_windows = []
    win32gui.EnumChildWindows(parent_hwnd, callback, child_windows)
    return child_windows



def send_command(hwnd, command_id):
    """发送WM_COMMAND消息，触发指定的菜单项"""
    win32gui.SendMessage(hwnd, win32con.WM_COMMAND, 0, command_id)

def get_listview_item_count(hwnd):
    """获取列表控件中的行数"""
    return win32gui.SendMessage(hwnd, win32con.LVM_GETITEMCOUNT, 0, 0)

def get_listview_item_text(listview_hwnd, item_index, subitem_index=0, buffer_size=512):
    # 创建用于接收文本的缓冲区
    text_buffer = ctypes.create_unicode_buffer(buffer_size)
    
    # 初始化 LVITEMW 结构，mask 设置为 LVIF_TEXT（值为 0x0001）
    lvitem = LVITEMW()
    lvitem.mask = 0x0001  # LVIF_TEXT
    lvitem.iItem = item_index
    lvitem.iSubItem = subitem_index
    lvitem.pszText = text_buffer
    lvitem.cchTextMax = buffer_size

    # 调用 SendMessageW 获取文本
    SendMessageW = ctypes.windll.user32.SendMessageW
    SendMessageW(listview_hwnd, LVM_GETITEMTEXTW, item_index, ctypes.byref(lvitem))
    
    # 返回缓冲区中的文本
    return text_buffer.value


def find_target_listview(listview_hwnds, target_text="ShopTitans.exe"):
    target_hwnd = None
    for hwnd in listview_hwnds:
        # 获取行数
        item_count = win32gui.SendMessage(hwnd, LVM_GETITEMCOUNT, 0, 0)
        print(f"ListView hwnd={hwnd:08X} 行数: {item_count}")
        
        if item_count > 0:
            # 遍历若干行进行试读
            for i in range(item_count):
                text = get_listview_item_text(hwnd, i, subitem_index=0)  # 假设进程名在第一列
                print(f"  行 {i}: {text}")
                if target_text.lower() in text.lower():
                    print(f"找到目标 '{target_text}' 在 hwnd={hwnd:08X}, 行 {i}")
                    target_hwnd = hwnd
                    return target_hwnd, i  # 返回目标 ListView 和行号
    return None, -1


window = find_window_by_title('360流量防火墙')
hwnd_list = find_child_window_by_class(window, 'SysListView32')


for hwnd in hwnd_list:
    if win32gui.IsWindowVisible(hwnd):
        print(f"{hwnd:08X}")
