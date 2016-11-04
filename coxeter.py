from optparse import OptionParser

parser = OptionParser()

parser.add_option("-o", "--output", dest="outputfilename", default="out.png",
                  help="save image to FILE", metavar="FILE")
parser.add_option("-p", "--sides", dest="p", default=7)
parser.add_option("-q", "--vertex",dest="q", default=3)
parser.add_option("-s", "--size", dest="size", default = 512)
parser.add_option("-i","--input", dest="inputfilename", default = None)
parser.add_option("-H","--half-plane",action="store_true", dest="halfplane", default = False)
parser.add_option("-m","--mobius",dest="mobius", default=None)
parser.add_option("-P","--polygon",dest="polygon",action="store_true", default=False)
parser.add_option("-I","--max-iterations",dest="iters",default=14)
parser.add_option("-z","--zoom", dest="zoom",default=1.01)
parser.add_option("-t","--translate", dest="translate",default=0+0j)

parser.add_option("-A","--alternating", dest="alternating", action="store_true", default=False)

parser.add_option("-M","--multisampling", dest="oversampling", default=1)

parser.add_option("--template", dest="template", action="store_true", default = False)

(options,args) = parser.parse_args()

from PIL import Image
from math import sin,cos,tan,sqrt,floor
from cmath import exp

import random

PI = 3.14159265359


# COLOURS

def HTMLColorToRGB(colorstring):
    """ convert #RRGGBB to an (R, G, B) tuple """
    colorstring = colorstring.strip()
    if colorstring[0] == '#': colorstring = colorstring[1:]
    if len(colorstring) != 6:
        raise ValueError, "input #%s is not in #RRGGBB format" % colorstring
    r, g, b = colorstring[:2], colorstring[2:4], colorstring[4:]
    r, g, b = [int(n, 16) for n in (r, g, b)]
    return (r, g, b, 255)

red = HTMLColorToRGB("#FF3333")
black =   HTMLColorToRGB("#000000")


#params
oversampling = int(options.oversampling)
size = int(options.size) * oversampling
SZ = (size,size)
MAX_ITER = int(options.iters)
p = int(options.p)
q = int(options.q)

template = options.template
alternating = options.alternating

if q < 0:#infinity
    q = 2**10

if (p-2)*(q-2) <= 4:
    print "Error: tessellation is not hyperbolic."
    exit(1)

if (alternating and (p%2 == 1)):
    print "Error: alternating mode cannot be used with odd p."
    exit(1)


# projection params
zoom = float(options.zoom)
translation_affine = complex(options.translate)



out = Image.new("RGB",SZ, "white")
out_pixels = out.load()

rot2PIp = exp(1j*2*PI/float(p))
tanPIp = tan(PI/float(p))

if (not alternating):
    rotator = rot2PIp
    curtanPIp = tanPIp
else:
    rotator = rot2PIp ** 2
   # halfrot = exp(1j*2*PI/float(p))
    #tanPIp = tan(PI/float(p))
    doubletanPIp = tan(2*PI/float(p))

    curtanPIp = doubletanPIp


d = sqrt (  (cos(PI/q)**2) / ( cos(PI/q)**2 - sin(PI/p)**2) )
r = sqrt (  (sin(PI/p)**2) / ( cos(PI/q)**2 - sin(PI/p)**2) )

centre = complex(d,0) # center of inversion circle
r2 = r*r

# geom functions

def abs2(w):
    return w.real**2 + w.imag**2

if (not alternating):
    def inFund(z):
        return ( (z.imag >= 0) and \
                 (z.imag < tanPIp * z.real) and \
                 (abs2(z - centre) > r2 ) )
else:
    rot_centre = rot2PIp * centre

    def inFund(z):
        return ( (z.imag >=0) and \
                (z.imag < doubletanPIp * z.real) and \
                ( (abs2(z-centre) > r2) and ( abs2(z-centre*rot2PIp)> r2) ) )



#Input sector precalc

phiangle = PI/2. - (PI/p + PI/q)

a = cos(phiangle)*r
x_input_sector = d-a
y_input_sector = sin(phiangle)*r

input_sector = max(x_input_sector,y_input_sector)

# template
if (template):
    templimg = Image.new("RGB",SZ,"white")
    templimg_pixels = templimg.load()
    for i in range(size):
        for j in range(size):
            z = (i + 1j*j)/(float(size))*input_sector
            if inFund(z):
                templimg_pixels[i,j] = (0,0,0,255)
    templimg.save("template.png")
    exit(0)



# load in image
usingImage = (options.inputfilename != None)
if usingImage:
    inimage = Image.open(options.inputfilename).convert("RGB")
    inimage_pixels = inimage.load()
    inW, inH = inimage.size


    print "computing average colour..."
    ar,ag,ab = 0,0,0
    count = 0

    for x in range(inW):
        for y in range(inH):
            temp = inimage_pixels[x,y]
            ar+=temp[0]
            ag+=temp[1]
            ab+=temp[2]
            count += 1
    average_colour = (ar/count,ag/count,ab/count)

    #print "average: ",average_colour


#bilinear sampling

def lerp(a, b, coord):
    if isinstance(a, tuple):
        return tuple([lerp(c, d, coord) for c,d in zip(a,b)])
    ratio = coord - floor(coord)
    return int(round(a * (1.0-ratio) + b * ratio))

def bilinear(im, x, y):
    x1, y1 = int(floor(x)), int(floor(y))
    x2, y2 = x1+1, y1+1
    left = lerp(im[x1, y1], im[x1, y2], y)
    right = lerp(im[x2, y1], im[x2, y2], y)
    return lerp(left, right, x)


# mobius
usingMobius = False
if options.mobius != None:
    usingMobius = True
    mobiusA = float(options.mobius)





# main iteration


for x in range(SZ[0]):
    if x%50 == 0:
        print str((x*100)/SZ[0]) + "%"
    for y in range(SZ[1]):
        if (options.halfplane):
            X = 2*float(x)/SZ[0]        
            Y = 2*float(SZ[1]-y)/SZ[1]  
            w = complex(X,Y)
            z = (w-1j)/(-1j*w + 1)
        else:
            # should allow for arbitrary affine maps
            X = (2*float(x)/SZ[0]-1. ) 
            Y = (2*float(y)/SZ[1]-1. )
            z = translation_affine + complex(X,Y) * zoom

        # exclude if outside the disk
        if (abs2(z)  > 1):
            continue

        #mobius
        if usingMobius:
            z = (z+mobiusA)/(1+ z*mobiusA)



        endflag = False # detect loop
        outflag = False # detect out of disk
        parity = 0      # count transformation parity

        for it in range(MAX_ITER): 
            # rotate z into fundamental wedge
            while( (abs(z.imag) > curtanPIp * z.real) ):
                if (z.imag < 0):
                    z *= rotator
                else:
                    z /= rotator

            if inFund(z):
                break

            # flip

            z = z.conjugate()
            if (not options.polygon):
                parity += 1
 
            if inFund(z):
                break


            # invert
            
            
            local_centre = centre if ((not alternating) or (abs(z.imag) < tanPIp * z.real)) else rot_centre

            w = z - local_centre
            w = w * r2 / abs2(w)
            nz = local_centre + w
            
            if (abs2(nz) < abs2(z)):
                z = nz    
                parity += 1

            if inFund(z):
                break

            if it == MAX_ITER - 1:
                endflag = True

            # outta disk (should not happen)
            #if (X*X + Y*Y  > 1):
            #    outflag = True
            #    break


        # produce colour
        if (inFund(z)):
            if usingImage:
                xx = int(z.real/input_sector*inW)
                yy = int(z.imag/input_sector*inH)
                try:
                    c = bilinear(inimage_pixels,xx,yy)
                except IndexError: # out of bounds
                    c = average_colour# (0,255,255,255)
            else:
                # c = (int(z.real*255),int(z.imag*255),0,255)
                c = red if (parity % 2 == 0) else black
        else:
            c = (0,255,0,255) # error?

        if (endflag):
            if usingImage:
                c = average_colour
            else:
                c = (0,0,255,255) # too many iters

        if (outflag):
            c = (255,0,255,255) # out of circle

        out_pixels[x,y] = c

if (oversampling > 1):
    out = out.resize( (int(options.size), int(options.size)) , Image.LANCZOS)

out.save(options.outputfilename)

