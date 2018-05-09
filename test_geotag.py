import unittest, geotag
from PIL import Image


class TestConversionMethods(unittest.TestCase):
    def test_coord_dec_to_dms(self):
        self.assertEqual(geotag.coord_dec_to_dms(0), ((0, 1), (0, 1), (0, 1e7)))
        self.assertEqual(geotag.coord_dec_to_dms(49.1234), ((49, 1), (7, 1), (int(24.24*1e7), 1e7)))
        self.assertEqual(geotag.coord_dec_to_dms(-49.1234), ((49, 1), (7, 1), (int(24.24 * 1e7), 1e7)))
        self.assertEqual(geotag.coord_dec_to_dms(123.123456789), ((123, 1), (7, 1), (244444404, 1e7)))

    def test_lat_dms_to_dec(self):
        self.assertEqual(geotag.lat_dms_to_dec(((0, 1), (0, 1), (0, 1e7)), 'S'), 0)
        self.assertEqual(geotag.lat_dms_to_dec(((0, 1), (0, 1), (0, 1e7)), 'n'), 0)
        self.assertEqual(geotag.lat_dms_to_dec(((33, 1), (7, 1), (244444404, 1e7)), 'S'), -33.1234568)
        self.assertEqual(geotag.lat_dms_to_dec(((33, 1), (7, 1), (244444404, 1e7)), 'N'), 33.1234568)
        self.assertEqual(geotag.lat_dms_to_dec(((68, 1), (56, 1), (492986400, 1e7)), 'S'), -68.9470274)
        self.assertEqual(geotag.lat_dms_to_dec(((90, 1), (0, 1), (0, 1e7)), 'S'), -90)
        self.assertEqual(geotag.lat_dms_to_dec(((90, 1), (0, 1), (0, 1e7)), 'N'), 90)
        with self.assertRaises(ValueError):
            geotag.lat_dms_to_dec(((91, 1), (0, 1), (0, 1)), 's')
        with self.assertRaises(ValueError):
            geotag.lat_dms_to_dec(((90.1, 1), (0, 1), (0, 1)), 'n')
        with self.assertRaises(ValueError):
            geotag.lat_dms_to_dec(((90, 1), (0, 1), (0, 1)), 'e')
            
    def test_lon_dms_to_dec(self):
        self.assertEqual(geotag.lon_dms_to_dec(((0, 1), (0, 1), (0, 1e7)), 'E'), 0)
        self.assertEqual(geotag.lon_dms_to_dec(((0, 1), (0, 1), (0, 1e7)), 'w'), 0)
        self.assertEqual(geotag.lon_dms_to_dec(((33, 1), (7, 1), (244444404, 1e7)), 'W'), -33.1234568)
        self.assertEqual(geotag.lon_dms_to_dec(((33, 1), (7, 1), (244444404, 1e7)), 'E'), 33.1234568)
        self.assertEqual(geotag.lon_dms_to_dec(((145, 1), (56, 1), (45934800, 1e7)), 'e'), 145.9346093)
        self.assertEqual(geotag.lon_dms_to_dec(((180, 1), (0, 1), (0, 1e7)), 'W'), -180)
        self.assertEqual(geotag.lon_dms_to_dec(((180, 1), (0, 1), (0, 1e7)), 'E'), 180)
        with self.assertRaises(ValueError):
            geotag.lon_dms_to_dec(((181, 1), (0, 1), (0, 1)), 'w')
        with self.assertRaises(ValueError):
            geotag.lon_dms_to_dec(((181.1, 1), (0, 1), (0, 1)), 'e')
        with self.assertRaises(ValueError):
            geotag.lon_dms_to_dec(((181.1, 1), (0, 1), (0, 1)), 'n')


class TestHelperFunctions(unittest.TestCase):
    def test_check_lat(self):
        geotag._check_lat(0)
        geotag._check_lat(90)
        geotag._check_lat(-90)
        geotag._check_lat(22.1241948)
        geotag._check_lat(1.00000001)
        with self.assertRaises(ValueError):
            geotag._check_lat(-91)
        with self.assertRaises(ValueError):
            geotag._check_lat(91)
            
    def test_check_lon(self):
        geotag._check_lon(0)
        geotag._check_lon(180)
        geotag._check_lon(-180)
        geotag._check_lon(122.1241948)
        geotag._check_lon(1.00000001)
        with self.assertRaises(ValueError):
            geotag._check_lon(-181)
        with self.assertRaises(ValueError):
            geotag._check_lon(180.0001)
            
    def test_check_hdg(self):
        geotag._check_hdg(0)
        geotag._check_hdg(359.99)
        geotag._check_hdg(180)
        geotag._check_hdg(122.1241948)
        geotag._check_hdg(1.00000001)
        with self.assertRaises(ValueError):
            geotag._check_hdg(-1)
        with self.assertRaises(ValueError):
            geotag._check_hdg(360)
            
    def test_get_lat_ref(self):
        self.assertEqual(geotag._get_lat_ref(0), 'N')
        self.assertEqual(geotag._get_lat_ref(1), 'N')
        self.assertEqual(geotag._get_lat_ref(-1), 'S')
        
    def test_get_lon_ref(self):
        self.assertEqual(geotag._get_lon_ref(0), 'E')
        self.assertEqual(geotag._get_lon_ref(1), 'E')
        self.assertEqual(geotag._get_lon_ref(-1), 'W')
        
    def test_get_alt_ref(self):
        self.assertEqual(geotag._get_alt_ref(0), 0)
        self.assertEqual(geotag._get_alt_ref(1), 0)
        self.assertEqual(geotag._get_alt_ref(-1), 1)

    def test_get_lat_sign(self):
        self.assertEqual(geotag._get_lat_sign('N'), 1)
        self.assertEqual(geotag._get_lat_sign('n'), 1)
        self.assertEqual(geotag._get_lat_sign('S'), -1)
        self.assertEqual(geotag._get_lat_sign('s'), -1)
        with self.assertRaises(ValueError):
            geotag._get_lat_sign('E')
    
    def test_get_lon_sign(self):
        self.assertEqual(geotag._get_lon_sign('E'), 1)
        self.assertEqual(geotag._get_lon_sign('e'), 1)
        self.assertEqual(geotag._get_lon_sign('W'), -1)
        self.assertEqual(geotag._get_lon_sign('w'), -1)
        with self.assertRaises(ValueError):
            geotag._get_lon_sign('N')
            
    def test_get_alt_sign(self):
        self.assertEqual(geotag._get_alt_sign(0), 1)
        self.assertEqual(geotag._get_alt_sign(1), -1)
        with self.assertRaises(ValueError):
            geotag._get_alt_sign(2)


class TestGeoTag(unittest.TestCase):
    def test_read_geo_tag(self):
        self.assertEqual(geotag.read_geo_tag('images/Apples.jpg'),
                         (49.0278408, -122.7727156, 30, None))
        self.assertEqual(geotag.read_geo_tag('images/img60.jpg'),
                         (49.9120223, -98.2690366, 261.64, 45.2))
        self.assertEqual(geotag.read_geo_tag('images/horse.jpg'),
                         (None, None, None, None))

    def test_write_geo_tag(self):
        img = Image.open('images/Apples.jpg')
        img.save('images/Apples_cpy.jpg')
        img.close()
        geotag.write_geo_tag('images/Apples_cpy.jpg', -49.9120223, -98.2690366, 261.64)
        self.assertEqual(geotag.read_geo_tag('images/Apples_cpy.jpg'),
                         (-49.9120223, -98.2690366, 261.64, None))

        img = Image.open('images/horse.jpg')
        img.save('images/horse_cpy.jpg')
        img.close()
        geotag.write_geo_tag('images/horse_cpy.jpg', -83.0923535, -0.9235098, 189.99, 359.99)
        self.assertEqual(geotag.read_geo_tag('images/horse_cpy.jpg'),
                         (-83.0923535, -0.9235098, 189.99, 359.99))


if __name__ == '__main__':
    unittest.main()