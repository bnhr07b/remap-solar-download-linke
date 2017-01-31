"""
DOWNLOAD LINKE TURBIDITY COEFFICIENT TOOL
A Python script that downloads Linke turbidity coefficient values
from the SoDA (Solar Radiation Data) webservice (www.soda-is.com)
into a .csv file.

The output .csv file is header-less with the following format
(LON, LAT, JAN, FEB, MAR, APR, MAY, JUN, JUL, AUG, SEP, OCT, NOV, DEC).

NB:
The Tool has only been tested for *buntu (Linux) OS and Python 2.7
The requirements/modules used are found in the included requirements.txt
This Tool is provided under the GNU General Public License v3.0.

Copyright (C) 2015 Ben Hur S. Pintor

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
__author__ = "Ben Hur S. Pintor"
__contact__ = "bhs.pintor<at>gmail.com"


from requests import Session
from robobrowser import RoboBrowser
from osgeo import gdal
from osgeo.gdalconst import *
import pyproj


def map_to_pixel(gtf, mx, my):
    """Transforms map coordinates to pixel coordinates using the geotransform
    parameters of an image.+
    :param gtf: the geotransform parameters
    :param mx: the x map coordinate to be transformed
    :param my: the y map coordinate to be transformed
    :return: the transformed pixel coordinates
    """

    '''Get values of the geotransform parameters.'''
    xorigin = float(gtf[0])
    yorigin = float(gtf[3])
    pixelwidth = float(gtf[1])
    pixelheight = float(gtf[5])

    '''Compute for the transformed pixel coordinates.'''
    px = int((mx - xorigin) / pixelwidth)
    py = int((my - yorigin) / pixelheight)

    return (px, py)


def get_extent_of_DEM(dem_name, crs_epsg, interval):
    """Returns a list containing tuples of lat,long values within the area
    covered by the DEM (disregards NULL values) in order to limit the number
    of downloads to areas within the DEM.

    :param dem: the gdal raster object of the DEM
    :param crs: the coordinate reference system of the input DEM
    :interval: the interval between points to be donwloaded (in degrees)
    :returns: a list of lat,lon tuples
    """

    gdal.AllRegister()
    dem = gdal.Open(dem_name)
    crs = pyproj.Proj(init="epsg:%s" %crs_epsg)
    wgs84 = pyproj.Proj(init="epsg:4326")

    coords = []

    gtf = dem.GetGeoTransform()
    incols = dem.RasterXSize
    inrows = dem.RasterYSize
    band = dem.GetRasterBand(1)
    data = band.ReadAsArray(0, 0, incols, inrows)
    nodata = band.GetNoDataValue()

    xorigin = gtf[0]
    xsize = gtf[1]
    yorigin = gtf[3]
    ysize = gtf[5]
    xlast = xorigin + (xsize * incols)
    ylast = yorigin + (ysize * inrows)

    lonwest, latnorth = pyproj.transform(crs, wgs84, xorigin, yorigin)
    loneast, latsouth = pyproj.transform(crs, wgs84, xlast, ylast)
    lon = lonwest
    lat = latsouth

    while lon < (loneast + (2 * interval)):
        while lat < (latnorth + (2 * interval)):
            mx, my = pyproj.transform(wgs84, crs, lon, lat)
            px, py = map_to_pixel(gtf, mx, my)
            if px > (incols - 1) or py > (inrows - 1):
                pass

            elif px < 0 or py < 0:
                pass

            else:
                if data[py, px] == nodata:
                    pass

                else:
                    coords.append((round(lon, 5), round(lat, 5)))

            lat += interval
        lon += interval
        lat = latsouth

    return coords


def get_linke_values(linke_table):

    linkes = []
    rows = linke_table.find_all('tr')
    for row in rows:
        cols = row.find_all('td')[1:]
        cols = [e.text for e in cols]
        linkes.append(cols)

    return linkes[1:]


def get_monthly_linke_str(linke_list):

    linke = ''
    for x in range(12):
        linke += linke_list[x][1] + ","

    return linke[:-1]


def download_linke(coords, proxy, port, saveFile, saveMode):

    # print proxy,  port
    # print proxy != ''

    url = ("http://www.soda-is.com/eng/services/service_invoke/gui.php?" +
           "xml_descript=soda_tl.xml&Submit2=Month")

    # url = "http://www.soda-pro.com/web-services/atmosphere/turbidity-linke-2003"

    session = Session()
    session.verify = False

    if proxy != '':
        proxies = {proxy: port}
        session.proxies = proxies

    br = RoboBrowser(session=session, parser="lxml")
    br.open(url)

    linke_form = br.get_forms()[1]

    num = len(coords)
    index = 0

    with open(saveFile, saveMode) as f:
        try:
            for coord in coords:
                inlon, inlat = coord
                linke_form['lat'].value = inlat
                linke_form['lon'].value = inlon

                sf = linke_form.submit_fields.getlist('execute')
                br.submit_form(linke_form, submit=sf[0])

                linke_table = br.find("table",
                                      {"cellspacing": "0", "cellpadding": "2"})

                linkes = get_monthly_linke_str(get_linke_values(linke_table))
                s = "%s,%s,%s\n" % (format(inlon, '0.5f'), format(inlat, '0.5f'), linkes)

                if len(s) > 48:
                    f.write(s)
                    print "Done with point %i of %i: (%s, %s)" % (index + 1, num, format(inlon, '0.5f'), format(inlat, '0.5f'))

                index += 1

                br.back()

            print "DONE!"

        except Exception as e:

            not_dl = list(coords[index:])
            with open(saveFile + "_notdownloaded.txt", "w") as nd:
                for c in not_dl:
                    nd.write("%s,%s\n" % (str(c[0]), str(c[1])))
            print e
