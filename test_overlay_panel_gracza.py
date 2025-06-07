import tkinter as tk
from gui.panel_gracza import PanelGracza

def test_overlay_size():
    root = tk.Tk()
    root.title("Test overlay_frame size")
    panel = PanelGracza(root, "Test", "assets/mapa_globalna.jpg", None)
    panel.pack(pady=20, padx=20)

    def print_overlay_size():
        panel.overlay_frame.update_idletasks()
        width = panel.overlay_frame.winfo_width()
        height = panel.overlay_frame.winfo_height()
        print(f"Wymiary overlay_frame: {width}x{height}")
        root.destroy()

    root.after(500, print_overlay_size)
    root.mainloop()

if __name__ == "__main__":
    test_overlay_size()
