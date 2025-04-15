# Inicjalizacja identyfikatora after
self.timer_id = None

# Wywołanie timera
self.timer_id = self.after(1000, self.update_timer)

# Dodanie metody end_turn
def end_turn(self):
    """Kończy podturę."""
    if self.timer_id:
        self.after_cancel(self.timer_id)  # Anulowanie zaplanowanego wywołania
    self.destroy()