import re
from decimal import Decimal

import requests
from bs4 import BeautifulSoup
from win10toast import *
from pkg_resources import Requirement
from pkg_resources import resource_filename
from win32api import GetModuleHandle
from win32api import PostQuitMessage
from win32con import CW_USEDEFAULT
from win32con import IDI_APPLICATION
from win32con import IMAGE_ICON
from win32con import LR_DEFAULTSIZE
from win32con import LR_LOADFROMFILE
from win32con import WM_DESTROY
from win32con import WM_USER
from win32con import WS_OVERLAPPED
from win32con import WS_SYSMENU
from win32gui import CreateWindow
from win32gui import DestroyWindow
from win32gui import LoadIcon
from win32gui import LoadImage
from win32gui import NIF_ICON
from win32gui import NIF_INFO
from win32gui import NIF_MESSAGE
from win32gui import NIF_TIP
from win32gui import NIM_ADD
from win32gui import NIM_DELETE
from win32gui import NIM_MODIFY
from win32gui import RegisterClass
from win32gui import UnregisterClass
from win32gui import Shell_NotifyIcon
from win32gui import UpdateWindow
from win32gui import WNDCLASS

class ToastNotifier2(ToastNotifier):
    def show_toast(self, title, msg, icon_path=None):
        message_map = {WM_DESTROY: self.on_destroy, }

        # Register the window class.
        self.wc = WNDCLASS()
        self.hinst = self.wc.hInstance = GetModuleHandle(None)
        self.wc.lpszClassName = str("PythonTaskbar")  # must be a string
        self.wc.lpfnWndProc = message_map  # could also specify a wndproc.
        try:
            self.classAtom = RegisterClass(self.wc)
        except:
            pass #not sure of this
        style = WS_OVERLAPPED | WS_SYSMENU
        self.hwnd = CreateWindow(self.classAtom, "Taskbar", style,
                                 0, 0, CW_USEDEFAULT,
                                 CW_USEDEFAULT,
                                 0, 0, self.hinst, None)
        UpdateWindow(self.hwnd)

        # icon
        if icon_path is not None:
            icon_path = path.realpath(icon_path)
        else:
            icon_path =  resource_filename(Requirement.parse("win10toast"), "win10toast/data/python.ico")
        icon_flags = LR_LOADFROMFILE | LR_DEFAULTSIZE
        try:
            hicon = LoadImage(self.hinst, icon_path,
                              IMAGE_ICON, 0, 0, icon_flags)
        except Exception as e:
            logging.error("Some trouble with the icon ({}): {}"
                          .format(icon_path, e))
            hicon = LoadIcon(0, IDI_APPLICATION)

        # Taskbar icon
        flags = NIF_ICON | NIF_MESSAGE | NIF_TIP
        nid = (self.hwnd, 0, flags, WM_USER + 20, hicon, "Tooltip")
        Shell_NotifyIcon(NIM_ADD, nid)
        Shell_NotifyIcon(NIM_MODIFY, (self.hwnd, 0, NIF_INFO,
                                      WM_USER + 20,
                                      hicon, "Balloon Tooltip", msg, 200,
                                      title))


page = requests.get('https://www.google.com.br/search?psb=1&tbm=shop&q=playstation+5&hl=pt-BR')
soup = BeautifulSoup(page.content, 'html.parser')
els = [i for i in soup.find_all('span') if 'R$' in i.text]

matches = []

for el in els:
    root = el.parent.parent
    children = list(root.children)
    title = next(root.children).text

    if not re.match(r'.*(ps\s*5|playstation\s+5).*', title, re.I):
        continue

    try:
        price_str = re.findall(r'\D*((\d{1,3}\.)*\d+,\d+)\D*', el.text)[0][0]
    except IndexError:
        continue

    price = Decimal(price_str.replace('.', '').replace(',', '.'))

    if price < 4000 or price > 6000:
        continue

    matches.append([title, el.text])

if matches:
    toaster = ToastNotifier2()
    toaster.show_toast(
        'PS5 Encontrados',
        '\n'.join(f'{i[1]} - {i[0]}' for i in matches)
    )