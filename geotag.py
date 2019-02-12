import pyexiv2
from PIL import Image
from fractions import Fraction

# --------------------------------------------------
# Conversion Functions
# --------------------------------------------------


def coord_dec_to_dms(coord):
    """Convert decimal lat/lon to degrees, minutes, seconds
    without reference
    
    Arguments:
        coord {float} -- coordinate in decimal degrees
    
    Returns:
        (Fraction, Fraction, Fraction) -- coordinate in dms
    """
    abs_coord = abs(_check_lon(coord))
    d = int(abs_coord)
    m = int((abs_coord - d) * 60)
    s = (abs_coord - d - m/60.0) * 3600
    return Fraction(d, 1), Fraction(m, 1), Fraction(int(s*1e7), int(1e7))


def lat_dms_to_dec(lat, lat_ref):
    """Convert latitude in degrees, minutes, seconds
    to decimal degrees

    Arguments:
        coord {(Fraction, Fraction, Fraction)} -- latitude in dms

    Returns:
        {float} -- latitude in decimal degrees
    """
    dec = abs(_check_lat(lat[0].numerator))
    dec += lat[1].numerator / 60.0
    dec += lat[2].numerator / lat[2].denominator / 3600
    return round(_get_lat_sign(lat_ref) * dec, 7)


def lon_dms_to_dec(lon, lon_ref):
    """Convert longitude in degrees, minutes, seconds
    to decimal degrees

    Arguments:
        coord {(Fraction, Fraction, Fraction)} -- longitude in dms

    Returns:
        {float} -- longitude in decimal degrees
    """
    dec = abs(_check_lon(lon[0].numerator))
    dec += lon[1].numerator / 60.0
    dec += lon[2].numerator / lon[2].denominator / 3600
    return round(_get_lon_sign(lon_ref) * dec, 7)


# --------------------------------------------------
# Helper Functions
# --------------------------------------------------


def _check_lat(lat):
    """Check if the latitude is valid (between -90 and 90 inclusive)
    
    Arguments:
        lat {float} -- latitude in decimal degrees
    
    Returns:
        float -- latitude in decimal degrees

    Raises:
        ValueError -- if latitude is out of range
    """
    if abs(lat) > 90:
        raise ValueError('Lat out of range')
    return lat


def _get_lat_ref(lat):
    """Get reference of latitude
    
    Arguments:
        lat {float} -- latitude in decimal degrees

    Returns:
        string -- If latitude is 0 or greater, N
                  If latitude is less than 0, S
    """
    return 'N' if _check_lat(lat) >= 0 else 'S'


def _get_lat_sign(lat_ref):
    """Get sign of latitude
    
    Arguments:
        lat_ref {string} -- Reference of latitude (i.e. 'N', 'S')
    
    Returns:
        int -- If latitude ref is N, 1
               If latitude ref is S, -1

    Raises:
        ValueError -- if latitude is not 'N', 'n', 'S', 's'
    """
    if lat_ref == 'N' or lat_ref == 'n':
        return 1
    elif lat_ref == 'S' or lat_ref == 's':
        return -1
    raise ValueError('Invalid lat ref')


def _check_lon(lon):
    """Check if the longitude is valid (between -180 and 180 inclusive)
    
    Arguments:
        lon {float} -- longitude in decimal degrees
    
    Returns:
        float -- longitude in decimal degrees

    Raises:
        ValueError -- if longitude is out of range
    """
    if abs(lon) > 180:
        raise ValueError('Lon out of range')
    return lon


def _get_lon_ref(lon):
    """Get reference of longitude
    
    Arguments:
        lon {float} -- longitude in decimal degrees

    Returns:
        string -- If longitude is 0 or greater, E
                  If longitude is less than 0, W
    """
    return 'E' if _check_lon(lon) >= 0 else 'W'


def _get_lon_sign(lon_ref):
    """Get sign of longitude
    
    Arguments:
        lat_ref {string} -- Reference of longitude (i.e. 'E', 'W')
    
    Returns:
        int -- If longitude ref is E, 1
               If longitude ref is W, -1

    Raises:
        ValueError -- if longitude is not 'E', 'e', 'W', 'w'
    """
    if lon_ref == 'E' or lon_ref == 'e':
        return 1
    elif lon_ref == 'W' or lon_ref == 'w':
        return -1
    raise ValueError('Invalid lon ref')


def _get_alt_ref(alt):
    """Get reference of absolute altitude
    
    Arguments:
        alt {float} -- altitude in metres
    
    Returns:
        byte -- If altitude is above sea level, 0
                If altitude is below sea level, 1
    """
    return b'0' if alt >= 0 else b'1'


def _get_alt_sign(alt_ref):
    """Get sign of altitude
    
    Arguments:
        alt_ref {str} -- Altitude reference (0 for above, 1 for below)

    Returns:
        int -- If altitude ref is 0, 1
                If altitude ref is 1, -1
    
    Raises:
        ValueError -- if not 0 or 1
    """
    if alt_ref == '0':
        return 1
    elif alt_ref == '1':
        return -1
    raise ValueError('Invalid alt ref')


def _check_angle(angle):
    """Check if the angle is valid (between 0 (inclusive) and 360 (exclusive))
    
    Arguments:
        angle {float} -- angle in degrees
    
    Returns:
        angle -- angle in degrees

    Raises:
        ValueError -- if angle is out of range
    """
    if angle < 0 or angle > 359.99:
        raise ValueError('Invalid angle')
    return angle


# --------------------------------------------------
# Read/Write Functions
# --------------------------------------------------
# Register custom Attitude namespace to store roll, pitch, yaw
pyexiv2.xmp.register_namespace('attitude/', 'Attitude')


def write_geo_tag(img_path, lat, lon, alt_abs, hdg=None, roll=None, pitch=None, yaw=None):
    """Writes geotags to an image

    Arguments:
        img_path {str} -- Path to image
        lat {float} -- latitude, in decimal degrees
        lon {float} -- longitude, in decimal degrees
        alt_abs {float} -- absolute altitude, in metres

    Keyword Arguments:
        hdg {float} -- Heading, in degrees (default: {None})
        roll {float} -- Roll, in degrees (default: {None})
        pitch {float} -- Pitch, in degrees (default: {None})
        yaw {float} -- Yaw, in degrees (default: {None})

    Raises:
        ValueError -- if image is not a JPEG or MPO
    """

    # Only JPEG and MPO have metadata
    img = Image.open(img_path)
    if not (img.format == 'JPEG' or img.format == "MPO"):
        raise ValueError('Image is not a JPEG or MPO')
    img.close()

    metadata = pyexiv2.ImageMetadata(img_path)
    metadata.read()

    # Add standard Exif Tags
    tags = ['Exif.GPSInfo.GPSLatitude', 'Exif.GPSInfo.GPSLatitudeRef',
            'Exif.GPSInfo.GPSLongitude', 'Exif.GPSInfo.GPSLongitudeRef',
            'Exif.GPSInfo.GPSAltitude', 'Exif.GPSInfo.GPSAltitudeRef']
    values = [coord_dec_to_dms(lat), _get_lat_ref(lat), coord_dec_to_dms(lon),
              _get_lon_ref(lon), Fraction(int(alt_abs*1e7), int(1e7)),
              _get_alt_ref(alt_abs)]

    for (tag, value) in zip(tags, values):
        metadata[tag] = pyexiv2.ExifTag(tag, value)

    if hdg is not None:
        tag = 'Exif.GPSInfo.GPSImgDirection'
        metadata[tag] = pyexiv2.ExifTag(tag, Fraction(int(_check_angle(hdg) * 100), 100))

    # Add roll, pitch, yaw as custom Xmp tags
    tags = ['Xmp.Attitude.Roll', 'Xmp.Attitude.Pitch', 'Xmp.Attitude.Yaw']
    values = [roll, pitch, yaw]
    attitudes = [roll, pitch, yaw]

    for (attitude, tag, value) in zip(attitudes, tags, values):
        if attitude is not None:
            metadata[tag] = pyexiv2.XmpTag(tag, str(_check_angle(value)))

    metadata.write()


def read_geo_tag(img_path):
    """Reads geotags to an image

    Arguments:
        img_path {str} -- Path to image

    Raises:
        ValueError -- if image is not a JPEG or MPO

    Returns:
        dict --
        lat -- latitude, in decimal degrees
        lon -- longitude, in decimal degrees
        alt_abs -- absolute altitude, in metres
        hdg -- Heading, in degrees
        roll -- Roll, in degrees
        pitch -- Pitch, in degrees
        yaw -- Yaw, in degrees
    """
    # Only JPEG and MPO have metadata
    img = Image.open(img_path)
    if not (img.format == 'JPEG' or img.format == "MPO"):
        raise ValueError('Image is not a JPEG or MPO')
    img.close()

    metadata = pyexiv2.ImageMetadata(img_path)
    metadata.read()

    lat = lon = alt = hdg = roll = pitch = yaw = None

    # Extract exif tags
    tag = 'Exif.GPSInfo.GPSLatitude'
    tag_ref = 'Exif.GPSInfo.GPSLatitudeRef'
    if tag in metadata.exif_keys and tag_ref in metadata.exif_keys:
        lat_ref = metadata[tag_ref].value
        lat = lat_dms_to_dec(metadata[tag].value, lat_ref)

    tag = 'Exif.GPSInfo.GPSLongitude'
    tag_ref = 'Exif.GPSInfo.GPSLongitudeRef'
    if tag in metadata.exif_keys and tag_ref in metadata.exif_keys:
        lon_ref = metadata[tag_ref].value
        lon = lon_dms_to_dec(metadata[tag].value, lon_ref)

    tag = 'Exif.GPSInfo.GPSAltitude'
    tag_ref = 'Exif.GPSInfo.GPSAltitudeRef'
    if tag in metadata.exif_keys and tag_ref in metadata.exif_keys:
        alt_sign = _get_alt_sign(metadata[tag_ref].value)
        alt = alt_sign * round(metadata[tag].value.numerator
                               / metadata[tag].value.denominator, 7)

    tag = 'Exif.GPSInfo.GPSImgDirection'
    if tag in metadata.exif_keys:
        hdg = round(metadata[tag].value.numerator / metadata[tag].value.denominator, 2)

    # Extract our custom xmp tags
    tags = ['Xmp.Attitude.Roll', 'Xmp.Attitude.Pitch', 'Xmp.Attitude.Yaw']

    if tags[0] in metadata.xmp_keys:
        roll = float(metadata[tags[0]].value)

    if tags[1] in metadata.xmp_keys:
        pitch = float(metadata[tags[1]].value)

    if tags[2] in metadata.xmp_keys:
        yaw = float(metadata[tags[2]].value)

    return {
        'lat': lat,
        'lon': lon,
        'alt': alt,
        'hdg': hdg,
        'roll': roll,
        'pitch': pitch,
        'yaw': yaw,
    }
