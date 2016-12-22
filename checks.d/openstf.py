import time
import requests

from checks import AgentCheck
from itertools import groupby
from hashlib import md5

class OpenSTFCheck(AgentCheck):
    def check(self, instance):
        host = self.init_config.get('host', "http://localhost:7100")
        url_devices = "/api/v1/devices"
        token = self.init_config.get('token', None)
        headers = {"Authorization":"Bearer %s" % token}


        default_timeout = self.init_config.get('default_timeout', 5)
        timeout = float(instance.get('timeout', default_timeout))

        try:
            r = requests.get(host + url_devices, timeout=timeout, headers = headers)
            body = r.json()
        except requests.exceptions.Timeout as e:
            # If there's a timeout
            return
        # if r.status_code != 200:
        #     self.status_code_event(url, r, aggregation_key)
        if r.status_code == 200:
            metrics = ['status', 'using', 'ready', 'present']

            for metric in metrics:
                for device in body['devices']:
                    self.gauge(
                        "openstf.device.%s" % metric,
                        1,
                        tags=["%s:%s" % (metric, device[metric])],
                        device_name = device['model'] if 'model' in device else 'undefined'
                    )

if __name__ == '__main__':
    check, instances = OpenSTFCheck.from_yaml('/etc/dd-agent/conf.d/openstf.yaml')
    for instance in instances:
        print "\nRunning the check against stf"
        check.check(instance)