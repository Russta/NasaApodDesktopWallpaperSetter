import ctypes
import os

# NASA APOD API Key. Set your own via the APOD_API_KEY environment variable
# (get one at https://api.nasa.gov/); "DEMO_KEY" works too but is limited to
# 30 requests/hour.
APOD_API_KEY = os.environ.get("APOD_API_KEY", "DEMO_KEY")
SERVICE_NAME = "NASA Wallpaper"

# constant to work with windows 
SPI_SETDESKWALLPAPER = 20
# changes the wallpaper of our system
def changeBG(path):
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, path, 3)