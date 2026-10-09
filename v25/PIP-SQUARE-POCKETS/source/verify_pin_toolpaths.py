"""Retained exact segment-to-cylinder test from V24; no print action."""
import numpy as np
def hits(P,Q,a,b,radius):
 axis=b-a;length=np.linalg.norm(axis);axis=axis/length
 rel=P-a;delta=Q-P;ax=rel@axis;step=delta@axis
 moving=np.abs(step)>1e-10
 lower=np.zeros(len(P));upper=np.ones(len(P))
 lower[moving]=np.maximum(0,np.minimum(-ax[moving]/step[moving],(length-ax[moving])/step[moving]))
 upper[moving]=np.minimum(1,np.maximum(-ax[moving]/step[moving],(length-ax[moving])/step[moving]))
 valid=(lower<=upper)&(moving|((ax>=0)&(ax<=length)))
 radial=rel-ax[:,None]*axis;dr=delta-step[:,None]*axis
 denom=(dr*dr).sum(1);t=np.zeros(len(P));vary=denom>1e-12
 t[vary]=-(radial[vary]*dr[vary]).sum(1)/denom[vary];t=np.clip(t,lower,upper)
 distance=np.linalg.norm(radial+t[:,None]*dr,axis=1)
 return valid&(distance<radius-.02)
