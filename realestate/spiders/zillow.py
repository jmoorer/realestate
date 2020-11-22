import csv
import json
import os
import re


import scrapy
from scrapy import Request
import urllib
from realestate.items import Property



class ZillowScraper(scrapy.Spider):
    name = 'zillow'
    start_urls = [
        'https://www.zillow.com/homes/Washington,-DC_rb/',
        'https://www.zillow.com/homes/Prince-Georges-County,-MD_rb/',
        'https://www.zillow.com/homes/Montgomery-County,-MD_rb/',
        'https://www.zillow.com/homes/Fairfax-County,-VA_rb/',
        'https://www.zillow.com/homes/Prince-William-County,-VA_rb/'
    ]
    base_url = 'https://www.zillow.com/'
    custom_settings = {
        'DEPTH_LIMIT': 1
    }


    headers = {
        # 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        # 'accept-encoding': 'gzip, deflate, br',
        # 'accept-language': 'en-US,en;q=0.9',
        # 'cache-control': 'no-cache',
        # 'cookie': 'zguid=23|%2403435e76-0699-4a32-b86d-77d033c907ef; _ga=GA1.2.1271511001.1575011821; zjs_user_id=null; zjs_anonymous_id=%2203435e76-0699-4a32-b86d-77d033c907ef%22; _gcl_au=1.1.1333357279.1575011822; _pxvid=3cfcc163-1278-11ea-bff8-0242ac12000b; ki_r=; __gads=ID=84d8013cfac6df96:T=1575012041:S=ALNI_MaSvVNZsir2JXJ17pv54bjsPuyfcw; ki_s=199442%3A0.0.0.0.0%3B199444%3A0.0.0.0.2; zgsession=1|c0999376-b167-4a47-a1cd-0e456d882d4e; _gid=GA1.2.55965867.1578668946; JSESSIONID=87D0662A6BC141A73F0D12620788519C; KruxPixel=true; DoubleClickSession=true; KruxAddition=true; ki_t=1575011869563%3B1578669044158%3B1578669044158%3B2%3B10; _pxff_tm=1; _px3=2e6809e35ce7e076934ff998c2bdb8140e8b793b53e08a27c5da11f1b4760755:DFItCmrETuS2OQcztcFmt0FYPUn00ihAAue2ynQgbfSq6H+p2yP3Rl3aeyls3Unr1VRJSgcNue8Rr1SUq4P1jA==:1000:9ueZvAJ6v5y4ny7psGF25dK+d3GlytY2Bh+Xj9UUhC4DaioIZ+FMXPU0mOX+Qnghqut0jIT61gLecN4fyu6qXaPDlBX6YsZVbIry1YyBN/37l0Ri3JP+E0h+m+QEBB+bqb6MbE2HtgGBJRJAry8dgOKGM5JtBGdX+X/nuQX1xaw=; AWSALB=E6JYC43gXQRlE2jPT9e2vAQOYPvdHnccBlqi0mcXevYExTaHro0M+uo/Qxahi6JyLz9LpotY9eLtEbYrAOeQXcCm6UhjWnTopQHernmjlR/ibE6JmE8F6tReiBn4; search=6|1581261153229%7Crect%3D40.96202658306895%252C-73.55498286718745%252C40.4487909557045%252C-74.40093013281245%26rid%3D6181%26disp%3Dmap%26mdm%3Dauto%26p%3D3%26z%3D0%26lt%3Dfsbo%26pt%3Dpmf%252Cpf%26fs%3D1%26fr%3D0%26mmm%3D1%26rs%3D0%26ah%3D0%26singlestory%3D0%26housing-connector%3D0%26abo%3D0%26garage%3D0%26pool%3D0%26ac%3D0%26waterfront%3D0%26finished%3D0%26unfinished%3D0%26cityview%3D0%26mountainview%3D0%26parkview%3D0%26waterview%3D0%26hoadata%3D1%26zillow-owned%3D0%09%01%096181%09%09%09%090%09US_%09',
        # 'pragma': 'no-cache',
        # 'upgrade-insecure-requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36'
    }
    params = {
        'searchQueryState': '{"pagination":{},"usersSearchTerm":"Washington, DC","mapBounds":{"west":-77.84877117138515,"east":-76.17994782861481,"south":38.279802942377074,"north":39.513151798270144},"isMapVisible":true,"filterState":{"fsba":{"value":false},"fsbo":{"value":false},"nc":{"value":false},"fore":{"value":false},"cmsn":{"value":false},"auc":{"value":false},"pmf":{"value":false},"pf":{"value":false},"fr":{"value":true},"ah":{"value":true},"mf":{"value":false},"manu":{"value":false},"land":{"value":false},"tow":{"value":false},"apa":{"value":false}},"isListVisible":true,"mapZoom":9}'
    }



    def start_requests(self):
        for url in self.start_urls:
            for page in range(1, 20):
                parsed_params = json.loads(self.params['searchQueryState'])
                parsed_params['pagination']['currentPage'] = str(page)
                # update string query parameters
                params = {'searchQueryState': json.dumps(parsed_params).replace(' ', '')}
                next_page = url + '?' + urllib.parse.urlencode(params)
                yield Request(url=next_page, callback=self.parse, headers=self.headers,
                              meta={
                                # "proxy": "http://localhost:8888/", 
                                # 'dont_redirect': True
                              })



    def parse(self, response, **kwargs):
        # card.find("a",class_="list-card-link").get("href")
        prop = Property()
        raw = response.css('script[data-zrr-shared-data-key=mobileSearchPageStore]').xpath('node()').extract_first()
        raw_data = json.loads(raw.replace("<!--", "").replace("-->", ""))

        items = raw_data['cat1']['searchResults']['listResults']
        imagesMap = dict((x['id'], x['imgSrc']) for x in items)

        for card in response.css('article.list-card'):
            details = card.css('ul.list-card-details > li')
            link= card.css("a.list-card-link::attr(href)").extract_first()
            id=card.xpath('@id').extract_first().replace("zpid_","")
            try:
                rent = int(asDigits(card.css('.list-card-price::text').extract_first()))
            except:
                rent = 0

            try:
                sqft = int(asDigits(details[2].xpath('text()').extract_first()))
            except:
                sqft = 0

            try:
                beds = int(details[0].xpath('text()').extract_first())
            except:
                beds = 0

            try:
                baths = float(details[1].xpath('text()').extract_first())
            except:
                baths = 0
            if id and len(details) == 3 and not link.startswith("/b/") and rent and baths and beds and sqft:

                address = card.css('.list-card-addr::text').extract_first()
                prop['id']= id
                prop['beds'] = beds
                prop['baths'] = baths
                prop['sqft'] = sqft
                prop['address'] = address
                prop['link'] = card.css("a.list-card-link::attr(href)").extract_first()
                prop['rent'] = int(asDigits(card.css('.list-card-price::text').extract_first()))
                prop['image']= imagesMap[id]
                #  Number($el.find('.list-card-price').text().replace(/\D/g, ''))
                yield prop

            else :
                pass
                # print('--------')
                # print(response.url)
                #
                # for  d in details:
                #     print(d.extract())
                # print('--------')

    def closed(self,r):
        pass
        # if r=='finished' and self.recordCount>0:
        #     ingest_json(self.json_out_file)
        # pass;

    # def saveCsv(self,data):
    #     with open(self.output_file, 'a', newline='') as f:
    #         writer = csv.DictWriter(f, fieldnames=data.keys())
    #         if self.recordCount == 0:
    #             writer.writeheader()
    #         writer.writerow(data)
    #         self.recordCount += 1
    #         print(f'data written :{self.recordCount}' )

    # def saveJson(self, data):
    #      with jsonlines.open(self.json_out_file, 'a') as writer:
    #         writer.write(data)
    #         self.recordCount += 1
    #         print(f'data written :{self.recordCount}')

def asDigits(s):
    return re.sub('[^0-9]', '',s)