# coxeter

This is a Python script to generate pictures of regular (and a few uniform) hyperbolic tilings, using also source images.

## Installation

Install with

```
python setup.py develop
```

You might need to run that as superuser. You might also need to install Cython; if it complains just do

```
pip install cython
```

## Usage

Regular tilings are indexed by naturals (p,q). p is the number of sides of the regular polygons, and q is the number of polygons per vertex. For the tiling to be hyperbolic, it must be that (p-2)*(q-2) - 4 > 0. If the LHS is < 0, it's a spherical tiling (i.e. a platonic solid) and if it's 0 then it's a tiling of the Euclidean plane. So, take (p,q) such that the tiling is hyperbolic, for example, p=6, q=4. Then

```
coxeter -p 6 -q 4 -s 500 hexagons.png
```

will generate a 500x500 image of the tiling by right-angled hexagons in the Poincaré disk model, and save it as `hexagons.png`. In addition, (p,∞) tilings can also be created, with infinite regular ideal p-gons joining at vertices at infinite, by setting `-q -1`. (∞,q) tilings are not available.

Actually, the will draw the fundamental domains of the tiling, the Schwarz triangles, coloured according to parity. If you want to actually colour the hexagons, try

```
python coxeter.py -p 6 -q 4 -s 500 --polygon hexagons.png
```

this will colour hexagons in an alternating fashion. Obviously, this is only available if q is even.

A way to visualize the polygons for any p and q is to draw the edges. Setting `--borders WIDTH` will draw borders whose thickness is a fraction WIDTH of the polygon size.

Depending on p,q, and the resolution some parts of the image will appear blue, these are pixels which haven't converged in the maximum number of iterations allowed. In that case, the number of iterations can be increased with `--max_iterations ITERS` (default 14).

The picture will often come out noisy or pixelated because of aliasing. This is normal. You can render it at a higher resolution and then resample it down with the `--multisampling` option. For example:

```
coxeter -p 6 -q 4 -s 500 --multisampling=2 hexagons.png
```

renders the image at 1000x1000 and then downscales it to 500x500 with Lanczos sampling.

### Colours

When not using image mode, colours for rendering can be fully customized with the following options

Command | Colour
--------|--------
`--colour_bg` | background colour
`--colour_primary` | first tile colour
`--colour_secundary` | second tile colour
`--colour_divergent` | colour for non-converging pixels (defaults to bright blue)
`--colour_truncation` | colour of polygons resulting from a truncation
`--colour_borders` | colour of borders when using `--border`

### Other models

Other projections of the hyperbolic plane can be used instead of the Poincaré disk.

Projection | Command
-----------|--------
Poincaré disk | None
Half-plane model | `--half_plane` or `-h`
Square | `--squircle`
Azimuthal equidistant | `--equidistant`

The first three projections are conformal. The map to the square is implemented through a Schwarz-Christoffel biholomorphism.

The azimuthal equidistant projection is not conformal, but represents radial distances faithfully.

The projections can be better appreciated by zooming in or out with the option `--zoom ZOOM_FACTOR`.

### Truncation

It's possible to obtain a uniform or complete truncation of a tiling by adding `--truncate-uniform` or `--truncate-complete`.

### Using images as input

To use an image as input for the tessellation, add `-i input.png`. Note the resolution of the input image has very little to no effect on the render time, so feel free to go big and detailed. 

To know how to set up the input image properly so that it is sampled correctly, run the program first with the intended parameters and `--template`. This will produce a template image of the size specified by `-s` with the fundamental region highlighted. Example

```
coxeter -p 7 -q 3 -s 500 --template template.png
```

Multisampling is ignored when templating. Make sure your input image is square and aligned with the fundamental domain in the template. The input image does not need to be the same size of the template; the sampling will be rescaled according to its size.

Note that when using input images, pixels which have not converged will be set to the average colour of the source image instead of blue. This might sometimes be preferable to the high-frequency noise in the outermost region of the disk, so it is possible that lower values of `--max_iterations` might yield slightly better results.

