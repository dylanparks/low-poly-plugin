"""Where a model's head, limbs and feet are, read from its rig instead of guessed from its height.

The first measuring tools found the head as "the front 16-25% of the length, above 40-45% of the height" and a foot as "the
mesh below 12% of the height". That holds for a standing mammal and fails on everything else: a crocodile's head is low (so
the head close-ups came out blank), a scorpion's highest point is its tail (so the eye tool found no head and divided by
zero), and the foot zone took in a sprawling knee, a tail lying on the ground and a bird's feather cuff. Three builders in the
agent trial bent their models to suit those rules. This module reads the same parts from the bones:

  limbs  A limb's top bone is one whose chain reaches the ground on one side only, while its parent's chain reaches both
         sides (the hips over two hind legs, the chest over two forelegs, a scorpion's body over eight legs). A chain reaches
         the ground where the skin its bones carry touches it (not where a joint is: a sprawling ankle stands high).
  feet   In each limb, the ankle is the lowest joint of the chain that stands clear of the ground (above 8% of the height):
         toe and paw joints lying on the ground are part of the foot below it. The foot is the ankle bone and everything
         below it, so a knee, however low, belongs to the leg.
  head   A bone named head or skull (outside the limbs) when the rig has one: names are the builder's own statement.
         Otherwise the bone on the midline, carrying skin, whose vertices lie furthest forward among the bones that are not
         part of a limb, then up to its parent while the parent carries more skin than the whole branch below it (a jaw or a
         snout bone sits under the head bone). Its region is that bone with its descendants (jaw, ears, eyelids), unless one of the
         descendants is a limb: then the head bone alone (a scorpion's carapace bone also carries its legs and tail).

A vertex belongs to a part when that part's bones carry at least half of its weight (a ring blended 50/50 at a joint
belongs to both sides of it); the limb and head search itself uses the bone that weights each vertex most. Every function says which rule it used, so a tool can print
it, and parts() returns None for a part the rig doesn't show (no rig, or no grounded chain): the tool then falls back to its
height rule and says so. Standard library only."""
import math, re


def _ancestors(i, parent):
    out = []
    while parent(i) is not None: i = parent(i); out.append(i)
    return out


def _qmul(a, b):
    ax, ay, az, aw = a; bx, by, bz, bw = b
    return (aw * bx + ax * bw + ay * bz - az * by, aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw, aw * bw - ax * bx - ay * by - az * bz)


def _qrot(q, v):
    x, y, z, w = q; vx, vy, vz = v
    tx, ty, tz = 2 * (y * vz - z * vy), 2 * (z * vx - x * vz), 2 * (x * vy - y * vx)
    return (vx + w * tx + y * tz - z * ty, vy + w * ty + z * tx - x * tz, vz + w * tz + x * ty - y * tx)


def joints(A):
    """each bone's joint in the bind pose (its world position)"""
    nb = len(A['bones']); par = A['parent']; W = [None] * nb
    for i in range(nb):
        q, p = tuple(A['rest'][i * 7:i * 7 + 4]), tuple(A['rest'][i * 7 + 4:i * 7 + 7]); pi = par[i]
        if pi is None or pi < 0 or pi == i or W[pi] is None: W[i] = (q, p)
        else:
            pq, pp = W[pi]; W[i] = (_qmul(pq, q), tuple(a + b for a, b in zip(pp, _qrot(pq, p))))
    return [w[1] for w in W]


def parts(A, V):
    """A: the model (bones, parent, rest); V: its corners as (position, [(bone, weight), ...]).
    Returns {'height', 'ymin', 'owner' (the dominant bone of each corner), 'limbs': [{'root', 'side', 'ankle', 'bones',
    'foot_bones'}], 'head': {'bone', 'bones', 'rule'} or None}. 'limbs' is empty when the rig shows none."""
    names, par = A['bones'], A['parent']; nb = len(names)
    P = [v[0] for v in V]; ys = [p[1] for p in P]; ymin, H = min(ys), (max(ys) - min(ys)) or 1.0
    xs = [p[0] for p in P]; Wd = (max(xs) - min(xs)) or 1.0
    J = joints(A) if nb else []
    def parent(i): p = par[i]; return p if p is not None and p >= 0 and p != i else None
    kids = {i: [k for k in range(nb) if parent(k) == i] for i in range(nb)}
    owner = [max(ws, key=lambda x: x[1])[0] if ws else None for _, ws in V]

    def sub(i):
        out = [i]
        for k in kids[i]: out += sub(k)
        return out

    # the sides (+1 / -1) on which each bone's own skin is near the ground (within 10% of the height of the lowest point: a
    # paw lifted in the bind pose still counts);
    # skin on the midline counts as neither. Read from the vertices, not the joints: a sprawling foot's ankle joint can sit
    # well above the ground while its sole lies on it
    touch = {}
    for c, b in enumerate(owner):
        if b is not None and P[c][1] < ymin + 0.10 * H and abs(P[c][0]) > 0.01 * H:
            touch.setdefault(b, set()).add(1 if P[c][0] > 0 else -1)

    def grounded(i):
        s = set(touch.get(i, ()))
        for k in kids[i]: s |= grounded(k)
        return s
    G = [grounded(i) for i in range(nb)]
    roots = [i for i in range(nb) if len(G[i]) == 1 and kids[i] and parent(i) is not None and len(G[parent(i)]) == 2]
    limbs = []
    for r in roots:
        # walk down the chain toward the ground (the child whose subtree reaches lowest); the ankle is the last joint clear
        # of the ground, and joints on the ground (paws, toes) belong to the foot under it
        chain, i = [r], r
        while kids[i]:
            i = min(kids[i], key=lambda k: min(J[b][1] for b in sub(k))); chain.append(i)
        clear = [b for b in chain if J[b][1] > ymin + 0.08 * H]
        ankle = clear[-1] if clear else chain[-1]
        if ankle == r and len(chain) > 1: ankle = chain[1]       # a limb of one bone below its root: the foot is all of it
        k = chain.index(ankle)                                    # a foot whose bones carry no skin: the joint above
        while k > 1 and not any(b in set(sub(chain[k])) for b in owner): k -= 1
        ankle = chain[k]
        limbs.append({'root': r, 'side': 1 if J[r][0] > 0 else -1, 'ankle': ankle, 'bones': set(sub(r)),
                      'foot_bones': set(sub(ankle))})
    limb_bones = set().union(*(l['bones'] for l in limbs)) if limbs else set()
    # the head: a midline bone outside the limbs that carries skin, the furthest forward by its vertices' mean
    cen = {}
    for c, b in enumerate(owner):
        if b is None: continue
        s = cen.setdefault(b, [0.0, 0.0, 0.0, 0]); s[0] += P[c][0]; s[1] += P[c][2]; s[3] += 1
    cand = [b for b, s in cen.items() if b not in limb_bones and s[3] >= 3 and abs(s[0] / s[3]) < 0.08 * Wd]
    own = lambda b: cen[b][3] if b in cen else 0
    named = [b for b in range(nb) if b not in limb_bones and sum(own(k) for k in sub(b)) >= 3 and re.search(r'(^|[^a-z])(head|skull)([^a-z]|$)', names[b].lower())]
    head, how = None, ''
    if named:                    # a bone named head or skull whose branch carries skin: the highest such in the hierarchy
        hb = min(named, key=lambda b: len(_ancestors(b, parent))); how = 'named'
    elif cand:                   # the frontmost midline bone, then up to the bone that carries the head's skin (a jaw, a
        hb = max(cand, key=lambda b: cen[b][1] / cen[b][3]); how = 'frontmost'      # snout, a nose bone sit under it)
        while parent(hb) is not None and parent(hb) not in limb_bones and own(parent(hb)) > sum(own(b) for b in sub(hb)):
            hb = parent(hb)
    if how:
        region = set(sub(hb))
        if region & limb_bones or any(len(G[k]) for k in region):
            head = {'bone': hb, 'bones': {hb}, 'rule': '%s bone %s alone (its children include limbs)' % (how, names[hb])}
        else:
            head = {'bone': hb, 'bones': region, 'rule': '%s bone %s and its %d descendants' % (how, names[hb], len(region) - 1)}
    return {'height': H, 'ymin': ymin, 'owner': owner, 'weights': [ws for _, ws in V], 'limbs': limbs, 'head': head,
            'names': names}


def _share(R, c, bones):
    return sum(w for b, w in R['weights'][c] if b in bones)


def head_triangles(R, T):
    """the triangles whose three corners all belong to the head: its bones carry at least half of each corner's weight (a
    neck ring blended 50/50 counts; None when the rig shows no head)"""
    if not R['head']: return None
    hb = R['head']['bones']; inh = [_share(R, c, hb) >= 0.5 - 1e-6 for c in range(len(R['weights']))]
    return [t for t in T if all(inh[i] for i in t)]


def foot_corners(R):
    """for each limb, the corners its foot bones carry at least half the weight of (an ankle ring blended 50/50 with the
    shin is the foot's; None when the rig shows no limbs)"""
    if not R['limbs']: return None
    return [{c for c in range(len(R['weights'])) if _share(R, c, l['foot_bones']) >= 0.5 - 1e-6} for l in R['limbs']]
