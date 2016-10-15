"""
Filename: LED-server.py
Author:  Peter Tsapatsaris

This program implements a cherrypy webserver that controls a LED-matrix that is attached to the server.  The LED is a 32x16 matrix sold by Adafruit, and this program utilizes an Adafruit Python library to control the LED display.

Three variables are provided to the ledDisplay function from an HTML form: (1) the message to be displayed, (2) the color of the text, and (3) the speed of the display.  The results are displayed in scrolling text on the LED, which is repeated until a new message is entered.  A log of messages is saved in message-log.html, and the current message is stored in current-message.html.  

""" 


import cherrypy
import os.path
import Image
import ImageDraw
import ImageFont
import math
import os
import time
from rgbmatrix import Adafruit_RGBmatrix
import sys
import select
from ast import literal_eval
import thread


#configurable global variables
width          = 64  # matrix width
height         = 16  # matrix height
myMatrix       = Adafruit_RGBmatrix(16, 2) # rows, chain length
fps            = 10 #speed of scrolling - this is adjusted later through input from the html form 
myFont         = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSans.ttf', 15) #local path for font used by LED.
easyColor      = (0, 0, 255) # text color
paddingStr = '        '  # padding for text scrolling
message = None
prevTime = 0
new_Message = True

#create image object and pane
myImage     = Image.new('RGB', (width, height))
drawPane    = ImageDraw.Draw(myImage)


#tile class to contain and advance scrolling text.  
class tile:
    def __init__(self, x, y, msg, fnt):
        self.x = x
        self.y = y
        self.message = paddingStr + msg + paddingStr
        self.myFont = fnt
        self.tileWidth = self.myFont.getsize(self.message)[0]
        self.nextMessage = self.message

    def draw(self):
        drawPane.text((self.x, self.y), self.message, font=self.myFont,
          fill=easyColor)

    def doNextMessage(self):
        self.message = paddingStr + self.nextMessage + paddingStr
        self.tileWidth = self.myFont.getsize(self.message)[0]

    def scroll(self):
        self.x -= 1
        if ( self.x < ( -1 * self.tileWidth ) ):
            self.x = 0
            self.doNextMessage()

#code to implement Cherrypy server
class myApp:
	
	def index(self):
		return open('index.html')
		
	index.exposed = True
	
	#code that activates LED display, taking variables from a separate HTML form.
	def ledDisplay(self, message, colorMenu, speedMenu):
		if message:

			#Variables to allow old loop to break if a new message is entered. The while loop below will break if new_Message = True
			global new_Message
			new_Message = True
			time.sleep(1)
			new_Message = False
			
			#write message to current-message.html, also handle an exception if non-unicode text is entered and redirect to error webpage.   
			log = open("current-message.html", 'w')
			try:
				log.write("<h2>The current message is: " + message + "</h2>")
			except UnicodeEncodeError:
				return open('nowhere.html')
				
			log.close()
			
			#write message to running log.  HTML format is to display on a different webpage. 
			with file('message-log.html', 'r') as original: data = original.read()
			with file('message-log.html', 'w') as modified: modified.write("<li>" + message + "</li>" + "\n" + data)
			
			#create tile object an intitiate loop.
			color = literal_eval(colorMenu)
			global easyColor
			easyColor = color
			global fps
			fps = int(speedMenu)
			t = tile ( 0, 0, message, myFont )
			
			def loop():		
				while True:	
					global prevTime
					#break old loop if a new message is generated
					if new_Message==True:
						break
				
					drawPane.rectangle((0, 0, width, height), fill=(0, 0, 0))
					t.draw()
					t.scroll()
					timeDelta   = (1.0 / fps) 
					# Offscreen buffer is copied to screen
					myMatrix.SetImage(myImage.im.id, 0, 0)
					drawPane.rectangle((0, 0, width, height), fill=(0, 0, 0))
					t.draw()
					t.scroll()
					currentTime = time.time()
					timeDelta   = (1.0 / fps) - (currentTime - prevTime)
					if(timeDelta > 0.0):
						if select.select([sys.stdin,],[],[],timeDelta)[0]:
							t.nextMessage = sys.stdin.readline()

					prevTime = currentTime

					# Offscreen buffer is copied to screen
					myMatrix.SetImage(myImage.im.id, 0, 0)
			
			#Create new thread to initiate while loop, and then redirect user to post-submission webpage.  
			thread.start_new_thread(loop, ())
			raise cherrypy.HTTPRedirect("archive.html")
		
		#if no message is entered, redirect to error webpage.  	
		else:
			return open('nowhere.html')
	ledDisplay.exposed = True
	
configfile = os.path.join(os.path.dirname(__file__), 'server.conf')
cherrypy.quickstart(myApp(), config = configfile)
