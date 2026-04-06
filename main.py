#pip install pillow

import requests
import datetime as dt
import tkinter as tk
from tkinter import scrolledtext
from PIL import Image, ImageTk

MBTA_url = (
    "https://api-v3.mbta.com/predictions?page%5Blimit%5D=6&sort=departure_time&fields%5Bprediction%5D=departure_time&filter%5Broute_type%5D=1&filter%5Bstop%5D=place-rugg&filter%5Broute%5D=Orange&filter%5Brevenue%5D=REVENUE&api_key=c0b3c16e2a1542af80fbe2a551abe811"
)

EMPTY_JSON = {"data": [], "jsonapi": {"version": "1.0"}}

#FB_DEVICE = "/dev/fb0"

class TrainPredict:
    def __init__(self, root):

        self.root = root
        self.root.title("OrangeLinePredict")
        self.root.geometry("320x240")
        self.root.resizable(0, 0)
        self.dVerify = ""
        self.create_widgets()
        self.poll()

    def poll(self):
        self.log_text.delete("1.0", tk.END)
        today = dt.datetime.today()
        weekday = today.weekday()

        try:
            response = requests.get(MBTA_url, timeout=10)
        except requests.RequestException:
            self.log("Connection error, retrying in 60 seconds...")
            self.root.after(60_000, self.poll)
            return

        if response.status_code != 200:
            self.log(f"Bad status {response.status_code}, retrying in 60 seconds...")
            self.root.after(60_000, self.poll)
            return

        data = response.json()

        if data == EMPTY_JSON:
            self.log("No prediction available for today.")
            if weekday <= 4:
                self.log("First Oak Grove train at 05:23 \nFirst Forest Hills train at 05:39")
            elif weekday == 5:
                self.log("First Oak Grove train at 05:23 \nFirst Forest Hills train at 05:40")
            else:
                self.log("First Oak Grove train at 06:08 \nFirst Forest Hills train at 06:25")
            self.root.after(60_000, self.poll)
            return

        time_now = today.strftime("%Y-%m-%d %H:%M:%S")

        for item in data["data"]:
            departure_time = item.get("attributes", {}).get("departure_time")
            if not departure_time: continue

            date, rest = departure_time.split("T")
            time_part = rest.split("-")[0]
            departure = f"{data} {time_part}"

            if departure <= time_now: continue

            direction_id = item.get("id", "").split("-")[3] if item.get("id") else ""
            direction = "Forest Hills" if direction_id == "140" else "Oak Grove"

            if self.dVerify != date:
                self.dVerify = date
                self.log(f"{date} \n{time_part}    {direction}")
            else:
                self.log(f"{time_part}    {direction}")

        self.dVerify = ""

        self.root.after(5_000, self.poll)

    def create_widgets(self):

        title = tk.Label(self.root, text = "Orange Line - Ruggles", font = ("Arial", 14, "bold"), bg = "#ed8b00", fg = "white", pady = 10)
        title.pack(fill = "x")

        frame = tk.Frame(self.root, padx = 20, pady = 10)
        frame.pack(fill = "both", expand = True)

        try:
            img = Image.open("MBTA.png").resize((40,40))
            self.logo = ImageTk.PhotoImage(img)
            tk.Label(title, image = self.logo, bg = "#ed8b00").pack(side = "left", padx = 8, pady = 5)
        except Exception:
            pass

        tk.Label(frame, text = "Predicted Train Departures", font = ("Arial", 14, "bold")).pack(anchor = "w")

        self.log_text = scrolledtext.ScrolledText(frame, height = 10, width = 70)
        self.log_text.pack(fill = "both", expand = True)

    def log(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

def main():
    root = tk.Tk()
    TrainPredict(root)
    root.mainloop()

if __name__ == "__main__":
    main()