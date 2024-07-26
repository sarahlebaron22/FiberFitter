## FiberFitter

Hello! This is the officical unofficial GitHub page for all code pertaining to Dr. Hogan's beam autoalignment project. For now, there are three main folders, though the latter two may at some point be divided based on what portion of the project they cover.

### 1.) The Experiments Folder
This folder contains all the junk I've made while testing general concepts. Expect no legible or useful code from this folder. Examples include scrap code meant for testing libraries for the Newport Picomotor8742, how to continually update labels for tkinter, etc. 

The only reason these files are kept are because of their use in troubleshooting (and because I spent way too much time on them initially, haha)

### 2.) Project Files
This folder contains all of the main project files in Jupyter Notebook formatting. I tend to write all code as a Jupyter Notebook first due to how handy individual cell excecution is for troubleshooting. While the "completed" project will be all .py files for the purpose of actual usage, I'm keeping the original notebooks around in case we want to modify the final files after the project is done (which we absolutely will like come on).

### 3.) Project Files (.py)
As the name implies, this folder is simply the contents of Project Files converted into a .py file. Once the project is "done", in so far as any project is ever truly finished, you'll want to download and run the contents of this file for beam alignment. Also, certain later project files will refer to a main.py which contains all of the important functions for this project, which means main.py will have to be imported. Even if you want to work in a Jupyter Notebook setting to modify these files, you'll have to download the .py file for main in order to operate these later files. Sorry 'bout that.

### Additional Comments
If the Project Files (.py) and Project Files folders are divided, they will be categorized by what they do and which set of systems they are related to. By that, I mean that this project uses a LabJack ADC, a few Newport Picomotor8742s, and may at some point implement some Pi Picos or other mini computers to independently run the aforementioned code in different parts of the lab where fiber coupling occurs. We may at some point want to isolate these project files by component for modularity purposes. For instance, if we want to repurpose the LabJack ADC code to track efficiency in other places WITHOUT implementing motor controls or whatever, we'd only need those LabJack related files. This isn't a division I'm gonna do now, but I could very well imagine myself doing so in the future as the project expands.

Finally, I am as much of a coder as a retired suburban dad with a cabin 20 miles from Lake Tahoe is a fisherman, which is to say that any game we talk is almost certainly unfounded. This code is crap. It is at best functional, and even that is a stretch. If you find ways to improve (which you will), please do us all a favor, change it, and let me know so I can replace existing files.
## Project To-Dos:

### 1.) For LabjackEfficiencyDatabase
I gotta add in some sort of method to have the CSV file write over itself after a given number of rows. As it stands, having the efficiency database refresh every second results in a CSV file that is 19.7kB long after having been run for only around 8.33 minutes (497 lines long). This means that, with a refresh rate of once a second, we can expect the file to grow by ~2.4kB a minute, or a little under 3.5 megabytes a day. This doesn't seem like a big deal to begin with, but idk how long we plan to have this file running in the long term. 

The solution would seem to be enforcing a hard cap on the number of rows the CSV file can contain and having the CSV file delete the first row in the file while writing a new row after that hard cap is reached. If ~500 rows produces a ~20kB file, this means that:
  1 mB = 25000 lines = ~7-8 hours
  10 mB = 250000 lines ~3 days
  100 mb = 2.5 million lines = ~1 month
Maybe I could have this be configurable in the startup prompt, but I feel like startup is already kind of long as-is. Maybe that's just because I've been launching and relaunching this application hundreds of times a day though. I could also just have this be a function argument, which I'll probably opt for. The main issue is figuring out how to delete row one of the CSV file consistently without using the Pandas module. Seeing as this whole program was built without the use of Pandas, reworking hundreds of lines of code JUST to implement this feature with Pandas seems a little drastic. I'll continue to look into it though. 
  

~~~
Thanks y'all <3
-Sarah
