# coxeter
This is a Python script to generate pictures of regular hyperbolic tilings, using also source images.

Regular tilings are indexed by naturals (p,q). p is the number of sides of the regular polygons, and q is the number of polygons per vertex. For the tiling to be hyperbolic, it must be that (p-2)*(q-2) - 4 > 0. If the LHS is < 0, it's a spherical tiling (i.e. a platonic solid) and if it's 0 then it's a tiling of the Euclidean plane. So, take (p,q) such that the tiling is hyperbolic, for example, p=6, q=4. Then

```
python coxeter.py -p 6 -q 4 -o hexagons.png -s 500
```

will generate a 500x500 image of the tiling by right-angled hexagons in the Poincaré disk model, and save it as `hexagons.png`. Actually, this will draw the fundamental domains of the tiling, the Schwarz triangles, coloured according to parity. If you want to actually colour the hexagons, try

```
python coxeter.py -p 6 -q 4 -o hexagons.png -s 500 --polygon
```

this will colour hexagons in an alternating fashion. Obviously, this is only available if q is even.

Depending on p,q, and the resolution some parts of the image will appear blue, these are pixels which haven't converged in the maximum number of iterations allowed. In that case, the number of iterations can be increased with `-I ITERS` (default 14).

The picture will often come out noisy or pixelated because of aliasing. This is normal. You can render it at a higher resolution and then resample it down with the `--multisampling` option. For example:

```
python coxeter.py -p 6 -q 4 -o hexagons.png -s 500 --multisampling=2
```

renders the image at 1000x1000 and then downscales it to 500x500 with Lanczos sampling.

You can also render the image in the half-plane model instead of the Poincaré disk by adding `-H`.

### Using images as input

To use an image as input for the tessellation, add `-i input.png`. Note the resolution of the input image has very little to no effect on the render time, so feel free to go big and detailed. To know how to set up the input image properly, run the program first with the intended parameters and `--template`. This will produce a `template.png` file, of the size specified by `-s`, with the fundamental region highlighted. Make sure your input image is square and aligned with the fundamental domain in the template.

Note that when using input images, pixels which have not converged will be set to the average colour of the source image instead of blue. This might sometimes be preferable to the high-frequency noise in the outermost region of the disk, so it is possible that lower values of `-I` might yield slightly better results.
