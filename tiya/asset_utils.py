"""Runtime asset generation — photo-realistic fruit sprites."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict

import cv2
import numpy as np

from .config import ASSET_DIR

ASSET_VERSION = "7"   # bump forces full regeneration


class AssetManager:
    def __init__(self, asset_dir: Path = ASSET_DIR) -> None:
        self.asset_dir = Path(asset_dir)
        self.asset_dir.mkdir(parents=True, exist_ok=True)
        self.version_file = self.asset_dir / ".asset_version"
        self._cache: Dict[str, np.ndarray] = {}
        self._bootstrap_assets()
        self._preload_all()

    def get(self, name: str) -> np.ndarray:
        return self._cache[name]

    def _preload_all(self) -> None:
        names = list(self._generators().keys())
        def _load(name):
            img = cv2.imread(str(self.asset_dir / name), cv2.IMREAD_UNCHANGED)
            return name, img
        with ThreadPoolExecutor(max_workers=8) as ex:
            for name, img in ex.map(_load, names):
                if img is not None:
                    self._cache[name] = img

    def _bootstrap_assets(self) -> None:
        force = self._read_version() != ASSET_VERSION
        self._ensure_core_assets(force=force)
        if force:
            self.version_file.write_text(ASSET_VERSION)

    def _read_version(self) -> str:
        try:
            return self.version_file.read_text().strip()
        except FileNotFoundError:
            return ""

    def _generators(self) -> dict:
        return {
            "watermelon.png":  self._draw_watermelon,
            "banana.png":      self._draw_banana,
            "orange.png":      self._draw_orange,
            "apple.png":       self._draw_apple,
            "pineapple.png":   self._draw_pineapple,
            "grapes.png":      self._draw_grapes,
            "strawberry.png":  self._draw_strawberry,
            "peach.png":       self._draw_peach,
            "cherries.png":    self._draw_cherries,
            "mango.png":       self._draw_mango,
            "kiwi.png":        self._draw_kiwi,
            "pear.png":        self._draw_pear,
            "lemon.png":       self._draw_lemon,
            "melon.png":       self._draw_melon,
            "blueberries.png": self._draw_blueberries,
            "bomb.png":        self._draw_bomb,
            "splash.png":      self._draw_splash,
            "life.png":        self._draw_life,
        }

    def _ensure_core_assets(self, *, force: bool = False) -> None:
        def _gen(item):
            filename, drawer = item
            path = self.asset_dir / filename
            if not force and path.exists():
                return
            cv2.imwrite(str(path), drawer(), [cv2.IMWRITE_PNG_COMPRESSION, 0])
        with ThreadPoolExecutor(max_workers=8) as ex:
            list(ex.map(_gen, self._generators().items()))

    # ═══════════════════════════════════════════════════════════════════════
    #  SHARED DRAWING HELPERS
    # ═══════════════════════════════════════════════════════════════════════

    def _canvas(self, size: int = 256) -> np.ndarray:
        return np.zeros((size, size, 4), dtype=np.uint8)

    def _radial(self, canvas, cx, cy, r, inner, outer):
        """Smooth radial gradient fill."""
        for i in range(r, 0, -2):
            t = i / r
            c = tuple(int(outer[k]*t + inner[k]*(1-t)) for k in range(4))
            cv2.circle(canvas, (cx, cy), i, c, -1, cv2.LINE_AA)

    def _soft_shadow(self, canvas, cx, cy, r):
        """Soft drop shadow below fruit."""
        shadow = self._canvas(canvas.shape[0])
        for i in range(r, 0, -3):
            alpha = int(60 * (1 - i/r))
            cv2.ellipse(shadow, (cx, cy + r//3), (i, i//2), 0, 0, 360,
                        (0,0,0,alpha), -1, cv2.LINE_AA)
        mask = shadow[:,:,3] > 0
        canvas[mask] = np.clip(
            canvas[mask].astype(np.float32)*0.6 + shadow[mask].astype(np.float32)*0.4,
            0, 255).astype(np.uint8)

    def _specular(self, canvas, cx, cy, r, brightness=220):
        """Bright specular highlight (top-left)."""
        hx, hy = cx - r//3, cy - r//3
        for i in range(r//4, 0, -1):
            t = i / (r//4)
            a = int(brightness * (1-t))
            cv2.circle(canvas, (hx, hy), i, (brightness,brightness,brightness,a),
                       -1, cv2.LINE_AA)

    def _rim_light(self, canvas, cx, cy, r, color):
        """Rim lighting on bottom-right edge for 3D depth."""
        rim = self._canvas(canvas.shape[0])
        cv2.circle(rim, (cx + r//5, cy + r//5), r, color, -1, cv2.LINE_AA)
        mask = rim[:,:,3] > 0
        canvas[mask] = np.clip(
            canvas[mask].astype(np.float32)*0.7 + rim[mask].astype(np.float32)*0.3,
            0, 255).astype(np.uint8)

    def _noise_texture(self, canvas, cx, cy, r, rng, color, count=120):
        """Subtle pore/skin texture dots."""
        for _ in range(count):
            ang = rng.uniform(0, 2*np.pi)
            d   = rng.uniform(0, 0.85) * r
            x, y = int(cx + d*np.cos(ang)), int(cy + d*np.sin(ang))
            if 0<=x<canvas.shape[1] and 0<=y<canvas.shape[0]:
                cv2.circle(canvas, (x,y), rng.integers(1,3), color, -1)

    # ═══════════════════════════════════════════════════════════════════════
    #  FRUIT DRAWERS
    # ═══════════════════════════════════════════════════════════════════════

    def _draw_watermelon(self) -> np.ndarray:
        S=320; c=S//2; canvas=self._canvas(S)
        # Dark green outer rind with lighter stripe pattern
        self._radial(canvas,c,c,c-4,(20,110,20,255),(8,55,8,255))
        rng=np.random.default_rng(1)
        # Light green stripes
        for ang in np.linspace(0,np.pi*2,8,endpoint=False):
            pts=np.array([[int(c+r*np.cos(ang)),int(c+r*np.sin(ang))]
                          for r in np.linspace(0,c-4,25)],np.int32)
            cv2.polylines(canvas,[pts],False,(60,180,60,255),10,cv2.LINE_AA)
        # Thin pale stripe on each
        for ang in np.linspace(0,np.pi*2,8,endpoint=False):
            pts=np.array([[int(c+r*np.cos(ang)),int(c+r*np.sin(ang))]
                          for r in np.linspace(0,c-12,20)],np.int32)
            cv2.polylines(canvas,[pts],False,(100,220,80,255),3,cv2.LINE_AA)
        # White rind ring
        cv2.circle(canvas,(c,c),c-26,(245,255,240,255),8,cv2.LINE_AA)
        # Deep red/pink flesh
        self._radial(canvas,c,c,c-34,(80,60,240,255),(40,20,180,255))
        # Realistic black seeds with white hilum
        for ang in np.linspace(0.3,np.pi*2-0.3,10,endpoint=False):
            dist=rng.uniform(0.18,0.58)*(c-40)
            sx,sy=int(c+dist*np.cos(ang)),int(c+dist*np.sin(ang))
            cv2.ellipse(canvas,(sx,sy),(12,7),np.degrees(ang),0,360,(5,5,5,255),-1,cv2.LINE_AA)
            cv2.ellipse(canvas,(sx-2,sy-2),(4,3),np.degrees(ang),0,360,(160,160,140,255),-1,cv2.LINE_AA)
        self._specular(canvas,c,c,c-6)
        return canvas

    def _draw_banana(self) -> np.ndarray:
        S=360; canvas=self._canvas(S)
        # Main curved body — deep golden yellow
        mask=np.zeros((S,S),np.uint8)
        cv2.ellipse(mask,(S//2-8,S//2+55),(165,88),-46,198,342,255,72)
        canvas[mask>0]=[0,210,255,255]
        # Lighter inner face
        inner=np.zeros((S,S),np.uint8)
        cv2.ellipse(inner,(S//2-18,S//2+44),(132,62),-49,208,332,255,28)
        canvas[inner>0]=[20,240,255,255]
        # Dark yellow-green tips
        for ox,oy in [(-105,15),(115,10)]:
            cv2.ellipse(canvas,(S//2+ox,S//2+oy),(28,18),0,0,360,(10,140,20,255),-1,cv2.LINE_AA)
            cv2.ellipse(canvas,(S//2+ox,S//2+oy),(18,10),0,0,360,(5,100,10,255),-1,cv2.LINE_AA)
        # Lengthwise ridges (3 lines)
        ridge=np.zeros((S,S),np.uint8)
        for offset in [-18,0,18]:
            cv2.ellipse(ridge,(S//2-8+offset,S//2+55),(155,78),-46,205,335,255,4)
        canvas[ridge>0,2]=np.clip(canvas[ridge>0,2].astype(int)-25,0,255)
        # Specular shine strip
        shine=np.zeros((S,S),np.uint8)
        cv2.ellipse(shine,(S//2-55,S//2+18),(65,30),-46,212,328,255,16)
        hi=shine>0
        canvas[hi,:3]=np.clip(canvas[hi,:3].astype(np.float32)*0.3+255*0.7,0,255).astype(np.uint8)
        return canvas

    def _draw_orange(self) -> np.ndarray:
        S=280; c=S//2; canvas=self._canvas(S)
        # Deep orange radial
        self._radial(canvas,c,c,c-4,(0,180,255,255),(0,110,200,255))
        # Subtle dimple texture
        rng=np.random.default_rng(7)
        self._noise_texture(canvas,c,c,c-8,rng,(0,140,200,90))
        # Navel circle at bottom
        cv2.circle(canvas,(c,c+c//2-10),14,(0,90,160,255),-1,cv2.LINE_AA)
        cv2.circle(canvas,(c,c+c//2-10), 8,(0,110,180,255),-1,cv2.LINE_AA)
        cv2.circle(canvas,(c,c+c//2-10), 4,(0,80,140,255),-1,cv2.LINE_AA)
        # Green leaf + stem
        cv2.line(canvas,(c,c-c+8),(c,c-c-18),(40,25,5,255),7,cv2.LINE_AA)
        for ang,sz in [(-30,20),( 30,18),(  0,15)]:
            r=np.radians(ang)
            lx=int(c+40*np.sin(r)); ly=int(c-c+5-40*np.cos(r))
            cv2.ellipse(canvas,(lx,ly),(sz+10,sz),-60+ang,0,360,(20,160,35,255),-1,cv2.LINE_AA)
        self._specular(canvas,c,c,c-6)
        self._rim_light(canvas,c,c,c-6,(0,80,160,120))
        return canvas

    def _draw_apple(self) -> np.ndarray:
        S=280; canvas=self._canvas(S); c=(S//2,S//2+14)
        # Rich red gradient
        self._radial(canvas,c[0],c[1],S//2-6,(25,55,230,255),(5,10,160,255))
        # Left lobe shadow
        lobe=self._canvas(S)
        cv2.circle(lobe,(c[0]-22,c[1]),S//2-14,(0,0,0,40),-1,cv2.LINE_AA)
        mask=lobe[:,:,3]>0
        canvas[mask]=np.clip(canvas[mask].astype(np.float32)*0.75,0,255).astype(np.uint8)
        # Top indent
        cv2.ellipse(canvas,(c[0],c[1]-S//2+14),(16,12),0,0,360,(5,8,140,255),-1,cv2.LINE_AA)
        # Yellow blush stripe
        blush=self._canvas(S)
        cv2.ellipse(blush,(c[0]+35,c[1]),(55,S//2-10),0,0,360,(0,180,255,100),-1,cv2.LINE_AA)
        bm=blush[:,:,3]>0
        canvas[bm]=np.clip(canvas[bm].astype(np.float32)*0.65+blush[bm].astype(np.float32)*0.35,0,255).astype(np.uint8)
        # Brown stem
        cv2.line(canvas,(c[0]+2,c[1]-S//2+16),(c[0]+8,c[1]-S//2-24),(35,18,5,255),8,cv2.LINE_AA)
        cv2.ellipse(canvas,(c[0]+38,c[1]-S//2-8),(42,18),-40,0,360,(20,165,45,255),-1,cv2.LINE_AA)
        self._specular(canvas,c[0]-15,c[1]-20,55)
        self._rim_light(canvas,c[0],c[1],S//2-8,(0,30,120,100))
        return canvas

    def _draw_pineapple(self) -> np.ndarray:
        S=340; canvas=self._canvas(S); cx,cy=S//2,S//2+28
        # Golden-brown body
        self._radial(canvas,cx,cy,108,(0,200,240,255),(0,130,185,255))
        cv2.ellipse(canvas,(cx,cy),(100,132),0,0,360,(0,170,220,255),-1,cv2.LINE_AA)
        # Diamond scale pattern — each diamond shaded individually
        for row in range(-5,6):
            for col in range(-4,5):
                px=cx+col*30+(row%2)*15; py=cy+row*26
                d=((px-cx)**2/100**2+(py-cy)**2/132**2)**0.5
                if d>0.9: continue
                shade=int(220*(1-d*0.4))
                pts=np.array([[px,py-11],[px+13,py],[px,py+11],[px-13,py]],np.int32)
                cv2.fillPoly(canvas,[pts],(0,shade//2,shade,255))
                cv2.polylines(canvas,[pts],True,(0,shade//3,shade//2,255),2,cv2.LINE_AA)
                # Tiny bright center
                cv2.circle(canvas,(px,py),3,(0,shade,shade,255),-1)
        # Spiky green crown
        for i in range(9):
            ang=-65+i*16
            tx=cx+int(np.sin(np.radians(ang))*35)
            ty=cy-132-abs(i-4)*14+5
            length=55+abs(4-i)*8
            cv2.ellipse(canvas,(tx,ty),(18,length),ang,0,360,(15,145,35,255),-1,cv2.LINE_AA)
            # Dark centre vein
            ex2=tx+int(np.sin(np.radians(ang))*5)
            ey2=ty-length+12
            cv2.line(canvas,(tx,ty),(ex2,ey2),(8,80,18,255),2,cv2.LINE_AA)
        self._specular(canvas,cx-30,cy-50,70,180)
        return canvas

    def _draw_grapes(self) -> np.ndarray:
        S=290; canvas=self._canvas(S)
        positions=[(145,185),(108,163),(178,163),(124,135),(162,135),
                   (145,108),(112,110),(175,110),(145,82)]
        for i,(x,y) in enumerate(positions):
            r=30-i//3*2
            # Deep purple grape
            self._radial(canvas,x,y,r,(110,45,195,255),(55,8,130,255))
            # Lighter reflection spot
            cv2.circle(canvas,(x-r//3,y-r//3),r//4,(150,80,230,200),-1,cv2.LINE_AA)
            # Tiny specular
            cv2.circle(canvas,(x-r//4,y-r//4),r//8,(220,180,255,230),-1,cv2.LINE_AA)
        # Brown stem
        cv2.line(canvas,(145,52),(145,28),(50,28,8,255),9,cv2.LINE_AA)
        cv2.line(canvas,(145,52),(125,42),(40,22,5,255),5,cv2.LINE_AA)
        # Leaf
        for ang,ox,oy in [(-20,28,-18),(15,-5,-25)]:
            cv2.ellipse(canvas,(145+ox,48+oy),(36,18),ang,0,360,(22,150,45,255),-1,cv2.LINE_AA)
            cv2.line(canvas,(145+ox,48+oy),(145+ox+8,38+oy),(14,100,28,255),2,cv2.LINE_AA)
        return canvas

    def _draw_strawberry(self) -> np.ndarray:
        S=260; canvas=self._canvas(S)
        # Heart-ish berry shape
        contour=np.array([[130,42],[198,82],[205,148],[178,192],[130,222],[82,192],[55,148],[62,82]],np.int32)
        cv2.fillPoly(canvas,[contour],(28,28,195,255))
        # Subtle lighter middle
        mid=np.array([[130,65],[178,95],[182,148],[155,182],[130,205],[105,182],[78,148],[82,95]],np.int32)
        cv2.fillPoly(canvas,[mid],(40,40,215,255))
        # Shading on left
        shd=self._canvas(S)
        cv2.fillPoly(shd,[np.array([[130,42],[82,82],[55,148],[82,192],[130,222]],np.int32)],(0,0,0,40))
        sm=shd[:,:,3]>0
        canvas[sm]=np.clip(canvas[sm].astype(np.float32)*0.75,0,255).astype(np.uint8)
        # Realistic seeds — small oval yellow indentations
        rng=np.random.default_rng(3)
        for _ in range(28):
            sx,sy=int(rng.uniform(68,192)),int(rng.uniform(72,205))
            if cv2.pointPolygonTest(contour,(float(sx),float(sy)),False)>2:
                # Seed indentation shadow
                cv2.ellipse(canvas,(sx,sy),(7,9),rng.uniform(-20,20),0,360,(10,10,140,255),-1,cv2.LINE_AA)
                # Actual seed
                cv2.ellipse(canvas,(sx-1,sy-1),(5,7),rng.uniform(-20,20),0,360,(30,200,240,255),-1,cv2.LINE_AA)
        # Green sepals (leafy crown)
        for ang in range(0,360,45):
            r=np.radians(ang)
            lx,ly=int(130+22*np.sin(r)),int(44-22*np.cos(r))
            cv2.ellipse(canvas,(lx,ly),(14,26),ang,0,360,(18,165,42,255),-1,cv2.LINE_AA)
        cv2.circle(canvas,(130,44),10,(25,185,50,255),-1,cv2.LINE_AA)
        self._specular(canvas,105,105,55,200)
        return canvas

    def _draw_peach(self) -> np.ndarray:
        S=280; c=S//2; canvas=self._canvas(S)
        # Warm peachy-pink base
        self._radial(canvas,c,c+8,c-5,(100,185,255,255),(55,105,220,255))
        # Orange-red blush on one side
        blush=self._canvas(S)
        cv2.circle(blush,(c+38,c+12),72,(30,80,230,180),-1,cv2.LINE_AA)
        bm=blush[:,:,3]>0
        canvas[bm]=np.clip(canvas[bm].astype(np.float32)*0.55+blush[bm].astype(np.float32)*0.45,0,255).astype(np.uint8)
        # Slight secondary blush top
        blush2=self._canvas(S)
        cv2.circle(blush2,(c-20,c-30),50,(60,110,240,120),-1,cv2.LINE_AA)
        bm2=blush2[:,:,3]>0
        canvas[bm2]=np.clip(canvas[bm2].astype(np.float32)*0.7+blush2[bm2].astype(np.float32)*0.3,0,255).astype(np.uint8)
        # Crease line with shadow
        cv2.line(canvas,(c,c-52),(c,c+62),(80,110,190,255),5,cv2.LINE_AA)
        cv2.line(canvas,(c+2,c-52),(c+2,c+62),(130,160,230,120),2,cv2.LINE_AA)
        # Fuzzy skin texture
        rng=np.random.default_rng(5)
        self._noise_texture(canvas,c,c+8,c-8,rng,(70,100,200,60),80)
        # Stem + leaf
        cv2.line(canvas,(c,c-66),(c+4,c-98),(38,18,4,255),7,cv2.LINE_AA)
        cv2.ellipse(canvas,(c+30,c-80),(36,16),-32,0,360,(18,155,45,255),-1,cv2.LINE_AA)
        self._specular(canvas,c-18,c-22,58,210)
        return canvas

    def _draw_cherries(self) -> np.ndarray:
        S=250; canvas=self._canvas(S)
        for cx,cy,r in [(88,158,44),(155,155,42)]:
            # Deep red cherry
            self._radial(canvas,cx,cy,r,(40,20,200,255),(8,0,130,255))
            # Highlight crescent
            hx,hy=cx-r//3,cy-r//3
            cv2.circle(canvas,(hx,hy),r//3,(80,40,220,160),-1,cv2.LINE_AA)
            # Specular dot
            cv2.circle(canvas,(hx+3,hy+3),r//7,(200,150,240,230),-1,cv2.LINE_AA)
        # Green curved stems
        for (sx,sy),(ex,ey) in [((88,114),(122,52)),((155,113),(122,52))]:
            for t in np.linspace(0,1,20):
                mx,my=int(sx+(ex-sx)*t),int(sy+(ey-sy)*t-18*np.sin(np.pi*t))
                cv2.circle(canvas,(mx,my),4,(32,120,32,255),-1)
        # Leaf
        cv2.ellipse(canvas,(148,44),(30,14),-18,0,360,(22,155,42,255),-1,cv2.LINE_AA)
        cv2.line(canvas,(148,44),(162,36),(14,95,25,255),2,cv2.LINE_AA)
        return canvas

    def _draw_mango(self) -> np.ndarray:
        S=300; canvas=self._canvas(S); cx,cy=S//2+12,S//2+12
        # Deep golden-orange teardrop body
        cv2.ellipse(canvas,(cx,cy),(92,122),-22,0,360,(0,145,235,255),-1,cv2.LINE_AA)
        # Gradient overlay dark→bright
        for i in range(118,0,-2):
            t=i/118
            g=int(130*t+210*(1-t)); rv=int(185*t+255*(1-t))
            cv2.ellipse(canvas,(cx-int(i*0.08),cy-int(i*0.04)),(int(i*0.80),int(i)),
                        -22,0,360,(0,g,rv,255),-1,cv2.LINE_AA)
        # Red-pink blush on shoulder
        blush=self._canvas(S)
        cv2.ellipse(blush,(cx+28,cy-28),(56,65),-22,0,360,(30,60,225,160),-1,cv2.LINE_AA)
        bm=blush[:,:,3]>0
        canvas[bm]=np.clip(canvas[bm].astype(np.float32)*0.55+blush[bm].astype(np.float32)*0.45,0,255).astype(np.uint8)
        # Green tip (stem end)
        cv2.ellipse(canvas,(cx-62,cy-72),(22,14),-22,0,360,(20,145,35,255),-1,cv2.LINE_AA)
        # Brown stem nub
        cv2.circle(canvas,(cx-68,cy-78),8,(35,18,5,255),-1,cv2.LINE_AA)
        # Subtle skin texture
        rng=np.random.default_rng(8)
        self._noise_texture(canvas,cx,cy,90,rng,(0,100,160,50),80)
        self._specular(canvas,cx-25,cy-35,55,200)
        return canvas

    def _draw_kiwi(self) -> np.ndarray:
        S=260; c=S//2; canvas=self._canvas(S)
        # Fuzzy brown outer skin
        self._radial(canvas,c,c,c-4,(65,75,100,255),(18,22,38,255))
        # Fuzzy texture lines
        rng=np.random.default_rng(9)
        for _ in range(120):
            ang=rng.uniform(0,2*np.pi)
            r1=rng.uniform(0.55,0.96)*(c-4)
            r2=rng.uniform(0.50,0.90)*(c-4)
            cv2.line(canvas,(int(c+r1*np.cos(ang)),int(c+r1*np.sin(ang))),
                     (int(c+r2*np.cos(ang+0.18)),int(c+r2*np.sin(ang+0.18))),
                     (int(rng.uniform(35,60)),int(rng.uniform(45,75)),int(rng.uniform(60,100)),180),2,cv2.LINE_AA)
        # Bright green flesh ring
        cv2.circle(canvas,(c,c),c-20,(30,190,105,255),-1,cv2.LINE_AA)
        # White pith ring
        cv2.circle(canvas,(c,c),c-38,(240,252,238,255),-1,cv2.LINE_AA)
        # Pale yellow-green centre
        self._radial(canvas,c,c,c-44,(210,240,200,255),(180,225,170,255))
        # Radiating seed chambers (dark lines from centre)
        for ang in np.linspace(0,2*np.pi,16,endpoint=False):
            ex2=int(c+np.cos(ang)*(c-40)); ey2=int(c+np.sin(ang)*(c-40))
            cv2.line(canvas,(c,c),(ex2,ey2),(80,150,80,120),1,cv2.LINE_AA)
        # Black seeds with white tips
        for ang in np.linspace(0.2,2*np.pi-0.2,14,endpoint=False):
            sx=int(c+np.cos(ang)*50); sy=int(c+np.sin(ang)*50)
            cv2.ellipse(canvas,(sx,sy),(8,14),np.degrees(ang),0,360,(5,12,5,255),-1,cv2.LINE_AA)
            cv2.circle(canvas,(sx,sy),3,(200,225,195,255),-1,cv2.LINE_AA)
        self._specular(canvas,c-5,c-5,c-12,150)
        return canvas

    def _draw_pear(self) -> np.ndarray:
        S=290; canvas=self._canvas(S); cx=S//2
        # Bottom bulb — warm yellow-green
        self._radial(canvas,cx,S//2+48,78,(30,220,200,255),(12,148,110,255))
        # Top narrower bulb
        self._radial(canvas,cx,S//2-52,50,(38,235,210,255),(15,158,122,255))
        # Russet blush (brownish patch)
        blush=self._canvas(S)
        cv2.ellipse(blush,(cx+28,S//2+38),(45,58),15,0,360,(15,100,140,160),-1,cv2.LINE_AA)
        bm=blush[:,:,3]>0
        canvas[bm]=np.clip(canvas[bm].astype(np.float32)*0.6+blush[bm].astype(np.float32)*0.4,0,255).astype(np.uint8)
        # Subtle texture
        rng=np.random.default_rng(14)
        self._noise_texture(canvas,cx,S//2+20,85,rng,(10,80,80,50),90)
        # Stem
        cv2.line(canvas,(cx,S//2-98),(cx+3,S//2-132),(38,18,4,255),8,cv2.LINE_AA)
        cv2.ellipse(canvas,(cx+32,S//2-116),(36,16),-22,0,360,(18,158,42,255),-1,cv2.LINE_AA)
        self._specular(canvas,cx-12,S//2-18,58,200)
        return canvas

    def _draw_lemon(self) -> np.ndarray:
        S=260; c=S//2; canvas=self._canvas(S)
        # Bright yellow ellipse
        self._radial(canvas,c,c,0,(255,255,255,255),(255,255,255,255))
        cv2.ellipse(canvas,(c,c),(108,74),0,0,360,(0,228,255,255),-1,cv2.LINE_AA)
        # Slightly darker at equator
        cv2.ellipse(canvas,(c,c),(108,74),0,0,360,(0,200,235,255),3,cv2.LINE_AA)
        # Nipple bumps at each end
        for ox in (-106,106):
            cv2.ellipse(canvas,(c+ox,c),(20,16),0,0,360,(0,210,245,255),-1,cv2.LINE_AA)
            cv2.ellipse(canvas,(c+ox,c),(12,10),0,0,360,(0,225,255,255),-1,cv2.LINE_AA)
        # Dimpled peel texture
        rng=np.random.default_rng(5)
        self._noise_texture(canvas,c,c,98,rng,(0,180,210,80),140)
        # Inner lighter highlight band
        cv2.ellipse(canvas,(c,c),(80,52),0,0,360,(15,240,255,255),-1,cv2.LINE_AA)
        cv2.ellipse(canvas,(c,c),(48,30),0,0,360,(30,248,255,255),-1,cv2.LINE_AA)
        self._specular(canvas,c-22,c-22,42,230)
        self._rim_light(canvas,c,c,90,(0,140,180,80))
        return canvas

    def _draw_melon(self) -> np.ndarray:
        S=300; c=S//2; canvas=self._canvas(S)
        # Pale green-beige base (honeydew-ish)
        self._radial(canvas,c,c,c-4,(140,210,140,255),(80,160,80,255))
        # Raised net/webbing pattern
        for ang in range(0,180,18):
            cv2.ellipse(canvas,(c,c),(c-8,c-42),ang,0,360,(160,230,160,255),3,cv2.LINE_AA)
        # Slightly lighter between netting
        cv2.circle(canvas,(c,c),c-16,(150,220,150,255),-1,cv2.LINE_AA)
        for ang in range(0,180,18):
            cv2.ellipse(canvas,(c,c),(c-20,c-58),ang,0,360,(170,240,165,255),2,cv2.LINE_AA)
        # Darker shading on lower half
        shd=self._canvas(S)
        cv2.ellipse(shd,(c,c+c//3),(c-8,c//2),0,0,360,(0,0,0,45),-1,cv2.LINE_AA)
        sm=shd[:,:,3]>0
        canvas[sm]=np.clip(canvas[sm].astype(np.float32)*0.75,0,255).astype(np.uint8)
        # Stem scar
        cv2.circle(canvas,(c,c-c+10),12,(90,150,90,255),-1,cv2.LINE_AA)
        cv2.circle(canvas,(c,c-c+10), 6,(70,130,70,255),-1,cv2.LINE_AA)
        self._specular(canvas,c,c,c-10,160)
        return canvas

    def _draw_blueberries(self) -> np.ndarray:
        S=250; canvas=self._canvas(S)
        positions=[(125,132),(85,150),(162,150),(104,104),(146,104),(125,78)]
        for cx,cy in positions:
            r=36
            # Blue-purple berry
            self._radial(canvas,cx,cy,r,(115,55,195,255),(52,12,125,255))
            # Characteristic star-shaped crown
            star_pts=[]
            for a in np.linspace(0,2*np.pi,5,endpoint=False):
                star_pts.append([int(cx+10*np.cos(a)),int(cy-r+8+5*np.sin(a))])
            cv2.polylines(canvas,[np.array(star_pts,np.int32)],True,(70,28,135,255),2,cv2.LINE_AA)
            # Dusky bloom (whitish powder coating)
            bloom=self._canvas(S)
            cv2.circle(bloom,(cx,cy),r,(180,160,220,35),-1,cv2.LINE_AA)
            bm=bloom[:,:,3]>0
            canvas[bm]=np.clip(canvas[bm].astype(np.float32)*0.8+bloom[bm].astype(np.float32)*0.2,0,255).astype(np.uint8)
            # Specular
            cv2.circle(canvas,(cx-r//3,cy-r//3),r//5,(155,100,225,180),-1,cv2.LINE_AA)
        # Stem + leaf
        cv2.line(canvas,(155,68),(155,45),(40,22,5,255),6,cv2.LINE_AA)
        cv2.ellipse(canvas,(178,42),(28,14),-22,0,360,(20,148,42,255),-1,cv2.LINE_AA)
        return canvas

    def _draw_bomb(self) -> np.ndarray:
        S=300; canvas=self._canvas(S); cx,cy=S//2,S//2+18
        # Shiny black sphere
        self._radial(canvas,cx,cy,100,(70,70,72,255),(12,12,14,255))
        # Large highlight blob (glossy)
        cv2.circle(canvas,(cx+26,cy-28),30,(105,105,108,255),-1,cv2.LINE_AA)
        cv2.circle(canvas,(cx+30,cy-32),16,(145,145,148,255),-1,cv2.LINE_AA)
        cv2.circle(canvas,(cx+33,cy-35), 7,(200,200,202,255),-1,cv2.LINE_AA)
        # Metal collar / fuse housing
        cv2.rectangle(canvas,(cx-11,cy-118),(cx+11,cy-74),(75,75,78,255),-1)
        cv2.rectangle(canvas,(cx-11,cy-118),(cx+11,cy-74),(55,55,58,255), 2)
        # Twisted rope fuse
        for i,t in enumerate(np.linspace(0,1,28)):
            fx=int(cx + 22*np.sin(t*np.pi*3.5))
            fy=int(cy-118 - t*80)
            col=(int(80+40*np.sin(t*20)),int(60+30*np.sin(t*20+1)),20,255)
            cv2.circle(canvas,(fx,fy),4,col,-1,cv2.LINE_AA)
        # Bright sparking flame
        flame_cx=cx+int(22*np.sin(3.5*np.pi)); flame_cy=cy-198
        for col,r in [((0,180,255,255),22),((0,255,200,255),14),((50,255,255,255),8),((255,255,255,255),4)]:
            cv2.circle(canvas,(flame_cx,flame_cy),r,col,-1,cv2.LINE_AA)
        return canvas

    def _draw_splash(self) -> np.ndarray:
        S=200; canvas=self._canvas(S); c=S//2
        for idx,color in enumerate([(0,200,80,80),(0,230,120,140),(0,255,160,210)]):
            cv2.circle(canvas,(c,c),c-idx*16,color,-1,cv2.LINE_AA)
        canvas[:]=cv2.GaussianBlur(canvas,(0,0),10)
        return canvas

    def _draw_life(self) -> np.ndarray:
        canvas=self._canvas(96)
        for angle in np.linspace(0,np.pi,300):
            x=24*np.sin(angle)**3
            y=13*np.cos(angle)-5*np.cos(2*angle)-2*np.cos(3*angle)-np.cos(4*angle)
            cv2.circle(canvas,(int(canvas.shape[1]/2+x),int(canvas.shape[0]/2-y*2.2)),
                       9,(0,30,220,255),-1,cv2.LINE_AA)
        return canvas
