import requests as req
import time
import zlib
import os, glob
from datetime import datetime
from bs4 import BeautifulSoup


SISMOLOGIA_URL = 'http://www.sismologia.cl'
SISMOLOGIA_URL_ULTIMOS = ''.join((SISMOLOGIA_URL, '/links/tabla.html'))
PATH_DETAILS = 'details'

def get_lasted(list_only = True):
    sismos_table = make_request(SISMOLOGIA_URL_ULTIMOS, False)
    soup = BeautifulSoup(sismos_table, 'html.parser')
    list_rows = soup.find_all('tr')
    url_sismos = [row.find('a')['href'] for row in list_rows[1:]]
    if list_only:
        return url_sismos
    else:
        print "lista de sismos con cache, esto generara mucha carga"
        list_details_sismos = [detail_sismo(x) for x in url_sismos]
        return list_details_sismos

def make_request(url_site, check_cache=False):
    crc_path = str(zlib.crc32(url_site) ).replace('-', '')
    if not check_cache:
        try:
            res = req.get(url_site)
            content = res.text.encode('utf-8')
            with open(os.path.join(PATH_DETAILS, crc_path + '.cache'), "w") as f:
                f.write(content)
                f.close()
                return content
        except Exception as ex:
            print "Error en generacion de cache"
            print ex
            return None
    else:
        try:
            with open(os.path.join(PATH_DETAILS, crc_path + '.cache'), "r") as f:
                print "Sismo cacheado - " + crc_path
                content = f.readlines()
                content = [x.strip() for x in content]
                f.close()
                return ''.join(content)#tuple to string
        except Exception as ex:
            print "Generando cache - " + crc_path
            return make_request(url_site, False)

def parse_time(str_time):
    return datetime.strptime(str_time, '%H:%M:%S %d/%m/%Y')

def detail_sismo(path_url):
    url_detail_sismo = ''.join((SISMOLOGIA_URL, str(path_url)))
    detail_sismo = make_request(url_detail_sismo, True)
    if detail_sismo:
        soup = BeautifulSoup(detail_sismo, 'html.parser')
        detail = {}
        tr_details = soup.find_all('tr')
        detail['time_local'] = tr_details[0].find_all('td')[1].string
        detail['time_utc'] = tr_details[1].find_all('td')[1].string
        detail['lat'] = tr_details[2].find_all('td')[1].string
        detail['long'] = tr_details[3].find_all('td')[1].string
        detail['depth'] = tr_details[4].find_all('td')[1].string
        detail['mag'] = tr_details[5].find_all('td')[1].string
        detail['ref'] = tr_details[6].find_all('td')[1].string.encode('utf-8')
        detail['epoch'] = time.mktime(parse_time(detail['time_local']).timetuple()) * 1000
        return detail

def clear_details_cached():
    filelist = [ f for f in os.listdir(os.path.join(PATH_DETAILS)) if f.endswith(".cache")]
    print filelist
    for f in filelist:
        os.remove(os.path.join(PATH_DETAILS, f))
    return True
