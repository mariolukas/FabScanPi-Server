import json
from PIL import Image
import base64
from fabscan.server.services.api.FSBaseHandler import FSBaseHandler
from fabscan.util.FSUtil import json2obj

class FSPreviewHandler(FSBaseHandler):

    def post(self):
        pass

    def create_preview_image(self, data, scan_id):

        object = json2obj(str(data))

        dir_name = self.config.folders.scans
        png = base64.decodestring(object.image[22:])
        image_file = open(dir_name+scan_id+"/"+scan_id+".png", "w")
        image_file.write(png)

        preview_image = dir_name+scan_id+"/"+scan_id+".png"
        thumbnail_image = dir_name+scan_id+"/thumbnail_"+scan_id+".png"

        image_file.close()
        image_file = Image.open(preview_image)
        image_file.thumbnail((160,120),Image.ANTIALIAS)
        image_file.save(thumbnail_image)

        response = dict()
        response['preview_image'] = preview_image
        response['thumbnail_image'] = thumbnail_image
        response['response'] = "PREVIEW_IMAGE_SAVED"

        return response