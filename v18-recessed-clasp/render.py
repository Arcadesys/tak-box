from pathlib import Path
import sys,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,'/workspace/shared/tak-travel-cad/clasp-comparison/B/vendor')
import trimesh,cadquery as cq
from build import receiver,keeper,slider,box
R=Path(__file__).parent;D=R/'renders';D.mkdir(exist_ok=True)
F='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';B=F.replace('.ttf','-Bold.ttf')
def render(parts,path,title,subtitle,section=False):
 W,H=1400,850;az,el=map(math.radians,[-67,32]);f=np.array([math.cos(el)*math.cos(az),math.cos(el)*math.sin(az),math.sin(el)]);u=np.array([-math.sin(az),math.cos(az),0]);v=np.cross(f,u)
 meshes=[];allp=[]
 for name,shape,color in parts:
  if section:shape=shape.intersect(box(-30,100,20,50,-10,60))
  vs,fs=shape.tessellate(.08);m=trimesh.Trimesh(vertices=[x.toTuple() for x in vs],faces=fs,process=False)
  p=np.c_[m.vertices@u,m.vertices@v,m.vertices@f];allp.append(p);meshes.append((m,p,np.array(color)))
 a=np.vstack(allp);lo=a.min(0);hi=a.max(0);scale=min((W-100)/(hi[0]-lo[0]),(H-270)/(hi[1]-lo[1]));center=(lo+hi)/2
 rgb=np.full((H,W,3),246,dtype=np.uint8);depth=np.full((H,W),-1e30);light=np.array([-.3,-.6,.75]);light/=np.linalg.norm(light)
 for m,p,color in meshes:
  p[:,0]=(p[:,0]-center[0])*scale+W/2;p[:,1]=H/2+35-(p[:,1]-center[1])*scale
  for face,n in zip(m.faces,m.face_normals):
   if n@f<=0:continue
   a,b,c=p[face];xmin=max(0,int(np.floor(min(a[0],b[0],c[0]))));xmax=min(W-1,int(np.ceil(max(a[0],b[0],c[0]))));ymin=max(0,int(np.floor(min(a[1],b[1],c[1]))));ymax=min(H-1,int(np.ceil(max(a[1],b[1],c[1]))))
   if xmin>xmax or ymin>ymax:continue
   det=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
   if abs(det)<1e-10:continue
   xx,yy=np.meshgrid(np.arange(xmin,xmax+1)+.5,np.arange(ymin,ymax+1)+.5)
   w0=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/det;w1=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/det;w2=1-w0-w1;zz=w0*a[2]+w1*b[2]+w2*c[2];dd=depth[ymin:ymax+1,xmin:xmax+1];mask=(w0>=-1e-9)&(w1>=-1e-9)&(w2>=-1e-9)&(zz>dd);dd[mask]=zz[mask];rgb[ymin:ymax+1,xmin:xmax+1][mask]=np.clip(color*(.6+.4*max(0,n@light)),0,255).astype(np.uint8)
 im=Image.fromarray(rgb);dr=ImageDraw.Draw(im);dr.text((45,28),title,font=ImageFont.truetype(B,36),fill='#182b39');dr.text((45,81),subtitle,font=ImageFont.truetype(F,23),fill='#425563')
 # Mark the real press surface in locked/pressed poses, without changing CAD geometry.
 if 'LOCKED' in title or 'PRESS DOWN' in title:
  q=np.array([27,20,6.8 if 'LOCKED' in title else 4.75]);pp=np.array([q@u,q@v,q@f]);px=(pp[0]-center[0])*scale+W/2;py=H/2+35-(pp[1]-center[1])*scale
  dr.line([(px,py),(px+65,py-100)],fill='#172f42',width=4);dr.ellipse((px-6,py-6,px+6,py+6),fill='#172f42');dr.text((px+35,py-135),'PRESS',font=ImageFont.truetype(B,23),fill='#172f42')
 dr.text((45,H-77),'BLUE: fixed receiver   •   GOLD: sliding bolt + release leaf   •   TEAL: opening keeper',font=ImageFont.truetype(F,22),fill='#263f50');dr.text((45,H-40),'Actual CAD geometry • Unprinted V18 test coupon • No physical performance claim',font=ImageFont.truetype(F,20),fill='#61717b');im.save(path)
for i,(d,t,z,title,sub) in enumerate([(0,0,0,'1  LOCKED','Square tooth blocks sliding; rigid bolt overlaps keeper by 4 mm'),(1.8,0,0,'2  PRESS DOWN','Leaf bends ~1.8 mm at tooth; keeper is still blocked'),(1.8,10,0,'3  HOLD + SLIDE LEFT','Slide bolt 10 mm while pressed, until the keeper is clear'),(0,10,12,'4  LIFT OPEN','Release button; lift the keeper. Bolt stays within the guard outline.')],1):
 ps=[('receiver',receiver,(73,122,162)),('slider',slider(d,t),(231,171,63)),('keeper',keeper.translate((0,0,z)),(59,159,147))]
 render(ps,D/f'{i}-assembled.png',f'V18  |  {title}',sub)
 render(ps,D/f'{i}-cutaway.png',f'V18  |  {title}  /  CUTAWAY',sub,True)
imgs=[Image.open(D/f'{i}-cutaway.png').resize((1000,607)) for i in range(1,5)];sheet=Image.new('RGB',(2000,1214),'white')
for i,im in enumerate(imgs):sheet.paste(im,((i%2)*1000,(i//2)*607))
sheet.save(D/'V18-release-sequence.png')
