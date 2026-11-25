"""glTF 2.0 in and out for the low-poly animal tools. Standard library only.

The measuring tools work on one in-memory model layout (the "viewer" layout, from the project the tools were first written in):
  {'id', 'name', 'tex': [texture names], 'bones': [names], 'parent': [index or None per bone],
   'rest': 7 floats per bone (local rotation x, y, z, w, then local position),
   'inv': 7 floats per bone (the inverse bind transform as rotation and translation),
   'subs': [{'v': base64 of 16 float32 per corner (position 3, normal 3, uv 2, weights 4, bone indices 4),
             'i': base64 of uint16 triangle indices, 'r': [[texture index, first triangle, triangle count]]}],
   'anims': {clip: {'d': seconds, 'k': base64 float32: per bone, rotation key count, position key count, then the rotation
             keys (t, x, y, z, w) and position keys (t, x, y, z), t from 0 to 1}},
   'idle': the default clip}
write_gltf() turns that into a .gltf (JSON) with a .bin and the texture PNG beside it; read_gltf() turns a .gltf or .glb back
into it, so every tool reads glTF without changing its measuring code. Texture UVs follow glTF's convention (0, 0 at the
image's top-left), the same as the layout's.
"""
import base64, json, math, os, struct, tempfile


# ---------------------------------------------------------------- small maths
def q_to_mat(q, p):
    x, y, z, w = q
    m = [1 - 2 * (y * y + z * z), 2 * (x * y + z * w), 2 * (x * z - y * w), 0,
         2 * (x * y - z * w), 1 - 2 * (x * x + z * z), 2 * (y * z + x * w), 0,
         2 * (x * z + y * w), 2 * (y * z - x * w), 1 - 2 * (x * x + y * y), 0,
         p[0], p[1], p[2], 1]
    return m                                               # column-major, as glTF stores it


def mat_to_q(m):
    """column-major 4x4 (rotation and translation only) -> (quaternion x, y, z, w), position"""
    r00, r10, r20 = m[0], m[1], m[2]; r01, r11, r21 = m[4], m[5], m[6]; r02, r12, r22 = m[8], m[9], m[10]
    tr = r00 + r11 + r22
    if tr > 0:
        s = math.sqrt(tr + 1.0) * 2; w = 0.25 * s; x = (r21 - r12) / s; y = (r02 - r20) / s; z = (r10 - r01) / s
    elif r00 > r11 and r00 > r22:
        s = math.sqrt(1.0 + r00 - r11 - r22) * 2; w = (r21 - r12) / s; x = 0.25 * s; y = (r01 + r10) / s; z = (r02 + r20) / s
    elif r11 > r22:
        s = math.sqrt(1.0 + r11 - r00 - r22) * 2; w = (r02 - r20) / s; x = (r01 + r10) / s; y = 0.25 * s; z = (r12 + r21) / s
    else:
        s = math.sqrt(1.0 + r22 - r00 - r11) * 2; w = (r10 - r01) / s; x = (r02 + r20) / s; y = (r12 + r21) / s; z = 0.25 * s
    n = math.sqrt(x * x + y * y + z * z + w * w) or 1.0
    return (x / n, y / n, z / n, w / n), (m[12], m[13], m[14])


# ---------------------------------------------------------------- write
def write_gltf(A, out_path, texture_png=None):
    """Write model A (the layout above) to out_path (.gltf), with <name>.bin and the texture PNG beside it."""
    base = os.path.splitext(out_path)[0]; binname = os.path.basename(base) + '.bin'
    buf = bytearray(); views, accs = [], []

    def add(data, target=None):
        while len(buf) % 4: buf.append(0)
        off = len(buf); buf.extend(data)
        v = {'buffer': 0, 'byteOffset': off, 'byteLength': len(data)}
        if target: v['target'] = target
        views.append(v); return len(views) - 1

    def acc(view, ctype, count, typ, mn=None, mx=None):
        a = {'bufferView': view, 'componentType': ctype, 'count': count, 'type': typ}
        if mn is not None: a['min'] = mn; a['max'] = mx
        accs.append(a); return len(accs) - 1

    nb = len(A['bones'])
    nodes = []
    for i, name in enumerate(A['bones']):
        r = A['rest'][i * 7:i * 7 + 7]
        nodes.append({'name': name, 'rotation': list(r[0:4]), 'translation': list(r[4:7])})
    for i, par in enumerate(A['parent']):
        if par is not None and par >= 0 and par != i: nodes[par].setdefault('children', []).append(i)
    roots = [i for i, par in enumerate(A['parent']) if par is None or par < 0 or par == i]
    ibm = []
    for i in range(nb):
        v = A['inv'][i * 7:i * 7 + 7]; ibm += q_to_mat(tuple(v[0:4]), tuple(v[4:7]))
    ibm_acc = acc(add(struct.pack('<%df' % len(ibm), *ibm)), 5126, nb, 'MAT4')

    prims = []
    for s in A['subs']:
        raw = base64.b64decode(s['v']); n = len(raw) // 64
        C = [struct.unpack_from('<16f', raw, k * 64) for k in range(n)]
        pos = [c[0:3] for c in C]; nrm = [c[3:6] for c in C]; uv = [c[6:8] for c in C]
        w = [c[8:12] for c in C]; j = [tuple(int(round(b)) for b in c[12:16]) for c in C]
        pa = acc(add(struct.pack('<%df' % (3 * n), *[x for p in pos for x in p]), 34962), 5126, n, 'VEC3',
                 [min(p[k] for p in pos) for k in range(3)], [max(p[k] for p in pos) for k in range(3)])
        na = acc(add(struct.pack('<%df' % (3 * n), *[x for p in nrm for x in p]), 34962), 5126, n, 'VEC3')
        ua = acc(add(struct.pack('<%df' % (2 * n), *[x for p in uv for x in p]), 34962), 5126, n, 'VEC2')
        wa = acc(add(struct.pack('<%df' % (4 * n), *[x for p in w for x in p]), 34962), 5126, n, 'VEC4')
        ja = acc(add(struct.pack('<%dH' % (4 * n), *[x for p in j for x in p]), 34962), 5123, n, 'VEC4')
        ix = struct.unpack('<%dH' % (len(base64.b64decode(s['i'])) // 2), base64.b64decode(s['i']))
        for tex_index, first, count in s['r']:
            sub = ix[first * 3:(first + count) * 3]
            ia = acc(add(struct.pack('<%dH' % len(sub), *sub), 34963), 5123, len(sub), 'SCALAR')
            prims.append({'attributes': {'POSITION': pa, 'NORMAL': na, 'TEXCOORD_0': ua, 'WEIGHTS_0': wa, 'JOINTS_0': ja},
                          'indices': ia, 'material': tex_index})
    mesh_node = len(nodes); nodes.append({'name': A.get('name', 'animal'), 'mesh': 0, 'skin': 0})

    anims = []
    for cname, src in A['anims'].items():
        f = struct.unpack('<%df' % (len(base64.b64decode(src['k'])) // 4), base64.b64decode(src['k'])); p = 0
        dur = src['d'] if src['d'] > 0 else 1.0
        chans, samps = [], []
        for b in range(nb):
            nr, npk = int(f[p]), int(f[p + 1]); p += 2
            rot = [f[p + 5 * k:p + 5 * k + 5] for k in range(nr)]; p += 5 * nr
            pos = [f[p + 4 * k:p + 4 * k + 4] for k in range(npk)]; p += 4 * npk
            for keys, path, width in ((rot, 'rotation', 4), (pos, 'translation', 3)):
                if not keys: continue
                times = [k[0] * dur for k in keys]
                ti = acc(add(struct.pack('<%df' % len(times), *times)), 5126, len(times), 'SCALAR', [min(times)], [max(times)])
                vals = [x for k in keys for x in k[1:1 + width]]
                vi = acc(add(struct.pack('<%df' % len(vals), *vals)), 5126, len(keys), 'VEC4' if width == 4 else 'VEC3')
                samps.append({'input': ti, 'output': vi, 'interpolation': 'LINEAR'})
                chans.append({'sampler': len(samps) - 1, 'target': {'node': b, 'path': path}})
        anims.append({'name': cname, 'channels': chans, 'samplers': samps, 'extras': {'duration': src['d']}})

    images, textures, materials = [], [], []
    for k, tname in enumerate(A['tex']):
        materials.append({'name': tname or 'untextured', 'pbrMetallicRoughness': {'metallicFactor': 0.0, 'roughnessFactor': 1.0}})
        if tname and texture_png:
            src_png = texture_png[k] if isinstance(texture_png, (list, tuple)) else texture_png
            if src_png and os.path.exists(src_png):
                img_name = os.path.basename(base) + ('' if k == 0 else '_%d' % k) + '.png'
                open(os.path.join(os.path.dirname(out_path) or '.', img_name), 'wb').write(open(src_png, 'rb').read())
                images.append({'uri': img_name}); textures.append({'source': len(images) - 1, 'sampler': 0})
                materials[-1]['pbrMetallicRoughness']['baseColorTexture'] = {'index': len(textures) - 1}
    doc = {'asset': {'version': '2.0', 'generator': 'lowpoly gltf_io'},
           'scene': 0, 'scenes': [{'nodes': roots + [mesh_node]}], 'nodes': nodes,
           'meshes': [{'name': A.get('name', 'animal'), 'primitives': prims}],
           'skins': [{'joints': list(range(nb)), 'inverseBindMatrices': ibm_acc}],
           'animations': anims, 'materials': materials, 'accessors': accs, 'bufferViews': views,
           'buffers': [{'uri': binname, 'byteLength': len(buf)}],
           'extras': {'lowpoly': {'id': A.get('id'), 'name': A.get('name'), 'tex': A['tex'], 'idle': A.get('idle', '')}}}
    if images: doc['images'] = images; doc['textures'] = textures; doc['samplers'] = [{'magFilter': 9729, 'minFilter': 9729}]
    open(os.path.join(os.path.dirname(out_path) or '.', binname), 'wb').write(bytes(buf))
    open(out_path, 'w', encoding='utf-8').write(json.dumps(doc, indent=1))
    return out_path


# ---------------------------------------------------------------- read
def _load(path):
    """-> (json doc, list of buffer bytes, base dir)"""
    d = os.path.dirname(os.path.abspath(path))
    data = open(path, 'rb').read()
    if data[:4] == b'glTF':                                  # .glb: a JSON chunk, then an optional BIN chunk
        jl, jt = struct.unpack_from('<II', data, 12); doc = json.loads(data[20:20 + jl].decode('utf-8'))
        p = 20 + jl; bins = []
        if p < len(data):
            bl, bt = struct.unpack_from('<II', data, p); bins.append(data[p + 8:p + 8 + bl])
        bufs = []
        for b in doc.get('buffers', []):
            bufs.append(_uri_bytes(b['uri'], d) if 'uri' in b else bins[0])
        return doc, bufs, d
    doc = json.loads(data.decode('utf-8'))
    bufs = [_uri_bytes(b['uri'], d) for b in doc.get('buffers', [])]
    for b, raw in zip(doc.get('buffers', []), bufs):           # a .gltf copied without its own .bin reads another model's data
        if 'byteLength' in b and len(raw) != b['byteLength']:
            raise ValueError('%s: buffer %s is %d bytes but the glTF says %d: the .bin is not the one this file was written with '
                             '(a copied .gltf still pointing at the .bin of another model?)' % (os.path.basename(path), b.get('uri', '')[:60], len(raw), b['byteLength']))
    return doc, bufs, d


def _uri_bytes(uri, d):
    if uri.startswith('data:'): return base64.b64decode(uri.split(',', 1)[1])
    return open(os.path.join(d, uri), 'rb').read()


_FMT = {5126: ('f', 4), 5123: ('H', 2), 5125: ('I', 4), 5121: ('B', 1), 5122: ('h', 2), 5120: ('b', 1)}
_N = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}


def _accessor(doc, bufs, i):
    a = doc['accessors'][i]; v = doc['bufferViews'][a['bufferView']]
    fmt, size = _FMT[a['componentType']]; n = _N[a['type']]
    stride = v.get('byteStride', size * n); off = v.get('byteOffset', 0) + a.get('byteOffset', 0)
    b = bufs[v['buffer']]
    out = [struct.unpack_from('<%d%s' % (n, fmt), b, off + k * stride) for k in range(a['count'])]
    if a.get('normalized') and fmt in ('H', 'B'):
        mx = 65535.0 if fmt == 'H' else 255.0; out = [tuple(x / mx for x in t) for t in out]
    return out


def read_gltf(path):
    """Read a .gltf or .glb with one skinned mesh into the model layout above. Returns (A, texture file path or None)."""
    doc, bufs, d = _load(path)
    skin = doc['skins'][0]; joints = skin['joints']; jix = {n: k for k, n in enumerate(joints)}
    nodes = doc['nodes']
    parent_node = {}
    for i, n in enumerate(nodes):
        for c in n.get('children', []): parent_node[c] = i
    bones = [nodes[n].get('name', 'bone%d' % k) for k, n in enumerate(joints)]
    parent = [jix.get(parent_node.get(n)) for n in joints]
    rest = []
    for n in joints:
        nd = nodes[n]
        if 'matrix' in nd: q, p = mat_to_q(nd['matrix'])
        else: q, p = tuple(nd.get('rotation', (0, 0, 0, 1))), tuple(nd.get('translation', (0, 0, 0)))
        rest += list(q) + list(p)
    if 'inverseBindMatrices' in skin:
        inv = [x for m in _accessor(doc, bufs, skin['inverseBindMatrices']) for x in (lambda qp: list(qp[0]) + list(qp[1]))(mat_to_q(m))]
    else: inv = [0, 0, 0, 1, 0, 0, 0] * len(joints)
    mesh_i = next(n['mesh'] for n in nodes if 'mesh' in n and 'skin' in n)
    subs, attr_cache = [], {}
    corners, tris, ranges = [], [], []
    base_of = {}
    for prim in doc['meshes'][mesh_i]['primitives']:
        at = prim['attributes']; key = tuple(sorted(at.items()))
        if key not in base_of:                               # primitives sharing attribute accessors share corners
            P = _accessor(doc, bufs, at['POSITION']); n = len(P)
            N = _accessor(doc, bufs, at['NORMAL']) if 'NORMAL' in at else [(0, 1, 0)] * n
            UV = _accessor(doc, bufs, at['TEXCOORD_0']) if 'TEXCOORD_0' in at else [(0, 0)] * n
            W = _accessor(doc, bufs, at['WEIGHTS_0']) if 'WEIGHTS_0' in at else [(1, 0, 0, 0)] * n
            J = _accessor(doc, bufs, at['JOINTS_0']) if 'JOINTS_0' in at else [(0, 0, 0, 0)] * n
            base_of[key] = len(corners)
            for k in range(n): corners.append(tuple(P[k]) + tuple(N[k]) + tuple(UV[k]) + tuple(W[k]) + tuple(float(x) for x in J[k]))
        b0 = base_of[key]
        ix = [t[0] for t in _accessor(doc, bufs, prim['indices'])] if 'indices' in prim else list(range(len(corners) - b0))
        first = len(tris)
        for k in range(0, len(ix), 3): tris.append((b0 + ix[k], b0 + ix[k + 1], b0 + ix[k + 2]))
        ranges.append([prim.get('material', 0), first, len(tris) - first])
    flat = [x for c in corners for x in c]
    subs.append({'v': base64.b64encode(struct.pack('<%df' % len(flat), *flat)).decode(),
                 'i': base64.b64encode(struct.pack('<%dH' % (3 * len(tris)), *[i for t in tris for i in t])).decode(), 'r': ranges})
    anims = {}
    for an in doc.get('animations', []):
        per = {b: {'rotation': [], 'translation': []} for b in range(len(joints))}
        dur = 0.0
        for ch in an['channels']:
            node = ch['target']['node']; path = ch['target']['path']
            if node not in jix or path not in ('rotation', 'translation'): continue
            s = an['samplers'][ch['sampler']]
            times = [t[0] for t in _accessor(doc, bufs, s['input'])]; vals = _accessor(doc, bufs, s['output'])
            dur = max(dur, max(times) if times else 0.0)
            per[jix[node]][path] = list(zip(times, vals))
        d_ext = an.get('extras', {}).get('duration')
        D = d_ext if d_ext is not None else dur
        norm = dur if dur > 0 else 1.0
        if d_ext is not None and d_ext > 0: norm = d_ext
        elif d_ext == 0: norm = 1.0
        buf = []
        for b in range(len(joints)):
            r, t = per[b]['rotation'], per[b]['translation']
            buf += [float(len(r)), float(len(t))]
            for tm, q in r: buf += [tm / norm] + list(q)
            for tm, p in t: buf += [tm / norm] + list(p)
        anims[an.get('name', 'clip%d' % len(anims))] = {'d': D, 'k': base64.b64encode(struct.pack('<%df' % len(buf), *buf)).decode()}
    ex = doc.get('extras', {}).get('lowpoly', {})
    A = {'id': ex.get('id') or os.path.splitext(os.path.basename(path))[0], 'name': ex.get('name') or os.path.basename(path),
         'tex': ex.get('tex') or [m.get('name', '') for m in doc.get('materials', [])] or [''],
         'bones': bones, 'parent': parent, 'rest': rest, 'inv': inv, 'subs': subs, 'anims': anims, 'idle': ex.get('idle', '')}
    tex_path = None
    imgs = doc.get('images', [])
    if imgs:
        im = imgs[0]
        if 'uri' in im and not im['uri'].startswith('data:'): tex_path = os.path.join(d, im['uri'])
        else:
            data = _uri_bytes(im['uri'], d) if 'uri' in im else (lambda v: bufs[v['buffer']][v.get('byteOffset', 0):v.get('byteOffset', 0) + v['byteLength']])(doc['bufferViews'][im['bufferView']])
            tex_path = os.path.join(tempfile.gettempdir(), 'lowpoly_%s.png' % os.path.splitext(os.path.basename(path))[0])
            open(tex_path, 'wb').write(data)
    return A, tex_path


def load_viewer(root, aid):
    """the viewer project's animals.js / custom_animals*.js / monsters.js -> (A, texture path)"""
    import glob
    def load(fn):
        s = open(fn, encoding='utf-8').read()
        i = s.index('[', s.index('concat(') if 'concat(' in s else 0); j = s.rindex(']')
        return json.loads(s[i:j + 1])
    files = [os.path.join(root, 'animals.js')] + sorted(glob.glob(os.path.join(root, 'custom_animals*.js'))) + glob.glob(os.path.join(root, 'monsters.js'))
    A = next(a for f in files if os.path.exists(f) for a in load(f) if a['id'] == aid)
    tp = os.path.join(root, 'textures', A['tex'][0] + '.png') if A['tex'] and A['tex'][0] else None
    return A, tp
