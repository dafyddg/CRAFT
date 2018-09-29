# CRAFT
Description: Online prosody acoustics teaching platform, aimed at students of phonetics and related disciplines, with the goal of raising critical awareness in the handling of tools for the analysis of rhythm and melody of speech.

HTML GUI Input selections:
1. Data (fixed selection, no uploading). Note: no data files are included, own data must be supplied. The data filenames are left in the data <select> element as examples.
2. Parameter selection (algorithm choice, parameter choice, figure dimensions)

HTML GUI Output:
Graphs, statistical analyses, comparison of speech signal transformations.

In order to use CRAFT, a CGI capable web server must be installed and the file paths must be defined appropriately for the server environment. The server used in CRAFT development is Lighty (httpd):
- https://www.lighttpd.net/
- https://en.wikipedia.org/wiki/Lighttpd

In order to use the RAPT and Praat F0 estimation options, esps and get_f0 and Praat must be installed:
- ESPS: http://www.phon.ox.ac.uk/releases (Debian .deb file for Ubuntu 12.04, ok also for 16.04)
- Praat: http://www.fon.hum.uva.nl/praat/ (various operating systems)

Method:
CRAFT: Fundamental frequency (F0, 'pitch') estimation algorithms and parameters.
