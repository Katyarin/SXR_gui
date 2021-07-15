import python.process.ripper as ripper
from scipy.signal import savgol_filter
import numpy as np

def get_data(shotn, data):
    raw_data, link = ripper.extract('//172.16.12.127/data', shotn, data)
    data = {}
    for key in dict.keys(raw_data):
        data[key] = {}
        data[key]['name'] = raw_data[key]['name']
        data[key]['time'], data[key]['data'] = ripper.x_y(raw_data[key])
    return data


def do_normal_data(data, shotn):
    data_clean = {}
    data_clean['Shotn'] = shotn
    data_clean['time'] = [i * 1000 for i in data[list(dict.keys(data))[0]]['time']]

    # удаление из дальнейших расчетов стремного сигнала SXR80
    namber_of_sxr_80 = 0
    for key in dict.keys(data):
        if data[key]['name'] == 'SXR 80 mkm':
            namber_of_sxr_80 += 1

    if namber_of_sxr_80 == 2:
        key1 = 0
        key2 = 1
        for key in dict.keys(data):
            if data[key]['name'] == 'SXR 80 mkm':
                if key1 < key2:
                    key1 = key
                else:
                    key2 = key
        del data[key2]

    for key in dict.keys(data):
        try:
            yy_filtered = savgol_filter(data[key]['data'], 201, 2)
        except:
            yy_filtered = savgol_filter(data[key]['data'], 201, 2)
        base_line = np.mean(yy_filtered[0:50000])
        data_clean[data[key]['name']] = list(yy_filtered - base_line)

    change_dict = {'SXR 15 мкм': 'SXR 15', 'SXR 27 мкм': 'SXR 27', 'SXR 127 мкм': 'SXR 127',
                   'SXR 50 mkm': 'SXR 50', 'SXR 80 mkm': 'SXR 80', 'НXR Подушниковой': 'HXR',
                   'CIII 465 nm': 'CIII'}

    beauty_data = {}

    for key in data_clean.keys():
        beauty_data[change_dict[key]] = data_clean[key]

    return beauty_data


def sht_view(shotn, signals):
    print('shot selected: ', shotn, 'signals selected: ', signals)
    if int(shotn) > 40087:
        if 'SXR 27' in signals:
            return {
                'ok': False,
                'descriptions': 'foil 27 mkm was deleted, you need 127 mkm'
            }
    else:
        if 'SXR 127' in signals:
            return {
                'ok': False,
                'descriptions': 'foil 127 mkm not installed yet, you need 27 mkm'
            }
    raw_data = get_data(shotn, signals)
    result_data = do_normal_data(raw_data, shotn)
    return {
        'ok': True,
        'data': result_data
    }