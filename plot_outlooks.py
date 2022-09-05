from zipfile import ZipFile
import numpy as np
from lxml import html
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle
import requests
import os.path
import matplotlib as mpl
import pandas as pd
from utils import StormReports

mpl.rcParams['hatch.linewidth'] = 0.2

# Colors used in the SPC outlooks
colors = dict({})
colors['TSTM'] = dict({'outline': '#646464', 'fill': '#C1E9C1'})  # General thunder
colors['MRGL'] = dict({'outline': '#3C783C', 'fill': '#80C580'})  # Marginal risk
colors['SLGT'] = dict({'outline': '#FF9600', 'fill': '#F7F780'})  # Slight risk
colors['ENH'] = dict({'outline': '#FF7F00', 'fill': '#E6C280'})  # Enhanced risk
colors['MDT'] = dict({'outline': '#CD0000', 'fill': '#E68080'})  # Moderate risk
colors['HIGH'] = dict({'outline': '#FF00FF', 'fill': '#FF80FF'})  # High risk
colors['TOR2'] = dict({'outline': '#008200', 'fill': '#80C580'})  # 2% tornado risk
colors['TOR5'] = dict({'outline': '#8B4726', 'fill': '#C5A393'})  # 5% tornado risk
colors['TOR10'] = dict({'outline': '#FF9600', 'fill': '#FFEB80'})  # 10% tornado risk
colors['TOR15'] = dict({'outline': '#FF0000', 'fill': '#FF8080'})  # 15% tornado risk
colors['TOR30'] = dict({'outline': '#FF00FF', 'fill': '#FF80FF'})  # 30% tornado risk
colors['TOR45'] = dict({'outline': '#912CEE', 'fill': '#C896F7'})  # 45% tornado risk
colors['TOR60'] = dict({'outline': '#083058', 'fill': '#104E8B'})  # 60% tornado risk
colors['WIND5'] = dict({'outline': '#8B4726', 'fill': '#C5A393'})  # 5% wind risk
colors['WIND15'] = dict({'outline': '#FF9600', 'fill': '#FFEB80'})  # 15% wind risk
colors['WIND30'] = dict({'outline': '#FF0000', 'fill': '#FF8080'})  # 30% wind risk
colors['WIND45'] = dict({'outline': '#FF00FF', 'fill': '#FF80FF'})  # 45% wind risk
colors['WIND60'] = dict({'outline': '#912CEE', 'fill': '#C896F7'})  # 60% wind risk
colors['HAIL5'] = dict({'outline': '#8B4726', 'fill': '#C5A393'})  # 5% hail risk
colors['HAIL15'] = dict({'outline': '#FF9600', 'fill': '#FFEB80'})  # 15% hail risk
colors['HAIL30'] = dict({'outline': '#FF0000', 'fill': '#FF8080'})  # 30% hail risk
colors['HAIL45'] = dict({'outline': '#FF00FF', 'fill': '#FF80FF'})  # 45% hail risk
colors['HAIL60'] = dict({'outline': '#912CEE', 'fill': '#C896F7'})  # 60% hail risk
colors['Elevated'] = dict({'outline': '#FF8000', 'fill': '#FFC081'})  # Elevated fire risk
colors['Critical'] = dict({'outline': '#FF0000', 'fill': '#FF8181'})  # Critical fire risk
colors['Extreme'] = dict({'outline': '#FF0000', 'fill': '#FF81FF'})  # Extreme fire risk
colors['Iso DryT'] = dict({'outline': '#8C4521', 'fill': 'None'})  # Isolated dry thunderstorm risk
colors['Scattered DryT'] = dict({'outline': '#F10E16', 'fill': 'None'})  # Scattered dry thunderstorm risk

# Sample polygons that will be used to make outlook legends
poly_TSTM = Polygon([[0, 0], [0, 0]], facecolor=colors['TSTM']['fill'], edgecolor=colors['TSTM']['outline'])  # General thunder
poly_MRGL = Polygon([[0, 0], [0, 0]], facecolor=colors['MRGL']['fill'], edgecolor=colors['MRGL']['outline'])  # Marginal risk
poly_SLGT = Polygon([[0, 0], [0, 0]], facecolor=colors['SLGT']['fill'], edgecolor=colors['SLGT']['outline'])  # Slight risk
poly_ENH = Polygon([[0, 0], [0, 0]], facecolor=colors['ENH']['fill'], edgecolor=colors['ENH']['outline'])  # Enhanced risk
poly_MDT = Polygon([[0, 0], [0, 0]], facecolor=colors['MDT']['fill'], edgecolor=colors['MDT']['outline'])  # Moderate risk
poly_HIGH = Polygon([[0, 0], [0, 0]], facecolor=colors['HIGH']['fill'], edgecolor=colors['HIGH']['outline'])  # High risk
poly_TOR2 = Polygon([[0, 0], [0, 0]], facecolor=colors['TOR2']['fill'], edgecolor=colors['TOR2']['outline'])  # 2% tornado risk
poly_TOR5 = Polygon([[0, 0], [0, 0]], facecolor=colors['TOR5']['fill'], edgecolor=colors['TOR5']['outline'])  # 5% tornado risk
poly_TOR10 = Polygon([[0, 0], [0, 0]], facecolor=colors['TOR10']['fill'], edgecolor=colors['TOR10']['outline'])  # 10% tornado risk
poly_TOR15 = Polygon([[0, 0], [0, 0]], facecolor=colors['TOR15']['fill'], edgecolor=colors['TOR15']['outline'])  # 15% tornado risk
poly_TOR30 = Polygon([[0, 0], [0, 0]], facecolor=colors['TOR30']['fill'], edgecolor=colors['TOR30']['outline'])  # 30% tornado risk
poly_TOR45 = Polygon([[0, 0], [0, 0]], facecolor=colors['TOR45']['fill'], edgecolor=colors['TOR45']['outline'])  # 45% tornado risk
poly_TOR60 = Polygon([[0, 0], [0, 0]], facecolor=colors['TOR60']['fill'], edgecolor=colors['TOR60']['outline'])  # 60% tornado risk
poly_SIGTOR = Polygon([[0, 0], [0, 0]], facecolor='None', edgecolor='#000000', hatch='//////////////')  # Significant tornado risk (10% EF2+)
poly_WIND5 = Polygon([[0, 0], [0, 0]], facecolor=colors['WIND5']['fill'], edgecolor=colors['WIND5']['outline'])  # 5% wind risk
poly_WIND15 = Polygon([[0, 0], [0, 0]], facecolor=colors['WIND15']['fill'], edgecolor=colors['WIND15']['outline'])  # 15% wind risk
poly_WIND30 = Polygon([[0, 0], [0, 0]], facecolor=colors['WIND30']['fill'], edgecolor=colors['WIND30']['outline'])  # 30% wind risk
poly_WIND45 = Polygon([[0, 0], [0, 0]], facecolor=colors['WIND45']['fill'], edgecolor=colors['WIND45']['outline'])  # 45% wind risk
poly_WIND60 = Polygon([[0, 0], [0, 0]], facecolor=colors['WIND60']['fill'], edgecolor=colors['WIND60']['outline'])  # 60% wind risk
poly_SIGWIND = Polygon([[0, 0], [0, 0]], facecolor='None', edgecolor='#000000', hatch='//////////////')  # Significant wind risk (10% ≥75mphs)
poly_HAIL5 = Polygon([[0, 0], [0, 0]], facecolor=colors['HAIL5']['fill'], edgecolor=colors['HAIL5']['outline'])  # 5% hail risk
poly_HAIL15 = Polygon([[0, 0], [0, 0]], facecolor=colors['HAIL15']['fill'], edgecolor=colors['HAIL15']['outline'])  # 15% hail risk
poly_HAIL30 = Polygon([[0, 0], [0, 0]], facecolor=colors['HAIL30']['fill'], edgecolor=colors['HAIL30']['outline'])  # 30% hail risk
poly_HAIL45 = Polygon([[0, 0], [0, 0]], facecolor=colors['HAIL45']['fill'], edgecolor=colors['HAIL45']['outline'])  # 45% hail risk
poly_HAIL60 = Polygon([[0, 0], [0, 0]], facecolor=colors['HAIL60']['fill'], edgecolor=colors['HAIL60']['outline'])  # 60% hail risk
poly_SIGHAIL = Polygon([[0, 0], [0, 0]], facecolor='None', edgecolor='#000000', hatch='//////////////')  # Significant hail risk (10% ≥2in diameter)
poly_ELEVATED = Polygon([[0, 0], [0, 0]], facecolor=colors['Elevated']['fill'], edgecolor=colors['Elevated']['outline'])  # Elevated fire risk
poly_CRITICAL = Polygon([[0, 0], [0, 0]], facecolor=colors['Critical']['fill'], edgecolor=colors['Critical']['outline'])  # Critical fire risk
poly_EXTREME = Polygon([[0, 0], [0, 0]], facecolor=colors['Extreme']['fill'], edgecolor=colors['Extreme']['outline'])  # Extreme fire risk
poly_ISODRYT = Polygon([[0, 0], [0, 0]], facecolor=colors['Iso DryT']['fill'], edgecolor=colors['Iso DryT']['outline'], linestyle='--', linewidth=0.7)  # Isolated dry thunderstorm risk
poly_SCATTEREDDRYT = Polygon([[0, 0], [0, 0]], facecolor=colors['Scattered DryT']['fill'], edgecolor=colors['Scattered DryT']['outline'], linestyle='--', linewidth=0.7)  # Scattered dry thunderstorm risk

valid_convective_outlook_times = [[1200, 1300, 1630, 2000, 100], [600, 1730], [730, ]]  # [[Day 1], [Day 2], [Day 3]]
valid_fire_outlook_times = [[1200, 1700], [1200, 2000]]  # [[Day 1], [Day 2]]


def plot_background(extent, ax=None, linewidth=0.4):
    """
    Returns new background for the plot.
    Parameters
    ----------
    extent: iterable with 4 ints
        - Iterable containing the extent/boundaries of the plot in the format of [min lon, max lon, min lat, max lat].
    ax: matplotlib.axes.Axes instance or None
        - Axis on which the background will be plotted.
    linewidth: float
        - Thickness of coastlines and the borders of states and countries.
    Returns
    -------
    ax: matplotlib.axes.Axes instance
        - New plot background.
    """
    if ax is None:
        crs = ccrs.Miller(central_longitude=250)
        ax = plt.axes(projection=crs)
    else:
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=linewidth, zorder=9, alpha=0.15)
        ax.add_feature(cfeature.BORDERS, linewidth=linewidth, zorder=9, alpha=0.15)
        ax.add_feature(cfeature.STATES, linewidth=linewidth, zorder=9, alpha=0.15)
        ax.set_extent(extent, crs=ccrs.PlateCarree())
    return ax


def categorical_convective_outlook(outlook_day, year, month, day, time=None, include_reports=False):
    """
    Plots and saves an SPC categorical convective outlook

    Parameters
    ----------
    outlook_day: int
        Outlook day.
    year: int
        YYYY
    month: int
        MM
    day: int
        DD
    time: int
        Time in UTC. HHMM
    include_reports: bool
        Include storm reports on top of the outlook.

    Raises
    ------
    ValueError
        - If 'time' is not valid for a given 'outlook_day'.
    """

    if 0 < outlook_day < 4:
        valid_times = valid_convective_outlook_times[outlook_day - 1]
        timestring = '_%04d' % time
        if time not in valid_times:
            valid_times = [str(x) for x in valid_times]
            raise ValueError(f"Day {outlook_day} convective outlooks are not released at %04d UTC. Valid times for day 1 "
                             f"convective outlooks: {', '.join(valid_times)}." % time)
    else:
        timestring = ''

    local_filename = f'day{outlook_day}otlk_{year}%02d%02d{timestring}.kmz' % (month, day)
    full_path = f'./outlooks/{local_filename}'

    if not os.path.isfile(full_path):
        link = f'https://www.spc.noaa.gov/products/outlook/archive/{year}/day{outlook_day}otlk_{year}%02d%02d{timestring}.kmz' % (month, day)
        outlook_file = requests.get(link)

        if outlook_file.status_code != 200:
            raise FileNotFoundError(f'{link} not found')
        with open(full_path, 'wb') as f:
            f.write(outlook_file.content)

    kmz = ZipFile(full_path, 'r')
    kml = kmz.open(local_filename.replace('kmz', 'kml'), 'r').read()

    doc = html.fromstring(kml)

    crs = ccrs.Miller(central_longitude=250)
    fig, ax = plt.subplots(1, 1, subplot_kw={'projection': crs})
    handles, labels = plt.gca().get_legend_handles_labels()

    pm = doc.cssselect('Folder')[0].cssselect('Placemark')  # Index 0 of the folders contains the categorical outlook data

    for i in range(len(pm)):

        extendeddata = pm[i].cssselect('extendeddata')[0].text_content()
        simpledata = pm[i].cssselect('simpledata')[0].text_content()
        coord_sets = pm[i].cssselect('coordinates')

        if 'General Thunder' in extendeddata or 'Marginal Risk' in extendeddata or 'Slight Risk' in extendeddata or 'Enhanced Risk' in extendeddata \
                or 'Moderate Risk' in extendeddata or 'High Risk' in extendeddata:

            if 'General Thunder' in extendeddata:
                zorder = 0
                polygon_colors = colors['TSTM']
            elif 'Marginal Risk' in extendeddata:
                zorder = 1
                polygon_colors = colors['MRGL']
            elif 'Slight Risk' in extendeddata:
                zorder = 2
                polygon_colors = colors['SLGT']
            elif 'Enhanced Risk' in extendeddata:
                zorder = 3
                polygon_colors = colors['ENH']
            elif 'Moderate Risk' in extendeddata:
                zorder = 4
                polygon_colors = colors['MDT']
            else:
                zorder = 5
                polygon_colors = colors['HIGH']

            for coord_set in coord_sets:
                coord_pairs = coord_set.text_content().split(' ')
                for coord_pair in range(len(coord_pairs)):
                    coord_pairs[coord_pair] = coord_pairs[coord_pair].split(',')
                coordinates = np.array(coord_pairs, dtype=float)
                poly = Polygon(coordinates, label=simpledata, facecolor=polygon_colors['fill'], edgecolor=polygon_colors['outline'], linewidth=0.5, zorder=zorder, transform=ccrs.PlateCarree())
                ax.add_patch(poly)

    # Add polygons + labels to the legend
    handles.extend([poly_TSTM]), labels.extend(['TSTM'])
    handles.extend([poly_MRGL]), labels.extend(['MRGL (1/5)'])
    handles.extend([poly_SLGT]), labels.extend(['SLGT (2/5)'])
    handles.extend([poly_ENH]), labels.extend(['ENH (3/5)'])
    handles.extend([poly_MDT]), labels.extend(['MDT (4/5)'])
    handles.extend([poly_HIGH]), labels.extend(['HIGH (5/5)'])

    plot_background([233, 295, 20, 50], ax=ax)  # Plot background on main subplot containing fronts and probabilities

    # capitals_excel = pd.read_excel('usa.xlsx')
    # capitals = capitals_excel['capital'].values
    # coordinates = capitals_excel[['lat', 'lon']].values
    #
    # for capital, coords in zip(capitals, coordinates):
    #     plt.plot(coords[1], coords[0], marker='o', markersize=0.5, color='red', transform=ccrs.PlateCarree())
    #     plt.text(coords[1], coords[0]+0.3, s=capital, ha='center', fontdict={'fontsize': 2.5}, transform=ccrs.PlateCarree())

    # Create fake reports at (0, 0) for each type of report so labels and points will appear in the legend (reports will not be visible or counted)

    if include_reports:

        storm_reports = StormReports(year, month, day)
        tornado_reports = storm_reports.load_tornado_reports(filtered=False)[['Lat', 'Lon']].values
        hail_reports = storm_reports.load_hail_reports(filtered=False)[['Size', 'Lat', 'Lon']]
        wind_reports = storm_reports.load_wind_reports(filtered=False)[['Speed', 'Lat', 'Lon']].replace(to_replace={'UNK': '58'})

        marker = 'o'
        facecolor = 'red'
        edgecolor = 'black'
        num_tornado_reports = 0
        for report in tornado_reports:
            plt.scatter(report[1], report[0], s=3, marker=marker, edgecolor=edgecolor, linewidth=0.2, facecolor=facecolor, transform=ccrs.PlateCarree(), zorder=15)
            num_tornado_reports += 1

        wind_reports['Speed'] = np.array(wind_reports['Speed'].values, dtype=int)
        wind_reports = wind_reports.values
        num_wind_reports = 0
        num_sigwind_reports = 0
        max_wind = int(np.max(wind_reports, axis=0)[0])
        for report in wind_reports:
            if report[0] < 75:
                marker = 'o'
                facecolor = 'blue'
                edgecolor = 'black'
                num_wind_reports += 1
                zorder = 11
                s = 3
            elif report[0] != max_wind:
                marker = 's'
                facecolor = 'black'
                edgecolor = 'gray'
                num_sigwind_reports += 1
                zorder = 12
                s = 4
            else:
                marker = '*'
                facecolor = 'blue'
                edgecolor = 'black'
                num_sigwind_reports += 1
                zorder = 13
                s = 10
            plt.scatter(report[2], report[1], s=s, marker=marker, edgecolor=edgecolor, linewidth=0.2, facecolor=facecolor, transform=ccrs.PlateCarree(), zorder=zorder)

        report_WIND = plt.scatter(0, 0, s=8, marker='o', edgecolor='black', linewidth=0.2, facecolor='blue', transform=ccrs.PlateCarree(), label=f'Wind ({num_wind_reports})')
        report_SIGWIND = plt.scatter(0, 0, s=10, marker='s', edgecolor='gray', linewidth=0.2, facecolor='black', transform=ccrs.PlateCarree(), label=f'Sig. Wind ({num_sigwind_reports})')
        report_MAXWIND = plt.scatter(0, 0, s=14, marker='*', edgecolor='black', linewidth=0.2, facecolor='blue', transform=ccrs.PlateCarree(), label=f'Highest wind report ({max_wind} mph)')

        hail_reports['Size'] = np.array(hail_reports['Size'].values, dtype=int)
        hail_reports = hail_reports.values
        num_hail_reports = 0
        num_sighail_reports = 0
        max_hail = np.round(np.max(hail_reports, axis=0)[0]/100, 2)
        for report in hail_reports:
            if report[0] < 200:
                marker = 'o'
                facecolor = 'green'
                edgecolor = 'black'
                num_hail_reports += 1
                zorder = 11
                size = 3
            elif report[0]/100 != max_hail:
                marker = '^'
                facecolor = 'black'
                edgecolor = 'gray'
                num_sighail_reports += 1
                zorder = 12
                size = 4
            else:
                marker = '*'
                facecolor = 'green'
                edgecolor = 'black'
                num_sighail_reports += 1
                zorder = 13
                size = 10
            plt.scatter(report[2], report[1], s=size, marker=marker, edgecolor=edgecolor, linewidth=0.2, facecolor=facecolor, transform=ccrs.PlateCarree(), zorder=zorder)
        report_HAIL = plt.scatter(0, 0, s=8, marker='o', edgecolor='black', linewidth=0.2, facecolor='green', transform=ccrs.PlateCarree(), label=f'Hail ({num_hail_reports})')
        report_SIGHAIL = plt.scatter(0, 0, s=10, marker='^', edgecolor='gray', linewidth=0.2, facecolor='black', transform=ccrs.PlateCarree(), label=f'Sig. Hail ({num_sighail_reports})')
        report_MAXHAIL = plt.scatter(0, 0, s=14, marker='*', edgecolor='black', linewidth=0.2, facecolor='green', transform=ccrs.PlateCarree(), label=f'Largest hail report ({max_hail}")')

        total_storm_reports = num_tornado_reports + num_hail_reports + num_sighail_reports + num_wind_reports + num_sigwind_reports

        report_TOR = plt.scatter(0, 0, s=8, marker='o', edgecolor='black', linewidth=0.2, facecolor='red', transform=ccrs.PlateCarree(), label=f'Tornado ({num_tornado_reports})')

        reports_legend = plt.legend(handles=[report_TOR, report_HAIL, report_WIND, report_SIGHAIL, report_SIGWIND, report_MAXHAIL, report_MAXWIND], loc='lower left', ncol=1, fontsize=4, title=f'Storm reports ({total_storm_reports})', title_fontsize=5)
        ax2 = plt.gca().add_artist(reports_legend)

    plt.legend(handles=handles, labels=labels, loc='lower right', ncol=3, fontsize=5, framealpha=1, title='Categorical risk', title_fontsize=7).set_zorder(10)
    ####################################################################################################################

    title_text = f'{year}-%02d-%02d %04d UTC Day {outlook_day} Convective Outlook' % (month, day, time)

    if time is not None:
        outlook_plot_file = f'day{outlook_day}otlk_{year}%02d%02d_%04d_cat.png' % (month, day, time)
    else:
        outlook_plot_file = f'day{outlook_day}otlk_{year}%02d%02d_cat.png' % (month, day)

    plt.title(title_text)
    plt.savefig(outlook_plot_file, bbox_inches='tight', dpi=1000)
    plt.close()


def tornado_outlook(outlook_day, year, month, day, time, include_reports=True):

    local_filename = f'day{outlook_day}otlk_{year}%02d%02d_%04d.kmz' % (month, day, time)
    full_path = f'./outlooks/{local_filename}'

    if not os.path.isfile(full_path):
        link = f'https://www.spc.noaa.gov/products/outlook/archive/{year}/day{outlook_day}otlk_{year}%02d%02d_%04d.kmz' % (month, day, time)
        outlook_file = requests.get(link)

        if outlook_file.status_code != 200:
            raise FileNotFoundError(f'{link} not found')
        with open(full_path, 'wb') as f:
            f.write(outlook_file.content)

    kmz = ZipFile(full_path, 'r')
    kml = kmz.open(local_filename.replace('kmz', 'kml'), 'r').read()

    doc = html.fromstring(kml)

    crs = ccrs.Miller(central_longitude=250)
    fig, ax = plt.subplots(1, 1, subplot_kw={'projection': crs})
    handles, labels = plt.gca().get_legend_handles_labels()

    folders = doc.cssselect('Folder')

    pm, pm_sig = None, None
    for folder in folders:
        if '_torn' in folder.cssselect('name')[0].text_content():
            pm = folder.cssselect('Placemark')
        if '_sigtorn' in folder.cssselect('name')[0].text_content():
            pm_sig = folder.cssselect('Placemark')

    if pm is None:
        raise ValueError(f"No tornado data found in {local_filename}")

    for i in range(len(pm)):
        name = pm[i].cssselect('name')[0].text_content()
        simpledata = pm[i].cssselect('simpledata')[0].text_content()
        coord_sets = pm[i].cssselect('coordinates')

        if name == '2 %':
            zorder = 0
            polygon_colors = colors['TOR2']
        elif name == '5 %':
            zorder = 1
            polygon_colors = colors['TOR5']
        elif name == '10 %':
            zorder = 2
            polygon_colors = colors['TOR10']
        elif name == '15 %':
            zorder = 3
            polygon_colors = colors['TOR15']
        elif name == '30 %':
            zorder = 4
            polygon_colors = colors['TOR30']
        elif name == '45 %':
            zorder = 5
            polygon_colors = colors['TOR45']
        else:
            zorder = 6
            polygon_colors = colors['TOR60']

        for coord_set in coord_sets:
            coord_pairs = coord_set.text_content().split(' ')
            for coord_pair in range(len(coord_pairs)):
                coord_pairs[coord_pair] = coord_pairs[coord_pair].split(',')
            coordinates = np.array(coord_pairs, dtype=float)
            poly = Polygon(coordinates, label=simpledata, facecolor=polygon_colors['fill'], edgecolor=polygon_colors['outline'], linewidth=0.5, zorder=zorder, transform=ccrs.PlateCarree())
            ax.add_patch(poly)

    if len(pm_sig) > 0:
        for j in range(len(pm_sig)):
            coord_sets = pm_sig[j].cssselect('coordinates')

            for coord_set in coord_sets:
                coord_pairs = coord_set.text_content().split(' ')
                for coord_pair in range(len(coord_pairs)):
                    coord_pairs[coord_pair] = coord_pairs[coord_pair].split(',')
                coordinates = np.array(coord_pairs, dtype=float)
                poly = Polygon(coordinates, facecolor='None', edgecolor='#000000', hatch='/////', linewidth=0.5, zorder=7, transform=ccrs.PlateCarree())
                ax.add_patch(poly)

    # capitals_excel = pd.read_excel('usa.xlsx')
    # capitals = capitals_excel['capital'].values
    # coordinates = capitals_excel[['lat', 'lon']].values
    #
    # for capital, coords in zip(capitals, coordinates):
    #     plt.plot(coords[1], coords[0], marker='o', markersize=0.5, color='red', transform=ccrs.PlateCarree())
    #     plt.text(coords[1], coords[0]+0.3, s=capital, ha='center', fontdict={'fontsize': 2.5}, transform=ccrs.PlateCarree())

    plot_background([233, 295, 20, 50], ax=ax)  # Plot background on main subplot containing fronts and probabilities

    marker = 'o'
    facecolor = 'red'
    edgecolor = 'black'

    if include_reports:
        num_tornado_reports = 0
        storm_reports = StormReports(year, month, day)
        tornado_reports = storm_reports.load_tornado_reports(filtered=False)[['Lat', 'Lon']].values

        for report in tornado_reports:
            num_tornado_reports += 1
            plt.scatter(report[1], report[0], s=3, marker=marker, edgecolor=edgecolor, linewidth=0.2, facecolor=facecolor, transform=ccrs.PlateCarree(), zorder=11)

        report_TOR = plt.scatter(0, 0, s=8, marker='o', edgecolor='black', linewidth=0.2, facecolor='red', transform=ccrs.PlateCarree(), label=f'Tornado reports ({num_tornado_reports})')

        reports_legend = plt.legend(handles=[report_TOR], loc='lower left', ncol=1, fontsize=5)
        ax2 = plt.gca().add_artist(reports_legend)

    # Add labels to the legend
    handles.extend([poly_TOR2]), labels.extend(['2%'])
    handles.extend([poly_TOR5]), labels.extend(['5%'])
    handles.extend([poly_TOR10]), labels.extend(['10%'])
    handles.extend([poly_TOR15]), labels.extend(['15%'])
    handles.extend([poly_TOR30]), labels.extend(['30%'])
    handles.extend([poly_TOR45]), labels.extend(['45%'])
    handles.extend([poly_TOR60]), labels.extend(['60%'])
    handles.extend([poly_SIGTOR]), labels.extend(['10% EF2+'])

    plt.legend(handles=handles, labels=labels, loc='lower right', ncol=4, fontsize=5, framealpha=1, title='Probability of a tornado within 25 miles of a point', title_fontsize=6).set_zorder(10)
    ####################################################################################################################

    title_text = f'{year}-%02d-%02d %04d UTC Day {outlook_day} Convective Outlook: Tornado' % (month, day, time)

    plt.title(title_text)
    plt.savefig(f'day{outlook_day}otlk_{year}%02d%02d_%04d_torn.png' % (month, day, time), bbox_inches='tight', dpi=1000)
    plt.close()


def wind_outlook(outlook_day, year, month, day, time, include_reports=False):

    local_filename = f'day{outlook_day}otlk_{year}%02d%02d_%04d.kmz' % (month, day, time)
    full_path = f'./outlooks/{local_filename}'

    if not os.path.isfile(full_path):
        link = f'https://www.spc.noaa.gov/products/outlook/archive/{year}/day{outlook_day}otlk_{year}%02d%02d_%04d.kmz' % (month, day, time)
        outlook_file = requests.get(link)

        if outlook_file.status_code != 200:
            raise FileNotFoundError(f'{link} not found')
        with open(full_path, 'wb') as f:
            f.write(outlook_file.content)

    kmz = ZipFile(full_path, 'r')
    kml = kmz.open(local_filename.replace('kmz', 'kml'), 'r').read()

    doc = html.fromstring(kml)

    crs = ccrs.Miller(central_longitude=250)
    fig, ax = plt.subplots(1, 1, subplot_kw={'projection': crs})
    handles, labels = plt.gca().get_legend_handles_labels()

    folders = doc.cssselect('Folder')
    pm_wind = folders[3].cssselect('Placemark')  # Wind placemarks
    pm_sigwind = folders[4].cssselect('Placemark')  # Sig wind placemarks

    if pm_wind is None:
        raise ValueError(f"No wind data found in {local_filename}")

    for i in range(len(pm_wind)):
        simpledata = pm_wind[i].cssselect('simpledata')[0].text_content()
        coord_sets = pm_wind[i].cssselect('coordinates')

        try:
            name = pm_wind[i].cssselect('name')[0].text_content()
        except:
            name = str(simpledata) + ' %'

        if name != '10 %':  # Ignore the significant wind risk area until later
            if name == '5 %':
                zorder = 0
                polygon_colors = colors['WIND5']
            elif name == '15 %':
                zorder = 1
                polygon_colors = colors['WIND15']
            elif name == '30 %':
                zorder = 2
                polygon_colors = colors['WIND30']
            elif name == '45 %':
                zorder = 3
                polygon_colors = colors['WIND45']
            elif name == '60 %':
                zorder = 4
                polygon_colors = colors['WIND60']
            else:
                raise ValueError(f"Unkown wind risk category: {name}")

            for coord_set in coord_sets:
                coord_pairs = coord_set.text_content().split(' ')
                for coord_pair in range(len(coord_pairs)):
                    coord_pairs[coord_pair] = coord_pairs[coord_pair].split(',')
                coordinates = np.array(coord_pairs, dtype=float)
                poly = Polygon(coordinates, label=simpledata, facecolor=polygon_colors['fill'], edgecolor=polygon_colors['outline'], linewidth=0.5, zorder=zorder, transform=ccrs.PlateCarree())
                ax.add_patch(poly)

    if len(pm_sigwind) > 0:
        for j in range(len(pm_sigwind)):
            coord_sets = pm_sigwind[j].cssselect('coordinates')

            for coord_set in coord_sets:
                coord_pairs = coord_set.text_content().split(' ')
                for coord_pair in range(len(coord_pairs)):
                    coord_pairs[coord_pair] = coord_pairs[coord_pair].split(',')
                coordinates = np.array(coord_pairs, dtype=float)
                poly = Polygon(coordinates, facecolor='None', edgecolor='#000000', hatch='/////', linewidth=0.5, zorder=7, transform=ccrs.PlateCarree())
                ax.add_patch(poly)

    # capitals_excel = pd.read_excel('usa.xlsx')
    # capitals = capitals_excel['capital'].values
    # coordinates = capitals_excel[['lat', 'lon']].values
    #
    # for capital, coords in zip(capitals, coordinates):
    #     plt.plot(coords[1], coords[0], marker='o', markersize=0.5, color='red', transform=ccrs.PlateCarree())
    #     plt.text(coords[1], coords[0]+0.3, s=capital, ha='center', fontdict={'fontsize': 2.5}, transform=ccrs.PlateCarree())

    plot_background([233, 295, 20, 50], ax=ax)  # Plot background on main subplot containing fronts and probabilities

    if include_reports:

        storm_reports = StormReports(year, month, day)
        wind_reports = storm_reports.load_wind_reports(filtered=False)[['Speed', 'Lat', 'Lon']].replace(to_replace={'UNK': '58'})
        wind_reports['Speed'] = np.array(wind_reports['Speed'].values, dtype=int)
        wind_reports = wind_reports.values
        num_wind_reports = 0
        num_sigwind_reports = 0
        max_wind = int(np.max(wind_reports, axis=0)[0])
        for report in wind_reports:
            if report[0] < 75:
                marker = 'o'
                facecolor = 'blue'
                edgecolor = 'black'
                num_wind_reports += 1
                zorder = 11
                s = 3
            elif report[0] != max_wind:
                marker = 's'
                facecolor = 'black'
                edgecolor = 'gray'
                num_sigwind_reports += 1
                zorder = 12
                s = 4
            else:
                marker = '*'
                facecolor = 'blue'
                edgecolor = 'black'
                num_sigwind_reports += 1
                zorder = 13
                s = 10
            plt.scatter(report[2], report[1], s=s, marker=marker, edgecolor=edgecolor, linewidth=0.2, facecolor=facecolor, transform=ccrs.PlateCarree(), zorder=zorder)

        report_WIND = plt.scatter(0, 0, s=8, marker='o', edgecolor='black', linewidth=0.2, facecolor='blue', transform=ccrs.PlateCarree(), label=f'Wind ({num_wind_reports})')
        report_SIGWIND = plt.scatter(0, 0, s=10, marker='s', edgecolor='gray', linewidth=0.2, facecolor='black', transform=ccrs.PlateCarree(), label=f'Sig. Wind ({num_sigwind_reports})')
        report_MAXWIND = plt.scatter(0, 0, s=14, marker='*', edgecolor='black', linewidth=0.2, facecolor='blue', transform=ccrs.PlateCarree(), label=f'Highest wind report ({max_wind} mph)')

        reports_legend = plt.legend(handles=[report_WIND, report_SIGWIND, report_MAXWIND], loc='lower left', ncol=1, fontsize=5, title=f'Wind reports ({num_wind_reports + num_sigwind_reports})', title_fontsize=6)
        ax2 = plt.gca().add_artist(reports_legend)

    # Add labels to the legend
    handles.extend([poly_WIND5]), labels.extend(['5%'])
    handles.extend([poly_WIND15]), labels.extend(['15%'])
    handles.extend([poly_WIND30]), labels.extend(['30%'])
    handles.extend([poly_WIND45]), labels.extend(['45%'])
    handles.extend([poly_WIND60]), labels.extend(['60%'])
    handles.extend([poly_SIGWIND]), labels.extend(['10% ≥ 75 mph'])

    plt.legend(handles=handles, labels=labels, loc='lower right', ncol=3, fontsize=5, framealpha=1, title='Probability of severe winds (≥ 58 mph) within 25 miles of a point', title_fontsize=4.5).set_zorder(10)
    ####################################################################################################################

    title_text = f'{year}-%02d-%02d %04d UTC Day {outlook_day} Convective Outlook: Wind' % (month, day, time)

    plt.title(title_text)
    plt.savefig(f'day{outlook_day}otlk_{year}%02d%02d_%04d_wind.png' % (month, day, time), bbox_inches='tight', dpi=1000)
    plt.close()


def hail_outlook(outlook_day, year, month, day, time, include_reports=False):

    local_filename = f'day{outlook_day}otlk_{year}%02d%02d_%04d.kmz' % (month, day, time)
    full_path = f'./outlooks/{local_filename}'

    if not os.path.isfile(full_path):
        link = f'https://www.spc.noaa.gov/products/outlook/archive/{year}/day{outlook_day}otlk_{year}%02d%02d_%04d.kmz' % (month, day, time)
        outlook_file = requests.get(link)

        if outlook_file.status_code != 200:
            raise FileNotFoundError(f'{link} not found')
        with open(full_path, 'wb') as f:
            f.write(outlook_file.content)

    kmz = ZipFile(full_path, 'r')
    kml = kmz.open(local_filename.replace('kmz', 'kml'), 'r').read()

    doc = html.fromstring(kml)

    crs = ccrs.Miller(central_longitude=250)
    fig, ax = plt.subplots(1, 1, subplot_kw={'projection': crs})
    handles, labels = plt.gca().get_legend_handles_labels()

    folders = doc.cssselect('Folder')
    pm_hail = folders[5].cssselect('Placemark')  # hail placemarks
    pm_sighail = folders[6].cssselect('Placemark')  # Sig hail placemarks

    if pm_hail is None:
        raise ValueError(f"No hail data found in {local_filename}")

    for i in range(len(pm_hail)):
        simpledata = pm_hail[i].cssselect('simpledata')[0].text_content()
        coord_sets = pm_hail[i].cssselect('coordinates')

        try:
            name = pm_hail[i].cssselect('name')[0].text_content()
        except:
            name = str(simpledata) + ' %'

        if name != '10 %' and name != '0 %':  # Ignore the significant hail polygon until later
            if name == '5 %':
                zorder = 0
                polygon_colors = colors['HAIL5']
            elif name == '15 %':
                zorder = 1
                polygon_colors = colors['HAIL15']
            elif name == '30 %':
                zorder = 2
                polygon_colors = colors['HAIL30']
            elif name == '45 %':
                zorder = 3
                polygon_colors = colors['HAIL45']
            elif name == '60 %':
                zorder = 4
                polygon_colors = colors['HAIL60']
            else:
                raise ValueError(f"Unknown hail risk category: {name}")

            for coord_set in coord_sets:
                coord_pairs = coord_set.text_content().split(' ')
                for coord_pair in range(len(coord_pairs)):
                    coord_pairs[coord_pair] = coord_pairs[coord_pair].split(',')
                coordinates = np.array(coord_pairs, dtype=float)
                poly = Polygon(coordinates, label=simpledata, facecolor=polygon_colors['fill'], edgecolor=polygon_colors['outline'], linewidth=0.5, zorder=zorder, transform=ccrs.PlateCarree())
                ax.add_patch(poly)

    if len(pm_sighail) > 0:
        for j in range(len(pm_sighail)):
            coord_sets = pm_sighail[j].cssselect('coordinates')

            for coord_set in coord_sets:
                coord_pairs = coord_set.text_content().split(' ')
                for coord_pair in range(len(coord_pairs)):
                    coord_pairs[coord_pair] = coord_pairs[coord_pair].split(',')
                coordinates = np.array(coord_pairs, dtype=float)
                poly = Polygon(coordinates, facecolor='None', edgecolor='#000000', hatch='/////', linewidth=0.5, zorder=7, transform=ccrs.PlateCarree())
                ax.add_patch(poly)

    # capitals_excel = pd.read_excel('usa.xlsx')
    # capitals = capitals_excel['capital'].values
    # coordinates = capitals_excel[['lat', 'lon']].values
    #
    # for capital, coords in zip(capitals, coordinates):
    #     plt.plot(coords[1], coords[0], marker='o', markersize=0.5, color='red', transform=ccrs.PlateCarree())
    #     plt.text(coords[1], coords[0]+0.3, s=capital, ha='center', fontdict={'fontsize': 2.5}, transform=ccrs.PlateCarree())

    plot_background([233, 295, 20, 50], ax=ax)  # Plot background on main subplot containing fronts and probabilities

    if include_reports:
        storm_reports = StormReports(year, month, day)
        hail_reports = storm_reports.load_hail_reports(filtered=False)[['Size', 'Lat', 'Lon']]
        hail_reports['Size'] = np.array(hail_reports['Size'].values, dtype=int)
        hail_reports = hail_reports.values
        num_hail_reports = 0
        num_sighail_reports = 0
        max_hail = np.round(np.max(hail_reports, axis=0)[0]/100, 2)
        for report in hail_reports:
            if report[0] < 200:
                marker = 'o'
                facecolor = 'green'
                edgecolor = 'black'
                num_hail_reports += 1
                zorder = 11
                size = 3
            elif report[0]/100 != max_hail:
                marker = '^'
                facecolor = 'black'
                edgecolor = 'gray'
                num_sighail_reports += 1
                zorder = 12
                size = 4
            else:
                marker = '*'
                facecolor = 'green'
                edgecolor = 'black'
                num_sighail_reports += 1
                zorder = 13
                size = 10
            plt.scatter(report[2], report[1], s=size, marker=marker, edgecolor=edgecolor, linewidth=0.2, facecolor=facecolor, transform=ccrs.PlateCarree(), zorder=zorder)
        report_HAIL = plt.scatter(0, 0, s=8, marker='o', edgecolor='black', linewidth=0.2, facecolor='green', transform=ccrs.PlateCarree(), label=f'Hail ({num_hail_reports})')
        report_SIGHAIL = plt.scatter(0, 0, s=10, marker='^', edgecolor='gray', linewidth=0.2, facecolor='black', transform=ccrs.PlateCarree(), label=f'Sig. Hail ({num_sighail_reports})')
        report_MAXHAIL = plt.scatter(0, 0, s=14, marker='*', edgecolor='black', linewidth=0.2, facecolor='green', transform=ccrs.PlateCarree(), label=f'Largest hail report ({max_hail}")')

        reports_legend = plt.legend(handles=[report_HAIL, report_SIGHAIL, report_MAXHAIL], loc='lower left', ncol=1, fontsize=5, title=f'Hail reports ({num_hail_reports + num_sighail_reports})', title_fontsize=6)
        ax2 = plt.gca().add_artist(reports_legend)

    # Add labels to the legend
    handles.extend([poly_HAIL5]), labels.extend(['5%'])
    handles.extend([poly_HAIL15]), labels.extend(['15%'])
    handles.extend([poly_HAIL30]), labels.extend(['30%'])
    handles.extend([poly_HAIL45]), labels.extend(['45%'])
    handles.extend([poly_HAIL60]), labels.extend(['60%'])
    handles.extend([poly_SIGHAIL]), labels.extend(['10% ≥ 2" diameter'])

    plt.legend(handles=handles, labels=labels, loc='lower right', ncol=3, fontsize=5, framealpha=1, title='Probability of severe hail (≥ 1" diameter) within 25 miles of a point', title_fontsize=4.5).set_zorder(10)
    ####################################################################################################################

    title_text = f'{year}-%02d-%02d %04d UTC Day {outlook_day} Convective Outlook: Hail' % (month, day, time)

    plt.title(title_text)
    plt.savefig(f'day{outlook_day}otlk_{year}%02d%02d_%04d_hail.png' % (month, day, time), bbox_inches='tight', dpi=1000)
    plt.close()


def fire_outlook(outlook_day, year, month, day, time):

    local_filename = '%s%02d%02d_%04d_day%dfirewx.kmz' % (str(year)[2:], month, day, time, outlook_day)
    full_path = f'./outlooks/{local_filename}'

    if not os.path.isfile(full_path):
        link = f'https://www.spc.noaa.gov/products/fire_wx/{year}/%s%02d%02d_%04d_day%dfirewx.kmz' % (str(year)[2:], month, day, time, outlook_day)
        outlook_file = requests.get(link)

        if outlook_file.status_code != 200:
            raise FileNotFoundError(f'{link} not found')
        with open(full_path, 'wb') as f:
            f.write(outlook_file.content)

    kmz = ZipFile(full_path, 'r')
    kml = kmz.open(local_filename.replace('kmz', 'kml'), 'r').read()

    doc = html.fromstring(kml)

    crs = ccrs.Miller(central_longitude=250)
    fig, ax = plt.subplots(1, 1, subplot_kw={'projection': crs})
    handles, labels = plt.gca().get_legend_handles_labels()

    folders = doc.cssselect('Folder')

    pm, pm_ltg = None, None
    for folder in folders:
        if 'dryltg' in folder.cssselect('name')[0].text_content():
            pm_ltg = folder.cssselect('Placemark')
        else:
            pm = folder.cssselect('Placemark')

    if pm is None and pm_ltg is None:
        raise ValueError(f"No fire data found in {local_filename}")

    if len(pm) > 1:
        for i in range(len(pm)):
            name = pm[i].cssselect('name')[0].text_content()
            simpledata = pm[i].cssselect('simpledata')[0].text_content()
            coord_sets = pm[i].cssselect('coordinates')

            if 'Elevated' in name:
                zorder = 0
                polygon_colors = colors['Elevated']
            elif 'Critical' in name:
                zorder = 1
                polygon_colors = colors['Critical']
            elif 'Extreme' in name:
                zorder = 2
                polygon_colors = colors['Extreme']

            for coord_set in coord_sets:
                coord_pairs = coord_set.text_content().split(' ')
                for coord_pair in range(len(coord_pairs)):
                    coord_pairs[coord_pair] = coord_pairs[coord_pair].split(',')
                coordinates = np.array(coord_pairs, dtype=float)
                poly = Polygon(coordinates, label=simpledata, facecolor=polygon_colors['fill'], edgecolor=polygon_colors['outline'], linewidth=0.5, zorder=zorder, transform=ccrs.PlateCarree())
                ax.add_patch(poly)

    if len(pm_ltg) > 1:
        for i in range(len(pm_ltg)):
            name = pm_ltg[i].cssselect('name')[0].text_content()
            simpledata = pm_ltg[i].cssselect('simpledata')[0].text_content()
            coord_sets = pm_ltg[i].cssselect('coordinates')

            if 'Isolated' in name:
                zorder = 3
                polygon_colors = colors['Iso DryT']
            elif 'Scattered' in name:
                zorder = 4
                polygon_colors = colors['Scattered DryT']

            for coord_set in coord_sets:
                coord_pairs = coord_set.text_content().split(' ')
                for coord_pair in range(len(coord_pairs)):
                    coord_pairs[coord_pair] = coord_pairs[coord_pair].split(',')
                coordinates = np.array(coord_pairs, dtype=float)
                poly = Polygon(coordinates, label=simpledata, facecolor=polygon_colors['fill'], edgecolor=polygon_colors['outline'], linewidth=0.7, zorder=zorder, transform=ccrs.PlateCarree(), linestyle='--')
                ax.add_patch(poly)

    plot_background([233, 295, 20, 50], ax=ax)  # Plot background on main subplot containing fronts and probabilities

    # Add labels to the legend
    handles.extend([poly_ELEVATED]), labels.extend(['Elevated'])
    handles.extend([poly_CRITICAL]), labels.extend(['Critical'])
    handles.extend([poly_EXTREME]), labels.extend(['Extreme'])
    handles.extend([poly_ISODRYT]), labels.extend(['Iso DryT'])
    handles.extend([poly_SCATTEREDDRYT]), labels.extend(['Scattered DryT'])

    plt.legend(handles=handles, labels=labels, loc='lower right', ncol=2, fontsize=5, framealpha=1, title='Fire outlook legend', title_fontsize=6).set_zorder(10)
    ####################################################################################################################

    title_text = f'{year}-%02d-%02d %04d UTC Day {outlook_day} Fire Weather Outlook' % (month, day, time)

    plt.title(title_text)
    plt.savefig(f'firewx_day{outlook_day}otlk_{year}%02d%02d_%04d.png' % (month, day, time), bbox_inches='tight', dpi=1000)
    plt.close()
