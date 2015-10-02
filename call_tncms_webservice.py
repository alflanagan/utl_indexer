#!/usr/bin/env python3

from requests.auth import HTTPBasicAuth
import requests
import json
from pprint import pprint


def main():
    # data = {'user': 'ALFlanagan'}
    # login = HTTPBasicAuth('16ED26C62A6711E591E4B3E58BAF2E49', '55A57143E3404')
    # resp = requests.post('https://richmond-dot-com.bloxcms-ny1.com/tncms/webservice/v1/user/get/',
    #                      data=data, auth=login)
    # print(resp.text)
    services = ['business', 'job', 'user', 'editorial', 'eedition', 'classifieds']
    URL_ROOT = "https://certification13-dot-townnews365-dot-com.bloxcms.com/tncms/webservice/v1/"
    data = {"user": "Flanagan"}
    login = HTTPBasicAuth('089F86E02A6211E5A24353BD6EAA3E6B', '55A568C86DF17')
    for service in services:
        resp = requests.post("{}{}/".format(URL_ROOT, service), data=data, auth=login)
        resp_dict = json.loads(resp.text)
        api_list = resp_dict['apis']
        for api_desc in api_list:
            print(api_desc['path'])
            for oper in api_desc['operations']:
                print("    {}: {}".format(oper['httpMethod'], oper['summary']))

    RICHMOND_URL="https://richmond-dot-com.bloxcms-ny1.com/tncms/webservice/v1/"
    # http://www.richmond.com/tncms/webservice/v1/editorial/get/?
    data = {'id': '72c2ab48-2976-11e5-a21b-a7f967e75fca'}
    login = HTTPBasicAuth("16ED26C62A6711E591E4B3E58BAF2E49", "55A57143E3404")
    resp = requests.post("{}editorial/get/".format(RICHMOND_URL), data=data, auth=login)
    asset = json.loads(resp.text)
    pprint(asset)


if __name__ == '__main__':
    main()
