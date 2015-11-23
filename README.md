# camcam
A python based CAM scripting system

This is a system for designing 2D objects and outputting GCode, svg etc

to produce output 
python camcam.py -m [mode] file1.py file2.py
mode:
diagram - produces one file with all the parts drawn on
visualise - produces an svg with all parts, and the cutting line around the outside
dave-emc - emc2 compatible gcode
makespacerouter - very simple gcode formatted as DOS file
eagle - a file you can import into eagle PCB software
laser - individual svg files for each part 


python camcam.py -B 
will produce a bill of materials

as the docs indicate this is very alpha atm
