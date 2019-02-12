# GeoTag
Read and write exif/xmp geotags from/to JPEG images

## Dependencies
* [py3exiv2](https://launchpad.net/py3exiv2)
* [Pillow](https://pillow.readthedocs.io/en/latest/)

## Functions
```python
# Convert decimal lat/lon to degrees, minutes, seconds (dms)
coord_dec_to_dms(coord)

# Convert dms lat to decimal form
# lat_ref specifies N or S
lat_dms_to_dec(lat, lat_ref)

# Convert dms lon to decimal form
# lon_ref specifies E or W
lon_dms_to_dec(lon, lon_ref)

# write geotags (lat, lon, absolute alt, heading, roll, pitch, yaw) to image
write_geo_tag(img_path, lat, lon, alt_abs, hdg=None, roll=None, pitch=None, yaw=None)

# read geotags from an image in the form (lat, lon, abs alt, hdg, roll, pitch, yaw)
read_geo_tag(img_path)
```