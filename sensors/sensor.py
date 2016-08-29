import requests
import json
from requests.auth import HTTPBasicAuth

from st2reactor.sensor.base import PollingSensor


class TestSensor(PollingSensor):
    def __init__(self, sensor_service, config):
        super(TestSensor, self).__init__(sensor_service=sensor_service, config=config, poll_interval=10)
        self._logger = self.sensor_service.get_logger(name=self.__class__.__name__)
        self._stop = False

    def setup(self):
        pass

    def cleanup(self):
        self._stop = True

    def poll(self):
        auth = HTTPBasicAuth('test', 'test')
        headers = {
            'Content-Type': 'application/json'
        }

        commands = ['show interface summary']

        payload = {
            "ins_api": {
                "version": "1.0",
                "type": "cli_show",
                "chunk": "0",
                "sid": "1",
                "input": commands,
                "output_format": "json"
            }
        }
        url = 'http://n9k2/ins'

        response = requests.post(url, data=json.dumps(payload), headers=headers, auth=auth)
        rx_object = json.loads(response.text)['ins_api']['outputs']['output']['body']


        for interface in rx_object['TABLE_interface']['ROW_interface']:
            if interface['interface'] == 'Ethernet2/4':
                if interface.get('state') != 'connected':
                    self._dispatch_trigger(result=interface.get('state'))


    def _dispatch_trigger(self, result):
        trigger = 'st2-nxos_command.event1'

        payload = {
            'measurements': result
        }
        self._sensor_service.dispatch(trigger=trigger, payload=payload)

    # Methods required for programmable sensors.
    def add_trigger(self, trigger):
        pass

    def update_trigger(self, trigger):
        pass

    def remove_trigger(self, trigger):
        pass
