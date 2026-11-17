"""Convert PNG slides to JPEG (Instagram API accepts JPEG only). Usage: python to_jpg.py <in_dir> <out_dir>"""
import sys, pathlib
from PIL import Image
src, dst = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]); dst.mkdir(parents=True, exist_ok=True)
for p in sorted(src.glob("*.png")):
    Image.open(p).convert("RGB").save(dst / (p.stem + ".jpg"), quality=92, optimize=True)
    print(dst / (p.stem + ".jpg"))
