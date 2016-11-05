import click
from coxeter import coxeter
from PIL import Image


@click.command()
@click.option("-p", type=int, default=7)
@click.option("-q", type=int, default=3)
@click.option("-s", "--size", type=int, default=512)
@click.option("-i", "--input_file_name", type=click.Path(), default=None)
@click.option("-h", "--half_plane", is_flag=True)
@click.option("-m", "--mobius", type=float, default=0)
@click.option("--polygon", is_flag=True)
@click.option("--max_iterations", type=int, default=14)
@click.option("-z", "--zoom", type=float, default=1.01)
@click.option("-t", "--translate", type=complex, default=0 + 0j)
@click.option("-a", "--alternating", is_flag=True)
@click.option("--oversampling", type=int, default=1)
@click.option("--truncate_uniform",is_flag=True)
@click.option("--truncate_complete",is_flag=True)
@click.option("--template",is_flag=True)
@click.option("--colour_bg",        default = "#FFFFFF")
@click.option("--colour_primary",   default = "#000000")
@click.option("--colour_secundary", default = "#FF3333")
@click.option("--colour_truncation",default = "#FFCC00")
@click.option("--colour_divergent", default = "#0000FF")
@click.argument("output_file_name", nargs=1, type=click.Path())
def main(
        p,
        q,
        size,
        input_file_name,
        half_plane,
        mobius,
        polygon,
        max_iterations,
        zoom,
        translate,
        alternating,
        oversampling,
        output_file_name,
        template,
        truncate_uniform,
        truncate_complete,
        colour_bg,
        colour_primary,
        colour_secundary,
        colour_truncation,
        colour_divergent
        ):
    if input_file_name:
        input_image = Image.open(input_file_name).convert("RGB")
    else:
        input_image = 0
    out = coxeter.main(
        p,
        q,
        size,
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
        (
            colour_bg,
            colour_primary,
            colour_secundary,
            colour_truncation,
            colour_divergent
        )
    )
    out.save(output_file_name)
