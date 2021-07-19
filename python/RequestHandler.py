import python.process.example as example
import python.process.signals as signals


def __init__():
    return

SXR_path = 'c:/work/SXR_ML/'
models_path = 'Models/Good/'
class Handler:
    def __init__(self):
        self.HandlingTable = {
            'view': {
                'refresh': self.refresh_func,
                'get_shot': self.get_shot,
                'selected_signals': self.view_sig
                #'obtain_Te': self.Te_prediction
            }
        }
        self.models_path = '%s%s' % (SXR_path, models_path)
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

    def get_shot(self, req):
        if 'shotn' not in req:
            return {
                'ok': False,
                'description': 'Request is missing field "shotn".'
            }
        resp = {'ok': True, 'header': req['shotn']}
        # m.b. check resp for errors
        return resp

    def refresh_func(self, req):
        return {
            'ok': True,
            'description': 'Alive'
        }

    def view_sig(self, req):
        if 'shotn' not in req:
            return {
                'ok': False,
                'description': 'Request is missing field "shotn".'
            }
        if 'selected_signals' not in req:
            return {
                'ok': False,
                'description': 'Request is missing field "selected_signals".'
            }
        resp = signals.sht_view(req['shotn'], req['selected_signals'])
        return resp
