import matplotlib as mpl

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

valid_convective_outlook_times = [[1200, 1300, 1630, 2000, 100], [600, 1730], [730, ]]  # [[Day 1], [Day 2], [Day 3]]
valid_fire_outlook_times = [[1200, 1700], [1200, 2000]]  # [[Day 1], [Day 2]]
