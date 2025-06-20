
import requests
import dropbox
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime

# === Dropbox Permanent Access Token ===
DROPBOX_ACCESS_TOKEN = "sl.u.AFxhCGTaG1eRcLZIilsaLx6ooEBdKiQQKvaT7v-CAPxaDjDn3aRTI9ont6EPS1-yqOHfTEHJ4CWXzz9LfH3AM5TBpLb74ONBOVppx6PllyccqtJtuWuCPUPUw6Kufgf8zvIvfc01iFv9nOFXVagjT4kumcQxNbetFXbQLRIPdb5Kt00_mNCQu-k_auYMAZEV3ZvSEP0CiJSVSU2-UkB_qLrl52Dftp4aGLU2gw2p3sZQli8gytsULHogqD0GYQu5e5ctPQFkukRkYWIfDWWtdtJt17Ts-YRdmAqodFvI8e5ZpQaHsVdZYcBu7WIHAFi97N1E_49uxBYMIT2SwXbFWpryPfyXquFi9bVl8c5uC8_tPIYORquy5jieRp5CAoLah8wvNA8AWxuek8Cjc41oZ8Gy1mX1HMHlM_Wr9RwJHS-JCxfy6-1a4vihwzWOcFWz8sUorrIWxlP5Fzw4LowMspB2-XLXmcHvt2Ctnl1B_Ly7WxQaloWbWm1QPpGY56it886Vy30RfoCwUI0oZ72plKJ0aPMnOF_LRe6HGOs-wEsibfz3RwZKiBUvKIl3i_WcjI_PTD93eBeIDf-opK3ts1j9t6FqwJq9TWMi1savjkejlsqOoHP6ClqN8AcJ_-cRtvg2U9zMfJBF5OLuc-NmMo8m4778U3peb97NwCsii_3V4vW7fY57sLJptMZu8hp1KSTkJPn9XQ0lnIO7CsQKnnPQy5CW2jNz6SCazaefkH6sCHod-xroJAYXMf19b-ZPJzjXEo3aFkj9xewv_hONsBEcU6Dw-WelDS6e9ByRTFCLtNICG0zzCvCZSFHJAlZfc2afGpWPZeYwOCSfChJFmHvtWMioidmHAlLiCMCKcPWPzlyE2Wxgwvuc75-4M3zqBhKMgBNqv-LOCr-PcdBu61EIWBZaNEjRcx-lxRUDEIvI_6A8eBOqUathse7BABWmfZMSEMGR3GPm8_f2PF0HHlW-sQovyVDk40liHaFvlcS5QHYAcd4CWh8puLySuKGdnSiahgcEUbBb1RLs8qRAzuaWfsm2O4nV8zhkmV67XDQO3UUkw_V8ffYrPenJccI02zXTsuJY_0Y8K36rpy87EN0jpZuLXKtoWU-5owtRCProoxAl-mK616MpXFVm9QGrJHL2HZG8PPrbi-rA0ZqYH6b_5i3CH60qb_9KLois8WvRFsjKwFDniupZFDXBRHzoRKG4j5QyKERCmEz5M_AvvnpSaiqq0V73Uru2gN7BnStqZhTCH7yMdGth8XOH2HZji9c"

# === NWS Forecast Endpoint ===
forecast_url = "https://api.weather.gov/gridpoints/DVN/61,73/forecast"

# === Files ===
TEMPLATE_IMAGE = "forecast_template.png"
OUTPUT_IMAGE = "miws_forecast.png"
ICON_FOLDER = "icons"

# === Icon Map ===
ICON_MAP = {
    'sunny': '32.png',
    'partly sunny': '30.png',
    'partly cloudy': '28.png',
    'mostly sunny': '34.png',
    'rain': '12.png',
    'showers': '12.png',
    'thunderstorm': '3.png',
    'snow': '13.png',
    'sleet': '35.png',
    'hail': '17.png',
    'fog': '19.png',
    'windy': '23.png',
    'cloudy': '26.png',
    'mostly cloudy': '28.png'
}

# === Get Forecast Data ===
def get_forecast():
    res = requests.get(forecast_url)
    res.raise_for_status()
    return res.json()['properties']['periods']

# === Draw Forecast Image ===
def draw_forecast(forecast):
    base = Image.open(TEMPLATE_IMAGE).convert("RGBA")
    draw = ImageDraw.Draw(base)
    font_large = ImageFont.load_default()
    font_small = ImageFont.load_default()

    x_start = 890
    spacing = 440
    y_day = 700
    y_icon = 800
    y_high = 1700

    daytime = [p for p in forecast if p['isDaytime']][:7]

    for i, period in enumerate(daytime):
        x = x_start + i * spacing
        day = datetime.fromisoformat(period['startTime']).strftime("%a")
        draw.text((x, y_day), day, font=font_small, fill="black", anchor="mm")

        key = period['shortForecast'].lower()
        icon_path = next((os.path.join(ICON_FOLDER, v) for k, v in ICON_MAP.items() if k in key), None)
        if icon_path and os.path.exists(icon_path):
            icon = Image.open(icon_path).resize((400, 400))
            base.paste(icon, (x - 200, y_icon), icon)

        temp = f"{period['temperature']}\u00b0"
        draw.text((x, y_high), temp, font=font_large, fill="black", anchor="mm")

    base.save(OUTPUT_IMAGE)

# === Upload to Dropbox ===
def upload_to_dropbox():
    dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
    with open(OUTPUT_IMAGE, 'rb') as f:
        dbx.files_upload(f.read(), f"/{OUTPUT_IMAGE}", mode=dropbox.files.WriteMode.overwrite)

# === Run ===
def main():
    try:
        forecast = get_forecast()
        draw_forecast(forecast)
        upload_to_dropbox()
        print(f"Forecast updated and uploaded at {datetime.now()}")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
