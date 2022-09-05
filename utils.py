import pandas as pd


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
