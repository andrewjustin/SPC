import pandas as pd
from matplotlib.patches import Polygon
from settings import colors

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


class StormReports:
    def __init__(self, year, month, day):
        """
        year: YYYY
        month: int
        day: int
        """
        self.base_link = 'https://www.spc.noaa.gov/climo/reports/%s%02d%02d_rpts' % (str(year)[2:], month, day)

    def load_tornado_reports(self, filtered=True):
        """ Load tornado reports for the given day. """
        report_set = ''  # raw report set
        if filtered:
            report_set = '_filtered'
        return pd.read_csv(f'{self.base_link}{report_set}_torn.csv')

    def load_hail_reports(self, filtered=True):
        """ Load hail reports for the given day. """
        report_set = ''  # raw report set
        if filtered:
            report_set = '_filtered'
        return pd.read_csv(f'{self.base_link}{report_set}_hail.csv')

    def load_wind_reports(self, filtered=True):
        """ Load wind reports for the given day. """
        report_set = ''  # raw report set
        if filtered:
            report_set = '_filtered'
        return pd.read_csv(f'{self.base_link}{report_set}_wind.csv')
