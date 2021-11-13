from urllib.request import urlopen
from collections import namedtuple
from tempfile import NamedTemporaryFile
from shutil import copyfileobj
import os
import cv2

Region = namedtuple('Region', ['x','y','w','h'])

class ExtractRegionService:
    def download(self, image_url):
        with urlopen(image_url) as response:
            with NamedTemporaryFile(delete=False) as tmpfile:
                copyfileobj(response, tmpfile)
                return tmpfile

    def extract_contours(self, image):
        imgray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        ret,thresh = cv2.threshold(imgray,127,255,cv2.THRESH_BINARY_INV)
        return cv2.findContours(thresh,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)[-2:]

    def isbox(self, contour, area_eps=0.1):
        x,y,w,h = cv2.boundingRect(contour)
        hull = cv2.convexHull(contour)
        area = cv2.contourArea(hull)
        # TODO: この辺のパラメータがベタ書きなのはどうする？
        if w <10 or h < 10 or 500 <w or 500 < h:
            return False
        return (1 - area_eps) < w*h/area < (1 + area_eps)

    def extract(self, image_url):
        try:
            image_file = self.download(image_url)
        except Exception as e:
            raise Exception('画像ダウンロードに失敗しました') from e
        # 画像からスペースっぽい領域抽出
        regions = []
        try:
            image = cv2.imread(image_file.name)
            contours, hierarchy = self.extract_contours(image)
            for contour, hi in zip(contours, hierarchy[0]):
                if self.isbox(contour) and hi[2] == -1:# スペースっぽい四角で入れ子じゃないもの
                    x,y,w,h = cv2.boundingRect(contour)
                    regions.append(Region(x,y,w,h))
            return regions
        except Exception as e:
            raise Exception('画像の解析に失敗しました') from e
        finally:
            os.unlink(image_file.name)

