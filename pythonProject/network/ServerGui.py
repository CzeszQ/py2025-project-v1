import tkinter as tk
from tkinter import ttk, messagebox
from threading import Thread
import time
from server.Server import Server

class ServerGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Serwer TCP - GUI")
        self.master.geometry("800x500")

        self.server = None
        self.server_thread = None

        self.port_var = tk.StringVar(value="5000")
        self.status_var = tk.StringVar(value="Zatrzymano")

        self.sensor_data = {}

        self._create_widgets()
        self._update_table_loop()

    def _create_widgets(self):
        # Górny panel
        top_frame = ttk.Frame(self.master)
        top_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(top_frame, text="Port:").pack(side="left")
        ttk.Entry(top_frame, textvariable=self.port_var, width=10).pack(side="left", padx=5)
        ttk.Button(top_frame, text="Start", command=self.start_server).pack(side="left", padx=5)
        ttk.Button(top_frame, text="Stop", command=self.stop_server).pack(side="left", padx=5)

        # Środkowy panel - tabela
        columns = ("Sensor", "Last Value", "Unit", "Timestamp", "Avg 1h", "Avg 12h")
        self.tree = ttk.Treeview(self.master, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
        self.tree.pack(expand=True, fill="both", padx=10, pady=5)

        # Dolny panel - status
        status_frame = ttk.Frame(self.master)
        status_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(status_frame, textvariable=self.status_var).pack(side="left")

    def start_server(self):
        if self.server:
            messagebox.showinfo("Info", "Serwer już działa")
            return

        try:
            port = int(self.port_var.get())
            self.server = Server(port)
            self.server.on_new_reading = self._on_new_reading
            self.server.on_status_change = self._on_status_change

            self.server_thread = Thread(target=self.server.start, daemon=True)
            self.server_thread.start()
        except Exception as e:
            messagebox.showerror("Błąd", str(e))

    def stop_server(self):
        if self.server:
            self.server.stop()
            self.server = None

    def _on_new_reading(self, reading):
        self.sensor_data[reading['sensor_id']] = reading

    def _on_status_change(self, status):
        self.status_var.set(status)

    def _update_table_loop(self):
        self._refresh_table()
        self.master.after(5000, self._update_table_loop)

    def _refresh_table(self):
        if self.server:
            stats = self.server.get_sensor_stats()
            self.tree.delete(*self.tree.get_children())
            for stat in stats:
                self.tree.insert("", "end", values=(
                    stat['sensor'],
                    stat['last_value'],
                    stat['unit'],
                    stat['timestamp'],
                    stat['avg_1h'],
                    stat['avg_12h']
                ))

if __name__ == "__main__":
    root = tk.Tk()
    app = ServerGUI(root)
    root.mainloop()
