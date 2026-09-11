#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
card 120 spike — prove Win32 SendInput commits an Объект.* attribute where the pure protocol cannot.

Faithful: runs the REAL qa_mcp.protocol.native_xtest.write_form_value_xtest flow (protocol open+focus by name ->
OS input -> protocol read-back). Only the OS-input primitive is swapped from xdotool(XTEST) to Win32 SendInput
via ctypes (the IDENTICAL user32!SendInput the Go agent will call). `committed=True` in the read-back == the
genuine edit committed to the form object -> the exact thing the protocol replay alone fails to do.

Config is read from a UTF-8 JSON sibling (default <scriptdir>/spike_cfg.json or $QA_SPIKE_CFG):
  {src, capture, value, pid, port, save, out, shot}
Run with pythonw.exe (NO cmd console -> nothing steals the foreground from the 1C client).
"""
import ctypes
import json
import os
import subprocess
import sys
import time
import traceback
from ctypes import wintypes

CFG_PATH = os.environ.get("QA_SPIKE_CFG") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "spike_cfg.json")
with open(CFG_PATH, "r", encoding="utf-8") as fh:
    CFG = json.load(fh)
SRC     = CFG["src"]
CAPTURE = CFG["capture"]
VALUE   = CFG.get("value", "QA SendInput Тест 2026")
PID     = int(CFG.get("pid", 0))
PORT    = int(CFG.get("port", 15381))
SAVE    = bool(CFG.get("save", False))
OUT     = CFG.get("out", os.path.join(os.environ.get("TEMP", "."), "qa_spike_result.json"))
SHOT    = CFG.get("shot", os.path.join(os.environ.get("TEMP", "."), "qa_spike_after.png"))

sys.path.insert(0, SRC)

user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
ULONG_PTR = ctypes.c_ulonglong

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD),
                ("dwFlags", wintypes.DWORD), ("time", wintypes.DWORD), ("dwExtraInfo", ULONG_PTR)]
class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", wintypes.LONG), ("dy", wintypes.LONG), ("mouseData", wintypes.DWORD),
                ("dwFlags", wintypes.DWORD), ("time", wintypes.DWORD), ("dwExtraInfo", ULONG_PTR)]
class _U(ctypes.Union):
    _fields_ = [("ki", KEYBDINPUT), ("mi", MOUSEINPUT)]
class INPUT(ctypes.Structure):
    _fields_ = [("type", wintypes.DWORD), ("u", _U)]

INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
VK_TAB, VK_RETURN, VK_ESCAPE, VK_CONTROL, VK_S = 0x09, 0x0D, 0x1B, 0x11, 0x53
SW_MINIMIZE, SW_RESTORE, SW_SHOW = 6, 9, 5

def _send(*items):
    arr = (INPUT * len(items))(*items)
    if user32.SendInput(len(items), arr, ctypes.sizeof(INPUT)) != len(items):
        raise ctypes.WinError(ctypes.get_last_error())

def _key(vk=0, scan=0, flags=0):
    return INPUT(type=INPUT_KEYBOARD, u=_U(ki=KEYBDINPUT(vk, scan, flags, 0, 0)))

def type_unicode(text, delay=0.012):
    for ch in text:
        cp = ord(ch)
        _send(_key(scan=cp, flags=KEYEVENTF_UNICODE))
        _send(_key(scan=cp, flags=KEYEVENTF_UNICODE | KEYEVENTF_KEYUP))
        time.sleep(delay)

def tap(vk):
    _send(_key(vk=vk)); time.sleep(0.04); _send(_key(vk=vk, flags=KEYEVENTF_KEYUP))

def chord(mod, vk):
    _send(_key(vk=mod)); _send(_key(vk=vk)); time.sleep(0.04)
    _send(_key(vk=vk, flags=KEYEVENTF_KEYUP)); _send(_key(vk=mod, flags=KEYEVENTF_KEYUP))

WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

def win_title(hwnd):
    n = user32.GetWindowTextLengthW(hwnd)
    buf = ctypes.create_unicode_buffer(n + 1)
    user32.GetWindowTextW(hwnd, buf, n + 1)
    return buf.value

def find_main_window(pid):
    found = []
    def cb(hwnd, _):
        wpid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(wpid))
        if wpid.value == pid and user32.IsWindowVisible(hwnd):
            r = wintypes.RECT(); user32.GetWindowRect(hwnd, ctypes.byref(r))
            found.append(((r.right - r.left) * (r.bottom - r.top), hwnd))
        return True
    user32.EnumWindows(WNDENUMPROC(cb), 0)
    found.sort()
    return found[-1][1] if found else None

def minimize_others(keep_pid):
    """Get terminals/other apps out of the way so the 1C client is the unobstructed foreground."""
    def cb(hwnd, _):
        wpid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(wpid))
        if wpid.value != keep_pid and user32.IsWindowVisible(hwnd) and win_title(hwnd):
            user32.ShowWindow(hwnd, SW_MINIMIZE)
        return True
    user32.EnumWindows(WNDENUMPROC(cb), 0)

def force_foreground(hwnd):
    """Robustly bring hwnd to the OS foreground (the foreground-lock + AttachThreadInput + SwitchToThisWindow
    dance). Returns the resulting foreground hwnd so the caller can verify it actually took."""
    SPI_SETFOREGROUNDLOCKTIMEOUT = 0x2001
    val = ctypes.c_uint(0)
    user32.SystemParametersInfoW(SPI_SETFOREGROUNDLOCKTIMEOUT, 0, ctypes.byref(val), 0)
    fg = user32.GetForegroundWindow()
    fg_tid = user32.GetWindowThreadProcessId(fg, None) if fg else 0
    tid = user32.GetWindowThreadProcessId(hwnd, None)
    cur = kernel32.GetCurrentThreadId()
    for t in {fg_tid, cur} - {0}:
        user32.AttachThreadInput(t, tid, True)
    user32.ShowWindow(hwnd, SW_RESTORE)
    user32.BringWindowToTop(hwnd)
    try:
        user32.SwitchToThisWindow(hwnd, True)
    except Exception:
        pass
    user32.SetForegroundWindow(hwnd)
    for t in {fg_tid, cur} - {0}:
        user32.AttachThreadInput(t, tid, False)
    time.sleep(0.4)
    return user32.GetForegroundWindow()

class GUITHREADINFO(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.DWORD), ("flags", wintypes.DWORD),
                ("hwndActive", wintypes.HWND), ("hwndFocus", wintypes.HWND),
                ("hwndCapture", wintypes.HWND), ("hwndMenuOwner", wintypes.HWND),
                ("hwndMoveSize", wintypes.HWND), ("hwndCaret", wintypes.HWND),
                ("rcCaret", wintypes.RECT)]

def focus_info():
    """The control that actually holds the KEYBOARD focus right now (GetGUIThreadInfo of the foreground
    thread). This is the decisive diagnostic: is the focused control a 1C window (our PID) or something else?"""
    fg = user32.GetForegroundWindow()
    tid = user32.GetWindowThreadProcessId(fg, None)
    gti = GUITHREADINFO(); gti.cbSize = ctypes.sizeof(GUITHREADINFO)
    user32.GetGUIThreadInfo(tid, ctypes.byref(gti))
    fh = gti.hwndFocus or gti.hwndActive
    cls = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(fh, cls, 256)
    wpid = wintypes.DWORD(); user32.GetWindowThreadProcessId(fh, ctypes.byref(wpid))
    return {"focus_hwnd": fh, "focus_class": cls.value, "focus_pid": wpid.value,
            "is_our_client": wpid.value == PID, "fg_hwnd": fg, "fg_title": win_title(fg)}

def screenshot(path, hwnd=None):
    """Capture the 1C window by PrintWindow(PW_RENDERFULLCONTENT) — renders the window content even when a
    concurrent session's terminal overlaps it (z-order independent). Falls back to full-screen."""
    p = path.replace("\\", "\\\\")
    if hwnd:
        ps = (
            "Add-Type -AssemblyName System.Drawing;"
            "Add-Type @'\nusing System;using System.Runtime.InteropServices;\n"
            "public class WC{[DllImport(\"user32.dll\")]public static extern bool PrintWindow(IntPtr h,IntPtr dc,uint f);"
            "[DllImport(\"user32.dll\")]public static extern bool GetWindowRect(IntPtr h,out R r);"
            "public struct R{public int L,T,Rg,B;}}\n'@;"
            "$h=[IntPtr]%d;$r=New-Object WC+R;[void][WC]::GetWindowRect($h,[ref]$r);"
            "$w=$r.Rg-$r.L;$ht=$r.B-$r.T;if($w-lt1){$w=1};if($ht-lt1){$ht=1};"
            "$bmp=New-Object System.Drawing.Bitmap $w,$ht;$g=[System.Drawing.Graphics]::FromImage($bmp);"
            "$dc=$g.GetHdc();[void][WC]::PrintWindow($h,$dc,2);$g.ReleaseHdc($dc);$bmp.Save('%s');" % (int(hwnd), p))
    else:
        ps = ("Add-Type -AssemblyName System.Windows.Forms,System.Drawing;"
              "$b=[System.Windows.Forms.Screen]::PrimaryScreen.Bounds;"
              "$bmp=New-Object System.Drawing.Bitmap $b.Width,$b.Height;"
              "$g=[System.Drawing.Graphics]::FromImage($bmp);"
              "$g.CopyFromScreen($b.Location,[System.Drawing.Point]::Empty,$b.Size);$bmp.Save('%s');" % p)
    try:
        subprocess.run(["powershell", "-NoProfile", "-Command", ps], timeout=30,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

TARGET_HWND = find_main_window(PID) if PID else None
diag = {}

import qa_mcp.protocol.native_xtest as nx  # noqa: E402

def patched_xtest_type(display, text, delay_ms=60):
    diag["fg_before"] = {"hwnd": user32.GetForegroundWindow(), "title": win_title(user32.GetForegroundWindow())}
    if TARGET_HWND:
        took = False
        for _ in range(4):  # contended desktop — retry until 1C is foreground right up against the type
            minimize_others(PID)
            fg = force_foreground(TARGET_HWND)
            took = fg == TARGET_HWND
            if took:
                break
        diag["fg_after"] = {"hwnd": fg, "title": win_title(fg), "target": TARGET_HWND,
                            "target_title": win_title(TARGET_HWND), "took": took}
    time.sleep(0.15)
    diag["focus_pre_type"] = focus_info()  # the control that has keyboard focus at the instant we type
    chord(VK_CONTROL, 0x41); time.sleep(0.05); tap(0x2E)  # Ctrl+A, Delete — clear any accumulated text first
    type_unicode(text, max(0.008, delay_ms / 1000.0 / 5))
    diag["focus_post_type"] = focus_info()
    time.sleep(0.3)
    screenshot(SHOT, hwnd=TARGET_HWND)  # PrintWindow the 1C window — z-order independent (terminal overlap OK)

def patched_send_keys(keys, display=":89", settle_sec=0.15):
    seq = [keys] if isinstance(keys, str) else list(keys)
    for k in seq:
        kl = k.lower()
        if kl == "tab":
            tap(VK_TAB)
        elif kl in ("return", "enter"):
            tap(VK_RETURN)
        elif kl in ("escape", "esc"):
            tap(VK_ESCAPE)
        elif kl == "ctrl+s":
            chord(VK_CONTROL, VK_S)
        else:
            raise ValueError("spike: unmapped key %r" % k)
        time.sleep(settle_sec)
    return {"keys": seq, "sent": len(seq), "via": "SendInput"}

nx.xtest_type = patched_xtest_type
nx.send_keys = patched_send_keys

result = {"value": VALUE, "pid": PID, "target_hwnd": TARGET_HWND, "save": SAVE, "port": PORT}
try:
    res = nx.write_form_value_xtest(
        CAPTURE, VALUE, "Наименование",
        host="127.0.0.1", port=PORT, display="(win-sendinput)",
        setup_stop=17, read_start=25, read_frame=28, blur=True, save=SAVE,
    )
    result.update(res)
    result["ok"] = True
except Exception as e:
    result["ok"] = False
    result["error"] = "%s: %s" % (type(e).__name__, e)
    result["trace"] = traceback.format_exc()
result["diag"] = diag

with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(result, fh, ensure_ascii=False, indent=2)
try:
    print("QA_SPIKE_RESULT " + json.dumps(result, ensure_ascii=False))
except Exception:
    pass
