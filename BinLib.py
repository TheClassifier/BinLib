# Made By : Zach without love
# Date : 2022-08-20
# Version : 1.0
# Description : This is an API wrapper for doxbin.com that allows you to search and get dox content.

import os, sys
from json import dump, loads
from requests import Session
from bs4 import BeautifulSoup
from time import sleep as wait
import undetected_chromedriver as uc


class DoxBin: # DoxBin class for interacting with doxbin.com

    def __init__(self) -> None:
        self.session = Session()
        self.session.headers.update({
            'authority': 'doxbin.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'max-age=0',
            'referer': 'https://doxbin.com/search',
            'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
        }) # headers 
        self.base_url = "https://doxbin.com/" # base url
        pass

    def load_session(self, session_file:str) -> dict: # load session from session_file to request dox content
        ucookies = {}
        with open(session_file, 'r') as f:
            json_data = loads(f.read())
            ucookies.update(json_data)

        self.session.cookies.update(ucookies) # update session cookies
    
    def init_session(self) -> dict: # initialize session to request dox content
        if os.path.exists('session.json'):

            self.load_session('session.json')
            return 

        self.options = uc.ChromeOptions() # initialize chrome options
        self.options.headless = True # set headless to true 
        self.options.add_argument('--log-level=3') # set log level to 3 (info)

        self.driver = uc.Chrome(options=self.options) # initialize chrome driver
        sys.stdout.flush()
        sys.stdout.write("\r\033c")
        self.driver.get(self.base_url) # go to doxbin
        wait(5.5) # wait for page to load (5.5 seconds)
        cookies = self.driver.get_cookies() # get cookies
        ucookies = {}
        for cookie in cookies:
            cookie_obj = {cookie['name']: cookie['value']}
            ucookies.update(cookie_obj)
            
        self.session.cookies.update(ucookies) # update session cookies
        self.driver.quit() # close driver
        with open('session.json', 'w') as f:
            dump(ucookies, f) # save session to session.json

        return ucookies
    def get_xsrf_token(self) -> str: # get xsrf token from doxbin to initialize session to request dox content
        r = self.session.get(self.base_url) # get xsrf token
        soup = BeautifulSoup(r.text, 'html.parser')
        return soup.find('input', {'name': '_token'})['value'] # get xsrf token from doxbin html

    def get_dox_content(self, dox_url:str) -> str: # get dox content from dox url
        last_char = dox_url[-1]
        if last_char == '/':
            dox_url = dox_url[:-1] # remove last character if it is a '/'
        dox_url = dox_url.replace('/raw', '')
        dox_url = dox_url+"/raw"
        r = self.session.get(dox_url) # get dox content
        return r.text # return dox content

    def search(self, query: str) -> dict: # Search for dox and return a list of dox urls
        dox_list = [] # list of dox entries found
        data = {
            '_token': self.get_xsrf_token(),
            'search-query': query,
            'bpToken': 'br3nt0n',
        } # data to send to doxbin
        r = self.session.post(self.base_url+'search', data=data) # send data to doxbin

        soup = BeautifulSoup(r.text, 'html.parser') # parse doxbin html

        div = soup.find('div', {'class': 'col-md-7'})
        table = div.find('table', {'class': 'table table-striped table-hover'})
        tbody = table.find('tbody')
        trs = tbody.find_all('tr') 

        for tr in trs:
            dox_title = tr.find('td', {"colspan":"3"} ).find('a').get('title').strip()
            dox_href = tr.find('td', {"colspan":"3"} ).find('a').get('href')
            dox_uploader = tr.find('td', {"style":"padding-bottom: 0; max-width: 140px;"} ).text.strip()
            dox_date = tr.find('td', {"class":"text-center r-hide"} ).text.strip()
            
            dox_dict = {
                'title': dox_title,
                'href': dox_href,
                'uploader': dox_uploader,
                'date': dox_date,
            } # dox entry dictionary
            
            if dox_dict not in dox_list: # if dox entry is not in list, add it
                dox_list.append(dox_dict)

        return dox_list # return list of dox entries
    