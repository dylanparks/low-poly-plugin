"""Building blocks for clips that read as alive (lowpoly-core/references/motion-principles.md): quaternions, a two-bone
limb solved in three dimensions (so a pelvis can turn, tilt and shift over feet that stay planted, pivot or step), and
timing curves: an ease, an overshoot that settles, a damped wobble, a phase with holds, and a lag for running a chain of
bones one after another. Standard library only; quaternions are (x, y, z, w), and a rig's rest rotations are taken as
identity (a bone's key is its turn from the bind pose, in its parent's frame).

    python -m lowpoly.animate        runs the self-test
"""
import math

# ---------------------------------------------------------------- vectors and quaternions


def add(a, b): return tuple(x + y for x, y in zip(a, b))
def sub(a, b): return tuple(x - y for x, y in zip(a, b))
def mul(a, s): return tuple(x * s for x in a)
def dot(a, b): return sum(x * y for x, y in zip(a, b))
def cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def norm(a):
    l = math.sqrt(dot(a, a)) or 1.0
    return tuple(x / l for x in a)


IDENT = (0.0, 0.0, 0.0, 1.0)


def qaxis(axis, angle):
    ax = norm(axis); s = math.sin(angle / 2)
    return (ax[0] * s, ax[1] * s, ax[2] * s, math.cos(angle / 2))


def qx(a): return (math.sin(a / 2), 0.0, 0.0, math.cos(a / 2))
def qy(a): return (0.0, math.sin(a / 2), 0.0, math.cos(a / 2))
def qz(a): return (0.0, 0.0, math.sin(a / 2), math.cos(a / 2))


def qmul(a, b):
    ax, ay, az, aw = a; bx, by, bz, bw = b
    return (aw * bx + ax * bw + ay * bz - az * by, aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw, aw * bw - ax * bx - ay * by - az * bz)


def qconj(q): return (-q[0], -q[1], -q[2], q[3])
def qrot(q, v): return qmul(qmul(q, (v[0], v[1], v[2], 0.0)), qconj(q))[:3]


def slerp(a, b, t):
    d = dot(a, b)
    if d < 0: b = tuple(-x for x in b); d = -d
    if d > 0.9995: q = tuple(x + (y - x) * t for x, y in zip(a, b))
    else:
        th = math.acos(d); s0 = math.sin((1 - t) * th) / math.sin(th); s1 = math.sin(t * th) / math.sin(th)
        q = tuple(s0 * x + s1 * y for x, y in zip(a, b))
    l = math.sqrt(dot(q, q)) or 1.0
    return tuple(x / l for x in q)


def qscale(q, k):
    """a rotation taken k times as far (k may pass 1: an overshoot)"""
    if q[3] < 0: q = tuple(-x for x in q)
    s = math.sqrt(max(0.0, 1 - q[3] * q[3]))
    if s < 1e-9: return IDENT
    ang = 2 * math.atan2(s, q[3]) * k
    return qaxis((q[0] / s, q[1] / s, q[2] / s), ang)


def q_from_frames(x0, y0, x1, y1):
    """the rotation that takes the frame (x0, y0, x0 x y0) onto (x1, y1, x1 x y1); each pair unit and at right angles"""
    z0, z1 = cross(x0, y0), cross(x1, y1)
    m = [[x1[i] * x0[j] + y1[i] * y0[j] + z1[i] * z0[j] for j in range(3)] for i in range(3)]
    tr = m[0][0] + m[1][1] + m[2][2]
    if tr > 0:
        s = math.sqrt(tr + 1.0) * 2; q = ((m[2][1] - m[1][2]) / s, (m[0][2] - m[2][0]) / s, (m[1][0] - m[0][1]) / s, 0.25 * s)
    elif m[0][0] > m[1][1] and m[0][0] > m[2][2]:
        s = math.sqrt(1.0 + m[0][0] - m[1][1] - m[2][2]) * 2
        q = (0.25 * s, (m[0][1] + m[1][0]) / s, (m[0][2] + m[2][0]) / s, (m[2][1] - m[1][2]) / s)
    elif m[1][1] > m[2][2]:
        s = math.sqrt(1.0 + m[1][1] - m[0][0] - m[2][2]) * 2
        q = ((m[0][1] + m[1][0]) / s, 0.25 * s, (m[1][2] + m[2][1]) / s, (m[0][2] - m[2][0]) / s)
    else:
        s = math.sqrt(1.0 + m[2][2] - m[0][0] - m[1][1]) * 2
        q = ((m[0][2] + m[2][0]) / s, (m[1][2] + m[2][1]) / s, 0.25 * s, (m[1][0] - m[0][1]) / s)
    l = math.sqrt(dot(q, q)) or 1.0
    return tuple(c / l for c in q)


# ---------------------------------------------------------------- a two-bone limb in three dimensions


def two_bone(root, target, la, lb, pole):
    """the middle joint of a two-bone chain from root to target (clamped to what the bones reach), bent toward pole (a
    direction: forward for a knee, backward for an elbow). Returns (middle joint, the end actually reached, how far of the
    chain's full length the reach is: 1 is a locked-straight limb)"""
    v = sub(target, root); d = math.sqrt(dot(v, v)) or 1e-9
    dc = max(abs(la - lb) + 1e-5, min(la + lb - 1e-5, d)); e = mul(v, 1.0 / d)
    p = sub(pole, mul(e, dot(pole, e)))
    if dot(p, p) < 1e-12:                                     # the pole lies along the limb: any side will do
        p = cross(e, (1.0, 0.0, 0.0)) if abs(e[0]) < 0.9 else cross(e, (0.0, 0.0, 1.0))
    p = norm(p)
    al = math.acos(max(-1.0, min(1.0, (la * la + dc * dc - lb * lb) / (2 * la * dc))))
    mid = add(root, add(mul(e, la * math.cos(al)), mul(p, la * math.sin(al))))
    return mid, add(root, mul(e, dc)), dc / (la + lb)


def limb_rotations(parent_q, root, j_root, j_mid, j_end, target, pole, end_q=None):
    """the local rotations of a two-bone limb whose bind joints are j_root, j_mid, j_end, with its root joint now at
    `root` under a parent turned by parent_q, reaching for `target` and bent toward `pole`. end_q, if given, is the world
    turn wanted for the bone at the end (a foot kept flat, a hand kept level); its local rotation is returned third.
    Returns (upper, lower, end or None, reach)."""
    a0, b0 = sub(j_mid, j_root), sub(j_end, j_mid)
    la, lb = math.sqrt(dot(a0, a0)), math.sqrt(dot(b0, b0))
    mid, end, reach = two_bone(root, target, la, lb, pole)
    h0 = cross(a0, b0)
    if dot(h0, h0) < 1e-12:                                   # a limb bound dead straight: its hinge from the pole
        h0 = cross(pole, a0)
    h0 = norm(h0)
    a1, b1 = sub(mid, root), sub(end, mid)
    h1 = cross(a1, b1)
    if dot(h1, h1) < 1e-10: h1 = cross(pole, a1)
    h1 = norm(h1)
    if dot(cross(pole, a1), h1) < 0 and dot(cross(pole, a0), h0) > 0: h1 = mul(h1, -1.0)
    qu = q_from_frames(h0, norm(a0), h1, norm(a1)); ql = q_from_frames(h0, norm(b0), h1, norm(b1))
    upper = qmul(qconj(parent_q), qu); lower = qmul(qconj(qu), ql)
    return upper, lower, (qmul(qconj(ql), end_q) if end_q is not None else None), reach


# ---------------------------------------------------------------- timing


def smooth(e0, e1, x):
    """a smooth step from 0 at e0 to 1 at e1 (e0 > e1 runs it backwards)"""
    if e0 == e1: return 0.0 if x < e0 else 1.0
    t = max(0.0, min(1.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def ease_in(t): t = max(0.0, min(1.0, t)); return t * t * t                      # slow out of the hold, fast at the end
def ease_out(t): t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3              # fast at once, slow into the pose


def overshoot(t, amount=0.12, swings=1.5):
    """0 to 1 as an eased move that runs past 1 by about `amount` and settles back: a fast arrival with its momentum
    carried through. t in 0..1; the first 45% is the move, the rest the settle"""
    t = max(0.0, min(1.0, t))
    if t < 0.45: return ease_out(t / 0.45) * (1 + 0.0)
    u = (t - 0.45) / 0.55
    return 1 + amount * math.sin(u * math.pi * 2 * swings) * (1 - u) ** 2 * (1 if swings else 0)


def wobble(t, t0, freq, decay, amp=1.0):
    """a damped swing that starts at t0: what a mass does after it is stopped (a settle). Seconds, hertz, 1/seconds"""
    if t < t0: return 0.0
    u = t - t0
    return amp * math.exp(-decay * u) * math.sin(2 * math.pi * freq * u)


def bump(t, t0, t1, t2):
    """0 before t0, up to 1 at t1, back to 0 at t2 (each side eased)"""
    return smooth(t0, t1, t) * (1 - smooth(t1, t2, t))


def lagged(fn, t, delay, period=None):
    """a curve run `delay` later: the same motion on the next bone out along a chain. With a period, the curve loops"""
    u = t - delay
    return fn(u % period if period else u)


def chain(fn, t, delays, period=None):
    """one curve sampled for each bone of a chain, each a little later than the last (delays in the curve's own units)"""
    return [lagged(fn, t, d, period) for d in delays]


if __name__ == '__main__':
    # the limb reaches its target, bends toward its pole, and the rotations rebuild the joints
    jr, jm, je = (0.09, 0.915, 0.0), (0.10, 0.485, 0.012), (0.108, 0.085, -0.012)
    worst = 0.0
    for k in range(200):
        a = k * 0.37
        pq = qmul(qy(0.5 * math.sin(a)), qmul(qz(0.2 * math.cos(a * 1.3)), qx(0.2 * math.sin(a * 0.7))))
        root = add(jr, (0.05 * math.sin(a), 0.04 * math.cos(a * 2) - 0.05, 0.06 * math.sin(a * 1.7)))
        tgt = add(je, (0.10 * math.sin(a * 1.1), 0.25 * (0.5 + 0.5 * math.sin(a * 0.9)), 0.35 * math.cos(a * 0.6)))
        pole = qrot(qy(0.5 * math.sin(a)), (0.0, 0.0, 1.0))
        up, lo, _, reach = limb_rotations(pq, root, jr, jm, je, tgt, pole)
        wq_u = qmul(pq, up); wq_l = qmul(wq_u, lo)
        mid = add(root, qrot(wq_u, sub(jm, jr))); end = add(mid, qrot(wq_l, sub(je, jm)))
        wmid, want, _ = two_bone(root, tgt, math.dist(jr, jm), math.dist(jm, je), pole)
        worst = max(worst, math.dist(end, want), math.dist(mid, wmid))
        e = norm(sub(want, root)); side = sub(pole, mul(e, dot(pole, e)))
        assert dot(sub(mid, root), side) > -1e-9, 'the knee bent away from its pole'
    assert worst < 1e-6, worst
    assert abs(overshoot(1.0) - 1) < 1e-9 and max(overshoot(k / 100) for k in range(101)) > 1.05
    assert abs(smooth(0, 1, 0.5) - 0.5) < 1e-12 and bump(0.5, 0, 0.5, 1) == 1.0
    print('selftest ok: the limb reaches its target and its middle joint within %.1e m over 200 poses' % worst)
