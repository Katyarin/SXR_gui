import python.process.ripper as ripper
from scipy.signal import savgol_filter
import numpy as np
import joblib
import pandas as pd

model_path = 'c:/work/SXR_ML/Models/Good/'

def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth

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
        if key == 'Shotn' or key == 'time':
            beauty_data[key] = data_clean[key]
        else:
            beauty_data[change_dict[key]] = data_clean[key]

    return beauty_data


def sht_view(shotn, signals):
    print('shot selected: ', shotn, 'signals selected: ', signals)
    print(signals)
    if shotn == '':
        return {
            'ok': False,
            'description': 'Введите номер разряда'
        }
    if 'HXR' in signals:
        signals[signals.index('HXR')] = 'НXR Подушниковой'
    if int(shotn) > 40087:
        if 'SXR 27' in signals:
            return {
                'ok': False,
                'description': 'foil 27 mkm was deleted, you need 127 mkm'
            }
    else:
        if 'SXR 127' in signals:
            return {
                'ok': False,
                'description': 'foil 127 mkm not installed yet, you need 27 mkm'
            }
    k = 0
    try:
        raw_data = get_data(int(shotn), signals)
    except IndexError:
        return {
            'ok': False,
            'description': 'Один из выбранных сигналов недоступен'
        }
    result_data = do_normal_data(raw_data, int(shotn))
    if 'НXR Подушниковой' in signals:
        signals[signals.index('НXR Подушниковой')] = 'HXR'
    return {
        'ok': True,
        'data': result_data
    }

def Te_prediction(shotn, signals):
    first = sht_view(shotn, signals)
    if first['ok'] == False:
        return first
    data = first['data']
    norm_data = pd.DataFrame(data)
    if 'SXR 15' in signals and 'SXR 27' in signals and 'SXR 50' in signals and 'SXR 80' in signals:
        if 'HXR' in signals and 'CIII' in signals:
            model = 'PART3_RNDe34d19msl11_HXR_SXR_with_zeros100_immisC_time.joblib'
            work_data = norm_data.drop('Shotn', axis=1)
            print('ok 1')
        elif 'HXR' in signals:
            return {
                'ok': False,
                'description': 'Not done yet 1'
            }
        elif 'CIII' in signals:
            return {
                'ok': False,
                'description': 'Not done yet 2'
            }
        else:
            model = 'NEW_SEASON1_RNDe30d19msl7_SXR.joblib'
            work_data = norm_data.drop('Shotn', axis=1)
    elif 'SXR 15' in signals and 'SXR 27' in signals and 'SXR 50' in signals:
        return {
            'ok': False,
            'description': 'Not done yet'
        }
    elif 'SXR 15' in signals and 'SXR 27' in signals and 'SXR 80' in signals:
        if 'HXR' in signals and 'CIII' in signals:
            return {
                'ok': False,
                'description': 'Not done yet'
            }
        elif 'HXR' in signals:
            return {
                'ok': False,
                'description': 'Not done yet'
            }
        elif 'CIII' in signals:
            return {
                'ok': False,
                'description': 'Not done yet'
            }
        else:
            print('just all sxr')
    elif 'SXR 15' in signals and 'SXR 50' in signals and 'SXR 80' in signals:
        if 'HXR' in signals and 'CIII' in signals:
            return {
                'ok': False,
                'description': 'Not done yet'
            }
        elif 'HXR' in signals:
            model = 'NEW_SEASON1_RNDe40d20msl8_SXR_with_zeros100_with_HXR.joblib'
        elif 'CIII' in signals:
            model = 'NEW_SEASON1_RNDe37d13msl8_SXR_with_zeros100_with_CIII.joblib'
        else:
            model = 'NEW_SEASON1_RNDe47d13msl8_SXR_with_zeros100_no27.joblib'
    elif 'SXR 27' in signals and 'SXR 50' in signals and 'SXR 80' in signals:
        return {
            'ok': False,
            'description': 'Not done yet'
        }
    elif 'SXR 127' in signals:
        return {
            'ok': False,
            'description': 'Расчет температуры с фольгой 127 мкм пока недоступен'
        }
    else:
        return {
            'ok': False,
            'description': 'Пожалуйста, выберите хотя бы 3 SXR сигнала'
        }
    rnd_reg = joblib.load(model_path + model)
    Te_from_SXR = rnd_reg.predict(work_data)
    time = data['time']
    print(Te_from_SXR)
    print(type(Te_from_SXR))
    return {
        'ok': True,
        'data': {'time': time, 'Te': list(smooth(Te_from_SXR, 401))}
    }
