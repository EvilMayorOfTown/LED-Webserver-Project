# LED-Webserver-Project

This program implements a cherrypy webserver that takes input from the HTML form in "index.html" and outputs it to a matrix of adafruit RGB LED matrices.  The matrices can be found at:
https://www.adafruit.com/products/420
Adafruit provides python libraries to control the matrices, which are used by this program and are included in the repository.  

The cherrypy server is implemented in the "LED-server.py" file, and requires cherrypy to be installed on your system.  Once the server is running, input into the html form in "index.html" will (1) display on the LED matrix; (2) be written into the "message-log.html" file, which keeps a running list of all entries in an HTML formatted list; and (3) the "current-message.html" file is overwritten to contain the message.  If no message is given, or the message contains non-unicode characters, the user is redirected to "nowhere.html".  Otherwise the user is redirected to "archive.html", which displays the contents of "current-message.html" and "message-log.html". 
