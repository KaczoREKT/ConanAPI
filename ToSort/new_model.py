import cv2, numpy as np
from pathlib import Path

def resize_nearest_square(img, out=32):
    h,w = img.shape[:2]
    s = max(h,w)
    pad = [(s-h)//2, s-h-(s-h)//2, (s-w)//2, s-w-(s-w)//2]  # top,bottom,left,right
    img_p = cv2.copyMakeBorder(img, pad[0], pad[1], pad[2], pad[3], cv2.BORDER_CONSTANT, value=(0,0,0))
    return cv2.resize(img_p, (out,out), interpolation=cv2.INTER_NEAREST)

def quantize_palette(img, k=16):
    Z = img.reshape(-1,3).astype(np.float32)
    criteria=(cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER,20,0.5)
    ret,labels,centers = cv2.kmeans(Z,k,None,criteria,3,cv2.KMEANS_PP_CENTERS)
    centers = centers.astype(np.uint8)
    q = centers[labels.flatten()].reshape(img.shape)dupa
    idx = labels.reshape(img.shape[:2])
    return q, idx, centers

def edge_dirs(gray):
    gx = cv2.Sobel(gray, cv2.CV_16S,1,0,ksize=3)
    gy = cv2.Sobel(gray, cv2.CV_16S,0,1,ksize=3)
    mag = cv2.convertScaleAbs(np.hypot(gx,gy))
    ang = (np.rad2deg(np.arctan2(gy.astype(np.float32), gx.astype(np.float32))) + 180.0) % 180.0
    # 4 kierunki: 0,45,90,135
    bins = np.floor(ang/45.0).astype(np.int32) % 4
    return mag, bins

def grid_hist(idx_img, mag, dir_bins, grid=8, colors=16, edge_bins=4):
    H,W = idx_img.shape
    gh, gw = H//grid, W//grid
    feats=[]
    for gy in range(grid):
        for gx in range(grid):
            y0,y1 = gy*gh, (gy+1)*gh
            x0,x1 = gx*gw, (gx+1)*gw
            cell_idx = idx_img[y0:y1, x0:x1]
            cell_mag = mag[y0:y1, x0:x1]
            cell_dir = dir_bins[y0:y1, x0:x1]
            # histogram kolorów ważony jednorodnie
            hcol,_ = np.histogram(cell_idx, bins=colors, range=(0,colors), density=False)
            # histogram krawędzi ważony magnitudą
            hedg = np.zeros(edge_bins, np.float32)
            for b in range(edge_bins):
                hedg[b] = cell_mag[cell_dir==b].sum()
            feats.append(hcol.astype(np.float32))
            feats.append(hedg)
    return np.concatenate(feats, axis=0)  # 8*8*(16+4)=1280

def radial_shape_mask(mask, rays=16):
    # centroid
    ys,xs = np.where(mask>0)
    if len(xs)==0:
        return np.zeros(rays, np.float32)
    cx,cy = xs.mean(), ys.mean()
    h,w = mask.shape
    rmax = np.hypot(max(cx, w-1-cx), max(cy, h-1-cy))
    prof=[]
    for i in range(rays):
        theta = 2*np.pi*i/rays
        dx,dy = np.cos(theta), np.sin(theta)
        # próbkowanie wzdłuż promienia
        t=0.0; step=0.5; last=0.0
        while t<rmax:
            x = int(round(cx + dx*t))
            y = int(round(cy + dy*t))
            if x<0 or x>=w or y<0 or y>=h: break
            if mask[y,x]==0 and last>0:
                break
            last = mask[y,x]
            t += step
        prof.append(t/rmax)
    return np.array(prof, np.float32)  # 0..1

def object_mask(idx_img):
    # największa składowa ≠ tło: tło przyjmij kolor większościowy
    h,w = idx_img.shape
    vals, counts = np.unique(idx_img, return_counts=True)
    bg = int(vals[np.argmax(counts)])
    fg = (idx_img!=bg).astype(np.uint8)*255
    # oczyszczenie
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((3,3), np.uint8))
    num, lab, stats, _ = cv2.connectedComponentsWithStats(fg, connectivity=8)
    if num<=1:
        return fg
    largest = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
    return (lab==largest).astype(np.uint8)*255

def pixel_art_descriptor(img_bgr):
    # 1) normalizacja skali
    im = resize_nearest_square(img_bgr, 32)
    # 2) kwantyzacja
    q, idx, pal = quantize_palette(im, k=16)
    # 3) krawędzie
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    mag, db = edge_dirs(gray)
    # 4) histogramy siatki
    feat_grid = grid_hist(idx, mag, db, grid=8, colors=16, edge_bins=4)  # 1280
    # 5) maska i kształt radialny
    m = object_mask(idx)
    feat_shape = radial_shape_mask(m, rays=16)  # 16
    # 6) wektor końcowy
    feat = np.concatenate([feat_grid, feat_shape], axis=0)  # 1296
    # normalizacja
    feat = feat.astype(np.float32)
    if np.linalg.norm(feat)>0:
        feat /= (np.linalg.norm(feat)+1e-6)
    return feat, im, q, m

# --- przykład użycia ---
img = cv2.imread("zelda_items_images/Zelda.png")  # podaj ścieżkę
desc, im32, qimg, mask = pixel_art_descriptor(img)
print("Descriptor dim:", desc.shape)

# wizualizacja
vis = im32.copy()
contours,_ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(vis, contours, -1, (0,255,0), 1)
cv2.imshow("orig32", im32)
cv2.imshow("quantized", qimg)
cv2.imshow("mask", mask)
cv2.imshow("contour", vis)
cv2.waitKey(0)
cv2.destroyAllWindows()
