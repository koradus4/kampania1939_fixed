import tkinter as tk
from tkinter import messagebox
from pathlib import Path

class DeployNewTokensWindow(tk.Toplevel):
    def __init__(self, parent, gracz):
        super().__init__(parent)
        self.gracz = gracz
        self.title(f"Wystawianie nowych jednostek – Dowódca {gracz.id} ({gracz.nation})")
        self.geometry("200x200")
        self.configure(bg="darkolivegreen")
        # Jeden panel na miniatury żetonów (bez panelu mapy)
        self.main_frame = tk.Frame(self, bg="darkolivegreen")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        # Scrollowany panel na miniatury (ale widocznych max 5 żetonów)
        self.tokens_canvas = tk.Canvas(self.main_frame, bg="#556B2F", highlightthickness=0, height=80*5)
        self.tokens_scrollbar = tk.Scrollbar(self.main_frame, orient="vertical", command=self.tokens_canvas.yview)
        self.tokens_frame = tk.Frame(self.tokens_canvas, bg="#556B2F")
        self.tokens_frame.bind(
            "<Configure>", lambda e: self.tokens_canvas.configure(scrollregion=self.tokens_canvas.bbox("all"))
        )
        self.tokens_canvas.create_window((0, 0), window=self.tokens_frame, anchor="nw")
        self.tokens_canvas.configure(yscrollcommand=self.tokens_scrollbar.set)
        self.tokens_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.tokens_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._load_new_tokens()
        # Przycisk zamknięcia
        tk.Button(self.main_frame, text="Zamknij", command=self.destroy, bg="saddlebrown", fg="white", font=("Arial", 12, "bold")).pack(pady=10, fill=tk.X)

    def _load_new_tokens(self):
        from PIL import Image, ImageTk
        folder = Path(f"assets/tokens/nowe_dla_{self.gracz.id}/")
        for widget in self.tokens_frame.winfo_children():
            widget.destroy()
        if not folder.exists():
            tk.Label(self.tokens_frame, text="Brak nowych żetonów.", bg="#556B2F", fg="white", font=("Arial", 11, "italic")).pack(pady=5)
            return
        found = False
        count = 0
        for sub in folder.iterdir():
            if sub.is_dir() and (sub / "token.json").exists():
                found = True
                img_path = sub / "token.png"
                if img_path.exists():
                    try:
                        img = Image.open(img_path).resize((60, 60), Image.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                    except Exception:
                        photo = None
                else:
                    photo = None
                if photo:
                    lbl_img = tk.Label(self.tokens_frame, image=photo, bg="#556B2F")
                    lbl_img.image = photo  # referencja!
                    lbl_img.pack(padx=8, pady=8)
                else:
                    tk.Label(self.tokens_frame, text="(brak miniatury)", bg="#556B2F", fg="gray").pack(padx=8, pady=16)
                count += 1
                if count >= 5:
                    break
        if not found:
            tk.Label(self.tokens_frame, text="Brak nowych żetonów.", bg="#556B2F", fg="white", font=("Arial", 11, "italic")).pack(pady=5)
