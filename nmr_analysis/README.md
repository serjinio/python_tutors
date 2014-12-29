NMRAN
===

Small framework for data analysis and display

nmran - top-level package
 - analyse - analysis procs
 - dataio - module with data read/write routines
 - datavis - data visualiser

Use
---

Framework contains a bunch of helper routines for processing
FID signals. User supposed to write his script basing on those routines
and send to datavis.py for visualisation.

One of the main goals of the framework is to allow easy composition of scripts
which will obtain value of interest from individual input datasets, then batch
processing multiple data files to enable creation of summary plots.