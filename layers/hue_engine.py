"""Lil Omnis hue-shift engine (corrected Oct 23).
Sector table verified against colorsys for all 6 realm hues.
NEVER hand-roll the G vector again - it cost us a green Solana once."""
import numpy as np

def hsv_sector_rgb(h, s, v):
    """Vectorized HSV->RGB. h,s,v arrays of same shape, h in [0,1]."""
    i = (np.floor(h*6).astype(int)) % 6
    f = h*6 - np.floor(h*6)
    p = v*(1-s)
    q = v*(1-f*s)
    t = v*(1-(1-f)*s)
    R = np.select([i==0,i==1,i==2,i==3,i==4,i==5],[v,q,p,p,t,v])
    G = np.select([i==0,i==1,i==2,i==3,i==4,i==5],[t,v,v,q,p,p])
    B = np.select([i==0,i==1,i==2,i==3,i==4,i==5],[p,p,t,v,v,q])
    return R,G,B

def recolor_mask(img_rgb_float, mask, hue, sat_mix=0.55, val_mix=0.55, sat=None, val=None):
    """Recolor pixels in mask to target hue, preserving shading.
    sat/val default to blending original shading with realm palette."""
    a = img_rgb_float
    ys, xs = np.where(mask)
    r, g, b = a[ys,xs,0], a[ys,xs,1], a[ys,xs,2]
    mx = np.maximum(np.maximum(r,g),b); mn = np.minimum(np.minimum(r,g),b)
    vv = mx/255.0; ss = np.where(mx>0,(mx-mn)/np.maximum(mx,1),0)
    hsv_h = np.full(len(ys), hue/360.0)
    hsv_s = np.clip(ss*sat_mix + (sat if sat is not None else 0.7)*(1-sat_mix), 0, 1)
    hsv_v = np.clip(vv*val_mix + (val if val is not None else 0.8)*(1-val_mix), 0, 1)
    R,G,B = hsv_sector_rgb(hsv_h, hsv_s, hsv_v)
    out = a.copy()
    out[ys,xs,0] = R*255; out[ys,xs,1] = G*255; out[ys,xs,2] = B*255
    return out

REALM_HUES = {"ethereum":214.5,"base":192.8,"robinhood":145.0,"bnb":28.4,"solana":272.2,"sui":182.0}
