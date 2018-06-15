###START of function###
#This is the function which holds all the functionalities of the menu options.#
#This is imported in the main code.#
import numpy as np
from matplotlib import pyplot as plt
import scipy.ndimage.filters as fi
import cv2

###
# histeq_im(img)
# function to equalize the histogram of the given image using discrete CDF as transform function
# img --> input image
# Returns the histogram equalized image

def histeq_im(img):
    cols=len(img[0][:]) #y-axis
    rows=len(img[:,0])  #x-axis

    L=256 #max number of intensities. here 256 as gray scale is used.
    M=rows
    N=cols

    r=np.zeros(L) #contains histogram of r
    s=np.zeros(L) #contains histogram of s
    trans=np.zeros(L) #contains the mapping from input intensity to output intensity

    out_img=np.zeros_like(img) #output image

    #create histogram of input image
    for i in range(rows):
        for j in range(cols):
            intensity_value=img[i][j]
            r[intensity_value]=r[intensity_value]+1

    #create the mapping
    for i in range(L):
        sum=0
        for j in range(i+1):
            sum=sum+r[j]
            trans[i]=np.uint8(((L-1)/(M*N))*sum) #MOST IMPORTANT STEP IS uint8. Else doesn't work!!!!

    #create the output image
    for i in range(rows):
        for j in range(cols):
            out_img[i][j]=trans[img[i][j]]

    #create output histogram
    for i in range(rows):
        for j in range(cols):
            intensity_value=int(out_img[i][j])
            s[intensity_value]=s[intensity_value]+1

    return out_img
###

###
# gamma_im(image,gamma)
# function to implement gamma correction on input image
# image --> input image
# gamma --> gamma value required for correction. gamma < 1 brightens the image, gamma > 1 darkens it.
#           gamma = 1 is identity transform.
# Returns the gamma corrected image

def gamma_im(image,gamma):
    L=256 #as gray scale is used
    rows=image.shape[0]
    cols=image.shape[1]

    trans=np.zeros(L) #stores the transformation mapping of different intensities from 0 to 255.
    out_img=np.zeros_like(image) #output image

    #gamma value > 1 helps improving too much bright images as it helps in contrast stretching
    #for the high intensities
    #gamma value < 1 helps for dark images

    #Gamma correction formula: s = c*(r**gamma)
    #compute constant c
    try:
        c=(L-1)/((L-1)**gamma)
    except Exception as e:
        return None

    #find the transformation mapping
    for i in range(L):
        trans[i]=np.uint8(c*(i**gamma))

    #implement gamma correction
    for i in range(rows):
        for j in range(cols):
            out_img[i][j]=trans[image[i][j]]

    return out_img
###

###
# log_trans_im(image)
# function to implement log transformation on input image
# image --> input image
# Returns the log transformed image

def log_trans_im(image):
    L=256 #as gray scale is used
    rows=image.shape[0]
    cols=image.shape[1]

    trans=np.zeros(L) #stores the transformation mapping of different intensities from 0 to 255.
    out_img=np.zeros_like(image) #output image
    #Log transformation formula: s = c*log(1 + r)
    #compute constant c
    c=(L-1)/(np.log10(L))

    #find the transformation mapping
    for i in range(L):
        trans[i]=np.uint8(c*np.log10(1+i))

    #implement log transformation
    for i in range(rows):
        for j in range(cols):
            out_img[i][j]=trans[image[i][j]]

    return out_img
###

###
# convolve2d(image, kernel)
# This function which takes an image and a kernel and returns the convolution of them
# image --> input image.a numpy array of size [image_height, image_width].
# kernel--> a numpy array of size [kernel_height, kernel_width].
# Returns a numpy array of size [image_height, image_width] (convolution output)

def convolve2d(image, kernel):
    kernel = np.flipud(np.fliplr(kernel))    # Flip the kernel
    output_image = np.zeros_like(image)            # convolution output
    D=kernel.shape[0] #size of kernel
    # Add zero padding to the input image
    image_padded = np.zeros((image.shape[0] + (D-1), image.shape[1] + (D-1)))
    image_padded[int((D-1)/2):-int((D-1)/2), int((D-1)/2):-int((D-1)/2)] = image
    for x in range(image.shape[1]):     # Loop over every pixel of the image
        for y in range(image.shape[0]):
            # element-wise multiplication of the kernel and the image
            output_image[y,x]=(kernel*image_padded[y:y+D,x:x+D]).sum()
    return output_image
###

###
# gaussian_blur_im(image,kernel_size)
# function to implement gaussian blur on input image
# image --> input image
# kernel_size --> the size of the gaussian lowpass filter which will be used for convolution.
# Returns the lowpass filtered image i.e. gaussian blurred image

def gaussian_blur_im(image,kernel_size):
    #This function takes the image and kernel size as input and gives
    #the gaussian blurred image as output

    ##form the gaussian kernel
    sigma=kernel_size/6 #as kernel size max required to cover the gaussian is 6 sigma in size
    kernel=np.zeros((kernel_size, kernel_size))
    # set element at the middle to one, a dirac delta
    kernel[kernel_size//2, kernel_size//2] = 1
    # gaussian-smooth the dirac, resulting in a gaussian filter mask
    kernel=fi.gaussian_filter(kernel, sigma) #kernel is the gaussian kernel
    #output_image=convolve2d(image,kernel)
    ###
    #can also manually generate the gaussian kernel as below
    '''
    mean=int((kernel_size-1)/2)
    #form the gaussian kernel centered at mean
    for i in range(kernel_size):
        for j in range(kernel_size):
            kernel[i][j]=(np.exp(-((((i-mean)**2)+((j-mean)**2))/(2*(sigma**2)))))/(2*(np.pi)*(sigma**2))
    normalised_kernel=kernel/kernel.sum() #normalise the kernel
    '''
    ###
    output_image=cv2.filter2D(image,-1,kernel) #forced to use cv2 here as it works even for large kernel size. convolve2d hangs for this.

    return output_image
###

###
# butterworth_highpass_filter(image,width,order,dc_amplification)
# function to implement a highpass filtering on image using butterworth transfer function
# image --> input image
# width --> thershold i.e. D_0 for the filter
# order --> filter order
# dc_amplification --> a value i.e. value of transfer function for (u,v) = (0,0)
# Returns the highpass filtered image i.e. butterworth sharpened image

def butterworth_highpass_filter(image,width,order,dc_amplification):
    M=image.shape[0]  #rows
    N=image.shape[1]  #columns

    P=2*M
    Q=2*N

    ##Form the padded image

    padded_image=np.zeros((P, Q))
    padded_image[0:M,0:N]=image

    ##multiply by (-1^(x+y)) to centre frequency spectrum
    '''
    for i in range(P):
        for j in range(Q):
            padded_image[i][j] = padded_image[i][j] * (-1**(i+j))
    '''
    ##find FFT of image
    fft_padded_image = np.fft.fft2(padded_image)
    fshift = np.fft.fftshift(fft_padded_image)
    #magnitude_spectrum_pimage = 20*np.log(np.abs(fshift)) #magnitude spectrum of padded image

    ##Generate the filter tansform H(u,v)
    D_0=width
    n=order
    a=dc_amplification #Amplification of lowest frequency ie. 0 compared to highest

    H=np.zeros((P, Q)) #Transfer function matrix
    D=np.zeros((P, Q)) #Distance matrix

    #Form the Butterworth Transfer function matrix
    for i in range(P):
        for j in range(Q):
            D[i][j]=np.sqrt(((i-(P/2))**2)+((j-(Q/2))**2))
            if(D[i][j]==0):
                H[i][j]=a
            else:
                H[i][j]=a+(1/(1+((D_0/D[i][j])**(2*n))))
                if(H[i][j]>1):
                    H[i][j] = 1 #to maintain the a value as per definition

    ##form G(u,v)=H(u,v)F(u,v)
    G=np.zeros((P, Q))
    for i in range(P):
        for j in range(Q):
            fshift[i][j]=H[i][j]* fshift[i][j]

    # shift back (we shifted the center before)
    f_ishift = np.fft.ifftshift(fshift)

    # inverse fft to get the image back
    img_back = np.fft.ifft2(f_ishift)

    output_image=np.zeros_like(image)
    output_image=abs(img_back[0:M,0:N].real).astype(int)

    return output_image
###

###
# find_fft_mag(image)
# function to find fourier magnitude spectrum of image
# image --> input image
# Returns the log transformed fourier magnitude spectrum of image

def find_fft_mag(image):
    fft_out = np.fft.fft2(image) #find 2d-fourier transform
    fshift = np.fft.fftshift(fft_out) #center the Fourier transform
    magnitude_spectrum = 20*np.log(1+np.abs(fshift)) #log transform to scale the values for proper visualization

    return magnitude_spectrum
###

###
# find_fft_mag(image)
# function to find fourier phase spectrum of image
# image --> input image
# Returns the fourier phase spectrum of image

def find_fft_phase(image):
    fft_out = np.fft.fft2(image) #find 2d-fourier transform
    fshift = np.fft.fftshift(fft_out) #center the Fourier transform
    phase_spectrum = np.angle(fshift) #like arctan(a,b) for a+bj

    #Normalize phase spectrum
    max_phase=np.amax(phase_spectrum)
    for row in range(phase_spectrum.shape[0]):
        for col in range(phase_spectrum.shape[1]):
            phase_spectrum[row][col]=(phase_spectrum[row][col]/max_phase)*255

    return phase_spectrum
###
###END of Function###
