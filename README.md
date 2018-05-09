# GeoTag
Read and write exif geotags from JPEG images

## Dependencies
* [Piexif](https://github.com/hMatoba/Piexif)

## Functions
* <i>coord_dec_to_dms(coord)</i>
  * Convert decimal lat/lon to degrees, minutes, seconds (dms)
* <i>lat_dms_to_dec(lat, lat_ref)</i>
  * Convert dms lat to decimal form
  * lat_ref specifies N or S
* <i>lon_dms_to_dec(lon, lon_ref)</i>
  * Convert dms lon to decimal form
  * lon_ref specifies E or W
* <i>write_geo_tag(img_path, lat, lon, alt_abs, hdg=None)</i>
  * write exif geo tags (lat, lon, absolute alt, optional heading) to image
* <i>read_geo_tag(img_path)</i>
  * read exif geo tags from an image in the form (lat, lon, abs alt, hdg)
