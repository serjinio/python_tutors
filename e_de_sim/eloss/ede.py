import re
from os import listdir
from os.path import isfile, join
import numpy as np
import pandas as pd


# particle names/IDs


PROTON_ID = 'Hydrogen'
DEUTERON_ID = 'Deuteron'
TRITIUM_ID = 'Tritium'


# material IDs


NAI_ID = 'NaI'
BC400_ID = 'BC400'
BRASS_ID = 'Brass'


# data directories


DEFAULT_STOPPING_POWERS_DATA_DIR = "data"


### I/O helpers


def read_srim_stopping_power_csv(input_file):
    """
    Helper to read stopping power data from SRIM csv format.
    """
    df = pd.read_csv(input_file, sep=r"\s+", skiprows=25, skipfooter=13,
                     header=None, usecols=[0, 1, 2, 3, 4, 5], engine='python')
    df.columns = ['e', 'e_units', 'elec_de', 'nuc_de', 'range', 'range_units']

    # normalize units, all to MeV & mm
    df_rows = []
    for index, row in df.iterrows():
        if row['e_units'] == 'keV':
            row['e'] *= 1e-3
            row['elec_de'] *= 1e-3
            row['nuc_de'] *= 1e-3
        if row['range_units'] == 'um':
            row['range'] *= 1e-3
        elif row['range_units'] == 'm':
            row['range'] *= 1e3
        df_rows.append(row)
    df_norm = pd.DataFrame(df_rows, columns=df.columns)
    del df_norm['e_units']
    del df_norm['range_units']
    df_norm['tot_de'] = df_norm['elec_de'] + df_norm['nuc_de']
    df.norm = df_norm.sort(['e'])
    return df_norm


def read_kinematics_csv(input_file):
    """
    Helper, reads reaction kinematics CSV file.
    """
    df = pd.read_csv(input_file)
    df.columns = ['a', 'e']
    df = df.sort(['a'])
    return df


class MaterialStoppingPower:

    def __init__(self, material_id, stopping_power_csv_file, particle_id):
        """
        param: material_id - name of the material
        param: stopping_power_csv_file - SRIM stopping power data
        param: particle_id - particle name, for what particle
               this stopping power is
        """
        self.material_id = material_id
        self.stop_pow_data = read_srim_stopping_power_csv(
            stopping_power_csv_file)
        self.particle_id = particle_id

    def __str__(self):
        return name

    def __getitem__(self, e):
        """Return stopping power at a give energy in MeV."""
        return np.interp(e, self.stop_pow_data['e'],
                         self.stop_pow_data['tot_de'])

    def e_loss(self, particle_id, e, z, step=0.1):
        """
        Computes energy loss for a given thickness.

        param: particle_id - name of the particle
        param: e - energy of the incoming particle in MeV
        param: z - thickness for e-loss calculation in mm
        """
        if particle_id != self.particle_id:
            raise ValueError('Particle ID of this stopping power: {} cannot'
                             'be used with this particle: {}'.format(
                                 self.particle_id, particle_id))
        if e < 0:
            raise ValueError('Kin. energy cannot be lower than zero!')

        # loss, depth = 0.0, 0.0
        # current_e = e
        # while depth < z:
        #     if current_e < 0.1:
        #         return loss
        #     step_loss = self[current_e] * step
        #     loss += step_loss
        #     current_e -= step_loss
        #     depth += step
        # return loss

        particle_range = np.interp(e, self.stop_pow_data['e'],
                                   self.stop_pow_data['range'])
        if particle_range <= z:
            return e
        else:
            return e - np.interp(
                particle_range - z, self.stop_pow_data['range'],
                self.stop_pow_data['e'])


class StoppingPowersStore(object):

    def __init__(self, stopping_powers_data_dir=DEFAULT_STOPPING_POWERS_DATA_DIR):
        self.data_dir = stopping_powers_data_dir
        self.stopping_powers = []
        self.load_data()

    def load_data(self):
        """Scans data directories for files matching patter and tries to load
        stopping power data from them."""
        is_srim_data_file = lambda f: isfile(join(self.data_dir, f)) and \
                            re.match(r'(\w+)\s+in\s+(\w+)\.txt', f, flags=0)
        data_files = [f for f in listdir(self.data_dir)
                      if is_srim_data_file(f)]
        for f in data_files:
            fname_match = re.match(r'(\w+)\s+in\s+(\w+)\.txt', f, flags=0)
            particle_id, material_id = fname_match.group(1), fname_match.group(2)
            print 'reading stopping power for {} in {}'.format(particle_id, material_id)
            self.stopping_powers.append(MaterialStoppingPower(
                material_id, join(self.data_dir, f), particle_id))

    def find(self, material_id, particle_id):
        for stop_pow in self.stopping_powers:
            if stop_pow.material_id == material_id and \
               stop_pow.particle_id == particle_id:
                return stop_pow
        raise ValueError(('Requested stopping power: "{} in {}" '
                          'does not exist'.format(particle_id, material_id)))


DEFAULT_STOPPING_POWERS_STORE = StoppingPowersStore()


class ReactionKinematics:

    def __init__(self, particle_id, kinematics_csv_file):
        """
        param: particle_id - name of a particle for which this kinematics is
        """
        self.particle_id = particle_id
        self.kin_data = read_kinematics_csv(kinematics_csv_file)

    def __getitem__(self, angle):
        """Returns energy as a function of angle."""
        return np.interp(angle, self.kin_data['a'], self.kin_data['e'])


class Detector(object):
    """Base class for all detectors in this simulation."""

    def __init__(self, material_id,
                 stopping_powers_store=None):
        self.material_id = material_id
        if stopping_powers_store is None:
            self.stopping_powers_store = DEFAULT_STOPPING_POWERS_STORE
        else:
            self.stopping_powers_store = stopping_powers_store

    def _find_stop_pow(self, particle_id):
        """Tries to find suitable stopping power for a given particle ID."""
        return self.stopping_powers_store.find(self.material_id, particle_id)
