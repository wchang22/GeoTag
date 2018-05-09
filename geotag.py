import piexif
from PIL import Image

# --------------------------------------------------
# Conversion Functions
# --------------------------------------------------


def coord_dec_to_dms(coord):
    """
    Convert decimal lat/lon to degrees, minutes, seconds
    without reference
    """
    abs_coord = abs(_check_lon(coord))
    d = int(abs_coord)
    m = int((abs_coord - d) * 60)
    s = (abs_coord - d - m/60.0) * 3600
    return (d, 1), (m, 1), (int(s*1e7), int(1e7))


def lat_dms_to_dec(lat, lat_ref):
    """
    Convert dms lat to signed decimal form
    """
    dec = abs(_check_lat(lat[0][0]))
    dec += lat[1][0] / 60.0
    dec += lat[2][0] / lat[2][1] / 3600
    return round(_get_lat_sign(lat_ref) * dec, 7)


def lon_dms_to_dec(lon, lon_ref):
    """
    Convert dms lat to signed decimal form
    """
    dec = abs(_check_lon(lon[0][0]))
    dec += lon[1][0] / 60.0
    dec += lon[2][0] / lon[2][1] / 3600
    return round(_get_lon_sign(lon_ref) * dec, 7)


# --------------------------------------------------
# Helper Functions
# --------------------------------------------------


def _check_lat(lat):
    """
    Check if the latitude is valid
    """
    if abs(lat) > 90:
        raise ValueError('Lat out of range')
    return lat


def _get_lat_ref(lat):
    """
    Get reference of latitude
    Return: If latitude is 0 or greater, N
            If latitude is less than 0, S
    """
    return 'N' if _check_lat(lat) >= 0 else 'S'


def _get_lat_sign(lat_ref):
    """
    Get sign of latitude
    Return: If latitude ref is N, +
            If latitude ref is S, -
    """
    if lat_ref == 'N' or lat_ref == 'n':
        return 1
    elif lat_ref == 'S' or lat_ref == 's':
        return -1
    raise ValueError('Invalid lat ref')


def _check_lon(lon):
    """
    Check if the longitude is valid
    """
    if abs(lon) > 180:
        raise ValueError('Lon out of range')
    return lon


def _get_lon_ref(lon):
    """
    Get reference of longitude
    Return: If longitude is 0 or greater, E
            If longitude is less than 0, W
    """
    return 'E' if _check_lon(lon) >= 0 else 'W'


def _get_lon_sign(lon_ref):
    """
    Get sign of longitude
    Return: If longitude ref is E, +
            If longitude ref is W, -
    """
    if lon_ref == 'E' or lon_ref == 'e':
        return 1
    elif lon_ref == 'W' or lon_ref == 'w':
        return -1
    raise ValueError('Invalid lon ref')


def _get_alt_ref(alt):
    """
    Get reference of absolute altitude
    Return: If altitude is above sea level, 0
            If altitude is below sea level, 1
    """
    return 0 if alt >= 0 else 1


def _get_alt_sign(alt_ref):
    """
    Get sign of altitude
    Return: If altitude ref is 0, +
            If altitude ref is 1, -
    """
    if alt_ref == 0:
        return 1
    elif alt_ref == 1:
        return -1
    raise ValueError('Invalid alt ref')


def _check_hdg(hdg):
    """
    Check if the heading is valid
    """
    if hdg < 0 or hdg > 359.99:
        raise ValueError('Invalid hdg')
    return hdg


# --------------------------------------------------
# Read/Write Functions
# --------------------------------------------------


def write_geo_tag(img_path, lat, lon, alt_abs, hdg=None):
    """
    Writes latitude, longitude, absolute altitude, heading
    metadata into JPG image
    """
    img = Image.open(img_path)
    if img.format != 'JPEG':
        raise ValueError('Image is not a JPEG')

    try:
        exif_dict = piexif.load(img.info['exif'])
    except KeyError:
        exif_dict = {'GPS': {}}
    
    exif_dict['GPS'].setdefault(piexif.GPSIFD.GPSLatitude, 0)
    exif_dict['GPS'][piexif.GPSIFD.GPSLatitude] = coord_dec_to_dms(lat)
    exif_dict['GPS'].setdefault(piexif.GPSIFD.GPSLatitudeRef, 0)
    exif_dict['GPS'][piexif.GPSIFD.GPSLatitudeRef] = _get_lat_ref(lat)
    exif_dict['GPS'].setdefault(piexif.GPSIFD.GPSLongitude, 0)
    exif_dict['GPS'][piexif.GPSIFD.GPSLongitude] = coord_dec_to_dms(lon)
    exif_dict['GPS'].setdefault(piexif.GPSIFD.GPSLongitudeRef, 0)
    exif_dict['GPS'][piexif.GPSIFD.GPSLongitudeRef] = _get_lon_ref(lon)
    exif_dict['GPS'].setdefault(piexif.GPSIFD.GPSAltitude, 0)
    exif_dict['GPS'][piexif.GPSIFD.GPSAltitude] = (int(alt_abs*1e7), int(1e7))
    exif_dict['GPS'].setdefault(piexif.GPSIFD.GPSAltitudeRef, 0)
    exif_dict['GPS'][piexif.GPSIFD.GPSAltitudeRef] = _get_alt_ref(alt_abs)
    if hdg is not None:
        exif_dict['GPS'].setdefault(piexif.GPSIFD.GPSImgDirection, 0)
        exif_dict['GPS'][piexif.GPSIFD.GPSImgDirection] = \
        (int(_check_hdg(hdg) * 100), 100)
    exif_bytes = piexif.dump(exif_dict)
    
    img.save(img_path, 'jpeg', exif=exif_bytes)
    img.close()


def read_geo_tag(img_path):
    """
    Reads latitude, longitude, absolute altitude, heading
    metadata from a JPG image as a tuple
    """
    img = Image.open(img_path)
    if img.format != 'JPEG':
        raise ValueError('Image is not a JPEG')

    if 'exif' not in img.info.keys():
        return None, None, None, None

    exif_dict = piexif.load(img.info['exif'])

    try: 
        lat_ref = exif_dict['GPS'].get(
                  piexif.GPSIFD.GPSLatitudeRef, bytes('N', 'utf-8')) \
                  .decode('utf-8')
        lat = lat_dms_to_dec(exif_dict['GPS'][piexif.GPSIFD.GPSLatitude],
                             lat_ref)
    except KeyError:
        lat = None

    try:
        lon_ref = exif_dict['GPS'].get(
                  piexif.GPSIFD.GPSLongitudeRef, bytes('E', 'utf-8')) \
                  .decode('utf-8')
        lon = lon_dms_to_dec(exif_dict['GPS'][piexif.GPSIFD.GPSLongitude],
                             lon_ref)
    except KeyError:
        lon = None

    try:
        alt_sign = _get_alt_sign(exif_dict['GPS']
                                 .get(piexif.GPSIFD.GPSAltitudeRef, 1))        
        alt = alt_sign * \
              round(exif_dict['GPS'][piexif.GPSIFD.GPSAltitude][0] /
                    exif_dict['GPS'][piexif.GPSIFD.GPSAltitude][1], 7)
    except KeyError:
        alt = None

    try:
        hdg = round(exif_dict['GPS'][piexif.GPSIFD.GPSImgDirection][0] /
                    exif_dict['GPS'][piexif.GPSIFD.GPSImgDirection][1], 2)
    except KeyError:
        hdg = None
    
    img.close()
    return lat, lon, alt, hdg
