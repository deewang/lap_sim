# lap-sim

Setup PyChrono:
https://api.projectchrono.org/pychrono_installation.html

Note for Windows:
- gnuplot conda package doesn't exist for win64 so you need to download gnuplot directly from https://sourceforge.net/projects/gnuplot/files/gnuplot/6.0.3/

- Chrono::Cascade is only compatible with Python 3.8 or 3.9, so run `conda create -n chrono python=3.8` to create the Chrono conda environment

- Chrono::Sensor is optional, skip this in the installation process for now