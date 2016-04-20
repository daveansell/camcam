# camcam
A python based CAM scripting system

This is a system for designing 2D objects in python and outputting GCode, svg etc

to produce output the input files are created as python scripts which are executed within camcam.py
This is slightly odd but means they can behave more like save files, than source files.

Run like:

python camcam.py -m [mode] file1.py file2.py  
mode:  
diagram - produces one file with all the parts drawn on  
visualise - produces an svg with all parts, and the cutting line around the outside  
dave-emc - emc2 compatible gcode  
makespacerouter - very simple gcode formatted as DOS file  
eagle - a file you can import into eagle PCB software  
laser - individual svg files for each part   
laserdxf - individual dxf files for each part

python camcam.py -B  
will produce a bill of materials  

It has quite nice features for dealing with objects made of multiple layers
It can do funky things with finger joints including create arbitary polyhedra from them with the ArbitraryBox

as the docs indicate this is very alpha atm  

# Dependencies

python-kivy
dos2unix

# for 3d
openscad

pip packages

freetype-py
dxfwrite

# for experimental 3D
euclid
solidpython 
- as of 20160416 you will probably have to get the github version as pip version is too old
https://github.com/SolidCode/SolidPython
