import ctypes
import json
import os
import queue
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk
from ctypes import wintypes


APP_NAME = "Valorant Media Guard"
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

SRCCOPY = 0x00CC0020
DIB_RGB_COLORS = 0

WM_APPCOMMAND = 0x0319
HWND_BROADCAST = ctypes.c_void_p(0xFFFF)
APPCOMMAND_MEDIA_PLAY = 46
APPCOMMAND_MEDIA_PAUSE = 47
VK_MEDIA_PLAY_PAUSE = 0xB3
KEYEVENTF_KEYUP = 0x0002

SM_XVIRTUALSCREEN = 76
SM_YVIRTUALSCREEN = 77
SM_CXVIRTUALSCREEN = 78
SM_CYVIRTUALSCREEN = 79

user32 = ctypes.WinDLL("user32", use_last_error=True)
gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)

HANDLE = ctypes.c_void_p
HWND = ctypes.c_void_p
HDC = ctypes.c_void_p
HBITMAP = ctypes.c_void_p
HGDIOBJ = ctypes.c_void_p


class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", wintypes.DWORD),
        ("biWidth", wintypes.LONG),
        ("biHeight", wintypes.LONG),
        ("biPlanes", wintypes.WORD),
        ("biBitCount", wintypes.WORD),
        ("biCompression", wintypes.DWORD),
        ("biSizeImage", wintypes.DWORD),
        ("biXPelsPerMeter", wintypes.LONG),
        ("biYPelsPerMeter", wintypes.LONG),
        ("biClrUsed", wintypes.DWORD),
        ("biClrImportant", wintypes.DWORD),
    ]


class BITMAPINFO(ctypes.Structure):
    _fields_ = [
        ("bmiHeader", BITMAPINFOHEADER),
        ("bmiColors", wintypes.DWORD * 3),
    ]


user32.GetDC.argtypes = [HWND]
user32.GetDC.restype = HDC
user32.ReleaseDC.argtypes = [HWND, HDC]
user32.ReleaseDC.restype = ctypes.c_int
user32.GetSystemMetrics.argtypes = [ctypes.c_int]
user32.GetSystemMetrics.restype = ctypes.c_int
user32.GetForegroundWindow.argtypes = []
user32.GetForegroundWindow.restype = HWND
user32.GetWindowTextLengthW.argtypes = [HWND]
user32.GetWindowTextLengthW.restype = ctypes.c_int
user32.GetWindowTextW.argtypes = [HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetWindowTextW.restype = ctypes.c_int
user32.SendMessageW.argtypes = [HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.SendMessageW.restype = wintypes.LPARAM
user32.keybd_event.argtypes = [wintypes.BYTE, wintypes.BYTE, wintypes.DWORD, wintypes.WPARAM]
user32.keybd_event.restype = None

gdi32.CreateCompatibleDC.argtypes = [HDC]
gdi32.CreateCompatibleDC.restype = HDC
gdi32.CreateCompatibleBitmap.argtypes = [HDC, ctypes.c_int, ctypes.c_int]
gdi32.CreateCompatibleBitmap.restype = HBITMAP
gdi32.SelectObject.argtypes = [HDC, HGDIOBJ]
gdi32.SelectObject.restype = HGDIOBJ
gdi32.BitBlt.argtypes = [HDC, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, HDC, ctypes.c_int, ctypes.c_int, wintypes.DWORD]
gdi32.BitBlt.restype = wintypes.BOOL
gdi32.GetDIBits.argtypes = [HDC, HBITMAP, wintypes.UINT, wintypes.UINT, ctypes.c_void_p, ctypes.POINTER(BITMAPINFO), wintypes.UINT]
gdi32.GetDIBits.restype = ctypes.c_int
gdi32.DeleteObject.argtypes = [HGDIOBJ]
gdi32.DeleteObject.restype = wintypes.BOOL
gdi32.DeleteDC.argtypes = [HDC]
gdi32.DeleteDC.restype = wintypes.BOOL


DEFAULT_CONFIG = {
    "region": None,
    "interval_ms": 450,
    "red_pixel_percent": 1.0,
    "red_min_value": 140,
    "red_difference": 45,
    "stable_reads": 2,
    "require_valorant_foreground": True,
    "command_mode": "direct",
}


def set_dpi_awareness():
    try:
        shcore = ctypes.WinDLL("shcore", use_last_error=True)
        shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            user32.SetProcessDPIAware()
        except Exception:
            pass


def win_error(message):
    error = ctypes.get_last_error()
    if error:
        raise ctypes.WinError(error)
    raise OSError(message)


def load_config():
    data = dict(DEFAULT_CONFIG)
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as handle:
                loaded = json.load(handle)
            if isinstance(loaded, dict):
                data.update(loaded)
        except Exception:
            pass
    return data


def save_config(data):
    with open(CONFIG_PATH, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)


def get_virtual_screen():
    x = user32.GetSystemMetrics(SM_XVIRTUALSCREEN)
    y = user32.GetSystemMetrics(SM_YVIRTUALSCREEN)
    width = user32.GetSystemMetrics(SM_CXVIRTUALSCREEN)
    height = user32.GetSystemMetrics(SM_CYVIRTUALSCREEN)
    return x, y, width, height


def get_foreground_title():
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return ""
    length = user32.GetWindowTextLengthW(hwnd)
    buffer = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buffer, length + 1)
    return buffer.value


def is_valorant_foreground():
    return "VALORANT" in get_foreground_title().upper()


def send_appcommand(command):
    user32.SendMessageW(HWND_BROADCAST, WM_APPCOMMAND, 0, command << 16)


def send_media_play():
    send_appcommand(APPCOMMAND_MEDIA_PLAY)


def send_media_pause():
    send_appcommand(APPCOMMAND_MEDIA_PAUSE)


def send_media_toggle():
    user32.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, 0, 0)
    user32.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, KEYEVENTF_KEYUP, 0)


def capture_region(left, top, width, height):
    if width <= 0 or height <= 0:
        raise ValueError("Der Aufnahmebereich ist leer.")

    screen_dc = user32.GetDC(None)
    if not screen_dc:
        win_error("Konnte den Bildschirm nicht lesen.")

    mem_dc = gdi32.CreateCompatibleDC(screen_dc)
    if not mem_dc:
        user32.ReleaseDC(None, screen_dc)
        win_error("Konnte keinen Speicher-DC erstellen.")

    bitmap = gdi32.CreateCompatibleBitmap(screen_dc, width, height)
    if not bitmap:
        gdi32.DeleteDC(mem_dc)
        user32.ReleaseDC(None, screen_dc)
        win_error("Konnte kein Bildschirm-Bitmap erstellen.")

    old_object = gdi32.SelectObject(mem_dc, bitmap)
    try:
        ok = gdi32.BitBlt(mem_dc, 0, 0, width, height, screen_dc, left, top, SRCCOPY)
        if not ok:
            win_error("BitBlt ist fehlgeschlagen.")

        bitmap_info = BITMAPINFO()
        bitmap_info.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bitmap_info.bmiHeader.biWidth = width
        bitmap_info.bmiHeader.biHeight = -height
        bitmap_info.bmiHeader.biPlanes = 1
        bitmap_info.bmiHeader.biBitCount = 32
        bitmap_info.bmiHeader.biCompression = 0

        buffer_size = width * height * 4
        buffer = ctypes.create_string_buffer(buffer_size)
        rows = gdi32.GetDIBits(mem_dc, bitmap, 0, height, buffer, ctypes.byref(bitmap_info), DIB_RGB_COLORS)
        if rows != height:
            win_error("Konnte die Bildschirmdaten nicht kopieren.")
        return buffer.raw
    finally:
        if old_object:
            gdi32.SelectObject(mem_dc, old_object)
        gdi32.DeleteObject(bitmap)
        gdi32.DeleteDC(mem_dc)
        user32.ReleaseDC(None, screen_dc)


def get_red_percent(raw_bgra, width, height, red_min_value, red_difference):
    total = width * height
    if total <= 0:
        return 0.0, 0, 0

    red_pixels = 0
    for index in range(0, len(raw_bgra), 4):
        blue = raw_bgra[index]
        green = raw_bgra[index + 1]
        red = raw_bgra[index + 2]

        if red >= red_min_value and red - green >= red_difference and red - blue >= red_difference:
            red_pixels += 1

    return red_pixels * 100.0 / total, red_pixels, total


def detect_state_from_red(raw_bgra, width, height, red_pixel_percent, red_min_value, red_difference):
    percent, red_pixels, total = get_red_percent(raw_bgra, width, height, red_min_value, red_difference)
    state = "red" if percent >= red_pixel_percent else "no_red"
    return state, percent, red_pixels, total


def region_to_text(region):
    if not region:
        return "nicht gewaehlt"
    return f"x={region['left']} y={region['top']} w={region['width']} h={region['height']}"


class RegionSelector(tk.Toplevel):
    def __init__(self, master, callback):
        super().__init__(master)
        self.callback = callback
        self.start_x = None
        self.start_y = None
        self.rect_id = None
        self.virtual_x, self.virtual_y, self.virtual_w, self.virtual_h = get_virtual_screen()

        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.32)
        self.configure(bg="black")
        self.geometry(f"{self.virtual_w}x{self.virtual_h}+{self.virtual_x}+{self.virtual_y}")

        self.canvas = tk.Canvas(self, bg="black", cursor="crosshair", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_text(
            24,
            24,
            anchor="nw",
            fill="white",
            font=("Segoe UI", 16, "bold"),
            text="Bereich ziehen, in dem Rot erkannt werden soll. Esc bricht ab.",
        )
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<Escape>", lambda _event: self.cancel())
        self.focus_force()

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect_id = self.canvas.create_rectangle(event.x, event.y, event.x, event.y, outline="#ff4655", width=3)

    def on_drag(self, event):
        if self.rect_id is not None:
            self.canvas.coords(self.rect_id, self.start_x, self.start_y, event.x, event.y)

    def on_release(self, event):
        if self.start_x is None or self.start_y is None:
            self.cancel()
            return

        left = min(self.start_x, event.x) + self.virtual_x
        top = min(self.start_y, event.y) + self.virtual_y
        right = max(self.start_x, event.x) + self.virtual_x
        bottom = max(self.start_y, event.y) + self.virtual_y
        width = right - left
        height = bottom - top

        self.destroy()
        if width < 20 or height < 20:
            self.callback(None)
            return

        self.callback({"left": int(left), "top": int(top), "width": int(width), "height": int(height)})

    def cancel(self):
        self.destroy()
        self.callback(None)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.minsize(620, 440)

        self.config_data = load_config()
        self.events = queue.Queue()
        self.stop_event = threading.Event()
        self.monitor_thread = None

        self.region_var = tk.StringVar()
        self.red_settings_var = tk.StringVar()
        self.monitor_var = tk.StringVar(value="gestoppt")
        self.detected_var = tk.StringVar(value="-")
        self.log_var = tk.StringVar(value="Bereit.")
        self.interval_var = tk.StringVar(value=str(self.config_data.get("interval_ms", 450)))
        self.red_percent_var = tk.StringVar(value=str(self.config_data.get("red_pixel_percent", 1.0)))
        self.red_min_var = tk.StringVar(value=str(self.config_data.get("red_min_value", 140)))
        self.red_difference_var = tk.StringVar(value=str(self.config_data.get("red_difference", 45)))
        self.stable_var = tk.StringVar(value=str(self.config_data.get("stable_reads", 2)))
        self.require_valorant_var = tk.BooleanVar(value=bool(self.config_data.get("require_valorant_foreground", True)))
        self.command_mode_var = tk.StringVar(value=self.config_data.get("command_mode", "direct"))

        self.build_ui()
        self.refresh_labels()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.after(200, self.drain_events)

    def build_ui(self):
        root = ttk.Frame(self, padding=18)
        root.pack(fill="both", expand=True)
        root.columnconfigure(0, weight=1)

        title = ttk.Label(root, text=APP_NAME, font=("Segoe UI", 18, "bold"))
        title.grid(row=0, column=0, sticky="w")

        subtitle = ttk.Label(
            root,
            text="Bildschirm-Erkennung fuer Valorant: Rot im gewaehlten Bereich = Medien weiter, kein Rot = Medien pausieren.",
            wraplength=560,
        )
        subtitle.grid(row=1, column=0, sticky="w", pady=(2, 14))

        status = ttk.LabelFrame(root, text="Status", padding=12)
        status.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        status.columnconfigure(1, weight=1)
        self.add_status_row(status, 0, "Bereich", self.region_var)
        self.add_status_row(status, 1, "Rot-Regel", self.red_settings_var)
        self.add_status_row(status, 2, "Monitoring", self.monitor_var)
        self.add_status_row(status, 3, "Erkannt", self.detected_var)

        controls = ttk.LabelFrame(root, text="Einrichten", padding=12)
        controls.grid(row=3, column=0, sticky="ew", pady=(0, 12))
        controls.columnconfigure(0, weight=1)

        ttk.Button(controls, text="Bereich waehlen", command=self.select_region).grid(row=0, column=0, sticky="ew")

        settings = ttk.LabelFrame(root, text="Optionen", padding=12)
        settings.grid(row=4, column=0, sticky="ew", pady=(0, 12))
        for column in range(6):
            settings.columnconfigure(column, weight=1)

        ttk.Label(settings, text="Intervall ms").grid(row=0, column=0, sticky="w")
        ttk.Entry(settings, textvariable=self.interval_var, width=8).grid(row=0, column=1, sticky="ew", padx=(4, 12))
        ttk.Label(settings, text="Rot %").grid(row=0, column=2, sticky="w")
        ttk.Entry(settings, textvariable=self.red_percent_var, width=8).grid(row=0, column=3, sticky="ew", padx=(4, 12))
        ttk.Label(settings, text="Stabil").grid(row=0, column=4, sticky="w")
        ttk.Entry(settings, textvariable=self.stable_var, width=8).grid(row=0, column=5, sticky="ew", padx=(4, 0))

        ttk.Label(settings, text="Rot min").grid(row=1, column=0, sticky="w", pady=(10, 0))
        ttk.Entry(settings, textvariable=self.red_min_var, width=8).grid(row=1, column=1, sticky="ew", padx=(4, 12), pady=(10, 0))
        ttk.Label(settings, text="Rot Abstand").grid(row=1, column=2, sticky="w", pady=(10, 0))
        ttk.Entry(settings, textvariable=self.red_difference_var, width=8).grid(row=1, column=3, sticky="ew", padx=(4, 12), pady=(10, 0))

        ttk.Checkbutton(settings, text="Nur reagieren, wenn Valorant im Vordergrund ist", variable=self.require_valorant_var).grid(
            row=2, column=0, columnspan=6, sticky="w", pady=(10, 4)
        )
        ttk.Radiobutton(settings, text="Direkte Play/Pause-Befehle", variable=self.command_mode_var, value="direct").grid(
            row=3, column=0, columnspan=3, sticky="w"
        )
        ttk.Radiobutton(settings, text="Fallback: Medien-Toggle bei jedem Wechsel", variable=self.command_mode_var, value="toggle").grid(
            row=3, column=3, columnspan=3, sticky="w"
        )

        run = ttk.Frame(root)
        run.grid(row=5, column=0, sticky="ew")
        for column in range(4):
            run.columnconfigure(column, weight=1)

        ttk.Button(run, text="Start", command=self.start_monitoring).grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ttk.Button(run, text="Stop", command=self.stop_monitoring).grid(row=0, column=1, sticky="ew", padx=4)
        ttk.Button(run, text="Test Play", command=send_media_play).grid(row=0, column=2, sticky="ew", padx=4)
        ttk.Button(run, text="Test Pause", command=send_media_pause).grid(row=0, column=3, sticky="ew", padx=(8, 0))

        log = ttk.Label(root, textvariable=self.log_var, wraplength=560)
        log.grid(row=6, column=0, sticky="ew", pady=(14, 0))

    def add_status_row(self, parent, row, label, variable):
        ttk.Label(parent, text=label + ":").grid(row=row, column=0, sticky="w", padx=(0, 10), pady=2)
        ttk.Label(parent, textvariable=variable, wraplength=460).grid(row=row, column=1, sticky="w", pady=2)

    def refresh_labels(self):
        self.region_var.set(region_to_text(self.config_data.get("region")))
        self.red_settings_var.set(
            f"Play ab {self.config_data.get('red_pixel_percent', 1.0)}% roten Pixeln "
            f"(Rot min {self.config_data.get('red_min_value', 140)}, Abstand {self.config_data.get('red_difference', 45)})"
        )

    def select_region(self):
        messagebox.showinfo(
            "Bereich waehlen",
            "Nach OK hast du 3 Sekunden, um Valorant sichtbar zu machen. Ziehe dann einen Bereich, "
            "in dem die rote Anzeige erscheinen soll.",
        )
        self.withdraw()
        self.after(3000, self.open_region_selector)

    def open_region_selector(self):
        RegionSelector(self, self.region_selected)

    def region_selected(self, region):
        self.deiconify()
        self.lift()
        if not region:
            self.log_var.set("Bereichsauswahl abgebrochen oder zu klein.")
            return
        self.config_data["region"] = region
        save_config(self.config_data)
        self.refresh_labels()
        self.log_var.set("Bereich gespeichert. Start druecken, dann wird Rot in diesem Bereich erkannt.")

    def sync_settings(self):
        try:
            interval_ms = int(float(self.interval_var.get()))
            red_pixel_percent = float(self.red_percent_var.get())
            red_min_value = int(float(self.red_min_var.get()))
            red_difference = int(float(self.red_difference_var.get()))
            stable_reads = int(float(self.stable_var.get()))
        except ValueError:
            raise ValueError("Intervall, Rot %, Rot min, Rot Abstand und Stabil muessen Zahlen sein.")

        if interval_ms < 100:
            raise ValueError("Intervall muss mindestens 100 ms sein.")
        if red_pixel_percent < 0 or red_pixel_percent > 100:
            raise ValueError("Rot % muss zwischen 0 und 100 liegen.")
        if red_min_value < 0 or red_min_value > 255:
            raise ValueError("Rot min muss zwischen 0 und 255 liegen.")
        if red_difference < 0 or red_difference > 255:
            raise ValueError("Rot Abstand muss zwischen 0 und 255 liegen.")
        if stable_reads < 1:
            raise ValueError("Stabil muss mindestens 1 sein.")
        if self.command_mode_var.get() not in ("direct", "toggle"):
            self.command_mode_var.set("direct")

        self.config_data["interval_ms"] = interval_ms
        self.config_data["red_pixel_percent"] = red_pixel_percent
        self.config_data["red_min_value"] = red_min_value
        self.config_data["red_difference"] = red_difference
        self.config_data["stable_reads"] = stable_reads
        self.config_data["require_valorant_foreground"] = bool(self.require_valorant_var.get())
        self.config_data["command_mode"] = self.command_mode_var.get()
        save_config(self.config_data)
        self.refresh_labels()

    def start_monitoring(self):
        if self.monitor_thread and self.monitor_thread.is_alive():
            return
        if not self.config_data.get("region"):
            messagebox.showwarning("Fehlt", "Waehle zuerst einen Bereich.")
            return
        try:
            self.sync_settings()
        except Exception as exc:
            messagebox.showerror("Optionen pruefen", str(exc))
            return

        self.stop_event.clear()
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.monitor_var.set("laeuft")
        self.log_var.set("Monitoring gestartet. Das Fenster wird minimiert; du kannst es ueber die Taskleiste wieder oeffnen.")
        self.after(1200, self.iconify)

    def stop_monitoring(self):
        self.stop_event.set()
        self.monitor_var.set("stoppt...")
        self.log_var.set("Monitoring wird gestoppt.")

    def monitor_loop(self):
        region = dict(self.config_data["region"])
        interval = self.config_data["interval_ms"] / 1000.0
        red_pixel_percent = float(self.config_data["red_pixel_percent"])
        red_min_value = int(self.config_data["red_min_value"])
        red_difference = int(self.config_data["red_difference"])
        stable_reads = int(self.config_data["stable_reads"])
        require_valorant = bool(self.config_data["require_valorant_foreground"])
        command_mode = self.config_data.get("command_mode", "direct")

        candidate = None
        candidate_count = 0
        last_action_state = None

        while not self.stop_event.is_set():
            try:
                if require_valorant and not is_valorant_foreground():
                    self.events.put(("status", "wartet auf Valorant", "-", "Valorant ist nicht im Vordergrund."))
                    candidate = None
                    candidate_count = 0
                    time.sleep(interval)
                    continue

                raw = capture_region(region["left"], region["top"], region["width"], region["height"])
                state, percent, red_pixels, total = detect_state_from_red(
                    raw,
                    region["width"],
                    region["height"],
                    red_pixel_percent,
                    red_min_value,
                    red_difference,
                )

                readable = {
                    "red": "rot",
                    "no_red": "kein Rot",
                }[state]

                detail = f"{readable}  |  Rot {percent:.2f}% ({red_pixels}/{total})"
                self.events.put(("status", "laeuft", detail, ""))

                if candidate == state:
                    candidate_count += 1
                else:
                    candidate = state
                    candidate_count = 1

                if candidate_count >= stable_reads and state != last_action_state:
                    if command_mode == "toggle":
                        send_media_toggle()
                        action = "Medien-Toggle"
                    elif state == "red":
                        send_media_play()
                        action = "Play"
                    else:
                        send_media_pause()
                        action = "Pause"

                    last_action_state = state
                    self.events.put(("log", f"{action} gesendet, weil Zustand jetzt {readable} ist."))

                time.sleep(interval)
            except Exception as exc:
                self.events.put(("status", "Fehler", "-", str(exc)))
                time.sleep(max(interval, 1.0))

        self.events.put(("stopped",))

    def drain_events(self):
        try:
            while True:
                event = self.events.get_nowait()
                if event[0] == "status":
                    self.monitor_var.set(event[1])
                    self.detected_var.set(event[2])
                    if event[3]:
                        self.log_var.set(event[3])
                elif event[0] == "log":
                    self.log_var.set(event[1])
                elif event[0] == "stopped":
                    self.monitor_var.set("gestoppt")
                    self.detected_var.set("-")
        except queue.Empty:
            pass
        self.after(200, self.drain_events)

    def on_close(self):
        self.stop_event.set()
        self.destroy()


if __name__ == "__main__":
    set_dpi_awareness()
    app = App()
    app.mainloop()
