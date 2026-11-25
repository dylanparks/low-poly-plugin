"""Lay an animal's bind-pose side view over a reference image (a skeleton drawing, an anatomy plate, a photo), to see where the model
and the reference disagree: the joints, the depth of each part, the head and tail carriage. Standard library only; only reads the
viewer's files and the reference image (an 8-bit PNG).
Usage: python -I ref_overlay.py <model.gltf> - <reference.png> <out.png> <pixels per metre> <nose x px> <ground y px>
                                [view=side|top|front] [midline px]
  View "side" (the default) draws the side projection. "top" draws the view from above: the ground y is then ignored, and the
  midline px is the image row of the animal's midline (the spine). "front" draws the view from the front: the nose x is then
  ignored, and the midline px is the image column of the midline. A front drawing is drawn in perspective, with the head nearer
  the viewer than the hips, so use it for ratios within one plane (the stance, the foot width), not for one scale of everything.
  The animal faces left in the side and top references, like the model's nose at the left. Read the pixels per metre off the reference's total
  length (pixels from nose to tail tip divided by the model's length), the nose x off its nose tip, and the ground y off its
  planted foot. Use the same total length as the model, so that proportions, not scale, show up.
  With a mid-stride reference, trust the torso, the skull, the shoulder, the pelvis, the tail and the bone lengths; the limb angles
  differ because the pose does."""
import sys as _sys  # _usage_guard: too few arguments, or -h / --help, prints the usage above
if __name__ == '__main__' and (len(_sys.argv) < 8 or _sys.argv[1] in ('-h', '--help')):
    print(__doc__); _sys.exit(0 if _sys.argv[1:2] in (['-h'], ['--help']) else 2)
import contextlib, io, os, struct, sys, zlib

D, AID, REF, OUT = sys.argv[1:5]
SC, NX, GY = float(sys.argv[5]), float(sys.argv[6]), float(sys.argv[7])
VIEW = sys.argv[8] if len(sys.argv) > 8 else 'side'; MID = float(sys.argv[9]) if len(sys.argv) > 9 else 0.0
here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, 'foot_detail.py')).read(); exec(src[src.index('def read_png'):src.index('here = os.path')])
code = open(os.path.join(here, 'rig_study.py')).read().split("# ---- 1.")[0].split("print('== %s")[0]
g = {}; sys.argv = ['x', D, AID]
with contextlib.redirect_stdout(io.StringIO()): exec(code, g)
V, T = g['V'], g['T']; P = [v[0] for v in V]
w, h, img = read_png(REF)
img = [[tuple(px[:3]) for px in row] for row in img]
zmax = max(p[2] for p in P)
if VIEW == 'top': pt = lambda p: (NX + (zmax - p[2]) * SC, MID - p[0] * SC)
elif VIEW == 'front': pt = lambda p: (MID + p[0] * SC, GY - p[1] * SC)
else: pt = lambda p: (NX + (zmax - p[2]) * SC, GY - p[1] * SC)


def blend(x, y, c, a):
    if 0 <= x < w and 0 <= y < h:
        o = img[y][x]; img[y][x] = tuple(int(o[k] * (1 - a) + c[k] * a) for k in range(3))


for t in T:                                                    # fill every triangle a little, so the silhouette shows
    q = [pt(P[i]) for i in t]
    for y in range(int(min(p[1] for p in q)), int(max(p[1] for p in q)) + 1):
        xs = []
        for i in range(3):
            a, b = q[i], q[(i + 1) % 3]
            if (a[1] <= y + 0.5 < b[1]) or (b[1] <= y + 0.5 < a[1]): xs.append(a[0] + (y + 0.5 - a[1]) / (b[1] - a[1]) * (b[0] - a[0]))
        if len(xs) >= 2:
            for x in range(int(min(xs)), int(max(xs)) + 1): blend(x, y, (255, 40, 40), 0.22)
for t in T:                                                    # and draw the wireframe
    q = [pt(P[i]) for i in t]
    for i in range(3):
        a, b = q[i], q[(i + 1) % 3]; n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1]))) + 1
        for k in range(n + 1): blend(int(a[0] + (b[0] - a[0]) * k / n), int(a[1] + (b[1] - a[1]) * k / n), (255, 60, 60), 0.45)
if VIEW == 'side' or VIEW == 'front':
    for x in range(w): blend(x, int(GY), (0, 120, 0), 1.0)     # the ground
if VIEW == 'top':
    for x in range(w): blend(x, int(MID), (0, 120, 0), 1.0)    # the midline
else:
    if VIEW == 'front':
        for y in range(h): blend(int(MID), y, (0, 120, 0), 1.0)
raw = b''.join(b'\x00' + bytes(v for px in row for v in px) for row in img)
def chunk(t, d): return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
open(OUT, 'wb').write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))
print('%s over %s -> %s' % (AID, os.path.basename(REF), OUT))
