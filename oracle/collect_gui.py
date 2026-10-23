"""Collect oracle values from a running G*Power 3.1.9.7 window (Windows only).

Drives the GUI with Win32 messages (select combo item, set edit text, click
Calculate), reads the output fields exactly as displayed, and saves a
screenshot of the window for every vector. Error dialogs are captured too.

Usage (G*Power must be open):
    python -I oracle/collect_gui.py oracle/gpower_gui_vectors.csv
"""

from __future__ import annotations

import csv
import ctypes
import ctypes.wintypes as wt
import sys
import time
from pathlib import Path

from PIL import Image

u32 = ctypes.windll.user32
u32.SendMessageW.argtypes = [wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM]
u32.SendMessageW.restype = ctypes.c_ssize_t
u32.GetWindowThreadProcessId.argtypes = [wt.HWND, ctypes.POINTER(wt.DWORD)]
ctypes.windll.shcore.SetProcessDpiAwareness(2)

WM_SETTEXT, WM_GETTEXT, WM_GETTEXTLENGTH, WM_COMMAND, WM_CLOSE = 0x0C, 0x0D, 0x0E, 0x111, 0x10
BM_CLICK, CB_GETCOUNT, CB_GETLBTEXT, CB_GETLBTEXTLEN, CB_SETCURSEL = 0xF5, 0x146, 0x148, 0x149, 0x14E
ENUM = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

MODES = {
    "a-priori": "A priori", "post-hoc": "Post hoc", "compromise": "Compromise",
    "criterion": "Criterion", "sensitivity": "Sensitivity",
}
INPUT_LABELS = {
    "w": "Effect size w", "alpha": "α err prob", "power": "Power (1-β err prob)",
    "n_total": "Total sample size", "df": "Df", "beta_alpha_ratio": "β/α ratio",
}
OUTPUT_LABELS = {
    "Noncentrality parameter λ": "ncp", "Critical χ²": "critical_chi2",
    "Total sample size": "n_total", "Actual power": "actual_power",
    "Power (1-β err prob)": "power", "α err prob": "alpha", "β err prob": "beta",
    "Effect size w": "w",
}


def text(h):
    n = u32.SendMessageW(h, WM_GETTEXTLENGTH, 0, 0)
    buf = ctypes.create_unicode_buffer(n + 1)
    u32.SendMessageW(h, WM_GETTEXT, n + 1, ctypes.cast(buf, ctypes.c_void_p).value)
    return buf.value


def cls(h):
    buf = ctypes.create_unicode_buffer(256)
    u32.GetClassNameW(h, buf, 256)
    return buf.value


def rect(h):
    r = wt.RECT()
    u32.GetWindowRect(h, ctypes.byref(r))
    return r.left, r.top, r.right, r.bottom


def pid_of(h):
    p = wt.DWORD()
    u32.GetWindowThreadProcessId(h, ctypes.byref(p))
    return p.value


def top_windows(pid):
    out = []
    u32.EnumWindows(ENUM(lambda h, _: (out.append(h) if u32.IsWindowVisible(h) and pid_of(h) == pid else None) or True), 0)
    return out


def children(root):
    out = []
    u32.EnumChildWindows(root, ENUM(lambda h, _: (out.append(h) if u32.IsWindowVisible(h) else None) or True), 0)
    return out


def main_window():
    wins = []
    u32.EnumWindows(ENUM(lambda h, _: (wins.append(h) if u32.IsWindowVisible(h) and text(h).startswith("G*Power") else None) or True), 0)
    if not wins:
        sys.exit("G*Power window not found")
    return wins[0]


def notify(h, code):
    u32.SendMessageW(u32.GetParent(h), WM_COMMAND, (code << 16) | (u32.GetDlgCtrlID(h) & 0xFFFF), h)


def combo_select(h, prefix):
    for i in range(u32.SendMessageW(h, CB_GETCOUNT, 0, 0)):
        n = u32.SendMessageW(h, CB_GETLBTEXTLEN, i, 0)
        buf = ctypes.create_unicode_buffer(n + 1)
        u32.SendMessageW(h, CB_GETLBTEXT, i, ctypes.cast(buf, ctypes.c_void_p).value)
        if buf.value.startswith(prefix):
            u32.SendMessageW(h, CB_SETCURSEL, i, 0)
            notify(h, 1)  # CBN_SELCHANGE
            time.sleep(0.4)
            return
    raise KeyError(prefix)


def set_edit(h, value):
    buf = ctypes.create_unicode_buffer(str(value))
    u32.SendMessageW(h, WM_SETTEXT, 0, ctypes.cast(buf, ctypes.c_void_p).value)
    notify(h, 0x300)  # EN_CHANGE
    notify(h, 0x200)  # EN_KILLFOCUS


def panels(root):
    """Return (combos sorted top-down, input {label: edit}, output {label: edit}, buttons)."""
    hs = children(root)
    buttons = {text(h).strip(): h for h in hs if cls(h) == "Button"}
    out_x = rect(buttons["Output Parameters"])[0]
    statics = [(rect(h), text(h)) for h in hs if cls(h) == "Static" and text(h)]
    edits = [(rect(h), h) for h in hs if cls(h) == "Edit"]
    combos = sorted([(rect(h), h) for h in hs if cls(h) == "ComboBox"], key=lambda x: (x[0][1], x[0][0]))
    inp, out = {}, {}
    for r, label in statics:
        cy = (r[1] + r[3]) // 2
        for er, eh in edits:
            if abs((er[1] + er[3]) // 2 - cy) <= 3 and 0 <= er[0] - r[2] < 40:
                (out if r[0] >= out_x else inp)[label] = eh
    return combos, inp, out, buttons


def capture(h):
    """Render one window with PrintWindow, so other windows on top don't leak in."""
    l, t, r, b = rect(h)
    w, hgt = r - l, b - t
    gdi = ctypes.windll.gdi32
    hdc = u32.GetWindowDC(h)
    mem = gdi.CreateCompatibleDC(hdc)
    bmp = gdi.CreateCompatibleBitmap(hdc, w, hgt)
    gdi.SelectObject(mem, bmp)
    u32.PrintWindow(h, mem, 2)  # PW_RENDERFULLCONTENT
    buf = ctypes.create_string_buffer(w * hgt * 4)

    class BMI(ctypes.Structure):
        _fields_ = [("biSize", wt.DWORD), ("biWidth", wt.LONG), ("biHeight", wt.LONG),
                    ("biPlanes", wt.WORD), ("biBitCount", wt.WORD), ("biCompression", wt.DWORD),
                    ("biSizeImage", wt.DWORD), ("biXPelsPerMeter", wt.LONG), ("biYPelsPerMeter", wt.LONG),
                    ("biClrUsed", wt.DWORD), ("biClrImportant", wt.DWORD)]
    bmi = BMI(ctypes.sizeof(BMI), w, -hgt, 1, 32, 0, 0, 0, 0, 0, 0)
    gdi.GetDIBits(mem, bmp, 0, hgt, buf, ctypes.byref(bmi), 0)
    gdi.DeleteObject(bmp)
    gdi.DeleteDC(mem)
    u32.ReleaseDC(h, hdc)
    return Image.frombuffer("RGB", (w, hgt), buf, "raw", "BGRX", 0, 1), (l, t)


def snapshot(hwnds, path):
    """Main window plus any dialogs, each pasted at its screen position."""
    shots = [capture(h) for h in hwnds]
    x0 = min(p[0] for _, p in shots)
    y0 = min(p[1] for _, p in shots)
    x1 = max(p[0] + im.width for im, p in shots)
    y1 = max(p[1] + im.height for im, p in shots)
    canvas = Image.new("RGB", (x1 - x0, y1 - y0), "white")
    for im, (x, y) in shots:
        canvas.paste(im, (x - x0, y - y0))
    canvas.save(path)


def run_row(root, pid, row, shot_dir):
    combos, _, _, _ = panels(root)
    combo_select(combos[0][1], "χ² tests")
    combos, _, _, _ = panels(root)
    combo_select(combos[1][1], "Goodness-of-fit tests: Contingency tables")
    combos, _, _, _ = panels(root)
    combo_select(combos[2][1], MODES[row["mode"]])
    combos, inp, out, buttons = panels(root)
    for field, label in INPUT_LABELS.items():
        if row.get(field):
            set_edit(inp[label], row[field])
    before = set(top_windows(pid))
    u32.PostMessageW(buttons["Calculate"], BM_CLICK, 0, 0)
    time.sleep(1.5)
    dialogs = [h for h in top_windows(pid) if h not in before and h != root]
    result = {}
    shot = shot_dir / f"{row['id']}.png"
    if dialogs:
        msg = " | ".join(text(c) for d in dialogs for c in children(d) if cls(c) == "Static" and text(c))
        result["error_text"] = msg
        snapshot([root] + dialogs, shot)
        for d in dialogs:
            u32.PostMessageW(d, WM_CLOSE, 0, 0)
        time.sleep(0.5)
    else:
        snapshot([root], shot)
    _, _, out, _ = panels(root)
    for label, eh in out.items():
        if label in OUTPUT_LABELS:
            result[OUTPUT_LABELS[label]] = text(eh)
    return result, shot


def main():
    sys.stdout.reconfigure(encoding="utf-8")  # error texts contain β, α
    csv_path = Path(sys.argv[1])
    shot_dir = csv_path.parent / "screenshots"
    shot_dir.mkdir(exist_ok=True)
    root = main_window()
    pid = pid_of(root)
    u32.ShowWindow(root, 9)
    u32.SetForegroundWindow(root)
    with open(csv_path, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
        fields = list(rows[0])
    for extra in ("exp_error_text",):
        if extra not in fields:
            fields.insert(fields.index("screenshot"), extra)
    for row in rows:
        res, shot = run_row(root, pid, row, shot_dir)
        for k in ("n_total", "ncp", "critical_chi2", "actual_power", "power", "alpha", "beta", "w"):
            row[f"exp_{k}"] = ""
        # only modes' computed outputs are oracle values; inputs echoed in the output panel are dropped
        produced = {"a-priori": ("ncp", "critical_chi2", "n_total", "actual_power"),
                    "post-hoc": ("ncp", "critical_chi2", "power"),
                    "compromise": ("ncp", "critical_chi2", "alpha", "beta", "power"),
                    "criterion": ("ncp", "critical_chi2", "alpha"),
                    "sensitivity": ("ncp", "critical_chi2", "w")}[row["mode"]]
        if "error_text" in res:
            row["exp_error_text"] = res["error_text"]
        else:
            for k in produced:
                v = res.get(k, "")
                row[f"exp_{k}"] = "" if v in ("?", "") else v
        row["screenshot"] = f"screenshots/{shot.name}"
        print(row["id"], res, flush=True)
    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
