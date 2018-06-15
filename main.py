#CODE for the GUI made for EE610 Assignment 1#
import numpy as np
import matplotlib, sys, os
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib import pylab as plt
import PIL
from PIL import Image, ImageTk
import scipy.ndimage
import fun
import os
import shutil
import cv2

##check for system version as the imports for Tkinter vary between python2 and python3
if sys.version_info[0] < 3:
    import Tkinter as Tk
    from Tkinter import ttk
    from Tkinter import filedialog
    from Tkinter import simpledialog
    from Tkinter import messagebox
else:
    import tkinter as Tk
    from tkinter import ttk
    from tkinter import filedialog
    from tkinter import simpledialog
    from tkinter import messagebox

root = Tk.Tk() #defining my parent window
root.wm_title("Basic Image Editor EE610!!!!")

fig = plt.figure(figsize=(5,4)) #this is the basic figure which will be used for the plots.
#also when we run the code the size of window is defined by (5,4).
canvas = FigureCanvasTkAgg(fig, master=root)#this canvas is the blank white space for drawing.
image=np.zeros((1,1)) #will be used to store the input image. just an initialization to a numpy array.
script_path="" #this will be storing the path where our code is running
log_path="" #this will store the path for temporary log_folder used to store the processed images.
extension="" #stores extension of current loaded image eg: png

###
#below variables are defined for the popup window which comes in butterworth sharpening.
#lab_x_data are used to dynamically change the label text content. used for validation and user friendliness.
lab_5_data = Tk.StringVar()
lab_5_data.set("") #used to set the data of a Stringvar

lab_6_data = Tk.StringVar()
lab_6_data.set("") #used to set the data of a Stringvar

lab_7_data = Tk.StringVar()
lab_7_data.set("") #used to set the data of a Stringvar

#error_flag_x is used to store which entry received a wrong user input. like text instead of int, etc.used for validation.
error_flag_1=0
error_flag_2=0
error_flag_3=0

butter_width="" #stores value of threshold in filter i.e D_0
butter_order="" #stores filter order
butter_a="" #stores dc_amplification value

popup_true=0 #flag used to denote whether the popup was correctly filled or not
###

###
#popupmsg() function is used to diaplay a popup window to accept user values for butterworth sharpening
def popupmsg():
    global image,lab_5_data,lab_6_data,lab_7_data,error_flag_1,error_flag_2,error_flag_3,butter_width,butter_order,butter_a,popup_true

    butter_width=""
    butter_order=""
    butter_a=""

    #fetch_details() fetches the user filled values in entry widgets once the user clicks 'ok' button
    def fetch_details():
        global image,lab_5_data,lab_6_data,lab_7_data,error_flag_1,error_flag_2,error_flag_3,butter_width,butter_order,butter_a,popup_true
        lab_5_data.set("")
        lab_6_data.set("")
        lab_7_data.set("")

        error_flag_1=0
        error_flag_2=0
        error_flag_3=0

        try:   #the below try-catch are used for validation of user input filled in the entry widgets
            butter_width = int(e1.get()) #get() function is used to retrieve data filled in the entry widget
        except ValueError: #ValueError occurs if the typecasting to int was not successful
            lab_5_data.set("Plese enter integer")
            error_flag_1=1
        try:
            butter_order = int(e2.get())
        except ValueError:
            lab_6_data.set("Plese enter integer")
            error_flag_2=1
        try:
            butter_a = float(e3.get())
            #dc_amplification value can lie between 0 an 1 inclusive only.
            if((butter_a<0) or (butter_a>1)):
                lab_7_data.set("value between 0 and 1")
                error_flag_3=1
        except ValueError:
            lab_7_data.set("Plese enter float")
            error_flag_3=1
        #if there was erroneous input then destroy the popup and ask input again
        if((error_flag_1==1) or (error_flag_2==1) or (error_flag_3==1)):
            popup.destroy()
            popupmsg()
        else:
            popup_true=1 #no erroneous input from user
            var3.set(popup_true)

    popup = Tk.Tk() #defining a popup window over my parent window
    popup.wm_title("Please enter details")

    #callback3() is used to destroy popup window and return control to main window
    def callback3(*args):
        if(popup_true==1):
            popup.destroy()
            popup_return()
    ###
    #below portion defines the popup structure
    label1 = ttk.Label(popup, text="Width: ").grid(row=0)
    label2 = ttk.Label(popup, text="Order: ").grid(row=2)
    label3 = ttk.Label(popup, text="DC_amplification_factor(a): ").grid(row=4)

    e1 = ttk.Entry(popup)
    e2 = ttk.Entry(popup)
    e3 = ttk.Entry(popup)

    e1.grid(row=0, column=1)
    e2.grid(row=2, column=1)
    e3.grid(row=4, column=1)

    #if error_flag_x==0 then that entry x was not erroneous. thus retain the data filled in it.
    #user doesn't need to retype the data if he filled that entry correctly.
    if(error_flag_1==0):
        e1.insert(0,str(butter_width))   #insert(index, string)
    if(error_flag_2==0):
        e2.insert(0,str(butter_order))   #insert(index, string)
    if(error_flag_3==0):
        e3.insert(0,str(butter_a))   #insert(index, string)

    label4 = ttk.Label(popup, text="           ").grid(row=0,column=2)

    label5 = ttk.Label(popup, text=lab_5_data.get()).grid(row=1,column=1)
    label6 = ttk.Label(popup, text=lab_6_data.get()).grid(row=3,column=1)
    label7 = ttk.Label(popup, text=lab_7_data.get()).grid(row=5,column=1)

    B1 = ttk.Button(popup, text="Okay", command = fetch_details)
    B1.grid(row=6,column=1)
    ###
    var3=Tk.StringVar() #defining a callback for popup_true.
    #callback3() function will be called on each update of popup_true variable.
    var3.trace("w", callback3)

    popup.mainloop()
###

###
#callback() is defined for the functionality of undo and redo
#which options need to be enabled when is what is handled by this function.
def callback(*args):
    if(image_count == 0): #means the code just started running.
        editmenu.entryconfigure('undo last', state = "disabled")
        editmenu.entryconfigure('undo all', state = "disabled")
        editmenu.entryconfigure('redo last', state = "disabled")
        editmenu.entryconfigure('redo all', state = "disabled")

    if(image_count > 1): #means atleast one processing was done on original image.
        editmenu.entryconfigure('undo last', state = "normal")
        editmenu.entryconfigure('undo all', state = "normal")

    if(image_count == 1): #means I have returned after undo to my original image. can't undo further.
        editmenu.entryconfigure('undo last', state = "disabled")
        editmenu.entryconfigure('undo all', state = "disabled")

    #means my current image being displayed(image_count) is not the one which was processed at last(max_image_count).
    if(max_image_count > image_count):
        editmenu.entryconfigure('redo last', state = "normal")
        editmenu.entryconfigure('redo all', state = "normal")

    if(max_image_count == image_count): #means I have reached the last processed image after several redo clicks.
        editmenu.entryconfigure('redo last', state = "disabled")
        editmenu.entryconfigure('redo all', state = "disabled")
###

###
#callback2() handles when we need to enable the display_image option in view menu.
def callback2(*args):
    if(view_value=="000"): #means none of the other view options were clicked
        viewmenu.entryconfigure('Display image', state = "disabled")
    else:
        viewmenu.entryconfigure('Display image', state = "normal")
###

var = Tk.StringVar() #var holds variable for callback functionality of image_count
var.trace("w", callback)

var2 = Tk.StringVar() #var holds variable for callback functionality of view_value
var2.trace("w", callback2)


###
#load_image() is used for loading the user defined image from file system onto my canvas
def load_image():
    global image,script_path,log_path,image_count,extension,max_image_count,view_value
    script_path = os.path.dirname(os.path.realpath(__file__))
    log_path = script_path + "\log_folder"

    file_name=filedialog.askopenfilename() #opens up the file_system for user to select a file. returns file path
    #print(file_name) #prints the entire file path
    #print(os.path.basename(file_name)) #prints only the actual file name with extension

    if (not(file_name == "")): #in case user clicked on cancel or cross button
        if os.path.exists(log_path): #if the log_folder already exists then delete it and create a new one
            shutil.rmtree(log_path, ignore_errors=True) #remove the log_folder
            os.makedirs(log_path)
            #image_count=0
        else:
            os.makedirs(log_path)
            #image_count=0
        image_count=0  #as the image was just loaded
        max_image_count=0 #as no processing has yet happened on original image
        view_value="000" #initializing the values
        var.set(image_count) #used to call the callback functions so as to set the proper visibility for the menu options
        var2.set(view_value)

        fig.clf() #clear the current canvas
        fig.add_subplot(111) #makes a 1x1 image plot
        #some validations in case a 'gif' file or some other non-image file was selected
        try:
            name,extension= os.path.basename(file_name).split(".")
            if(extension=="gif"):
                raise exception
            image = scipy.ndimage.imread(file_name, mode='L') #read the image into an numpy.ndarray
            im = plt.imshow(image,vmin=0,vmax=255) #vmin and vmax are required to specify the gray scales.
            plt.set_cmap('gray') #setting the colormap
            canvas.draw() #displaying the image on the canvas

            #increment the image_count and store the current image in the log_folder.
            #will be required for undo and redo operations.
            image_count = image_count + 1
            var.set(image_count)

            #save current image in log_folder as 1.extension eg:1.jpg or 1.png
            current_file =  log_path + "\\" + str(image_count) + "." + str(extension)
            cv2.imwrite(current_file, image) #cv2.imwrite() is better compared to Image.fromarray() as it doesn't manipulate the image.
            #selected cv2 for the file write after I found some images getting manipulated by the rescaling required for Image.fromarray().
        except Exception as e:
            messagebox.showerror(title="Can't identify file!!!!",message="This file format is currently not supported")
###

###
#save_image() allows user to save an image currently being displayed on canvas, in the user defined extension. default in .png
def save_image():
    if(image.max()!=0): #i.e an image is actually present on the canvas for saving
        exportFile = filedialog.asksaveasfile(mode='w',defaultextension=".png",filetypes=(("PNG file", "*.png"),("All Files", "*.*")))
        #print(exportFile.name) #prints the entire file path
        if exportFile:
            cv2.imwrite(exportFile.name, image)
    else:
        messagebox.showerror(title="Can't save!!!!",message="Please load an image first")
###

###
#mquit() implements the exit functionality in the File menu
def mquit():
    #os.rmdir(log_path) #remove the log_folder but only if its empty
    mExit = messagebox.askokcancel(title="Quit",message="Are You Sure")
    if (mExit):
        shutil.rmtree(log_path, ignore_errors=True) #remove the log_folder. doesn't check whether empty or not.
        sys.exit()
        #root.destroy()
        #root.quit()
###

###
#histogram_equalize() functionality in Edit menu
def histogram_equalize():
    global image,extension,image_count,log_path,max_image_count,max_image_count
    if(image.max()!=0):
        image = fun.histeq_im(image) #call the function with the current image in canvas

        ###
        #Some general steps being followed in a image processing functions:
        #(1)clear the canvas
        #(2)draw the image on the canvas
        #(3)increment the image count as this is a new image and store this new image based on image_count to log_folder
        #(4)increment max_image_count which will be used for redo and undo functionalities
        #(5)remove_files() will remove all the images with count greater than the current image_count in the log_folder.
        #this is required in case I have 5 images say, 1,2,3,4,5 I undo and go to 2. Then I do a processing task.
        #then the new processed image will be stored as 3, and 4,5 will be removed from log_folder.
        ###
        fig.clf()
        fig.add_subplot(111)
        im = plt.imshow(image,vmin=0,vmax=255)
        plt.set_cmap('gray')
        canvas.draw()

        max_image_count=image_count+1
        image_count = image_count + 1
        var.set(image_count)

        #store the image in log_folder

        current_file =  log_path + "\\" + str(image_count) + "." + str(extension)
        cv2.imwrite(current_file, image)
        remove_files()
    else:
        messagebox.showerror("Error", "Please load an image first.")
###
###

###
#gamma_correct() implements gamma_correct functionality of Edit menu
def gamma_correct():
    global image,extension,image_count,log_path,max_image_count,max_image_count
    if(image.max()!=0):
        #ask for a user defined gamma value
        gamma = simpledialog.askfloat("Input", "Enter gamma value:",
                                parent=root,
                                minvalue=0.0)
        if (gamma is not None): #None will be when user clicks cancel. in that case no processing is done.
            image_bkp = fun.gamma_im(image,gamma)
            if (image_bkp is None): #If user enters a high value of gamma then can give exception. Function returns None in case of such exception
                messagebox.showerror("Error", "Please use a lower value of gamma.")
            else:
                image = image_bkp

                #general steps
                fig.clf()
                fig.add_subplot(111)
                im = plt.imshow(image,vmin=0,vmax=255)
                plt.set_cmap('gray')
                canvas.draw()

                max_image_count=image_count+1
                image_count = image_count + 1
                var.set(image_count)

                #store the image in log_folder

                current_file =  log_path + "\\" + str(image_count) + "." + str(extension)
                cv2.imwrite(current_file, image)
                remove_files()
    else:
        messagebox.showerror("Error", "Please load an image first.")
###

###
#log_transform() implements log transform functionality of Edit menu
def log_transform():
    global image,extension,image_count,log_path,max_image_count
    if(image.max()!=0):
        image = fun.log_trans_im(image)
        #general steps
        fig.clf()
        fig.add_subplot(111)
        im = plt.imshow(image,vmin=0,vmax=255)
        plt.set_cmap('gray')
        canvas.draw()

        max_image_count=image_count+1
        image_count = image_count + 1
        var.set(image_count)

        #store the image in log_folder

        current_file =  log_path + "\\" + str(image_count) + "." + str(extension)
        cv2.imwrite(current_file, image)
        remove_files()
    else:
        messagebox.showerror("Error", "Please load an image first.")
###

###
#gaussian_blur() implements gaussian blur functionality in Edit menu.
def gaussian_blur():
    global image,extension,image_count,log_path,max_image_count
    if(image.max()!=0):
        #ask the user if he wishes to use the default parameter values
        answer = messagebox.askyesno("Settings","Do you want to use default settings?\n"+"Kernel size = 3")
        if(answer==True):
            image=fun.gaussian_blur_im(image,3)
            #general steps
            fig.clf()
            fig.add_subplot(111)
            im = plt.imshow(image,vmin=0,vmax=255)
            plt.set_cmap('gray')
            canvas.draw()

            max_image_count=image_count+1
            image_count = image_count + 1
            var.set(image_count)

            #store the image in log_folder

            current_file =  log_path + "\\" + str(image_count) + "." + str(extension)
            cv2.imwrite(current_file, image)
            remove_files()
        else:
            flag=1
            while(flag==1): #take user input till he meets the conditions
                #ask user for a kernel size for the gaussian lowpass filter
                kernel_size = simpledialog.askinteger("Input", "Enter Kernel size (Odd values and min value 3):",
                                        parent=root,
                                        minvalue=3,maxvalue=min(image.shape[0],image.shape[1]))
                if(kernel_size is None): #cancel was clicked so go out of while loop
                    flag=0
                if(kernel_size is not None):
                    if(kernel_size%2==0):
                        messagebox.showinfo("Invalid kernel size", "Please enter an odd kernel size.")
                    else:
                        flag=0
                        image=fun.gaussian_blur_im(image,kernel_size)
                        #general steps
                        fig.clf()
                        fig.add_subplot(111)
                        im = plt.imshow(image,vmin=0,vmax=255)
                        plt.set_cmap('gray')
                        canvas.draw()

                        max_image_count=image_count+1
                        image_count = image_count + 1
                        var.set(image_count)

                        #store the image in log_folder

                        current_file =  log_path + "\\" + str(image_count) + "." + str(extension)
                        cv2.imwrite(current_file, image)
                        remove_files()
    else:
        messagebox.showerror("Error", "Please load an image first.")
###

###
#popup_return() is used in the butterworth sharpening functionality of Edit menu.
#this function is called after user has provided all correct input in the popup window.
def popup_return():
    global image,extension,image_count,log_path,max_image_count,lab_5_data,lab_6_data,lab_7_data,error_flag_1,error_flag_2,error_flag_3,butter_width,butter_order,butter_a,popup_true
    #print(butter_width)
    #print(butter_order)
    #print(butter_a)

    image = fun.butterworth_highpass_filter(image,butter_width,butter_order,butter_a)
    #general steps
    fig.clf()
    fig.add_subplot(111)
    im = plt.imshow(image,vmin=0,vmax=255)
    plt.set_cmap('gray')
    canvas.draw()

    max_image_count=image_count+1
    image_count = image_count + 1
    var.set(image_count)

    #store the image in log_folder

    current_file =  log_path + "\\" + str(image_count) + "." + str(extension)
    cv2.imwrite(current_file, image)
    remove_files()

###

###
#butterworth_sharpen() implements the butterworth sharpening functionality in Edit menu
def butterworth_sharpen():
    global image,extension,image_count,log_path,max_image_count,lab_5_data,lab_6_data,lab_7_data,error_flag_1,error_flag_2,error_flag_3,butter_width,butter_order,butter_a,popup_true
    if(image.max()!=0):
        #ask the user if he wishes to use the default parameter values
        answer = messagebox.askyesno("Settings","Do you want to use default settings?\n"+"width=3, order=2, a=0.5")
        if(answer==True):
            image = fun.butterworth_highpass_filter(image,3,2,0.5)
            #general steps
            fig.clf()
            fig.add_subplot(111)
            im = plt.imshow(image,vmin=0,vmax=255)
            plt.set_cmap('gray')
            canvas.draw()

            max_image_count=image_count+1
            image_count = image_count + 1
            var.set(image_count)

            #store the image in log_folder

            current_file =  log_path + "\\" + str(image_count) + "." + str(extension)
            cv2.imwrite(current_file, image)
            remove_files()
        else:
            ###initialize the variables before calling popup
            lab_5_data.set("")
            lab_6_data.set("")
            lab_7_data.set("")

            error_flag_1=0
            error_flag_2=0
            error_flag_3=0

            butter_width=""
            butter_order=""
            butter_a=""
            popup_true=0
            ###
            popupmsg()
    else:
        messagebox.showerror("Error", "Please load an image first.")
###

###
#display_image() function is called when display image option is clicked in the View menu.
#this function plots the current view(histogram, fourier magnitude,fourier phase) of
#current image on canvas along with the same view implemented on original image, for comparison.
def display_image():
    global image,extension,image_count,log_path,max_image_count,view_value,plot_number
    if(view_value=="100"): #show histogram
        plot_number=221 #changing the plot value dynamically to implement a 2x2 grid
        fig.clf()
        histogram_plot()
        image_count_backup = image_count
        image_count=1

        original_file =  log_path + "\\" + str(image_count) + "." + str(extension)
        image = scipy.ndimage.imread(original_file, mode='L')
        plot_number=223
        histogram_plot()

        #refresh the original values
        view_value="000"
        var2.set(view_value)
        image_count=image_count_backup

        backup_file =  log_path + "\\" + str(image_count) + "." + str(extension)
        image = scipy.ndimage.imread(backup_file, mode='L')

        plot_number=121

    if(view_value=="010"): #show fourier_magnitude
        plot_number=221
        fig.clf()
        fourier_mag()
        image_count_backup = image_count
        image_count=1

        original_file =  log_path + "\\" + str(image_count) + "." + str(extension)
        image = scipy.ndimage.imread(original_file, mode='L')
        plot_number=223
        fourier_mag()

        #refresh the original values
        view_value="000"
        var2.set(view_value)
        image_count=image_count_backup

        backup_file =  log_path + "\\" + str(image_count) + "." + str(extension)
        image = scipy.ndimage.imread(backup_file, mode='L')

        plot_number=121

    if(view_value=="001"): #show fourier_phase
        plot_number=221
        fig.clf()
        fourier_phase()
        image_count_backup = image_count
        image_count=1

        original_file =  log_path + "\\" + str(image_count) + "." + str(extension)
        image = scipy.ndimage.imread(original_file, mode='L')
        plot_number=223
        fourier_phase()

        #refresh the original values
        view_value="000"
        var2.set(view_value)
        image_count=image_count_backup

        backup_file =  log_path + "\\" + str(image_count) + "." + str(extension)
        image = scipy.ndimage.imread(backup_file, mode='L')

        plot_number=121
###

###
#histogram_plot() implements the histogram functionality of View menu.
#used to display the histogram of the current image on canvas alongside its histogram plot.
def histogram_plot():
    global image,extension,image_count,log_path,max_image_count,view_value,plot_number
    if(image.max()!=0):
        if(plot_number==121): #because this function will be called two times in display_original()
            fig.clf()
        fig.add_subplot(plot_number) #dynamically changing the grid plot
        im = plt.imshow(image,vmin=0,vmax=255)
        plt.set_cmap('gray')

        image_histogram=np.zeros(256) #contains histogram of image
        #create the image histogram
        for i in range(image.shape[0]):
            for j in range(image.shape[1]):
                intensity_value=int(abs(image[i][j])) #abs() is taken in case of negative image intensities
                image_histogram[intensity_value]=image_histogram[intensity_value]+1
        fig.add_subplot(plot_number+1)
        plt.stem(np.arange(256), image_histogram, markerfmt=' ') #plots a stem image of histogram

        canvas.draw()
        view_value="100" #set the callback so that the display image option is enabled
        var2.set(view_value)
    else:
        messagebox.showerror("Error", "Please load an image first.")
###

###
#fourier_mag() implements the fourier magnitude functionality of the View menu.
#this function plots the image alongside its fourier magnitude spectrum on the canvas.
def fourier_mag():
    global image,extension,image_count,log_path,max_image_count,view_value,plot_number
    if(image.max()!=0):
        if(plot_number==121): #because this function will be called two times in display_original()
            fig.clf()
        fig.add_subplot(plot_number) #dynamically change the grid plot
        im = plt.imshow(image,vmin=0,vmax=255)
        plt.set_cmap('gray')

        fourier_image = fun.find_fft_mag(image)
        fig.add_subplot(plot_number+1)
        im = plt.imshow(fourier_image,vmin=0,vmax=255)
        plt.set_cmap('gray')

        canvas.draw()
        view_value="010" #set the callback so that the display image option is enabled
        var2.set(view_value)
    else:
        messagebox.showerror("Error", "Please load an image first.")
###

###
#fourier_phase() implements the fourier phase functionality of the View menu.
#this function plots the image alongside its fourier phase spectrum on the canvas.
def fourier_phase():
    global image,extension,image_count,log_path,max_image_count,view_value,plot_number
    if(image.max()!=0):
        if(plot_number==121): #because this function will be called two times in display_original()
            fig.clf()
        fig.add_subplot(plot_number) #dynamically change the grid plot
        im = plt.imshow(image,vmin=0,vmax=255)
        plt.set_cmap('gray')

        phase_image = fun.find_fft_phase(image)
        fig.add_subplot(plot_number+1)
        im = plt.imshow(phase_image,vmin=0,vmax=255)
        plt.set_cmap('gray')

        canvas.draw()
        view_value="001" #set the callback so that the display image option is enabled
        var2.set(view_value)
    else:
        messagebox.showerror("Error", "Please load an image first.")
###

###
#undo_last() implements the undo last option in Edit menu.
#this function is used to load the previous image displayed on canvas.
#eg: if i have 5 images say, 1,2,3,4,5 in log_folder, and currently i am at 5, then it will take me to 4.
#NOTE_THIS:it won't delete 5.
def undo_last():
    global image,extension,image_count,log_path
    image_count=image_count-1 #image_count always holds the count of my current image displayed in canvas
    var.set(image_count) #set callback to change the views of options that are affected by image_count change accordingly

    if (image_count==1):
        #image_count=image_count+1
        #messagebox.showwarning("Original image", "Can't undo further.")
        editmenu.entryconfigure('undo last', state = "disabled")

    prev_file =  log_path + "\\" + str(image_count) + "." + str(extension)
    image = scipy.ndimage.imread(prev_file, mode='L')

    fig.clf()
    fig.add_subplot(111)
    im = plt.imshow(image,vmin=0,vmax=255)
    plt.set_cmap('gray')
    canvas.draw()
###

###
#undo_all() implements the undo all option in Edit menu.
#this function is used to load the original image (image 1) on canvas.
#eg: if i have 5 images say, 1,2,3,4,5 in log_folder, and currently i am at 5, then it will take me to 1.
#NOTE_THIS:it won't delete the other images 2,3,4,5.
def undo_all():
    global image,extension,image_count,log_path
    image_count=1 #set callback to affect the views accordingly
    var.set(image_count)

    first_file =  log_path + "\\" + str(image_count) + "." + str(extension)
    image = scipy.ndimage.imread(first_file, mode='L')

    fig.clf()
    fig.add_subplot(111)
    im = plt.imshow(image,vmin=0,vmax=255)
    plt.set_cmap('gray')
    canvas.draw()
###

###
#redo_last() implements the redo last option in Edit menu.
#this function is used to load the next image in log_folder on canvas.
#eg: if i have 5 images say, 1,2,3,4,5 in log_folder, and currently i am at 3, then it will take me to 4.
#NOTE_THIS:it won't delete 5. 5 will be deleted only if an image processing operation takes place when 4 is being viewed.
def redo_last():
     global image,extension,image_count,log_path
     image_count=image_count+1
     var.set(image_count)

     next_file =  log_path + "\\" + str(image_count) + "." + str(extension)
     image = scipy.ndimage.imread(next_file, mode='L')

     fig.clf()
     fig.add_subplot(111)
     im = plt.imshow(image,vmin=0,vmax=255)
     plt.set_cmap('gray')
     canvas.draw()
###

###
#redo_all() implements the redo all option in Edit menu.
#this function is used to load the last(image with max count) i.e the last processed image in log_folder on canvas.
#eg: if i have 5 images say, 1,2,3,4,5 in log_folder, and currently i am at 1, then it will take me to 5.
#NOTE_THIS:it won't delete 1,2,3,4.
def redo_all():
     global image,extension,image_count,log_path
     image_count = max_image_count
     var.set(image_count)

     last_file =  log_path + "\\" + str(image_count) + "." + str(extension)
     image = scipy.ndimage.imread(last_file, mode='L')

     fig.clf()
     fig.add_subplot(111)
     im = plt.imshow(image,vmin=0,vmax=255)
     plt.set_cmap('gray')
     canvas.draw()
###

###
#remove_files() function is used in case some image processing operation is performed
#when we are using undo, redo options. If I have files 1,2,3,4,5 and currently I am in file 2
#and I did some operation on file 2, a new file 3 will be created based on the operation
# and the previous files 4,5  will be deleted from log_folder
def remove_files():
    global view_value
    no_more_file=0
    view_value="000"
    image_count_next=image_count
    while(no_more_file==0):
        image_count_next=image_count_next+1
        next_file=log_path + "\\" + str(image_count_next) + "." + str(extension)
        if os.path.isfile(next_file):
            os.remove(next_file)
            #print(next_file + " removed\n")
        else:
            no_more_file=1
###

#set the icons in the undo and redo options of Edit menu
undo_image = Image.open("undo.png")
undo_icon = ImageTk.PhotoImage(undo_image)

redo_image = Image.open("redo.png")
redo_icon = ImageTk.PhotoImage(redo_image)

#define the menu layout
menubar=Tk.Menu(master = root)
#File menu definition
filemenu=Tk.Menu(menubar,tearoff=1)
filemenu.add_command(label="Load",command=load_image)
filemenu.add_command(label="Save as",command=save_image)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=mquit)
menubar.add_cascade(label="File",menu=filemenu)

#Edit menu definition
editmenu=Tk.Menu(menubar,tearoff=1)
editmenu.add_command(label="Equalize",command=histogram_equalize)
editmenu.add_command(label="Gamma correct",command=gamma_correct)
editmenu.add_command(label="Log Transform",command=log_transform)
editmenu.add_command(label="Gaussian blur",command=gaussian_blur)
editmenu.add_command(label="Butterworth sharpening",command=butterworth_sharpen)
editmenu.add_separator()
editmenu.add_command(label="undo last",command=undo_last,image=undo_icon,compound='left')
editmenu.add_command(label="redo last",command=redo_last,image=redo_icon,compound='left')
editmenu.add_command(label="undo all",command=undo_all)
editmenu.add_command(label="redo all",command=redo_all)
menubar.add_cascade(label="Edit",menu=editmenu)

#View menu definition
viewmenu=Tk.Menu(menubar,tearoff=1)
viewmenu.add_command(label="Display image",command=display_image)
viewmenu.add_command(label="Histogram",command=histogram_plot)
viewmenu.add_separator()
viewmenu.add_command(label="Fourier mag",command=fourier_mag)
viewmenu.add_command(label="Fourier phase",command=fourier_phase)
menubar.add_cascade(label="View",menu=viewmenu)

Tk.Tk.config(root, menu=menubar)

canvas.show() #display a blank canvas as its the first load. no image is currently drawn on it.
canvas.get_tk_widget().pack(side=Tk.BOTTOM, fill=Tk.BOTH, expand=True)

toolbar = NavigationToolbar2TkAgg(canvas, root) #this is the bottom left toolbar visible in the GUI
toolbar.update()
canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=True) #i.e cover the entire space available to you

image_count=0 #this value denotes the current image I am working with. used for undo, redo operations
max_image_count=0 #keeps count of the max image count present in log_folder
view_value="000" #keeps the current view value. 100 -> Histogram, 010 -> Fourier_magnitude, 001 -> Fourier_phase
plot_number=121 #this variable is used for the diaplay image functionality of View menu. used for dynamically changing the grid plot.

#set callbacks to define the proper views. i.e enable which options and disable which options which are affected by
#image_count and view_value.
var.set(image_count)
var2.set(view_value)

Tk.mainloop()
###END of main code###
