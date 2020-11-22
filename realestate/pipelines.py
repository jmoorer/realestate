# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json
import os
from firebase_admin.storage import bucket
from itemadapter import ItemAdapter
from geopy.geocoders import GoogleV3
import pygeohash as pgh
from scrapy.exceptions import DropItem
from firebase_admin import credentials, firestore, initialize_app
from firebase_admin import storage

import urllib.request


dir = os.path.dirname(__file__)
output_file = os.path.join(dir, 'zillow.csv')
json_out_file= os.path.join(dir,'zillow.jsonl')
geo_locator = GoogleV3(api_key=os.environ.get('MAP_KEY'))
cred = credentials.Certificate(os.path.join(dir, 'account.json'))
bucket_name=os.environ.get('BUCKET')
initialize_app(cred, {
    'storageBucket':bucket_name
})

class GeoPipeline:
    def process_item(self, item, spider):
        address= item['address']
        location = geo_locator.geocode(address).raw['geometry']['location']
        hash = pgh.encode(location['lat'], location['lng'])
        item['geohash']= hash
        item['longitude']= location['lng']
        item['latitude']= location['lat']

        return item

class JsonWriterPipeline:
    
    def open_spider(self, spider):
        self.file = open('rentals.jl', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(ItemAdapter(item).asdict()) + "\n"
        self.file.write(line)
        return item



class ImagePipeline:

    bucket = storage.bucket()

    def open_spider(self, spider):
       pass

    def close_spider(self, spider):
       pass

    async def process_item(self, item, spider):

        image_url= item["image"]
        id = item['id']
        file = urllib.request.urlopen(image_url)
        file_name=f"{id}/poster.jpeg"
        blob = self.bucket.blob(file_name)
        blob.upload_from_string(file.read(), content_type='image/jpg')
        item['image']='https://%(bucket)s.storage.googleapis.com/%(file)s' % {'bucket':bucket_name, 'file':file_name}
        return item


class FireStorePipeline(object):

    collection_name = "rentals"
    def __init__(self):
        self.store = firestore.client()

    def process_item(self, item, spider):
        valid = True
        for data in item:
            if not data:
                valid = False
                raise DropItem("Missing {0}!".format(data))
        if valid:
            doc_ref = self.store.collection(self.collection_name).add(dict(item))
            print(f"{doc_ref}")
        return item