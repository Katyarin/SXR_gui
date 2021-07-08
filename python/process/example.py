print('example module loaded')


def process(arg):
    print('procesing request with argument: ', arg)
    return {
        'ok': True,
        'data': [0, 1, 'asdf']
    }
