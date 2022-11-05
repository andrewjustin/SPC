from zipfile import ZipFile
import numpy as np
from lxml import html
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import requests
import os.path
import utils
import settings


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


def categorical_convective_outlook(outlook_day, year, month, day, time, outlook_kmz_dir, image_dir, include_reports=False, filtered_reports=False,
    remove_unknowns=False):
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
    outlook_kmz_dir: str
        Directory where the outlook kmz files will be stored.
    image_dir: str
        Directory where the images will be stored.
    include_reports: bool
        Include storm reports on top of the outlook.

    Raises
    ------
    ValueError
        - If 'time' is not valid for a given 'outlook_day'.
    """

    if 0 < outlook_day < 4:
        valid_times = settings.valid_convective_outlook_times[outlook_day - 1]
        timestring = '_%04d' % time
        if time not in valid_times:
            valid_times = [str(x) for x in valid_times]
            raise ValueError(f"Day {outlook_day} convective outlooks are not released at %04d UTC. Valid times for day 1 "
                             f"convective outlooks: {', '.join(valid_times)}." % time)
    else:
        timestring = ''

    local_filename = f'day{outlook_day}otlk_{year}%02d%02d{timestring}.kmz' % (month, day)
    full_path = f'{outlook_kmz_dir}/{local_filename}'

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
                polygon_colors = settings.colors['TSTM']
            elif 'Marginal Risk' in extendeddata:
                zorder = 1
                polygon_colors = settings.colors['MRGL']
            elif 'Slight Risk' in extendeddata:
                zorder = 2
                polygon_colors = settings.colors['SLGT']
            elif 'Enhanced Risk' in extendeddata:
                zorder = 3
                polygon_colors = settings.colors['ENH']
            elif 'Moderate Risk' in extendeddata:
                zorder = 4
                polygon_colors = settings.colors['MDT']
            else:
                zorder = 5
                polygon_colors = settings.colors['HIGH']

            for coord_set in coord_sets:
                coord_pairs = coord_set.text_content().split(' ')
                for coord_pair in range(len(coord_pairs)):
                    coord_pairs[coord_pair] = coord_pairs[coord_pair].split(',')
                coordinates = np.array(coord_pairs, dtype=float)
                poly = Polygon(coordinates, label=simpledata, facecolor=polygon_colors['fill'], edgecolor=polygon_colors['outline'], linewidth=0.5, zorder=zorder, transform=ccrs.PlateCarree())
                ax.add_patch(poly)

    # Add polygons + labels to the legend
    handles.extend([utils.poly_TSTM]), labels.extend(['TSTM'])
    handles.extend([utils.poly_MRGL]), labels.extend(['MRGL (1/5)'])
    handles.extend([utils.poly_SLGT]), labels.extend(['SLGT (2/5)'])
    handles.extend([utils.poly_ENH]), labels.extend(['ENH (3/5)'])
    handles.extend([utils.poly_MDT]), labels.extend(['MDT (4/5)'])
    handles.extend([utils.poly_HIGH]), labels.extend(['HIGH (5/5)'])

    plot_background([233, 295, 20, 50], ax=ax)  # Plot background on main subplot containing fronts and probabilities

    if include_reports:

        storm_reports = utils.StormReports(year, month, day)
        tornado_reports = storm_reports.load_tornado_reports(filtered=filtered_reports)[['Lat', 'Lon']].values
        hail_reports = storm_reports.load_hail_reports(filtered=filtered_reports)[['Size', 'Lat', 'Lon']]
        wind_reports = storm_reports.load_wind_reports(filtered=filtered_reports)[['Speed', 'Lat', 'Lon']]

        marker = 'o'
        facecolor = 'red'
        edgecolor = 'black'
        num_tornado_reports = 0
        for report in tornado_reports:
            plt.scatter(report[1], report[0], s=3, marker=marker, edgecolor=edgecolor, linewidth=0.2, facecolor=facecolor, transform=ccrs.PlateCarree(), zorder=15)
            num_tornado_reports += 1

        if remove_unknowns:
            wind_reports = wind_reports[wind_reports['Speed'] != 'UNK']
        else:
            wind_reports = wind_reports.replace(to_replace={'UNK': '58'})

        wind_reports['Speed'] = np.array(wind_reports['Speed'].values, dtype=int)
        wind_reports_values = wind_reports.values
        num_wind_reports = 0
        num_sigwind_reports = 0
        max_wind = int(np.max(wind_reports_values))
        for report in wind_reports_values:
            if report[0] == max_wind:
                marker = '*'
                facecolor = 'blue'
                edgecolor = 'black'
                num_sigwind_reports += 1
                zorder = 13
                s = 10
            elif report[0] > 74:
                marker = 's'
                facecolor = 'black'
                edgecolor = 'gray'
                num_sigwind_reports += 1
                zorder = 12
                s = 4
            else:
                marker = 'o'
                facecolor = 'blue'
                edgecolor = 'black'
                num_wind_reports += 1
                zorder = 11
                s = 3
            plt.scatter(report[2], report[1], s=s, marker=marker, edgecolor=edgecolor, linewidth=0.2, facecolor=facecolor, transform=ccrs.PlateCarree(), zorder=zorder)

        wind_report_label = f'Wind ({num_wind_reports})'
        if remove_unknowns:
            wind_report_label += '*'

        report_WIND = plt.scatter(0, 0, s=8, marker='o', edgecolor='black', linewidth=0.2, facecolor='blue', transform=ccrs.PlateCarree(), label=wind_report_label)
        report_SIGWIND = plt.scatter(0, 0, s=10, marker='s', edgecolor='gray', linewidth=0.2, facecolor='black', transform=ccrs.PlateCarree(), label=f'Sig. Wind ({num_sigwind_reports})')
        report_MAXWIND = plt.scatter(0, 0, s=14, marker='*', edgecolor='black', linewidth=0.2, facecolor='blue', transform=ccrs.PlateCarree(), label=f'Highest wind report ({max_wind} mph)')

        if remove_unknowns:
            plt.text(-16, 19.5, '* wind reports only include measured or estimated winds (no UNK reports)', fontdict={'fontsize': 4})

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

        if filtered_reports:
            report_legend_title = f'Filtered storm reports ({total_storm_reports})'
        else:
            report_legend_title = f'Storm reports ({total_storm_reports})'

        reports_legend = plt.legend(handles=[report_TOR, report_HAIL, report_WIND, report_SIGHAIL, report_SIGWIND, report_MAXHAIL, report_MAXWIND], loc='lower left', ncol=1, fontsize=4, title=report_legend_title, title_fontsize=5)
        plt.gca().add_artist(reports_legend)

    plt.legend(handles=handles, labels=labels, loc='lower right', ncol=3, fontsize=5, framealpha=1, title='Categorical risk', title_fontsize=7).set_zorder(10)
    ####################################################################################################################

    title_text = f'{year}-%02d-%02d %04d UTC Day {outlook_day} Convective Outlook' % (month, day, time)

    if time is not None:
        outlook_plot_file = f'{image_dir}/day{outlook_day}otlk_{year}%02d%02d_%04d_cat.png' % (month, day, time)
    else:
        outlook_plot_file = f'{image_dir}/day{outlook_day}otlk_{year}%02d%02d_cat.png' % (month, day)

    plt.title(title_text)
    plt.savefig(outlook_plot_file, bbox_inches='tight', dpi=1000)
    plt.close()


def tornado_outlook(outlook_day, year, month, day, time, outlook_kmz_dir, image_dir, include_reports=True):

    local_filename = f'day{outlook_day}otlk_{year}%02d%02d_%04d.kmz' % (month, day, time)
    full_path = f'{outlook_kmz_dir}/{local_filename}'

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
            polygon_colors = settings.colors['TOR2']
        elif name == '5 %':
            zorder = 1
            polygon_colors = settings.colors['TOR5']
        elif name == '10 %':
            zorder = 2
            polygon_colors = settings.colors['TOR10']
        elif name == '15 %':
            zorder = 3
            polygon_colors = settings.colors['TOR15']
        elif name == '30 %':
            zorder = 4
            polygon_colors = settings.colors['TOR30']
        elif name == '45 %':
            zorder = 5
            polygon_colors = settings.colors['TOR45']
        else:
            zorder = 6
            polygon_colors = settings.colors['TOR60']

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

    plot_background([233, 295, 20, 50], ax=ax)  # Plot background on main subplot containing fronts and probabilities

    marker = 'o'
    facecolor = 'red'
    edgecolor = 'black'

    if include_reports:
        num_tornado_reports = 0
        storm_reports = utils.StormReports(year, month, day)
        tornado_reports = storm_reports.load_tornado_reports(filtered=False)[['Lat', 'Lon']].values

        for report in tornado_reports:
            num_tornado_reports += 1
            plt.scatter(report[1], report[0], s=3, marker=marker, edgecolor=edgecolor, linewidth=0.2, facecolor=facecolor, transform=ccrs.PlateCarree(), zorder=11)

        report_TOR = plt.scatter(0, 0, s=8, marker='o', edgecolor='black', linewidth=0.2, facecolor='red', transform=ccrs.PlateCarree(), label=f'Tornado reports ({num_tornado_reports})')

        reports_legend = plt.legend(handles=[report_TOR], loc='lower left', ncol=1, fontsize=5)
        plt.gca().add_artist(reports_legend)

    # Add labels to the legend
    handles.extend([utils.poly_TOR2]), labels.extend(['2%'])
    handles.extend([utils.poly_TOR5]), labels.extend(['5%'])
    handles.extend([utils.poly_TOR10]), labels.extend(['10%'])
    handles.extend([utils.poly_TOR15]), labels.extend(['15%'])
    handles.extend([utils.poly_TOR30]), labels.extend(['30%'])
    handles.extend([utils.poly_TOR45]), labels.extend(['45%'])
    handles.extend([utils.poly_TOR60]), labels.extend(['60%'])
    handles.extend([utils.poly_SIGTOR]), labels.extend(['10% EF2+'])

    plt.legend(handles=handles, labels=labels, loc='lower right', ncol=4, fontsize=5, framealpha=1, title='Probability of a tornado within 25 miles of a point', title_fontsize=6).set_zorder(10)
    ####################################################################################################################

    title_text = f'{year}-%02d-%02d %04d UTC Day {outlook_day} Convective Outlook: Tornado' % (month, day, time)

    plt.title(title_text)
    plt.savefig(f'{image_dir}/day{outlook_day}otlk_{year}%02d%02d_%04d_torn.png' % (month, day, time), bbox_inches='tight', dpi=1000)
    plt.close()


def wind_outlook(outlook_day, year, month, day, time, outlook_kmz_dir, image_dir, include_reports=False, remove_unknowns=False,
    filtered_reports=False):

    local_filename = f'day{outlook_day}otlk_{year}%02d%02d_%04d.kmz' % (month, day, time)
    full_path = f'{outlook_kmz_dir}/{local_filename}'

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
                polygon_colors = settings.colors['WIND5']
            elif name == '15 %':
                zorder = 1
                polygon_colors = settings.colors['WIND15']
            elif name == '30 %':
                zorder = 2
                polygon_colors = settings.colors['WIND30']
            elif name == '45 %':
                zorder = 3
                polygon_colors = settings.colors['WIND45']
            elif name == '60 %':
                zorder = 4
                polygon_colors = settings.colors['WIND60']
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

    plot_background([233, 295, 20, 50], ax=ax)  # Plot background on main subplot containing fronts and probabilities

    if include_reports:

        storm_reports = utils.StormReports(year, month, day)
        wind_reports = storm_reports.load_wind_reports(filtered=filtered_reports)[['Speed', 'Lat', 'Lon']]

        if remove_unknowns:
            wind_reports = wind_reports[wind_reports['Speed'] != 'UNK']
        else:
            wind_reports = wind_reports.replace(to_replace={'UNK': '58'})

        wind_reports['Speed'] = np.array(wind_reports['Speed'].values, dtype=int)
        wind_reports_values = wind_reports.values
        num_wind_reports = 0
        num_sigwind_reports = 0
        max_wind = int(np.max(wind_reports_values))
        for report in wind_reports_values:
            if report[0] == max_wind:
                marker = '*'
                facecolor = 'blue'
                edgecolor = 'black'
                num_sigwind_reports += 1
                zorder = 13
                s = 10
            elif report[0] > 74:
                marker = 's'
                facecolor = 'black'
                edgecolor = 'gray'
                num_sigwind_reports += 1
                zorder = 12
                s = 4
            else:
                marker = 'o'
                facecolor = 'blue'
                edgecolor = 'black'
                num_wind_reports += 1
                zorder = 11
                s = 3
            plt.scatter(report[2], report[1], s=s, marker=marker, edgecolor=edgecolor, linewidth=0.2, facecolor=facecolor, transform=ccrs.PlateCarree(), zorder=zorder)

        report_WIND = plt.scatter(0, 0, s=8, marker='o', edgecolor='black', linewidth=0.2, facecolor='blue', transform=ccrs.PlateCarree(), label=f'Wind ({num_wind_reports})')
        report_SIGWIND = plt.scatter(0, 0, s=10, marker='s', edgecolor='gray', linewidth=0.2, facecolor='black', transform=ccrs.PlateCarree(), label=f'Sig. Wind ({num_sigwind_reports})')
        report_MAXWIND = plt.scatter(0, 0, s=14, marker='*', edgecolor='black', linewidth=0.2, facecolor='blue', transform=ccrs.PlateCarree(), label=f'Highest wind report ({max_wind} mph)')

        if filtered_reports:
            report_legend_title = f'Filtered wind reports ({num_wind_reports + num_sigwind_reports})'
        else:
            report_legend_title = f'Wind reports ({num_wind_reports + num_sigwind_reports})'

        if remove_unknowns:
            report_legend_title += '*'
            plt.text(-16, 19.5, '* wind reports only include measured or estimated winds (no UNK reports)', fontdict={'fontsize': 4})

        reports_legend = plt.legend(handles=[report_WIND, report_SIGWIND, report_MAXWIND], loc='lower left', ncol=1, fontsize=5, title=report_legend_title, title_fontsize=6)
        plt.gca().add_artist(reports_legend)

    # Add labels to the legend
    handles.extend([utils.poly_WIND5]), labels.extend(['5%'])
    handles.extend([utils.poly_WIND15]), labels.extend(['15%'])
    handles.extend([utils.poly_WIND30]), labels.extend(['30%'])
    handles.extend([utils.poly_WIND45]), labels.extend(['45%'])
    handles.extend([utils.poly_WIND60]), labels.extend(['60%'])
    handles.extend([utils.poly_SIGWIND]), labels.extend(['10% ≥ 75 mph'])

    plt.legend(handles=handles, labels=labels, loc='lower right', ncol=3, fontsize=5, framealpha=1, title='Probability of severe winds (≥ 58 mph) within 25 miles of a point', title_fontsize=4.5).set_zorder(10)
    ####################################################################################################################

    title_text = f'{year}-%02d-%02d %04d UTC Day {outlook_day} Convective Outlook: Wind' % (month, day, time)

    plt.title(title_text)
    plt.savefig(f'{image_dir}/day{outlook_day}otlk_{year}%02d%02d_%04d_wind.png' % (month, day, time), bbox_inches='tight', dpi=1000)
    plt.close()


def hail_outlook(outlook_day, year, month, day, time, outlook_kmz_dir, image_dir, include_reports=False):

    local_filename = f'day{outlook_day}otlk_{year}%02d%02d_%04d.kmz' % (month, day, time)
    full_path = f'{outlook_kmz_dir}/{local_filename}'

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
                polygon_colors = settings.colors['HAIL5']
            elif name == '15 %':
                zorder = 1
                polygon_colors = settings.colors['HAIL15']
            elif name == '30 %':
                zorder = 2
                polygon_colors = settings.colors['HAIL30']
            elif name == '45 %':
                zorder = 3
                polygon_colors = settings.colors['HAIL45']
            elif name == '60 %':
                zorder = 4
                polygon_colors = settings.colors['HAIL60']
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

    plot_background([233, 295, 20, 50], ax=ax)  # Plot background on main subplot containing fronts and probabilities

    if include_reports:
        storm_reports = utils.StormReports(year, month, day)
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
        plt.gca().add_artist(reports_legend)

    # Add labels to the legend
    handles.extend([utils.poly_HAIL5]), labels.extend(['5%'])
    handles.extend([utils.poly_HAIL15]), labels.extend(['15%'])
    handles.extend([utils.poly_HAIL30]), labels.extend(['30%'])
    handles.extend([utils.poly_HAIL45]), labels.extend(['45%'])
    handles.extend([utils.poly_HAIL60]), labels.extend(['60%'])
    handles.extend([utils.poly_SIGHAIL]), labels.extend(['10% ≥ 2" diameter'])

    plt.legend(handles=handles, labels=labels, loc='lower right', ncol=3, fontsize=5, framealpha=1, title='Probability of severe hail (≥ 1" diameter) within 25 miles of a point', title_fontsize=4.5).set_zorder(10)
    ####################################################################################################################

    title_text = f'{year}-%02d-%02d %04d UTC Day {outlook_day} Convective Outlook: Hail' % (month, day, time)

    plt.title(title_text)
    plt.savefig(f'{image_dir}/day{outlook_day}otlk_{year}%02d%02d_%04d_hail.png' % (month, day, time), bbox_inches='tight', dpi=1000)
    plt.close()


def fire_outlook(outlook_day, year, month, day, time, outlook_kmz_dir, image_dir):

    local_filename = '%s%02d%02d_%04d_day%dfirewx.kmz' % (str(year)[2:], month, day, time, outlook_day)
    full_path = f'{outlook_kmz_dir}/{local_filename}'

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
                polygon_colors = settings.colors['Elevated']
            elif 'Critical' in name:
                zorder = 1
                polygon_colors = settings.colors['Critical']
            elif 'Extreme' in name:
                zorder = 2
                polygon_colors = settings.colors['Extreme']

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
                polygon_colors = settings.colors['Iso DryT']
            elif 'Scattered' in name:
                zorder = 4
                polygon_colors = settings.colors['Scattered DryT']

            for coord_set in coord_sets:
                coord_pairs = coord_set.text_content().split(' ')
                for coord_pair in range(len(coord_pairs)):
                    coord_pairs[coord_pair] = coord_pairs[coord_pair].split(',')
                coordinates = np.array(coord_pairs, dtype=float)
                poly = Polygon(coordinates, label=simpledata, facecolor=polygon_colors['fill'], edgecolor=polygon_colors['outline'], linewidth=0.7, zorder=zorder, transform=ccrs.PlateCarree(), linestyle='--')
                ax.add_patch(poly)

    plot_background([233, 295, 20, 50], ax=ax)  # Plot background on main subplot containing fronts and probabilities

    # Add labels to the legend
    handles.extend([utils.poly_ELEVATED]), labels.extend(['Elevated'])
    handles.extend([utils.poly_CRITICAL]), labels.extend(['Critical'])
    handles.extend([utils.poly_EXTREME]), labels.extend(['Extreme'])
    handles.extend([utils.poly_ISODRYT]), labels.extend(['Iso DryT'])
    handles.extend([utils.poly_SCATTEREDDRYT]), labels.extend(['Scattered DryT'])

    plt.legend(handles=handles, labels=labels, loc='lower right', ncol=2, fontsize=5, framealpha=1, title='Fire outlook legend', title_fontsize=6).set_zorder(10)
    ####################################################################################################################

    title_text = f'{year}-%02d-%02d %04d UTC Day {outlook_day} Fire Weather Outlook' % (month, day, time)

    plt.title(title_text)
    plt.savefig(f'{image_dir}/firewx_day{outlook_day}otlk_{year}%02d%02d_%04d.png' % (month, day, time), bbox_inches='tight', dpi=1000)
    plt.close()
