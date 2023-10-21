import os

TEST_ROOT = "luxtest"

RENDERERS = [
    "karma",
    "ris",
    "arnold",
]

TESTS = [
    ("distant", 15),
    ("cylinder", 40),
    ("disk", 40),
    ("rect", 40),
    ("sphere", 40),
]

OUTPUT_DIR = "diff"

MAP = "magma"

HTML = \
"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>UsdLux Comparison</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="Comparison of hydra delegates to hdEmbree UsdLux reference">
    <link rel="stylesheet" href="luxtest.css">
  </head>
  <body>
"""

for name, end in TESTS:

    HTML += f"""<h1>{name}</h1>

<table>
  <tr>
    <td>Frame</td>
    <td>Ref</td>
"""
    for renderer in RENDERERS:
        HTML += f"""
    <td>{renderer}</td>
    <td>{renderer} diff</td>
"""

    HTML += """
  </tr>
"""

    for frame in range(1, end):
        HTML += "  <tr>\n"
        HTML += f"    <td>{frame:04}</td>"

        embree_base = os.path.join(TEST_ROOT, "embree", f"{name}-embree.{frame:04}")
        embree_exr = f"{embree_base}.exr"
        embree_png = f"{embree_base}.png"

        HTML += f'    <td><img src="{embree_png}"</td>\n'

        cmd = f"oiiotool {embree_exr} --ch R,G,B --colorconvert linear sRGB -o {embree_png}"
        os.system(cmd)

        for renderer in RENDERERS:
            renderer_base = os.path.join(TEST_ROOT, renderer, f"{name}-{renderer}.{frame:04}")
            renderer_exr = f"{renderer_base}.exr"
            renderer_png = f"{renderer_base}.png"

            cmd = f"oiiotool {renderer_exr} --ch R,G,B --colorconvert linear sRGB -o {renderer_png}"
            os.system(cmd)

            output_path = os.path.join(TEST_ROOT, "diff", f"{name}-{renderer}.{frame:04}.png")


            HTML += f'    <td><img src="{renderer_png}"</td>\n'
            HTML += f'    <td><img src="{output_path}"</td>\n'

            cmd = f"oiiotool {embree_exr} {renderer_exr} --diff --absdiff --mulc 2,2,2,1 --colormap {MAP} --colorconvert linear sRGB -o {output_path}"
            print(cmd)
            os.system(cmd)

        HTML += "  </tr>"

    HTML += "</table>\n"

with open("luxtest.html", "w") as f:
    f.write(HTML)