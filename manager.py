import tkinter as tk
from tkinter import font as tkFont
from datetime import datetime
import requests
import subprocess
import psutil
import threading

class SystemMonitorApp:
    def __init__(self, root):
        self.window = root
        self.window.title("System Stats, Weather, Time, and GPU Info Widget")
        self.window.overrideredirect(True)
        self.window.wm_attributes("-topmost", True)
        self.window.bind("<Button-1>", self.start_drag)
        self.window.bind("<B1-Motion>", self.drag_motion)

        # State variables
        self.CITY = "Wolverhampton"
        self.API_KEY = "Your-API"  # Replace with your actual API key: https://openweathermap.org
        self.prev_sent = 0
        self.prev_recv = 0

        # GUI Elements
        self.city_entry = tk.Entry(self.window, bg="#444444", fg="white")
        self.city_entry.insert(0, self.CITY)  # Pre-fill with the default city
        self.change_city_button = tk.Button(self.window, text="Change City", command=self.change_city, bg="#444444", fg="white")

        self.time_label = tk.Label(self.window)
        self.weather_label = tk.Label(self.window)
        self.system_label = tk.Label(self.window)
        self.gpu_label = tk.Label(self.window)

        self.apply_styles()  # Apply styles

        # Start updating functions in the background
        self.update_time()
        threading.Thread(target=self.update_weather).start()
        threading.Thread(target=self.update_system_stats).start()
        threading.Thread(target=self.update_gpu_temperature).start()

    def apply_styles(self):
        custom_font = tkFont.Font(family="Helvetica", size=10)
        self.window.config(bg='#333333')
        self.time_label.config(bg="#333333", fg="#ffffff", font=custom_font)
        self.weather_label.config(bg="#333333", fg="#ffffff", font=custom_font, justify="left")
        self.system_label.config(bg="#333333", fg="#ffffff", font=custom_font, justify="left")
        self.gpu_label.config(bg="#333333", fg="#ffffff", font=custom_font)

        close_button = tk.Button(self.window, text="X", command=self.window.destroy, bg="#ff4444", fg="white", borderwidth=0)
        close_button.pack(side="top", anchor="ne", padx=5, pady=5)

        self.time_label.pack(pady=5, padx=20)
        self.weather_label.pack(pady=5, padx=20)
        self.system_label.pack(pady=5, padx=20)
        self.gpu_label.pack(pady=5, padx=20)
        self.city_entry.pack(pady=5)
        self.change_city_button.pack(pady=5)
        self.window.attributes('-alpha', 0.85)
        self.window.geometry("380x520")  # Adjust height for additional information

    def update_time(self):
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.time_label.config(text=current_time)
        self.window.after(1000, self.update_time)

    def fetch_weather_data(self):
        base_url = f"http://api.openweathermap.org/data/2.5/weather?q={self.CITY}&appid={self.API_KEY}&units=metric"
        try:
            response = requests.get(base_url)
            if response.status_code == 200:
                return response.json()
        except requests.RequestException:
            pass
        return None

    def update_weather(self):
        weather_data = self.fetch_weather_data()
        if weather_data:
            self.display_weather_data(weather_data)
        else:
            self.weather_label.config(text="Error: Unable to fetch weather data.")
        self.window.after(600000, lambda: threading.Thread(target=self.update_weather).start())

    def display_weather_data(self, weather_data):
        city_name = weather_data['name']
        country = weather_data['sys']['country']
        temperature = weather_data['main']['temp']
        feels_like = weather_data['main']['feels_like']
        temp_min = weather_data['main']['temp_min']
        temp_max = weather_data['main']['temp_max']
        pressure = weather_data['main']['pressure']
        humidity = weather_data['main']['humidity']
        visibility = weather_data.get('visibility', 'N/A')
        wind_speed = weather_data['wind']['speed']
        wind_deg = weather_data['wind']['deg']
        clouds = weather_data['clouds']['all']
        description = weather_data['weather'][0]['description']
        sunrise = datetime.fromtimestamp(weather_data['sys']['sunrise']).strftime('%H:%M:%S')
        sunset = datetime.fromtimestamp(weather_data['sys']['sunset']).strftime('%H:%M:%S')

        weather_info = (
            f"Weather in {city_name}, {country}\n"
            f"Temperature: {temperature}°C (Feels like: {feels_like}°C)\n"
            f"Min Temp: {temp_min}°C, Max Temp: {temp_max}°C\n"
            f"Pressure: {pressure} hPa, Humidity: {humidity}%\n"
            f"Visibility: {visibility} meters\n"
            f"Wind: {wind_speed} m/s, Direction: {wind_deg}°\n"
            f"Cloudiness: {clouds}%\n"
            f"Condition: {description}\n"
            f"Sunrise: {sunrise}, Sunset: {sunset}"
        )
        self.weather_label.config(text=weather_info)

    def change_city(self):
        self.CITY = self.city_entry.get()
        self.update_weather()

    def update_system_stats(self):
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        swap_info = psutil.swap_memory()
        disk_usage = psutil.disk_usage('/')
        net_io = psutil.net_io_counters()

        sent = net_io.bytes_sent
        recv = net_io.bytes_recv
        sent_speed = (sent - self.prev_sent) * 8 / 1024  # Kbps
        recv_speed = (recv - self.prev_recv) * 8 / 1024  # Kbps
        self.prev_sent, self.prev_recv = sent, recv

        cpu_freq = psutil.cpu_freq().current
        total_memory = memory_info.total / (1024 ** 2)
        used_memory = memory_info.used / (1024 ** 2)
        total_swap = swap_info.total / (1024 ** 2)
        used_swap = swap_info.used / (1024 ** 2)
        total_disk = disk_usage.total / (1024 ** 3)
        used_disk = disk_usage.used / (1024 ** 3)

        disk_io = psutil.disk_io_counters()
        read_speed = disk_io.read_bytes / (1024 ** 2)
        write_speed = disk_io.write_bytes / (1024 ** 2)

        battery_info = psutil.sensors_battery()
        if battery_info:
            battery_percent = battery_info.percent
            is_charging = "Charging" if battery_info.power_plugged else "Not Charging"
            battery_status = f"Battery: {battery_percent}% ({is_charging})\n"
        else:
            battery_status = "Battery: Not Available\n"

        system_info = (
            f"CPU Usage: {cpu_usage}%\n"
            f"CPU Frequency: {cpu_freq:.2f} MHz\n"
            f"Memory Usage: {used_memory:.2f} MB / {total_memory:.2f} MB\n"
            f"Swap Usage: {used_swap:.2f} MB / {total_swap:.2f} MB\n"
            f"Disk Usage: {used_disk:.2f} GB / {total_disk:.2f} GB\n"
            f"Disk Read Speed: {read_speed:.2f} MB\n"
            f"Disk Write Speed: {write_speed:.2f} MB\n"
            f"Ethernet: Sent: {sent_speed:.2f} Kbps, Received: {recv_speed:.2f} Kbps\n"
            f"{battery_status}"
        )
        self.system_label.config(text=system_info)
        self.window.after(1000, lambda: threading.Thread(target=self.update_system_stats).start())

    def get_gpu_info(self):
        try:
            temp_result = subprocess.Popen(['nvidia-smi', '--query-gpu=temperature.gpu', '--format=csv,noheader,nounits'],
                                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            output, _ = temp_result.communicate()
            gpu_temp = output.decode('utf-8').strip()

            usage_result = subprocess.Popen(['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader,nounits'],
                                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            output, _ = usage_result.communicate()
            gpu_usage = output.decode('utf-8').strip()

            return f"GPU 0 Temperature: {gpu_temp}°C, Usage: {gpu_usage}%"
        except Exception as e:
            return "GPU Info: Not Available"

    def update_gpu_temperature(self):
        gpu_info = self.get_gpu_info()
        self.gpu_label.config(text=gpu_info)
        self.window.after(5000, self.update_gpu_temperature)

    def start_drag(self, event):
        self.drag_x = event.x
        self.drag_y = event.y

    def drag_motion(self, event):
        x = self.window.winfo_x() + event.x - self.drag_x
        y = self.window.winfo_y() + event.y - self.drag_y
        self.window.geometry(f"+{x}+{y}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SystemMonitorApp(root)
    root.mainloop()
