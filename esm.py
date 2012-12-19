"""
Info su lun e lv del VSX
"""

from re import match, IGNORECASE
from sys import argv
import requests
import simplejson as json
from config import esm_server, esm_user, esm_password

class VSX(object):
    """
    Rappresenta il VSX
    """

    def __init__(self):

        method = "https://"
        server = esm_server
        port = "8443"
        user = esm_user
        password = esm_password
        base_url = method + server + ":" + port
        admin_path = '/admin?op=login&username=%s&password=%s' % (
                      user, password)

        # Login and get cookie
        url  = base_url + admin_path
        resp = requests.post(url, verify=False)

        self.cookies = dict(JSESSIONID=resp.cookies['JSESSIONID']) 

        # Fetch luns info 
        url  = base_url + '/fetch?shelf=96&vsxlun'
        resp = requests.get(url, cookies=self.cookies, verify=False)
        info = json.loads(resp.text)

        self.luns = info[0][1]['reply']

    def printluns(self, alun=None):
        """
        Stampa le info di alun (o di tutte le lun per default)
        """

        print "-" * 56
        print "%-5s %21s %11s %10s %s" % ('lun', 'lv', 'size', 'pool', 'snaps')
        print "-" * 56

        for lun in self.luns:
            lunindex = [ lun['shelf'], lun['index'] ]
            if not alun or lunindex == map(int, alun.split('.')):
                print "%3s.%-4s %18s %8d GB %10s %5d" % (
                        lun['shelf'], lun['index'], lun['lv'],
                        lun['size']/1000, lun['pool'], lun['snapshotCount'])

    def printlv(self, lvs=None):
        """
        Stampa le info di lvs (o di tutti i lv per default)
        """

        def lvmatch(regex, lvs):
            """
            Ritorna True se la regex matcha lvs
            """
            return match(regex, lvs, IGNORECASE) is not None

        if not lvs:
            return

        regex = '^%s$' % lvs

        if lvs.startswith('*') and lvs.endswith('*'):
            lvs = lvs.replace('*', '')
            regex = ".*%s.*$" % lvs
        elif lvs.startswith('*'):
            lvs = lvs.replace('*', '')
            regex = ".*%s$" % lvs
        elif lvs.endswith('*'):
            lvs = lvs.replace('*', '')
            regex = "^%s.*" % lvs

        print regex

        print "-" * 56
        print "%-5s %21s %11s %10s %s" % ('lun', 'lv', 'size', 'pool', 'snaps')
        print "-" * 56

        for lun in self.luns:
            if lvmatch(regex, lun['lv']):
                print "%3s.%-4s %18s %8d GB %10s %5d" % (
                        lun['shelf'], lun['index'], lun['lv'],
                        lun['size']/1000, lun['pool'], lun['snapshotCount'])

def main():

    data = '*'

    try:
        data = argv[1]
    except IndexError:
        pass

    vsx = VSX()

    if match(r'\d+\.\d+', data):
        vsx.printluns(data)
    else:
        vsx.printlv(data)

if __name__ == "__main__":
    main()
