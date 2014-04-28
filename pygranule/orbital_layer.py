from datetime import datetime, timedelta
import numpy as np
from pyproj import Proj
from shapely import geometry

from abc import ABCMeta, abstractmethod

class OrbitalLayerError(Exception):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class OrbitalLayer(object):
    """
    Defines a common interface for accessing orbital
    information from an orbital package, such as
    pyorbital. This forms a convenient layer (model) between
    getsat and the orbital module.
    """
    __metaclass__ = ABCMeta

    instrument_info_db = {'AVHRR':{'scan_steps':2048},
                          'MODIS':{}}
    earth_radius = 6.37e6
    proj_out_of_bounds_value = 1.0e30

    def __init__(self, aoi, sat, instrument="AVHRR"):
        self.aoi = np.array([ [x for (x,y) in aoi],[y for (x,y) in aoi] ])
        self.sat = sat
        self.instrument = instrument
        self.instrument_info = self.instrument_info_db[instrument]

        # init working projection for aoi/observation polygons
        clon,clat = self.aoi_center()
        self.working_projection = {'proj':'ortho', 'lon_0':clon, 'lat_0':clat}
        self.proj = Proj(**self.working_projection)

    @abstractmethod
    def next_transit(self, start=datetime.now(), resolution=100):
        """
        Next transit time relative to center of aoi.
        Search resolution accuracy defined by subdivision of orbital period.
        """
        pass

    def next_sampling(self, start=datetime.now(), resolution=100, search_limit=timedelta(hours=30)):
	"""
	Returns next sampling of aoi, where swath intersects the aoi.
	Returns transit time relative to center of aoi and fraction of aoi area
	sampled by the instrument swath.
        """
        # next transit
        quarter_period = timedelta(minutes=self.orbital_period()/4.0)

        t = self.next_transit(start,resolution)
        Dt = t - start
        f = self.intersect_fraction(t-quarter_period, 2.0*quarter_period.total_seconds()/60.0)
        if f > 0.0:
            return t, f
        else:
            while Dt < search_limit:
                t = self.next_transit(t,resolution)
                Dt = t - start
                f = self.intersect_fraction(t-quarter_period, 2.0*quarter_period.total_seconds()/60.0)
                if f > 0.0:
                    return t, f
            raise Exception('AOI Sampling exceeded search limit')

    @abstractmethod
    def orbital_period(self):
        """
        Orbital period in floating point minutes.
        """
        pass

    def swath_lonlats(self, start, period=None):
        """
        Returns outline of the instrument swath in lonlat coordinates.
        This is useful for forming a polygon shape to test intercept with
        the area of interest.
        """
        # default period is 1 minute long granule
        if period is None:
            period = 1.0

        # 100th step of orbit should be sufficient resolution for resulting polygon
        # equivalent ot 1m AVHRR granule
        t_step = self.orbital_period()/100.0
        t_steps = np.arange(0.0, period+t_step, t_step)

        scans_lon = []
        scans_lat = []

        for dt in t_steps:
            t = start + timedelta(minutes=dt)
            pos_time = self.scan_line_lonlats(t)
            scans_lon.append( pos_time[0] )
            scans_lat.append( pos_time[1] )
        scans_lon = np.array(scans_lon)
        scans_lat = np.array(scans_lat)

        # pick out perimeter of swaths
        lons = scans_lon[0,:].tolist() + (scans_lon[1:-1,-1].tolist()) \
            + (scans_lon[-1,:])[::-1].tolist() + (scans_lon[1:-1,0])[::-1].tolist()

        lats = scans_lat[0,:].tolist() + scans_lat[1:-1,-1].tolist() \
            + (scans_lat[-1,:])[::-1].tolist() + (scans_lat[1:-1,0])[::-1].tolist()

        return np.array((lons,lats))


    @abstractmethod
    def scan_line_lonlats(self, t):
        """
        Returns a single instrument scan line starting at datetime t
        """
        pass

    def scan_line_working_projection(self, t):
        """
        Returns a single instrument scan line sarting at datetime t
        in working projection coordinates.
        """
        return np.array(self.proj(*self.scan_line_lonlats(t)))


    def swath_working_projection(self, start, period=None):
        """
        Returns the coordinate outline of the instrument swath in
        working projection coordinates.  Out of map projection bound 
        coordinates are handled by splitting up the outline into a list.
        """
        # default period is 1 minute long granule
        if period is None:
            period = 1.0

        # 100th step of orbit should be sufficient resolution for resulting polygon
        # equivalent ot 1m AVHRR granule
        t_step = self.orbital_period()/100.0
        t_steps = np.arange(0.0, period+t_step, t_step)

        # fetch all scan lines and index segments
        def has_valid_xy(A):
            return ((A[0] != self.proj_out_of_bounds_value) & (A[1] != self.proj_out_of_bounds_value)).any()

        def valid_xys(A):
            sel = (A[0] != self.proj_out_of_bounds_value) & (A[1] != self.proj_out_of_bounds_value)
            return A[:,sel]

        scans = []
        segment_idx = []
        count = 0
        idx = -1
        for dt in t_steps:
            t = start + timedelta(minutes=dt)
            pos = self.scan_line_working_projection(t)
            if has_valid_xy(pos):
                scans.append( valid_xys(pos) )
                if idx < 0: #begin segment
                    idx = count
                count += 1
            elif idx > -1:  #end segment
                segment_idx.append((idx,count-1))
                idx = -1
        if (pos < self.proj_out_of_bounds_value).any():
            segment_idx.append((idx,count-1))

        # pick out perimeters of segments (this is fast / above is bottleneck)
        segments = []
        for s in segment_idx:
            a,b = s
            xs = scans[a][0].tolist()
            ys = scans[a][1].tolist()
            for i in range(a+1,b):
                xs = scans[i][0,0:1].tolist() + xs + scans[i][0,-1:].tolist()
                ys = scans[i][1,0:1].tolist() + ys + scans[i][1,-1:].tolist()
            xs = xs + scans[b][0,::-1].tolist()
            ys = ys + scans[b][1,::-1].tolist()
            segments.append( np.array((xs,ys)) )

        return segments

    def intersect_polygon(self, start, period=None):
        """
        Returns a shapely polygon representing the intersection
        with the area of interest and the instrument swath sampled
        at datetime start for period number of minutes.
        """
        swath = self.swath_polygon(start, period)
        aoi = self.aoi_polygon()
        return aoi.intersection(swath)

    def intersect_fraction(self, start, period=None):
        """
        Returns the fractional area of the area of interest, sampled by the 
        instrument swath starting at datetime 'start' for a 'period' number of minutes.
        """
        swath = self.swath_polygon(start, period)
        aoi = self.aoi_polygon()
        intersect = aoi.intersection(swath)
        return intersect.area/aoi.area

    def does_swath_sample_aoi(self, start, period=None):
        """
        Check if swath starting at time 'start' samples (overlaps)
        the area of interest.
        """
        swath = self.swath_polygon(start, period)
        aoi = self.aoi_polygon()
        return swath.intersects(aoi)
        #return aoi.intersection(swath).area > 0.0
        # using area intersect because overlaps fails 
        # for small poly or if swath line does not cross (need to read pyshapely manual)
        #return swath.overlaps(aoi)

    def swath_polygon(self, start, period=None):
        segments = self.swath_working_projection(start,period=period)
        try:
            if len(segments) == 0:
                # empty polygon
                return geometry.Polygon()
            elif len(segments) == 1:
                return geometry.Polygon(segments[0].transpose().tolist())
            else:
                P = geometry.Polygon(segments[0].transpose().tolist())
                for i in range(1,len(segments)):
                    P = P.union( geometry.Polygon(
                            segments[i].transpose().tolist()) )
            return P
        except ValueError:
            # empty polygon if invalid polygon created
            return geometry.Polygon()

    def aoi_polygon(self):
        xys = np.array(self.proj(*self.aoi))
        coords = xys.transpose().tolist()
        if len(coords) > 2:
            return geometry.Polygon(coords)
        elif len(coords) == 2:
            return geometry.LineString(coords)
        else:
            return geometry.Point(coords[0])

    def show_swath(self, start, period=None):
        """
        A helper method that displays the orbital swath
        starting at datetime start, for a period number of minutes.
        If, start is iterable, then the method assumes it is an iterable
        of datetimes, plotting a number of swaths at those times.
        """
        # test if start is iterable, EAFP style:
        try:
            for e in start:
                pass
        except TypeError:
            start = [start]

        import matplotlib.pyplot as plt

        # fetch the coordinates
        (aoix,aoiy) = self.proj(*self.aoi)
        
        # plot AOI
        plt.axis('equal')
        plt.plot(aoix,aoiy,'r-')
        plt.plot((aoix[-1],aoix[0]),(aoiy[-1],aoiy[0]),'r-')

        # plot Earth
        Re = self.earth_radius
        circle=plt.Circle((0,0),Re,color='g',fill=False)
        fig = plt.gcf()
        fig.gca().add_artist(circle)

        plt.xlim((-1.5*Re,1.5*Re))
        plt.ylim((-1.5*Re,1.5*Re))

        # Plot granules
        for t in start:
            # fetch the coordinates
            xys_segs = self.swath_working_projection(t, period)
            for xys in xys_segs:
                plt.plot(xys[0],xys[1],'b-')
                plt.plot((xys[0][-1],xys[0][0]),(xys[1][-1],xys[1][0]),'b-')
                
        plt.show()

        #from mpl_toolkits.basemap import Basemap
        #m = Basemap(projection='ortho', lon_0=self.working_projection['lon_0'], 
        #            lat_0=self.working_projection['lat_0'],resolution='l')
        # convert and plot the predicted pixels in red
        #p1 = m.plot(x,y, marker='+', color='red', markerfacecolor='red', 
        #            markeredgecolor='red', markersize=1, markevery=1, zorder=4, linewidth=1.0)
        #m.fillcontinents(color='0.85', lake_color=None, zorder=3)
        #m.drawparallels(np.arange(-90.,90.,5.), labels=[1,0,1,0],fontsize=10, dashes=[1, 0], color=[0.8,0.8,0.8], zorder=1)
        #m.drawmeridians(np.arange(-180.,180.,5.), labels=[0,1,0,1],fontsize=10, dashes=[1, 0], color=[0.8,0.8,0.8], zorder=2)
        #plt.show()

    def show_swath_pycoast(self, start, period=None):
        """
        A helper method that displays the orbital swath
        starting at datetime start, for a period number of minutes.
        If, start is iterable, then the method assumes it is an iterable
        of datetimes, plotting a number of swaths at those times.
        """
        # test if start is iterable, EAFP style:
        try:
            for e in start:
                pass
        except TypeError:
            start = [start]


        from PIL import Image
        from pycoast import ContourWriterAGG
        img = Image.new('RGB', (650, 650))
        proj4_string = ""
        for x in self.working_projection:
            proj4_string += "+%s=%s "%(x,self.working_projection[x])
        area_extent = (-6700000.0, -6700000.0, 6700000.0, 6700000.0)
        area_def = (proj4_string, area_extent)
        cw = ContourWriterAGG()

        cw.add_grid(img, area_def, (10.0,10.0),(2.0,2.0), fill='blue',
                    outline='gray', outline_opacity=130, minor_outline=None, write_text=False)
        cw.add_coastlines(img, area_def, resolution='l')
        
        # Plot granules
        for t in start:
            # fetch the coordinates
            xys_segs = self.swath_working_projection(t, period)
            for xys in xys_segs:
                lls = self.proj(xys[0],xys[1],inverse=True)
                cw.add_polygon(img, area_def, zip(lls[0], lls[1]), outline="blue", fill="blue", fill_opacity=100, width=1)

        aoi_coords = zip(*self.aoi)
        ## TODO: Handle single point case.
        if len(aoi_coords) == 2:
            cw.add_line(img, area_def, aoi_coords, outline="red", fill="red", fill_opacity=100, width=2)
        else:
            cw.add_polygon(img, area_def, aoi_coords, outline="red", fill="red", fill_opacity=100, width=2)
        img.show()                

    def aoi_center(self):
        ## eventually do this in projection coordinate space instead.
        ## swath and aoi intersection will be evaluated in projection (e.g. orthographic).
        return sum(self.aoi[0])/len(self.aoi[0]), sum(self.aoi[1])/len(self.aoi[1])

    @abstractmethod
    def set_tle(self, line1, line2):
        """
        Use to apply a particular two line element.
        """
        pass
 
