"""
setup_regions.py — First-time interactive setup for BTC Rocket Trader.

Lets the user:
  1. Draw a rectangle on the screen to define the SCAN_REGION
     (where rockets appear at the bottom of the chart).
  2. Click to mark the BUY button position.
  3. Click to mark the SELL button position.
  4. (Optional) Draw a rectangle for the full CHART_REGION used when
     taking screenshots.

Saves results to config.json.

Run directly:
    python setup_regions.py
"""

import logging
import sys
import tkinter as tk
from tkinter import messagebox

import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _take_fullscreen_pil():
    """Return a full-screen PIL image."""
    import PIL.ImageGrab  # imported here so the module is optional until needed
    return PIL.ImageGrab.grab()


class RegionSelector:
    """
    Tkinter-based fullscreen overlay that lets the user drag a rectangle
    to define a region, then returns (x, y, width, height).
    """

    def __init__(self, root: tk.Tk, screenshot, instruction: str):
        self.root = root
        self.screenshot = screenshot
        self.instruction = instruction
        self.result: tuple | None = None

        self._start_x = self._start_y = 0
        self._rect_id = None

    def run(self) -> tuple | None:
        """Show the overlay and block until the user completes the selection."""
        import PIL.ImageTk

        win = tk.Toplevel(self.root)
        win.attributes("-fullscreen", True)
        win.attributes("-topmost", True)
        win.configure(cursor="crosshair")

        tk_img = PIL.ImageTk.PhotoImage(self.screenshot)
        canvas = tk.Canvas(win, highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        canvas.create_image(0, 0, anchor=tk.NW, image=tk_img)

        # Instruction label (semi-transparent look using a label)
        lbl_text = self.instruction + "\n(Click and drag to draw rectangle, then release)"
        lbl = tk.Label(
            win,
            text=lbl_text,
            font=("Arial", 14, "bold"),
            bg="#222222",
            fg="#FFFFFF",
            padx=10,
            pady=6,
        )
        canvas.create_window(10, 10, anchor=tk.NW, window=lbl)

        def on_press(event):
            self._start_x, self._start_y = event.x, event.y
            if self._rect_id:
                canvas.delete(self._rect_id)

        def on_drag(event):
            if self._rect_id:
                canvas.delete(self._rect_id)
            self._rect_id = canvas.create_rectangle(
                self._start_x, self._start_y, event.x, event.y,
                outline="#FF4400", width=2, dash=(4, 2),
            )

        def on_release(event):
            x1 = min(self._start_x, event.x)
            y1 = min(self._start_y, event.y)
            x2 = max(self._start_x, event.x)
            y2 = max(self._start_y, event.y)
            w = x2 - x1
            h = y2 - y1
            if w > 10 and h > 10:
                self.result = (x1, y1, w, h)
                win.destroy()
            else:
                messagebox.showwarning(
                    "Too small",
                    "The selected region is too small. Please try again.",
                    parent=win,
                )

        canvas.bind("<ButtonPress-1>", on_press)
        canvas.bind("<B1-Motion>", on_drag)
        canvas.bind("<ButtonRelease-1>", on_release)

        # Keep reference so GC won't collect the image
        win._tk_img = tk_img  # noqa: SLF001
        win.wait_window()
        return self.result


class PointSelector:
    """
    Tkinter-based fullscreen overlay that lets the user click a single point
    and returns (x, y).
    """

    def __init__(self, root: tk.Tk, screenshot, instruction: str):
        self.root = root
        self.screenshot = screenshot
        self.instruction = instruction
        self.result: tuple | None = None

    def run(self) -> tuple | None:
        import PIL.ImageTk

        win = tk.Toplevel(self.root)
        win.attributes("-fullscreen", True)
        win.attributes("-topmost", True)
        win.configure(cursor="crosshair")

        tk_img = PIL.ImageTk.PhotoImage(self.screenshot)
        canvas = tk.Canvas(win, highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        canvas.create_image(0, 0, anchor=tk.NW, image=tk_img)

        lbl_text = self.instruction + "\n(Click once on the center of the button)"
        lbl = tk.Label(
            win,
            text=lbl_text,
            font=("Arial", 14, "bold"),
            bg="#222222",
            fg="#FFFFFF",
            padx=10,
            pady=6,
        )
        canvas.create_window(10, 10, anchor=tk.NW, window=lbl)

        cross_ids: list = []

        def on_click(event):
            # Draw a crosshair marker
            for cid in cross_ids:
                canvas.delete(cid)
            size = 12
            cross_ids.append(canvas.create_line(
                event.x - size, event.y, event.x + size, event.y,
                fill="#00FF44", width=2,
            ))
            cross_ids.append(canvas.create_line(
                event.x, event.y - size, event.x, event.y + size,
                fill="#00FF44", width=2,
            ))
            self.result = (event.x, event.y)
            # Give user 300 ms to see the marker, then close
            win.after(300, win.destroy)

        canvas.bind("<ButtonPress-1>", on_click)

        win._tk_img = tk_img  # noqa: SLF001
        win.wait_window()
        return self.result


# ── Main setup flow ──────────────────────────────────────────────────────────

def run_setup() -> None:
    """Walk the user through the interactive setup and save config.json."""
    config.load()

    root = tk.Tk()
    root.withdraw()  # Hide the main window — we only use Toplevel overlays

    logger.info("Starting interactive setup…")
    print("\n" + "=" * 60)
    print("  BTC Rocket Trader — First-Time Setup")
    print("=" * 60)
    print(
        "\nThis tool will guide you through selecting:\n"
        "  1. The SCAN REGION  — the bottom area of the chart where 🚀 rockets appear\n"
        "  2. The BUY button   — 🔵 blue BUY button (top-left of TradingView)\n"
        "  3. The SELL button  — 🔴 red SELL button (top-left of TradingView)\n"
        "  4. The CHART REGION — full chart area used for screenshots\n"
        "\nMake sure TradingView Desktop App is open and visible before continuing.\n"
    )
    input("Press ENTER when TradingView is ready… ")

    screenshot = _take_fullscreen_pil()

    # ── Step 1: Scan region ────────────────────────────────────────────────
    print("\n[Step 1/4] Draw a rectangle around the BOTTOM area of the chart")
    print("           where 🚀 rocket emojis appear below the candles.")
    sel = RegionSelector(root, screenshot, "Step 1/4 — Draw the SCAN REGION (where rockets appear)")
    scan_region = sel.run()
    if scan_region is None:
        print("Setup cancelled.")
        root.destroy()
        return
    print(f"  ✔ Scan region: {scan_region}")

    # ── Step 2: BUY button ────────────────────────────────────────────────
    print("\n[Step 2/4] Click the CENTER of the 🔵 BUY button (top-left of TradingView).")
    sel2 = PointSelector(root, screenshot, "Step 2/4 — Click the center of the 🔵 BUY button")
    buy_pos = sel2.run()
    if buy_pos is None:
        print("Setup cancelled.")
        root.destroy()
        return
    print(f"  ✔ BUY button position: {buy_pos}")

    # ── Step 3: SELL button ───────────────────────────────────────────────
    print("\n[Step 3/4] Click the CENTER of the 🔴 SELL button (top-left of TradingView).")
    sel3 = PointSelector(root, screenshot, "Step 3/4 — Click the center of the 🔴 SELL button")
    sell_pos = sel3.run()
    if sell_pos is None:
        print("Setup cancelled.")
        root.destroy()
        return
    print(f"  ✔ SELL button position: {sell_pos}")

    # ── Step 4: Chart region (for screenshots) ────────────────────────────
    print("\n[Step 4/4] Draw a rectangle around the FULL CHART AREA (the larger area")
    print("           you want captured in the screenshot sent to your phone).")
    sel4 = RegionSelector(root, screenshot, "Step 4/4 — Draw the CHART REGION (full chart for screenshots)")
    chart_region = sel4.run()
    if chart_region is None:
        print("Setup cancelled.")
        root.destroy()
        return
    print(f"  ✔ Chart region: {chart_region}")

    root.destroy()

    # ── Save to config ─────────────────────────────────────────────────────
    config.save({
        "SCAN_REGION": list(scan_region),
        "BUY_BUTTON_POS": list(buy_pos),
        "SELL_BUTTON_POS": list(sell_pos),
        "CHART_REGION": list(chart_region),
    })

    print("\n" + "=" * 60)
    print("  ✅ Setup complete!  Settings saved to config.json")
    print("=" * 60)
    print("\nYou can now run:  python main.py\n")


if __name__ == "__main__":
    try:
        run_setup()
    except KeyboardInterrupt:
        print("\nSetup interrupted by user.")
        sys.exit(0)
