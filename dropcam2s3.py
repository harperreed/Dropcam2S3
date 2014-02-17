import boto
import datetime
from dropcam import Dropcam
import json
import logging
import StringIO
from slugify import slugify
import sys

# Yay!
#  ____  ____   __  ____   ___   __   _  _    ____    ____  ____
# (    \(  _ \ /  \(  _ \ / __) / _\ ( \/ )  (___ \  / ___)( __ \
#  ) D ( )   /(  O )) __/( (__ /    \/ \/ \   / __/  \___ \ (__ (
# (____/(__\_) \__/(__)   \___)\_/\_/\_)(_/  (____)  (____/(____/
#
# A quick script to post your dropcam cam snaps to s3.
#
# Upload this to iron.io and BAM your dropcam images will go to s3 magically.
#


#handle Iron.io payload args
payload_file = None
payload = None

for i in range(len(sys.argv)):
    if sys.argv[i] == "-payload" and (i + 1) < len(sys.argv):
        payload_file = sys.argv[i + 1]
        with open(payload_file, 'r') as f:
            payload = json.loads(f.read())
        break


DROPCAM_USERNAME = payload['DROPCAM_USERNAME']
DROPCAM_PASSWORD = payload['DROPCAM_PASSWORD']
AWS_ACCESS_KEY_ID = payload['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = payload['AWS_SECRET_ACCESS_KEY']
AWS_STORAGE_BUCKET_NAME = payload['AWS_STORAGE_BUCKET_NAME']


#Set up logger
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

#connect to s3!
s3_connection = boto.connect_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
bucket_name = AWS_STORAGE_BUCKET_NAME
bucket = s3_connection.get_bucket(bucket_name)

#Let's do the magic
log.info('Logging into Dropcam')
dropcam = Dropcam(DROPCAM_USERNAME, DROPCAM_PASSWORD)
log.info("Grabbing cameras")
for camera in dropcam.cameras():
    log.info("Grabbing image from " + camera.title)
    filename = "camera " + str(camera.id) + " " + str(camera.title) + " " + str(datetime.datetime.now().strftime("%Y-%m-%d.%H:%M:%S"))
    filename = slugify(unicode(filename))
    full_path_filename = slugify(unicode(camera.title)) + "/" + str(datetime.datetime.now().strftime("%Y/%m/%d/")) + filename + ".jpg"
    key = bucket.new_key(full_path_filename)
    log.info("Downloading image")
    image_response = camera.get_image()
    fp = StringIO.StringIO(image_response.read())   # Wrap object
    log.info("Uploading image to s3")
    key.set_contents_from_file(fp)

log.info('Done pulling images')
