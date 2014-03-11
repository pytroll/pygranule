from .orbital_layer import OrbitalLayer, OrbitalLayerError

from datetime import datetime, timedelta
import numpy as np

import os
from pyorbital.geoloc_instrument_definitions import avhrr
from pyorbital.geoloc import compute_pixels, get_lonlatalt
#from urllib2 import URLError
from pyorbital.orbital import Orbital


class PyOrbitalLayer(OrbitalLayer):
    """
    pyorbital based orbital layer
    """
    def __init__(self, aoi, sat, instrument="AVHRR"):
        OrbitalLayer.__init__(self,aoi,sat,instrument)
        # instantiate orbital module
        
        try:
            config_file_path = os.environ['PYGRANULE_CONFIG_PATH']
        except KeyError:
            raise OrbitalLayerError( "pygranule config file path missing.  Has the 'PYGRANULE_CONFIG_PATH' environment variable been set?")
        
        default_tle_file = config_file_path+"/default.tle"
        
        try:
            self.orbital = Orbital(sat,default_tle_file)
        except:
            print "Failed to open default tle file:", default_tle_file
            try:
                self.orbital = Orbital(sat)
            except:
                raise OrbitalLayerError("Pyorbital Failed to fetch TLE from internet.")
                
        # create scan geometry - one scan line.
        scan_steps = np.arange(0,self.instrument_info['scan_steps'],self.instrument_info['scan_steps']/8-1)
        scan_steps[-1] = self.instrument_info['scan_steps']-1
        self.scan_geom = avhrr(1,scan_steps)

    def set_tle(self, line1, line2):
        # for now restart pyorbital with these new elements.
        del self.orbital
        self.orbital = Orbital(self.sat,line1=line1, line2=line2)

    def orbital_period(self):
        return 24*60/self.orbital.tle.mean_motion

    def scan_line_lonlats(self, t):
        """
        Returns a single instrument scan line starting at datetime t
        """        
        s_times = self.scan_geom.times(t)
        pixels_pos = compute_pixels((self.orbital.tle.line1, self.orbital.tle.line2), 
                                    self.scan_geom, s_times)
        pos_time = get_lonlatalt(pixels_pos, s_times)
        return np.array((pos_time[0],pos_time[1]))

    def next_transit(self, start=datetime.now(), resolution=100):
        """
        Next transit time relative to center of aoi.
        Resolution accuracy defined by subdivision of orbital period.
        """
        # accuracy in mintues from mean orbital period
        dt = self.orbital_period()/resolution

        # observer position
        alt = 0.0
        lon, lat = self.aoi_center()
        
        # NOTE: For now I do not use the pyorbital
        # get_next_passes. Because it accepts integer (not float) hours
        # for the search period, and the accuracy of the transit time
        # search is not obvious to me at the moment.
        # Also I would like to allow negative transit time altitudes
        # - transits below horizon.
        # Therefore I re-implement the search myself, here to have more control:
        t_offsets = np.arange(0.0,self.orbital_period()*1.2,dt)
        e  = np.array( [ self.orbital.get_observer_look(start + timedelta(minutes=t_offset), lon, lat, alt)[1] \
                    for t_offset in t_offsets ] )
        
        # search for local maxima
        b = (np.roll(e,1)<e)&(np.roll(e,-1)<e)
        idx = np.where(b[1:]==True)[0][0]+1 #i.e. do not accept index 0 as maximum...
        
        ## return a quadratic maximum for good accuracy based on data.
        ## Quadratic fit to 3 points around maximum elevation 
        ## seems to improve accuracy by 100-fold.
        x,y = t_offsets[idx-1:idx+2],e[idx-1:idx+2]
        fit = np.polyfit(x,y,2)
        t = -fit[1]/(2.0*fit[0])

        #from matplotlib import pyplot as plt
        #plt.plot(x,y,'x')
        #fitx = np.arange(x[0]-1,x[2]+1,0.1)
        #fity = fit[2]+fit[1]*fitx+fit[0]*(fitx**2)
        #plt.plot(fitx,fity,'r-')
        #plt.show()
        
        return start + timedelta(minutes=t)
