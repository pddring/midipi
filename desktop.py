import time
from PIL import Image,ImageDraw,ImageFont,ImageColor,ImageTk
import tkinter
KEY_UP_PIN     = 6 
KEY_DOWN_PIN   = 19
KEY_LEFT_PIN   = 5
KEY_RIGHT_PIN  = 26
KEY_PRESS_PIN  = 13
KEY1_PIN       = 21
KEY2_PIN       = 20
KEY3_PIN       = 16
class ScreenController:
    def get_buttons(self):
        keys = self.keys
        self.keys = []
        return keys
        """if GPIO.input(KEY_UP_PIN) == 0:
            buttons.append("up")
        if GPIO.input(KEY_DOWN_PIN) == 0:
            buttons.append("down")
        if GPIO.input(KEY_LEFT_PIN) == 0:
            buttons.append("left")
        if GPIO.input(KEY_RIGHT_PIN) == 0:
            buttons.append("right")
        if GPIO.input(KEY_PRESS_PIN) == 0:
            buttons.append("middle")
        if GPIO.input(KEY1_PIN) == 0:
            buttons.append("1")
        if GPIO.input(KEY2_PIN) == 0:
            buttons.append("2")
        if GPIO.input(KEY3_PIN) == 0:
            buttons.append("3")"""
        return buttons

    def keydown(self, e):
        k = e.keysym.lower()
        if k == "return":
            k = "middle"
        if k not in self.keys:
            self.keys.append(k)

    def keyup(self, e):
        k = e.keysym.lower()
        if k == "return":
            k = "middle"
        if k in self.keys:
            self.keys.remove(k)

    def __init__(self):
        print("Setting up screen")
        self.root = tkinter.Tk()

        # Create blank image for drawing.
        # Make sure to create image with mode '1' for 1-bit color.
        self.width = 128
        self.height = 128
        self.image = Image.new('RGB', (self.width, self.height))

        self.tkimage = tkinter.Label(self.root)
        self.tkimage.pack(fill="both", expand="yes")

        self.root.bind("<KeyPress>", self.keydown)
        self.root.bind("<KeyRelease>", self.keyup)
        self.keys = []
        
        # Get drawing object to draw on image.
        draw = ImageDraw.Draw(self.image)

        # Draw a black filled box to clear the image.
        draw.rectangle((0,0, self.width, self.height), outline=0, fill=0)
        #self.disp.LCD_ShowImage(self.image,0,0)

    def load_image(self, filename):
        self.image = Image.open(filename)
        #self.disp.LCD_ShowImage(self.image,0,0)


    def update(self):
        #self.disp.LCD_ShowImage(self.image,0,0)
        img = ImageTk.PhotoImage(self.image)
        self.tkimage.configure(image=img)
        self.tkimage.image = img
        self.root.update()

    def get_drawing(self, new_image = False):
        if new_image == True:
            self.image = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(self.image)
        return draw


    def print(self, text, pos=(0,0), fill=(255,255,255,255), update=True):
        draw = ImageDraw.Draw(self.image)
        draw.text(pos, text, fill)
        if update:
            self.update()

    def show_status(self):
        draw = ImageDraw.Draw(self.image)
        # with canvas(device) as draw:
        if GPIO.input(KEY_UP_PIN) == 0: # button is released       
            draw.polygon([(20, 20), (30, 2), (40, 20)], outline=255, fill=0xff00)  #Up        
            print("Up"        )
        else: # button is pressed:
            draw.polygon([(20, 20), (30, 2), (40, 20)], outline=255, fill=0)  #Up filled
            
        if GPIO.input(KEY_LEFT_PIN) == 0: # button is released
            draw.polygon([(0, 30), (18, 21), (18, 41)], outline=255, fill=0xff00)  #left
            print("left"        )
        else: # button is pressed:       
            draw.polygon([(0, 30), (18, 21), (18, 41)], outline=255, fill=0)  #left filled
            
        if GPIO.input(KEY_RIGHT_PIN) == 0: # button is released
            draw.polygon([(60, 30), (42, 21), (42, 41)], outline=255, fill=0xff00) #right
            print("right")
        else: # button is pressed:
            draw.polygon([(60, 30), (42, 21), (42, 41)], outline=255, fill=0) #right filled       
            
        if GPIO.input(KEY_DOWN_PIN) == 0: # button is released
            draw.polygon([(30, 60), (40, 42), (20, 42)], outline=255, fill=0xff00) #down
            print("down")
        else: # button is pressed:
            draw.polygon([(30, 60), (40, 42), (20, 42)], outline=255, fill=0) #down filled
            
        if GPIO.input(KEY_PRESS_PIN) == 0: # button is released
            draw.rectangle((20, 22,40,40), outline=255, fill=0xff00) #center 
            print("center")
        else: # button is pressed:
            draw.rectangle((20, 22,40,40), outline=255, fill=0) #center filled
            
        if GPIO.input(KEY1_PIN) == 0: # button is released
            draw.ellipse((70,0,90,20), outline=255, fill=0xff00) #A button
            print("KEY1")
        else: # button is pressed:
            draw.ellipse((70,0,90,20), outline=255, fill=0) #A button filled
            
        if GPIO.input(KEY2_PIN) == 0: # button is released
            draw.ellipse((100,20,120,40), outline=255, fill=0xff00) #B button]
            print("KEY2")
        else: # button is pressed:
            draw.ellipse((100,20,120,40), outline=255, fill=0) #B button filled
            
        if GPIO.input(KEY3_PIN) == 0: # button is released
            draw.ellipse((70,40,90,60), outline=255, fill=0xff00) #A button
            print("KEY3")
        else: # button is pressed:
            draw.ellipse((70,40,90,60), outline=255, fill=0) #A button filled
        self.disp.LCD_ShowImage(self.image,0,0)

if __name__ == "__main__":
    s = ScreenController()
    s.load_image("images/brass.png")
    s.print("hello", pos=(0,10), fill=(0,0,0,255),update=False)
    s.update()
    s.root.mainloop()