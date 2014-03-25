.. _aggdraw: http://effbot.org/zone/aggdraw-index.htm

Examples (DRAFT)
----------------


Transferring files (DRAFT)
++++++++++++++++++++++++++++++
One very basic application of the GranuleFilter
is to observer a source directory, filter out
files of interest and transferring.

  >>> from pygranule import get_granule_filters()
  >>>
  >>> Filters = get_granule_filters()
  >>> for Filter in Filters:
  >>>     Filter().transfer()

Done.

This method of executing a file transfer is the
same, no matter in what form or subsetting the data
appears.
