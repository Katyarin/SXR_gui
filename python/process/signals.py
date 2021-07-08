import python.process.ripper as ripper

def get_data(shotn, data):
    raw_data, link = ripper.extract('//172.16.12.127/data', shotn, data)
    data = {}
    for key in dict.keys(raw_data):
        data[key] = {}
        data[key]['name'] = raw_data[key]['name']
        data[key]['time'], data[key]['data'] = ripper.x_y(raw_data[key])
    return data


def process(shotn, signals):
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
    return {
        'ok': True,
        'data': [0, 1, 'asdf']
    }