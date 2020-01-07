# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 13:47:21 2020

@author: simon
"""

import requests					# requesting webpages
from bs4 import BeautifulSoup 	# parsing html
import json
import optparse

parser = optparse.OptionParser('get-lszs')
parser.add_option('-o', '--outdir',	dest='outdir', help='[optional] output directory')
(opts, args) = parser.parse_args()

headers = { 'Host' : 'timetable.engadin-airport.ch',
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0',
            'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language' : 'en-US,en;q=0.5',
            'Accept-Encoding' : 'gzip, deflate',
            'DNT' : '1',
            'Connection' : 'keep-alive',
            'Upgrade-Insecure-Requests' : '1',
            'Cookie-Installing-Permission' : 'required',
            'Cache-Control' : 'max-age=0' }


def getLSZS():
    requrl = 'http://timetable.engadin-airport.ch/index.php'
    # website currently does not require to send the headers
    response = requests.get(requrl)
    
    if(response.status_code != 200):
        print('error: Website returned status code: ' + str(response.status_code))
        
    """
    <tr style="background:#FF0000;color:#FFFFFF">
     <td width="40"><img src=departure.gif pagespeed_url_hash="2442189937"></td>
     <td width="60">13:00</td>
     <td width="80" class="b">OYCKK</td>
     <td width="80" class="b">MMD6616</td>
     <td width="170">F2TH</td>
     <td width="524">
     <table width="324" cellpadding="0" cellspacing="0">
     <tbody><tr><td>Paris-Le-Bourget  (France)</td><td align="right">CANCEL</td></tr></tbody></table>
     </td>
    """
    
    parsed_html = BeautifulSoup(response.text, 'lxml')
    flt_table = parsed_html.find('div', {'id': 'timetable'}).find('tbody')
    # there is a nested table... ignore the <tr> from the inner levels
    # https://stackoverflow.com/questions/28058203/beautifulsoup-ignore-nested-tables-inside-table
    all_rows = flt_table.findAll('tr')
    rows = []
    for t in all_rows:
        if(len(t.find_parents('tr')) == 0):
            rows.append(t)
    
    # prepare json dict with empty array
    timetable = {}
    timetable['data'] = []
    
    for row in rows:
        td = row.findAll('td')
        if(len(td) > 0):
            entry = {}
            entry['aircraft'] = td[2].text  # registration
            entry['callsign'] = td[3].text  # callsign
            entry['type']     = td[4].text  # aircraft type
            entry['lastinfo'] = td[7].text  # additional info
            entry['destination'] = td[5].table.td.text.strip()
            entry['time'] = td[1].text
            
            img = td[0].find('img')
            entry['stats'] = ''
            if('arrival' in str(img).lower()):
                entry['stats'] = 'arrival'
            elif('departure' in str(img).lower()):
                entry['stats'] = 'departure'
                
            timetable['data'].append(entry)
    return timetable

def writeJsonFile(directory, data):
    with open(str(directory) + '/timetable.json', 'w') as outfile:
        json.dump(data, outfile)

#%%
def main():
    try:
        table = getLSZS()
        
        outdir = '.'
        if(opts.outdir is not None):
            outdir = opts.outdir
            
        writeJsonFile(outdir, table)
    except KeyboardInterrupt:
        print('')
        exit(0)


if __name__ == '__main__':
	main()
    
    