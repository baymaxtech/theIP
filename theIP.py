import requests
import socket
import uuid
import re

__version__ = '1.0'

def get_ip_from_taobao():
    global code, external_ip, country_id, location, isp, source, headers
    url = "http://ip.taobao.com/service/getIpInfo.php"
    req = requests.get(url, params="ip=myip", headers=headers)
    data = eval(req.content)
    code = data['code']
    if code == 0:
        country_id = data['data']['country_id']
        if country_id == 'CN':
            country, area = data['data']['country'].decode('unicode_escape'), data['data']['area'].decode('unicode_escape')
            external_ip, region, city = data['data']['ip'], data['data']['region'].decode('unicode_escape'), data['data']['city'].decode('unicode_escape')
            county, isp = data['data']['county'].decode('unicode_escape'), data['data']['isp'].decode('unicode_escape')
            location, source = country + area + region + city + county, 'ip.taobao.com'
        else:   get_ip_from_api()
    else:   get_ip_from_sohu()

def get_ip_from_api():
    global code, external_ip, country_id, location, isp, source, headers, org, timezone, zip_code, lon, lat
    url = "http://ip-api.com/json/"
    req = requests.get(url, headers=headers)
    data = eval(req.content)
    status = data['status']
    if status == 'success':
        code = 0
        external_ip, country, country_id, city = data['query'], data['country'], data['countryCode'], data['city']
        region, timezone, zip_code, lat, lon = data['regionName'], data['timezone'], data['zip'], data['lat'], data['lon']
        org, isp, location, source = data['org'], data['isp'], " ".join((city, region, country)), 'ip-api.com'
    else:   code = 1

def get_ip_from_sohu():
    global code, external_ip, location, source, headers
    url = "http://pv.sohu.com/cityjson"
    req = requests.get(url, headers=headers)
    data = eval(re.search('\{.*?\}', req.content).group())
    external_ip, location, source = data['cip'], data['cname'], 'pv.sohu.com'
    if location.isalpha():  get_ip_from_api()
    else:   code = 1 if external_ip == '' else 0

def show_result():
    if code == 1:  # Fail to obtain information
        print "All ip API sources are broken. Please modify the code for future uses!"
    else:
        print "Host Name: " + host_name + " | " + "Mac Addresss: " + mac_addr
        print "Interal IP Addr: " + internal_ip + " | " + "External IP Addr: " + external_ip
        print "Country Code: " + country_id + " | " + "Location: " + location
        print "Isp Provider:" + isp + " | " + "The information is gathered from: {}".format(source)
        if country_id != 'CN':
            print "Organization: " + org + " | " + "Timezone: " + timezone
            print "Zip code:" + zip_code + " | " + " Latitude: " + str(lat) + " | " + " Longtitude: " + str(lon)

# something wrong with mac
def get_local_info():
    global internal_ip, host_name, mac_addr
    internal_ip, host_name = socket.gethostbyname(socket.gethostname()), socket.getfqdn(socket.gethostname())
    mac_addr = uuid.UUID(int = uuid.getnode()).hex[-12:]
    mac_addr = ":".join([mac_addr[e:e+2] for e in range(0, 11, 2)])

if __name__ == '__main__':
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0'}

    get_local_info()
    get_ip_from_taobao()
    show_result()
