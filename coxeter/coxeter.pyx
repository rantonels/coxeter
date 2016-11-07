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
cdef extern from "complex.h":
    float creal(complex)
cdef extern from "complex.h":
    float cimag(complex)
cdef extern from "complex.h":
    complex conj(complex)

cdef float abs2(complex w):
    return creal(w)*creal(w) + cimag(w)*cimag(w)

cdef complex mobius_translation (complex w,complex a):
    return (w+a)/(1+w*a)
    
cdef float signum(float x):
    return (x>0) - (x<0)
cdef float rabs (float x):
    return x * signum(x)


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


# precalc defs

cdef complex rot2pip
cdef float tanpip
cdef complex centre,rotator, pivot_vertex, vertex_rotator
cdef doubletanpip,curtanpip
cdef float r2,r,d

cdef bint do_alternating

# fundamental region

cdef bint in_fund(complex zz):
    global do_alternating, doubletanpip, tanpip, rot2pip, r2, centre
    if do_alternating:
        return (
            (cimag(zz) >=0) and
            (cimag(zz) < doubletanpip * creal(zz)) and
            ((abs2(zz-centre) > r2) and ( abs2(zz - centre*rot2pip)> r2)))
    else:
        return (
            (zz.imag >= 0) and
            (zz.imag < tanpip * zz.real) and
            (abs2(zz - centre) > r2 ))

# flipper

cdef complex cI = 1j



cdef rotate_about_apotheme(complex zz,complex pivot):
    global vertex_rotator
    return mobius_translation( vertex_rotator *  mobius_translation(zz,-pivot)  , pivot)



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
        translate               = 0,
        flip                    = False,
        alternating             = False,
        oversampling            = None,
        template                = False,
        truncate_uniform        = False,
        truncate_complete       = False,
        colours                 = []):
    global do_alternating, doubletanpip, tanpip, rot2pip, r2, centre, r, d

    cdef bint do_flip = flip
    do_alternating = alternating

    if q < 0:#infinity
        q = 2**10

    if (p - 2) * (q - 2) <= 4:
        raise exceptions.NotHyperbolicError(
            "(p - 2) * (q - 2) < 4: tessellation is not hyperbolic")

    if (do_alternating and p % 2):
        raise exceptions.AlternatingModeError(
            "alternating mode cannot be used with odd p.")

    oversampled_size = size_original * oversampling
    shape = (oversampled_size, oversampled_size)

    #Input sector precalc

    phiangle = pi / 2 - (pi / p + pi / q)

    d = sqrt((cos(pi/q)**2) / (cos(pi/q)**2 - sin(pi/p)**2))
    r = sqrt((sin(pi/p)**2) / (cos(pi/q)**2 - sin(pi/p)**2))

    R = sqrt(r*r + d*d - 2*r*d*cos(phiangle)) # circumscribed circle radius
    centers_distance = 2 * (d-r) / (1+(d-r)**2) # distance between centres of adjacent polygons

    print centers_distance, d-r, mobius_translation(d-r,d-r)
    print rabs(1), rabs(-1)

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
    rotpip = exp(1j*pi/float(p))
    tanpip = tan(pi/float(p))


    if (not do_alternating):
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

    pivot_vertex = exp(1j * pi/float(p)) * R # pivot vertex for rotation.
    vertex_rotator = exp(-2j * pi/float(q))

    rot_centre = rot2pip * centre
    if truncate_uniform or truncate_complete:
        centre_truncation_uniform = exp(1j*pi/float(p)) * centre
    if truncate_complete:
        rprime2 = abs2( centre_truncation_uniform - (d-r) )



    # template

    if (template):
        templimg = Image.new("RGB",(size_original,size_original),"white")
        templimg_pixels = templimg.load()
        for i in range(size_original):
            for j in range(size_original):
                zz = (i + 1j*j)/(float(size_original))*input_sector
                if in_fund(zz):
                    templimg_pixels[i,j] = (0,0,0,255)
        return templimg

    # create main buffer

    out = Image.new("RGB", shape, col_bg)
    out_pixels = out.load()

    # render loop

    cdef int COLUMNS = shape[0]
    cdef int LINES = shape[1]
    cdef int xl,yl
    cdef complex z,nz

    cdef int max_iterations_int = max_iterations
    cdef int it

    cdef bint endflag, outflag
    cdef int parity = 0      # count transformation parity



    for xl in tqdm.trange(COLUMNS):
        for yl in range(LINES):
            if (half_plane):
                X = 2*float(xl)/shape[0]        
                Y = 2*float(shape[1]-yl)/shape[1]  
                w = complex(X,Y)
                z = (w-1j)/(-1j*w + 1)
            else:
                # should allow for arbitrary affine maps
                X = (2*float(xl)/shape[0]-1. ) 
                Y = (2*float(yl)/shape[1]-1. )
                z = translate + complex(X,Y) * zoom


            z += 0.0001*(random.random()+1j) # <- fix boundary errors

            # exclude if outside the disk
            if abs2(z) > 1.0:
                continue

            #mobius
            if mobius:
                z = (z+mobius)/(1+ z*mobius)

            endflag = False # detect loop
            outflag = False # detect out of disk
            parity = 0      # count transformation parity

            #if abs2( z - pivot_vertex ) < 0.001:
            #        outflag = True
            #        continue

            for it in range(max_iterations_int): 

                
                # rotate z into fundamental wedge
                emergency = 0
                while((rabs(z.imag) > curtanpip * z.real)):
                    if (z.imag < 0):
                        z *= rotator
                    else:
                        z /= rotator
                    emergency += 1
                    if emergency > 500:
                        break

                if in_fund(z):
                    break

                
                if do_flip:
                    # rotate about apotheme

                    #nz = rotate_about_apotheme(z,pivot_vertex)
                    #if abs2(nz) < abs2(z):
                    #    z = nz
                    #    parity += 1

                    #nz = rotate_about_apotheme(z,conj(pivot_vertex))
                    #if abs2(nz) < abs2(z):
                    #    z = nz
                    #    parity += 1

                    # translate back

                    if(cimag(z) <= 0):
                        z =  z*rot2pip
                        parity += 1

                    if in_fund(z):
                        break

                    z = mobius_translation(z, - centers_distance)
                    #if abs2(nz) < abs2(z):
                    #    z = nz


                    #if (abs2(nz) < abs2(z)):
                    #    z = nz
                    parity += 1

                else:
                    # flip
                    z = conj(z)
                    if (not polygon):
                        parity += 1
        
                    if in_fund(z):
                        break

                    # bring closer

                    # invert

                    local_centre = centre if ((not do_alternating) or (rabs(z.imag) < tanpip * z.real)) else rot_centre

                    w = z - local_centre
                    # w = w * r2 / abs2(w)
                    w = r2 / conj(w) # optimization
                    nz = local_centre + w
                    
                    if (abs2(nz) < abs2(z)):
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

            out_pixels[xl,yl] = c

    if (oversampling > 1):
        out = out.resize((size_original, size_original), Image.LANCZOS)

    return out
