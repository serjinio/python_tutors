import math
import numpy as np
from ede import Detector


# Detector definitions


class EspriPlastic(Detector):

    def __init__(self, material_id, thickness=4.):
        """
        param: material_id - name of the material from which it is made of
        param: stopping_powers - a list of stopping_powers for different
               particles
        param: thickness - thickness of plastic scintillator in mm
        """
        super(EspriPlastic, self).__init__(material_id)
        self.thickness = thickness
        # plastic resolution, percents from e-loss
        self.resolution_sigma = 5e-2

    def get_resolution_error(self, e_loss):
        if e_loss <= 1e-3:
            return 0
        err = np.random.normal(0, e_loss * self.resolution_sigma)
        return err

    def e_loss(self, particle_id, e):
        """
        Computes e-loss inside this plastic for a given particle type.

        param: e - Energy of the incident particle
        param particle_id - Name of the particle
        """
        stop_pow = self._find_stop_pow(particle_id)
        e_loss = stop_pow.e_loss(particle_id, e, self.thickness)
        e_loss += self.get_resolution_error(e_loss)
        return e_loss


class EspriNaI(Detector):

    def __init__(self, material_id, thickness=50.):
        """
        param: material_id - name of the material from which it is made of
        param: stopping_powers - a list of stopping_powers for different
               particles
        param: thickness - thickness of plastic scintillator in mm
        """
        super(EspriNaI, self).__init__(material_id)
        self.thickness = thickness
        # crystal resolution, percents from e-loss
        self.resolution_sigma = 2e-2

    def get_resolution_error(self, e_loss):
        if e_loss <= 1e-3:
            return 0
        err = np.random.normal(0, e_loss * self.resolution_sigma)
        return err

    def e_loss(self, particle_id, e):
        """
        Computes e-loss inside this plastic for a given particle type.

        param: e - Energy of the incident particle
        param particle_id - Name of the particle
        """
        stop_pow = self._find_stop_pow(particle_id)
        e_loss = stop_pow.e_loss(particle_id, e, self.thickness)
        e_loss += self.get_resolution_error(e_loss)
        return e_loss


class WedgeEnergyDegrader(Detector):

    def __init__(self, material_id, dist_from_target, base_angle,
                 thickness=30., min_thickness=2., length=230.):
        """
        param: dist_from_target - Distance from reaction point in mm
        param: base_angle - Angle between beam direction and base of the
               degrader.
        """
        super(WedgeEnergyDegrader, self).__init__(material_id)
        self.dist_from_target = dist_from_target
        self.base_angle = base_angle
        self.thickness = thickness
        self.min_thickness = min_thickness
        self.length = length

    def _compute_dist(self, angle_with_base_point, dist_from_target):
        """Computes distance from base of degrader.

        param: angle_with_base_point - angle between degrader base and
               the point to which we compute the distance
        """
        d = 2 * dist_from_target * math.tan(
            np.radians(angle_with_base_point / 2))
        return d

    def thickness_at(self, distance_from_base):
        """Computes thickness of the degrader given a distance from its base."""
        tan_angle = self.thickness / self.length
        length2 = self.length - distance_from_base
        t = length2 * tan_angle
        return t if t >= self.min_thickness else 0.

    def e_loss(self, particle_id, e, scattering_angle):
        """
        Computes e-loss inside this plastic for a given particle type.

        param: e - Energy of the incident particle
        param particle_id - Name of the particle
        """
        if scattering_angle < self.base_angle:
            return 0.
        stop_pow = self._find_stop_pow(particle_id)
        dist_from_base = self._compute_dist(scattering_angle - self.base_angle,
                                            self.dist_from_target)
        return stop_pow.e_loss(particle_id, e,
                               self.thickness_at(dist_from_base))
