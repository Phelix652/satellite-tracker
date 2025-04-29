import requests
from skyfield.api import load, EarthSatellite
from skyfield.constants import AU_KM
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from mpl_toolkits.basemap import Basemap

# Your location coordinates
my_lat = 16.8409
my_lon = 96.1735

# --- Fetch TLE Data Functions ---
def get_tle_iss():
    url = "https://celestrak.org/NORAD/elements/stations.txt"
    response = requests.get(url)
    lines = response.text.strip().split("\n")
    for i in range(0, len(lines), 3):
        if "ISS (ZARYA)" in lines[i]:
            return lines[i], lines[i + 1], lines[i + 2]
    raise ValueError("ISS not found!")

def get_tle_noaa():
    url = "https://celestrak.org/NORAD/elements/weather.txt"
    response = requests.get(url)
    lines = response.text.strip().split("\n")
    for i in range(0, len(lines), 3):
        if "NOAA 15" in lines[i]:
            return lines[i], lines[i + 1], lines[i + 2]
    raise ValueError("NOAA 15 not found!")

def get_tle_tianmu():
    url = "https://celestrak.org/NORAD/elements/weather.txt"
    response = requests.get(url)
    lines = response.text.strip().split("\n")
    for i in range(0, len(lines), 3):
        if "TIANMU-1 14" in lines[i]:
            return lines[i], lines[i + 1], lines[i + 2]
    raise ValueError("TIANMU-1 14 not found!")

def get_tle_meteor():
    url = "https://celestrak.org/NORAD/elements/weather.txt"
    response = requests.get(url)
    lines = response.text.strip().split("\n")
    for i in range(0, len(lines), 3):
        if "METEOR-M 2 4" in lines[i] or "METEOR-M2 4" in lines[i]:
            return lines[i], lines[i + 1], lines[i + 2]
    raise ValueError("METEOR-M2 4 not found!")

# --- Load Satellites ---
ts = load.timescale()

name_iss, tle1_iss, tle2_iss = get_tle_iss()
sat_iss = EarthSatellite(tle1_iss, tle2_iss, name_iss, ts)

name_noaa, tle1_noaa, tle2_noaa = get_tle_noaa()
sat_noaa = EarthSatellite(tle1_noaa, tle2_noaa, name_noaa, ts)

name_tianmu, tle1_tianmu, tle2_tianmu = get_tle_tianmu()
sat_tianmu = EarthSatellite(tle1_tianmu, tle2_tianmu, name_tianmu, ts)

name_meteor, tle1_meteor, tle2_meteor = get_tle_meteor()
sat_meteor = EarthSatellite(tle1_meteor, tle2_meteor, name_meteor, ts)

# --- Get Satellite Position and Path ---
def get_satellite_data(satellite):
    time_now = ts.now()
    geocentric = satellite.at(time_now)
    subpoint = geocentric.subpoint()
    lat = subpoint.latitude.degrees
    lon = subpoint.longitude.degrees

    times = ts.utc(time_now.utc_datetime().year,
                   time_now.utc_datetime().month,
                   time_now.utc_datetime().day,
                   np.linspace(0, 24, 100))
    positions = [satellite.at(t).subpoint() for t in times]
    lats = [pos.latitude.degrees for pos in positions]
    lons = [pos.longitude.degrees for pos in positions]

    return lat, lon, lats, lons

# --- Create Map ---
fig, ax = plt.subplots(figsize=(12, 6))
m = Basemap(projection='cyl', resolution='c', ax=ax)
m.drawcoastlines()
m.drawcountries()
m.drawmapboundary(fill_color='midnightblue')
m.fillcontinents(color='forestgreen', lake_color='darkgreen')

satellites = []

# ISS
lat_iss, lon_iss, path_lats_iss, path_lons_iss = get_satellite_data(sat_iss)
x_iss, y_iss = m(lon_iss, lat_iss)
scatter_iss = ax.scatter(x_iss, y_iss, color='yellow', s=100, label=name_iss)
path_x_iss, path_y_iss = m(path_lons_iss, path_lats_iss)
path_line_iss, = ax.plot(path_x_iss, path_y_iss, linestyle='--', color='yellow', visible=False)
satellites.append({"scatter": scatter_iss, "path": path_line_iss})

# NOAA 15
lat_noaa, lon_noaa, path_lats_noaa, path_lons_noaa = get_satellite_data(sat_noaa)
x_noaa, y_noaa = m(lon_noaa, lat_noaa)
scatter_noaa = ax.scatter(x_noaa, y_noaa, color='red', s=100, label=name_noaa)
path_x_noaa, path_y_noaa = m(path_lons_noaa, path_lats_noaa)
path_line_noaa, = ax.plot(path_x_noaa, path_y_noaa, linestyle='--', color='red', visible=False)
satellites.append({"scatter": scatter_noaa, "path": path_line_noaa})

# TIANMU-1 14
lat_tianmu, lon_tianmu, path_lats_tianmu, path_lons_tianmu = get_satellite_data(sat_tianmu)
x_tianmu, y_tianmu = m(lon_tianmu, lat_tianmu)
scatter_tianmu = ax.scatter(x_tianmu, y_tianmu, color='magenta', s=100, label=name_tianmu)
path_x_tianmu, path_y_tianmu = m(path_lons_tianmu, path_lats_tianmu)
path_line_tianmu, = ax.plot(path_x_tianmu, path_y_tianmu, linestyle='--', color='magenta', visible=False)
satellites.append({"scatter": scatter_tianmu, "path": path_line_tianmu})

# METEOR-M2 4
lat_meteor, lon_meteor, path_lats_meteor, path_lons_meteor = get_satellite_data(sat_meteor)
x_meteor, y_meteor = m(lon_meteor, lat_meteor)
scatter_meteor = ax.scatter(x_meteor, y_meteor, color='lime', s=100, label=name_meteor)
path_x_meteor, path_y_meteor = m(path_lons_meteor, path_lats_meteor)
path_line_meteor, = ax.plot(path_x_meteor, path_y_meteor, linestyle='--', color='lime', visible=False)
satellites.append({"scatter": scatter_meteor, "path": path_line_meteor})

# Plot your location
x_my, y_my = m(my_lon, my_lat)
ax.scatter(x_my, y_my, color='white', marker='^', s=100, label="My Location")

# Tooltip annotation
tooltip = ax.annotate(
    "", xy=(0, 0), xytext=(20, 20), textcoords="offset points",
    bbox=dict(boxstyle="round,pad=0.5", fc="black", alpha=0.7),
    color='white', fontsize=9,
    arrowprops=dict(arrowstyle="->", color='white')
)
tooltip.set_visible(False)

# --- Hover Event to Show Paths + Tooltip ---
def on_hover(event):
    if event.inaxes == ax:
        show = False
        for i, sat in enumerate(satellites):
            cont, _ = sat["scatter"].contains(event)
            sat["path"].set_visible(cont)
            if cont:
                sat_obj = [sat_iss, sat_noaa, sat_tianmu, sat_meteor][i]
                time_now = ts.now()
                geocentric = sat_obj.at(time_now)
                subpoint = geocentric.subpoint()
                velocity = geocentric.velocity.km_per_s
                speed = np.linalg.norm(velocity)
                tooltip.xy = (event.xdata, event.ydata)
                tooltip.set_text(
                    f"{sat_obj.name}\nLat: {subpoint.latitude.degrees:.2f}°\n"
                    f"Lon: {subpoint.longitude.degrees:.2f}°\nAlt: {subpoint.elevation.km:.1f} km\n"
                    f"Speed: {speed:.2f} km/s"
                )
                tooltip.set_visible(True)
                show = True
        if not show:
            tooltip.set_visible(False)
        fig.canvas.draw_idle()

fig.canvas.mpl_connect('motion_notify_event', on_hover)

# --- Reload Button ---
def reload(event):
    for sat in satellites:
        sat["scatter"].remove()
        sat["path"].remove()
    satellites.clear()

    # ISS
    lat_iss, lon_iss, path_lats_iss, path_lons_iss = get_satellite_data(sat_iss)
    x_iss, y_iss = m(lon_iss, lat_iss)
    scatter_iss = ax.scatter(x_iss, y_iss, color='yellow', s=100, label=name_iss)
    path_x_iss, path_y_iss = m(path_lons_iss, path_lats_iss)
    path_line_iss, = ax.plot(path_x_iss, path_y_iss, linestyle='--', color='yellow', visible=False)
    satellites.append({"scatter": scatter_iss, "path": path_line_iss})

    # NOAA 15
    lat_noaa, lon_noaa, path_lats_noaa, path_lons_noaa = get_satellite_data(sat_noaa)
    x_noaa, y_noaa = m(lon_noaa, lat_noaa)
    scatter_noaa = ax.scatter(x_noaa, y_noaa, color='red', s=100, label=name_noaa)
    path_x_noaa, path_y_noaa = m(path_lons_noaa, path_lats_noaa)
    path_line_noaa, = ax.plot(path_x_noaa, path_y_noaa, linestyle='--', color='red', visible=False)
    satellites.append({"scatter": scatter_noaa, "path": path_line_noaa})

    # TIANMU-1 14
    lat_tianmu, lon_tianmu, path_lats_tianmu, path_lons_tianmu = get_satellite_data(sat_tianmu)
    x_tianmu, y_tianmu = m(lon_tianmu, lat_tianmu)
    scatter_tianmu = ax.scatter(x_tianmu, y_tianmu, color='magenta', s=100, label=name_tianmu)
    path_x_tianmu, path_y_tianmu = m(path_lons_tianmu, path_lats_tianmu)
    path_line_tianmu, = ax.plot(path_x_tianmu, path_y_tianmu, linestyle='--', color='magenta', visible=False)
    satellites.append({"scatter": scatter_tianmu, "path": path_line_tianmu})

    # METEOR-M2 4
    lat_meteor, lon_meteor, path_lats_meteor, path_lons_meteor = get_satellite_data(sat_meteor)
    x_meteor, y_meteor = m(lon_meteor, lat_meteor)
    scatter_meteor = ax.scatter(x_meteor, y_meteor, color='lime', s=100, label=name_meteor)
    path_x_meteor, path_y_meteor = m(path_lons_meteor, path_lats_meteor)
    path_line_meteor, = ax.plot(path_x_meteor, path_y_meteor, linestyle='--', color='lime', visible=False)
    satellites.append({"scatter": scatter_meteor, "path": path_line_meteor})

    # Plot your location again
    ax.scatter(x_my, y_my, color='white', marker='^', s=100, label="My Location")

    plt.draw()

# Button to reload
ax_button = plt.axes([0.81, 0.01, 0.15, 0.045])
button = Button(ax_button, 'Reload', color='white', hovercolor='grey')
button.on_clicked(reload)

# Legend with satellite names + your location
ax.legend(loc='lower left', fontsize=10, framealpha=0.7, edgecolor='white')

plt.show()
