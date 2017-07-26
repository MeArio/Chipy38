#ChiPy38 - chip8 emulator(interpreter)


I wasn't actually expecting to finish this project, but I did it. As you can see this isn't that different from the many other Chip8 interpreters.
##Installation


I suggest you make a new virtual enviorment and install the dependencies using pip and the requirments.txt file.

*Linux*
```
$ virtualenv -p python3 Chipy38
$ git clone https://github.com/MeArio/Chipy38.git
$ cd Chipy38
$ source bin/activate
(Chipy38) pip install -r requirments.txt
```
I didn't test it on any other operating systems, but it should work and the installation should be similar.

##Usage


*Basic Usage:*
```
python main.py rom_file
```
*Optional arguments:*
```
-t int (adds a delay between each instruction default is 1)
-d (opens the rudimentary debugger "p" to unpause and "f" to step)
-s int (sets the scale of the window default is 10)
```

##Config


The config.py file is scarce and only has 4 properties:


keys (Dict) is the key map


timers_delay (Int) is the delay at which the timers get decremented

shift_quirk (Bool) makes the interpreter use the bitwise shift definition from Mastering CHIP-8 by Matthew Mikolay

load_quirk (Bool) makes the interpreter use the Fx55 and Fx65 definition from Mastering CHIP-8 by Matthew Mikolay

##Refferences



[Wikipedia page for the Chip-8](https://en.wikipedia.org/wiki/CHIP-8)

[Cowgod's Chip-8 Tehnical Refference](http://devernay.free.fr/hacks/chip8/C8TECH10.HTM#0.0)
(The docstrings for the opcodes are copy and pasted from there)


[Mastering the CHIP-8](http://mattmik.com/files/chip8/mastering/chip8.html)

##Notes


This was an intereseting project, but I recommand to anyone that wants to undertake it to prioritise Mastering the CHIP-8 as documentation over Cowgod's refference.

##License


This repository uses the MIT License.


Copyright (c) 2017 Dovleac Dorin