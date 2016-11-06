import tqdm
from PIL import Image
from math import sin, cos, tan, sqrt, floor, pi
from cmath import exp

import random
import exceptions


# COLOURS
def HTMLColorToRGB(colorstring):
    """ convert #RRGGBB to an (R, G, B) tuple """
    colorstring = colorstring.strip()
    if colorstring[0] == '#': colorstring = colorstring[1:]
    if len(colorstring) != 6:
        raise exceptions.ColorFormatError(
            "input #%s is not in #RRGGBB format" %colorstring)
    r, g, b = colorstring[:2], colorstring[2:4], colorstring[4:]
    try:
        r, g, b = [int(n, 16) for n in (r, g, b)]
    except ValueError:
        raise exceptions.ColorFormatError(
                "input #%s is not composed of hex literals" %colorstring)
    return (r, g, b, 255)


# geom functions
def abs2(w):
    return w.real*w.real + w.imag*w.imag


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


def main(
        p,
        q,
        size_original,
        input_image,
        half_plane,
        mobius,
        polygon,
        max_iterations,
        zoom,
        translate,
        alternating,
        oversampling,
        template,
        truncate_uniform,
        truncate_complete,
        colours):


    if q < 0:#infinity
        q = 2**10

    if (p - 2) * (q - 2) <= 4:
        raise exceptions.NotHyperbolicError(
            "(p - 2) * (q - 2) < 4: tessellation is not hyperbolic")

    if (alternating and p % 2):
        raise exceptions.AlternatingModeError(
            "alternating mode cannot be used with odd p.")

    oversampled_size = size_original * oversampling
    shape = (oversampled_size, oversampled_size)

    #Input sector precalc

    phiangle = pi / 2 - (pi / p + pi / q)

    d = sqrt((cos(pi/q)**2) / (cos(pi/q)**2 - sin(pi/p)**2))
    r = sqrt((sin(pi/p)**2) / (cos(pi/q)**2 - sin(pi/p)**2))

    a = cos(phiangle)*r
    x_input_sector = d-a
    y_input_sector = sin(phiangle)*r
    input_sector = max(x_input_sector, y_input_sector)


    # Colours parsing

    col_bg, col_primary , col_secundary, col_truncation, col_divergent = map(HTMLColorToRGB, colours)

    # palette = [ (random.randint(0,255),random.randint(0,255),random.randint(0,255),255) for j in range(15) ]

    # average input colour

    if input_image:
        inimage_pixels = input_image.load()
        inW, inH = input_image.size
        ar,ag,ab = 0,0,0
        count = 0

        for x in range(inW):
            for y in range(inH):
                temp = inimage_pixels[x,y]
                ar+=temp[0]
                ag+=temp[1]
                ab+=temp[2]
                count += 1
        average_colour = (ar // count, ag // count, ab // count)


    # precalc

    rot2pip = exp(1j*2*pi/float(p))
    tanpip = tan(pi/float(p))

    if (not alternating):
        rotator = rot2pip
        curtanpip = tanpip
    else:
        rotator = rot2pip ** 2
        # halfrot = exp(1j*2*pi/float(p))
        # tanpip = tan(pi/float(p))
        doubletanpip = tan(2*pi/float(p))
        curtanpip = doubletanpip


    centre = complex(d,0) # center of inversion circle
    r2 = r*r

    rot_centre = rot2pip * centre
    if truncate_uniform or truncate_complete:
        centre_truncation_uniform = exp(1j*pi/float(p)) * centre
    if truncate_complete:
        rprime2 = abs2( centre_truncation_uniform - (d-r) )

    # fundamental region

    def in_fund(z):
        if alternating:
            return (
                (z.imag >=0) and
                (z.imag < doubletanpip * z.real) and
                ((abs2(z-centre) > r2) and ( abs2(z - centre*rot2pip)> r2)))
        else:
            return (
                (z.imag >= 0) and
                (z.imag < tanpip * z.real) and
                (abs2(z - centre) > r2 ))

    # template

    if (template):
        templimg = Image.new("RGB",(size_original,size_original),"white")
        templimg_pixels = templimg.load()
        for i in range(size_original):
            for j in range(size_original):
                z = (i + 1j*j)/(float(size_original))*input_sector
                if in_fund(z):
                    templimg_pixels[i,j] = (0,0,0,255)
        return templimg

    # create main buffer

    out = Image.new("RGB", shape, col_bg)
    out_pixels = out.load()

    # render loop

    for x in tqdm.trange(shape[0]):
        for y in range(shape[1]):
            if (half_plane):
                X = 2*float(x)/shape[0]        
                Y = 2*float(shape[1]-y)/shape[1]  
                w = complex(X,Y)
                z = (w-1j)/(-1j*w + 1)
            else:
                # should allow for arbitrary affine maps
                X = (2*float(x)/shape[0]-1. ) 
                Y = (2*float(y)/shape[1]-1. )
                z = translate + complex(X,Y) * zoom


            z += 0.0001*(random.random()+1j) # <- fix boundary errors

            # exclude if outside the disk
            if (z.real*z.real + z.imag*z.imag  > 1): # optimization: explicit abs2 instead of calling
                continue

            #mobius
            if mobius:
                z = (z+mobius)/(1+ z*mobius)

            endflag = False # detect loop
            outflag = False # detect out of disk
            parity = 0      # count transformation parity

            for it in range(max_iterations): 

                # rotate z into fundamental wedge
                emergency = 0
                while((abs(z.imag) > curtanpip * z.real)):
                    if (z.imag < 0):
                        z *= rotator
                    else:
                        z /= rotator
                    emergency += 1
                    if emergency > 500:
                        break

                if in_fund(z):
                    break

                # flip
                z = z.conjugate()
                if (not polygon):
                    parity += 1
    
                if in_fund(z):
                    break


                # invert
                local_centre = centre if ((not alternating) or (abs(z.imag) < tanpip * z.real)) else rot_centre

                w = z - local_centre
                # w = w * r2 / abs2(w)
                w = r2 / w.conjugate() # optimization
                nz = local_centre + w
                
                #if (abs2(nz) < abs2(z)):
                if (nz.real*nz.real + nz.imag*nz.imag < z.real*z.real + z.imag*z.imag): # again optimization
                    z = nz    
                    parity += 1

                if in_fund(z):
                    break

                if it == max_iterations - 1:
                    endflag = True

            # produce colour
            if (in_fund(z)):
                if input_image:
                    xx = int(z.real/input_sector*inW)
                    yy = int(z.imag/input_sector*inH)
                    try:
                        c = bilinear(inimage_pixels,xx,yy)
                    except IndexError:
                        c = average_colour #(0,255,255,255)
                else:
                    # c = (int(z.real*255),int(z.imag*255),0,255)
                    c = col_secundary if (parity % 2 == 0) else col_primary
                    #c = palette[ parity % 3]
                    if truncate_uniform and (abs2(z-centre_truncation_uniform) < r2):
                        c = col_truncation
                    if truncate_complete and (abs2(z-centre_truncation_uniform) < rprime2):
                        c = col_truncation

            else:
                c = (0,255,0,255) # error?

            if (endflag):
                if input_image:
                    c = average_colour
                else:
                    c = col_divergent # too many iters

            if (outflag):
                c = (255,0,255,255) # out of circle

            out_pixels[x,y] = c

    if (oversampling > 1):
        out = out.resize((size_original, size_original), Image.LANCZOS)

    return out
