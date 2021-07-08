import python.process.example as example


def __init__():
    return


class Handler:
    def __init__(self):
        self.HandlingTable = {
            'example_group': {
                'example_action': self.do_example
            },
            'adc': {
            },
            'laser': {
            },
            'view': {
                'refresh': self.refresh_func
            }
        }
        return

    def handle_request(self, req):
        subsystem = req['subsystem']
        if subsystem not in self.HandlingTable:
            return {'ok': False, 'description': 'Subsystem is not listed.'}
        reqtype = req['reqtype']
        if reqtype in self.HandlingTable[subsystem]:
            return self.HandlingTable[subsystem][reqtype](req)
        else:
            return {'ok': False, 'description': 'Reqtype is not listed.'}

    def do_example(self, req):
        if 'argument' not in req:
            return {
                'ok': False,
                'description': 'Request is missing field "argument".'
            }
        resp = example.process(req['argument'])
        # m.b. check resp for errors
        return resp

    def refresh_func(self, req):
        return {
            'ok': True,
            'description': 'Alive'
        }
