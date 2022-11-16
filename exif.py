import exifread
import requests

import config


def get_tag(tags, key):
    tag = tags.get(key)
    return None if tag is None else tag.printable


def get_decimal_gps(tags):
    lat_retional = get_tag(tags, 'GPS GPSLatitude')
    lat_ref = get_tag(tags, 'GPS GPSLatitudeRef')
    long_retional = get_tag(tags, 'GPS GPSLongitude')
    long_ref = get_tag(tags, 'GPS GPSLongitudeRef')

    if lat_retional is None or long_retional is None:
        return (None, None)

    def eval(s):
        expressions = s.strip().split('/')
        return float(expressions[0]) if len(expressions) == 1 else float(expressions[0]) / float(expressions[1])

    lat = [eval(x) for x in lat_retional[1:-1].split(',')]
    lat = lat[0] + lat[1] / 60 + lat[2] / 3600

    long = [eval(x) for x in long_retional[1:-1].split(',')]
    long = long[0] + long[1] / 60 + long[2] / 3600

    if not lat_ref == 'N':
        lat = lat * -1
    if not long_ref == 'E':
        long = long * -1

    return (lat, long)


def get_location(lat, long):
    """
        使用百度地图Web Api逆查询地址
    """
    url = 'https://api.map.baidu.com/reverse_geocoding/v3/'
    r = requests.get(url, params={
        'ak': config.baidu_lbs_key,
        'output': 'json',
        'coordtype': 'wgs84ll',
        'location': f"{lat},{long}",
        'language': 'zh-CN',
    })
    data = r.json()
    print(data)
    return data['result']['formatted_address']


def get_brief_exif(f):
    tags = exifread.process_file(f, details=True)
    # for tag in tags.keys():
    #     if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
    #         print(f"Key {tag}, {type(tags[tag])} Value {tags[tag].printable}")
    return {
        '拍摄时间': get_tag(tags, 'EXIF DateTimeOriginal'),
        '照相机制造商': get_tag(tags, 'Image Make'),
        '照相机型号': get_tag(tags, 'Image Model'),
        '照片尺寸': (get_tag(tags, 'EXIF ExifImageWidth'), get_tag(tags, "EXIF ExifImageLength")),
        '经纬度': get_decimal_gps(tags),
        '地址': get_location(*get_decimal_gps(tags)),
    }

if __name__ == '__main__':
    with open('1.jpg', 'rb') as f:
        exif = get_brief_exif(f)
        print(exif)
