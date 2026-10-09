import sys
try:
    # When stdout/stderr are redirected to a file (e.g. by the scheduled task's
    # .bat file), Python falls back to the console's codepage (cp1252 on most
    # Windows setups) instead of UTF-8. APOD responses often contain characters
    # outside cp1252 (curly quotes, em dashes, Greek letters, etc.), which made
    # print() crash and kill the whole run before the wallpaper got set.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import wallpaper_utility
class ToastNotifier:
    def show_toast(self, *args, **kwargs):
        pass
import glob
import os
from random import choice, shuffle
from PIL import Image


from apod_object_parser import download_image, getProperDirectoryPath, get_data, get_data_array, get_date, get_hdurl, get_media_type, is_connected

# NASA Astronomical Picture of the Day API Key. "DEMO_KEY" value works too but with 30 requests per hour
# still since we update our wallpaper less frequently we need not worry about the key

# NASA's APOD site is mid-migration to science.nasa.gov/apod, and since the
# move the API has sometimes been returning this generic site logo as the
# hdurl/url for the current day's entry instead of an actual photo. Treat it
# the same as a missing/broken hdurl and fall back to the archive.
PLACEHOLDER_URL_MARKERS = ("nasa-logo",)

def is_placeholder_image_url(url):
    if not url:
        return True
    lowered = url.lower()
    return any(marker in lowered for marker in PLACEHOLDER_URL_MARKERS)

MIN_SAVED_WIDTH = 800
MIN_SAVED_HEIGHT = 500

def startSetWallpaperProcedure():
    try:
        wallpaper_image_path = getWallpaperFromNasa()
    except Exception as e:
        print(f"Couldn't get a photo from NASA ({e}); using a previously saved one")
        wallpaper_image_path = getRandomSavedImage()

    print(wallpaper_image_path)
    wallpaper_utility.changeBG(wallpaper_image_path)
    n.show_toast(wallpaper_utility.SERVICE_NAME, "Wallpaper changed!", duration = 10)


def getWallpaperFromNasa():
    response = get_data(wallpaper_utility.APOD_API_KEY)
    print(response)
    media_type = get_media_type(response)

    if media_type == "image":
        try:
            # best case, we'll get a hd walpaper for the day.
            hd_url = get_hdurl(response)
            if is_placeholder_image_url(hd_url):
                raise ValueError(f"hdurl is a placeholder image, not today's photo: {hd_url}")
            return download_image(hd_url, get_date(response))
        except Exception as e:
            print(f"Today's photo didn't work out ({e}); falling back to archive")

    return getOneWorkingImageFromArchive(get_date(response))


def getRandomSavedImage():
    candidates = []
    for path in glob.glob(os.path.join(getProperDirectoryPath(), "*.png")):
        try:
            with Image.open(path) as image:
                width, height = image.size
                image.verify()
        except Exception:
            continue
        if width >= MIN_SAVED_WIDTH and height >= MIN_SAVED_HEIGHT:
            candidates.append(path)

    if not candidates:
        n.show_toast(wallpaper_utility.SERVICE_NAME, "No saved wallpapers available", duration = 10)
        raise RuntimeError("No usable saved images found to fall back on")
    return choice(candidates)


def getOneWorkingImageFromArchive(image_date):
    responses_array = get_data_array(wallpaper_utility.APOD_API_KEY)
    print("checking archives:")
    archive_hd_urls = []
    print(responses_array)

    for res in responses_array:
        try:
            hd_url = get_hdurl(res)
            if is_placeholder_image_url(hd_url):
                continue
            archive_hd_urls.append(hd_url)
        except:
            pass

    shuffle(archive_hd_urls)
    for hd_url in archive_hd_urls:
        try:
            # download_image also validates that the response is actually an
            # image (not an HTML error page or a 403), so a broken candidate
            # raises here and we just move on to the next one.
            return download_image(hd_url, image_date)
        except Exception as e:
            print(f"Archive candidate failed ({e}); trying another...")

    n.show_toast(wallpaper_utility.SERVICE_NAME, "Archive retrieval failed", duration = 10)
    raise RuntimeError("No archive image could be downloaded")

n = ToastNotifier()

if __name__ == "__main__":
    print("Program Started")
    if not is_connected() :
        print("Internet Not Connected")
        n.show_toast(wallpaper_utility.SERVICE_NAME, "Internet not connected")
    else:
        print("Internet is connected")
        startSetWallpaperProcedure()
