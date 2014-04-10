.. pygranule documentation master file, created by
   sphinx-quickstart on Wed Nov 27 13:05:45 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. meta::
   :description: Python project adding logos, texts, and color scales to PIL images
   :keywords: Python, operational, meteorology, granules, scheduling


Welcome to pygranule's documentation!
======================================

pygranule is a package for validating, fetching and scheduling 
satellite data granules.
The source code of the package can be found on google code, googlecode_

.. image:: images/demo.png
        :width: 95%
	:align: center

The main purpose is to filter some satellite granule file names,

    >>> files = ['/home/msg/archive/AVHRR/avhrr_20140225_133000_noaa19.hrp.bz2', 
                 '/home/msg/archive/AVHRR/avhrr_20140225_133100_noaa19.hrp.bz2', 
		 '/home/msg/archive/AVHRR/avhrr_20140225_133200_noaa19.hrp.bz2',
		 ...,
		 '/home/msg/archive/AVHRR/avhrr_20140225_152900_noaa19.hrp.bz2']

Using a configuration to describe the file set,

    >>> config = {'config_name':"DummySatData",
                  'sat_name':"NOAA 19",
		  'instrument':"AVHRR",
                  'file_source_pattern':"/home/msg/archive/AVHRR/avhrr_%Y%m%d_%H%M00_noaa19.hrp.bz2",
                  'time_step':"00:01:00",
                  'time_step_offset':"00:00:00",
                  'area_of_interest':"(-25,62.5),(-25,67),(-13,67),(-13,62.5)"}
    >>> gf = OrbitalGranuleFilter(config)

We can now do some on the fly operations on the files,
e.g., show all the granules,

    >>> gf.show( files )

or filter the granules, allowing only those that match the configuration,

    >>> gf.show( gf( files ) )

Off course granule filter will be able to do much much more ...

.. _googlecode: http://code.google.com/p/pygranule/

Contents:

.. toctree::
   :maxdepth: 2

   installation
   usage
   examples
   programming


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

