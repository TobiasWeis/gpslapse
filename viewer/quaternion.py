#!/usr/bin/env python
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from utils import *

def quatConj(q):
    """Return the conjugate of quaternion `q`."""
    return np.append(q[0], -q[1:])

def quatHProd(p, q):
    """Compute the Hamilton product of quaternions `p` and `q`."""
    r = np.array([p[0]*q[0] - p[1]*q[1] - p[2]*q[2] - p[3]*q[3],
                  p[0]*q[1] + p[1]*q[0] + p[2]*q[3] - p[3]*q[2],
                  p[0]*q[2] - p[1]*q[3] + p[2]*q[0] + p[3]*q[1],
                  p[0]*q[3] + p[1]*q[2] - p[2]*q[1] + p[3]*q[0]])
    return r

def quatRecip(q):
    """Compute the reciprocal of quaternion `q`."""
    return quatConj(q) / np.dot(q,q)

def quatFromAxisAng(ax, theta):
    """Get a quaternion that performs the rotation around axis `ax` for angle
    `theta`, given as::

        q = (r, v) = (cos(theta/2), sin(theta/2)*ax).

    Note that the input `ax` needs to be a 3x1 unit vector."""
    return np.append(np.cos(theta/2), np.sin(theta/2)*ax)

def quatFromRotMatx(R):
    """Get a quaternion from a given rotation matrix `R`."""
    q = np.zeros(4)

    q[0] = ( R[0,0] + R[1,1] + R[2,2] + 1) / 4.0
    q[1] = ( R[0,0] - R[1,1] - R[2,2] + 1) / 4.0
    q[2] = (-R[0,0] + R[1,1] - R[2,2] + 1) / 4.0
    q[3] = (-R[0,0] - R[1,1] + R[2,2] + 1) / 4.0

    q[q<0] = 0   # Avoid complex number by numerical error.
    q = np.sqrt(q)

    q[1] *= np.sign(R[2,1] - R[1,2])
    q[2] *= np.sign(R[0,2] - R[2,0])
    q[3] *= np.sign(R[1,0] - R[0,1])

    return q



def quatToRotMatx(q):
    """Get a rotation matrix from the given unit quaternion `q`."""
    R = np.zeros((3,3))

    R[0,0] = 1 - 2*(q[2]**2 + q[3]**2)
    R[1,1] = 1 - 2*(q[1]**2 + q[3]**2)
    R[2,2] = 1 - 2*(q[1]**2 + q[2]**2)

    R[0,1] = 2 * (q[1]*q[2] - q[0]*q[3])
    R[1,0] = 2 * (q[1]*q[2] + q[0]*q[3])

    R[0,2] = 2 * (q[1]*q[3] + q[0]*q[2])
    R[2,0] = 2 * (q[1]*q[3] - q[0]*q[2])

    R[1,2] = 2 * (q[2]*q[3] - q[0]*q[1])
    R[2,1] = 2 * (q[2]*q[3] + q[0]*q[1])

    return R

def rotVecByQuat(u, q):
    """Rotate a 3-vector `u` according to the quaternion `q`. The output `v` is
    also a 3-vector such that::

        [0; v] = q * [0; u] * q^{-1}

    with Hamilton product."""
    v = quatHProd(quatHProd(q, np.append(0, u)), quatRecip(q))
    return v[1:]

def rotVecByAxisAng(u, ax, theta):
    """Rotate the 3-vector `u` around axis `ax` for angle `theta` (radians),
    counter-clockwisely when looking at inverse axis direction. Note that the
    input `ax` needs to be a 3x1 unit vector."""
    q = quatFromAxisAng(ax, theta)
    return rotVecByQuat(u, q)

def plotQuatRot(quat):

    # Rotation axis.
    #ax = np.array([1.0, 1.0, 1.0])
    #ax = ax / np.linalg.norm(ax)

    vec = [1.0, 1.0, 1.0]
    #quaternion = np.array([-0.80101704, -0.5917579, -0.0609498, -0.033204])
    v = rotVecByQuat(vec, quat)

    # Draw the circle frame.
    # 3d PLOT
    nSamples = 1000
    t = np.linspace(-np.pi, np.pi, nSamples)
    z = np.zeros(t.shape)
    fig = plt.figure()
    fig_ax = fig.add_subplot(111, projection="3d", aspect="equal")
    fig_ax.plot(np.cos(t), np.sin(t), z, 'b')
    fig_ax.plot(z, np.cos(t), np.sin(t), 'b')
    fig_ax.plot(np.cos(t), z, np.sin(t), 'b')
    fig_ax.plot([0, v[0]], [0, v[1]], [0, v[2]], 'm')

    fig_ax.view_init(elev=8, azim=80)
    #plt.show()

    # 2D plot
    '''
    fig = plt.figure()
    plt.plot([0, v[0]], [0,v[1]])
    plt.xlim([-1,1])
    plt.ylim([-1,1])
    '''

    # Draw rotation axis.
    #fig_ax.plot([0, ax[0]*2], [0, ax[1]*2], [0, ax[2]*2], 'r')

    # Rotate the `u` vector and draw results.
    #fig_ax.plot([0, vec[0]], [0, vec[1]], [0, vec[2]], 'm')
    
    #v = rotVecByAxisAng(vec, ax, theta)

    return fig2data(fig)


