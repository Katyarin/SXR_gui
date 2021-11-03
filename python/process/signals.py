import python.process.ripper as ripper
from scipy.signal import savgol_filter
import numpy as np
import joblib
import pandas as pd
import requests
import json

model_path = 'c:/work/SXR_ML/Models/Good/'
URL = "http://192.168.10.41:8082/api"


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


def get_TS_data(shotn):
    response = requests.post(url=URL, json={
        'subsystem': 'db',
        'reqtype': 'get_shot',
        'shotn': int(shotn)
    })

    try:
        data = response.json()
    except:
        print('Not a json?')
        return {
            'ok': False,
            'description': 'Not TS json?'
        }
    TS_data = {'time': [], 'data': [], 'err': []}
    polyn = 565
    if 'data' not in data:
        return {
            'ok': False,
            'description': data['description']
        }
    if 'polys' in data['data']:
        for poly in data['data']['polys']:
            if poly['R'] == 412:
                polyn = poly['ind']
    elif 'config' in data['data']:
        for poly in data['data']['config']['poly']:
            print(poly['R'])
            if 412 - 5 < poly['R'] < 412 + 5:
                polyn = poly['ind']
    else:
        return {
            'ok': False,
            'description': 'no polys, no config'
        }
    print('————')
    print(polyn)
    for event in data['data']['events']:
        if event['error'] == None:
            if event['T_e'][polyn]['error'] == None:
                TS_data['time'].append(event['timestamp'])
                TS_data['data'].append(event['T_e'][polyn]['T'])
                TS_data['err'].append(event['T_e'][polyn]['Terr'])

    return {
        'ok' : True,
        'data': TS_data
    }


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
                   'CIII 465 nm': 'CIII', 'Ip внутр.(Пр2ВК) (инт.18)': 'Ip in'}

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
            'description': 'Один или несколько выбранных сигналов недоступны'
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
    err = 'unknown'
    if 'SXR 15' in signals and 'SXR 27' in signals and 'SXR 50' in signals and 'SXR 80' in signals:
        if 'HXR' in signals and 'CIII' in signals:
            model = 'PART3_RNDe34d19msl11_HXR_SXR_with_zeros100_immisC_time.joblib'
            work_data = norm_data.drop('Shotn', axis=1)
            err = '18%'
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
            err = '22%'
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
            work_data = norm_data.drop('Shotn', axis=1)
        elif 'CIII' in signals:
            model = 'NEW_SEASON1_RNDe37d13msl8_SXR_with_zeros100_with_CIII.joblib'
            work_data = norm_data.drop('Shotn', axis=1)
        else:
            model = 'NEW_SEASON1_RNDe47d13msl8_SXR_with_zeros100_no27.joblib'
            work_data = norm_data.drop('Shotn', axis=1).drop('time', axis=1)
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
        'data': {'time': time, 'Te': list(smooth(Te_from_SXR, 401)), 'error': err}
    }


def Te_interpolation(shotn, signals):
    signals.append('Ip внутр.')
    first = sht_view(shotn, signals)
    if first['ok'] == False:
        return first
    data = first['data']
    SXR_data = pd.DataFrame(data)
    TS_data = get_TS_data(shotn)['data']

    print(SXR_data.keys())

    SXR_ratio = SXR_data[['time', 'Ip in']]
    for SXR1 in SXR_data.keys():
        for SXR2 in SXR_data.keys():
            if SXR1 < SXR2 and SXR1 != 'Ip in' and SXR1 != 'time' and SXR1 != 'Shotn' and SXR2 != 'Ip in' and\
                    SXR2 != 'time' and SXR2 != 'Shotn':
                SXR_ratio[SXR2 + "/" + SXR1] = SXR_data[SXR2] / SXR_data[SXR1]
    coeff = {}
    Ec = {'SXR 15': 1300, 'SXR 27': 1600, 'SXR 50': 2000, 'SXR 80': 2300, 'SXR 127': 2700}
    for ratio in SXR_ratio.keys():
        if ratio != 'Ip in' and ratio != 'time':
            coeff[ratio] = []
            for element in range(len(TS_data['time'])):
                coeff[ratio].append(SXR_ratio[ratio][int(TS_data['time'][element] * 1000)] * np.exp(
                    (Ec[ratio[:6]] - Ec[ratio[7:]]) / TS_data['data'][element]))
    k = 0
    coeff_for_SXR = {}
    for ratio in SXR_ratio.keys():
        k = 0
        if ratio != 'Ip in' and ratio != 'time':
            coeff_for_SXR[ratio] = []
            for element in range(len(SXR_ratio['time'])):
                if element <= int(TS_data['time'][-1] * 1000):
                    if element < int(TS_data['time'][k] * 1000):
                        if k > 0:
                            k_new = coeff[ratio][k - 1] + (coeff[ratio][k] - coeff[ratio][k - 1]) * (
                                        element - TS_data['time'][k - 1] * 1000) / (
                                                TS_data['time'][k] * 1000 - TS_data['time'][k - 1] * 1000)
                        else:
                            k_new = coeff[ratio][k] * element / (TS_data['time'][k] * 1000)
                        coeff_for_SXR[ratio].append(k_new)
                    else:
                        coeff_for_SXR[ratio].append(coeff[ratio][k])
                        k += 1
                else:
                    k_new = coeff[ratio][k - 1] + (- coeff[ratio][k - 1]) * (
                                element - TS_data['time'][k - 1] * 1000) / (- TS_data['time'][k - 1] * 1000)
                    coeff_for_SXR[ratio].append(k_new)
    new_coeff = pd.DataFrame(coeff_for_SXR)
    Te_ratio = SXR_ratio[['time', 'Ip in']]
    for ratio in SXR_ratio.keys():
        if ratio != 'Ip in' and ratio != 'time':
            Te_ratio[ratio] = (Ec[ratio[:6]] - Ec[ratio[7:]]) / np.log(new_coeff[ratio] / SXR_ratio[ratio])
    Te_dict = {}
    Te_ratio2 = Te_ratio.where(pd.notnull(Te_ratio), None)
    #Te_dict = Te_ratio2.to_dict()
    for key in Te_ratio:
        Te_dict[key] = list(Te_ratio2[key])
    with open('Te_res_test.json', 'w') as file:
        json.dump(Te_dict, file)
    return {
        'ok': True,
        'data': Te_dict
    }
