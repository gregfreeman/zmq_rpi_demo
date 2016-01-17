from __future__ import print_function, division
from numpy import matrix
from numpy.linalg import norm
import numpy as np


class Quaternion:

    """Quaternions for 3D rotations"""

    def __init__(self, q):
        self.q = np.asarray(q, dtype=float)

    @classmethod
    def identity(cls):
        """
        Construct identity quaternion
        """
        return cls([1, 0, 0, 0])

    @classmethod
    def from_v_theta(cls, v, theta):
        """
        Construct quaternion from unit vector v and rotation angle theta
        """
        theta = np.asarray(theta)
        v = np.asarray(v)

        s = np.sin(0.5 * theta)
        c = np.cos(0.5 * theta)
        vnrm = np.sqrt(np.sum(v * v))

        q = np.concatenate([[c], s * v / vnrm])
        return cls(q)

    @classmethod
    def from_euler(cls, roll, pitch, yaw):
        """
        Construct quaternion from euler angles in radians
        """

        sphi = np.sin(roll / 2)
        cphi = np.cos(roll / 2)
        stheta = np.sin(pitch / 2)
        ctheta = np.cos(pitch / 2)
        spsi = np.sin(yaw / 2)
        cpsi = np.cos(yaw / 2)

        q = [cphi * ctheta * cpsi + sphi * stheta * spsi,
             sphi * ctheta * cpsi - cphi * stheta * spsi,
             cphi * stheta * cpsi + sphi * ctheta * spsi,
             cphi * ctheta * spsi - sphi * stheta * cpsi,
             ]
        return cls(q)

    def __repr__(self):
        return "Quaternion:\n" + self.q.__repr__()

    def __mul__(self, other):
        # multiplication of two quaternions.
        if isinstance(other, Quaternion):
            prod = self.q[:, None] * other.q

            return self.__class__([(prod[0, 0] - prod[1, 1] -
                                    prod[2, 2] - prod[3, 3]),
                                   (prod[0, 1] + prod[1, 0] +
                                    prod[2, 3] - prod[3, 2]),
                                   (prod[0, 2] - prod[1, 3] +
                                    prod[2, 0] + prod[3, 1]),
                                   (prod[0, 3] + prod[1, 2] -
                                    prod[2, 1] + prod[3, 0])])
        else:
            # scalar multiplication
            return self.__class__(self.q * other)

    def __add__(self, other):
        # addition of two quaternions.
        return self.__class__(self.q + other.q)

    def normalize(self):
        # normalize to a unit quaternion.
        self.q = self.q / norm(self.q)

    def as_v_theta(self):
        """Return the v, theta equivalent of the (normalized) quaternion"""
        norm = np.sqrt((self.q ** 2).sum(0))
        theta = 2 * np.arccos(self.q[0] / norm)

        # compute the unit vector
        v = np.array(self.q[1:4], order='F', copy=True)
        v /= np.sqrt(np.sum(v ** 2, 0))

        return v, theta

    def as_euler(self):
        """Return the euler equivalent of the quaternion"""
        q = self.q
        roll = np.arctan2(2 * (q[0] * q[1] + q[2] * q[3]), 1 - 2 * (q[1]**2 + q[2]**2))
        pitch = np.arcsin(2 * (q[0] * q[2] - q[3] * q[1]))
        yaw = np.arctan2(2 * (q[0] * q[3] + q[1] * q[2]), 1 - 2 * (q[2]**2 + q[3]**2))

        return roll, pitch, yaw

    def mat_G(self):
        return matrix([[-self.q[1],  self.q[0],  self.q[3], -self.q[2]],
                       [-self.q[2], -self.q[3],  self.q[0],  self.q[1]],
                       [-self.q[3],  self.q[2], -self.q[1],  self.q[0]]])

    def mat_E(self):
        return matrix([[-self.q[1],  self.q[0], -self.q[3],  self.q[2]],
                       [-self.q[2],  self.q[3],  self.q[0], -self.q[1]],
                       [-self.q[3], -self.q[2],  self.q[1],  self.q[0]]])

    def as_rotation_matrix(self):
        """Return the rotation matrix of the (normalized) quaternion"""
        return self.mat_E()*self.mat_G().T


def dqdT(qq, w, Ts):
    omega = Quaternion([0, w[0], w[1], w[2]])
    dqdt = qq * omega * 0.5
    return qq+dqdt*Ts


