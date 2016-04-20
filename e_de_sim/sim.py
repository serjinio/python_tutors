"""
Simulates dE vs. E spectra for protons & deuterons.

Setup consists of:
 - particles source according to reaction kinematics:
   - 6He(p, p)6He - here we are interested in recoil p
   - C(d, d)C - here we want to simulate spectra of scattered fragment - d
 - dE ESPRI plastic: BC-400, 4 mm thick
 - E ESPRI crystal: NaI, 50 mm thick

Script runs through angular region of interests and plots dE vs E histogram
for recoil protons and scattered deutrons. This is done in order to estimate
how we can carry out PID of protons from background reaction on carbon in
target material.
"""

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

from eloss.ede import *
from eloss.detectors import *

# import seaborn as sns
# sns.set_context("poster")
plt.figure(figsize=(8, 6))


### Simulation parameters


# degrader distance from target in mm
DEGRADER_DIST_FROM_TARGET = 1070.
# angle at which degrader starts, its base is located at at this point
# e.g. in case of wedge degrader it is where the thickest part is
DEGRADER_BASE_ANGLE = 53.0



### Scattering kinematics data
RECOIL_P_KIN = ReactionKinematics(
    PROTON_ID, 'data/Recoil proton kin for 6He(p,p)6He.csv')
RECOIL_P_KIN_DET_LOSS = ReactionKinematics(
    PROTON_ID, 'data/recoil_proton_energies_det_loss.csv')
SCATT_D_KIN = ReactionKinematics(
    DEUTERON_ID, 'data/Deuteron kin for d(C, C)d.csv')
# To compute e losses we want total kin-e not MeV/u
SCATT_D_KIN.kin_data['e'] = SCATT_D_KIN.kin_data['e'] * 2


### Simulation of de & e in espri

class RandomDeuteronKinematics(object):

    def __init__(self, e_range):
        """
        param: particle_id - name of a particle for which this kinematics is
        """
        self.particle_id = DEUTERON_ID
        self.e_range = e_range

    def __getitem__(self, angle):
        """Returns energy as a function of angle."""
        # just a uniform distribution, no angle dependence, MeV/u
        e = np.random.uniform(self.e_range[0], self.e_range[1], 1)[0] * 2
        return e


class RandomTritiumKinematics(object):

    def __init__(self, e_range):
        """
        param: particle_id - name of a particle for which this kinematics is
        """
        self.particle_id = TRITIUM_ID
        self.e_range = e_range

    def __getitem__(self, angle):
        """Returns energy as a function of angle."""
        # just a uniform distribution, no angle dependence, MeV/u
        e = np.random.uniform(self.e_range[0], self.e_range[1], 1)[0] * 3
        return e


class RandomProtonKinematics(object):

    def __init__(self, e_range):
        """
        param: particle_id - name of a particle for which this kinematics is
        """
        self.particle_id = PROTON_ID
        self.e_range = e_range

    def __getitem__(self, angle):
        """Returns energy as a function of angle."""
        # just a uniform distribution, no angle dependence, MeV/u
        e = np.random.uniform(self.e_range[0], self.e_range[1], 1)[0] * 1
        return e


class EspriEdESim(object):
    """
    SImulates e-dE from ESPRI detector.
    """

    def __init__(self, angular_region, reaction_kinematics_data = [],
                 e_degrader_thickness=25.):
        ### Angular region where to compute E-dE
        self.angular_region = angular_region
        ### Detectors
        self.espri_plastic = EspriPlastic(BC400_ID)
        self.espri_nai = EspriNaI(NAI_ID)
        self.espri_e_degrader = WedgeEnergyDegrader(
            BRASS_ID, DEGRADER_DIST_FROM_TARGET,
            DEGRADER_BASE_ANGLE, e_degrader_thickness, 2., 220.)
        self.enable_e_degrader = True
        ### Scattering kinematics data
        self.reaction_kinematics_data = reaction_kinematics_data
        ### outputs store
        self.results = []
        ### private vars

    def do_reaction(self, react_kin, angle_step=0.001):
        df = pd.DataFrame(
            columns=['angle', 'tke', 'e_deg_e_loss', 'de', 'nai_e_loss',
                     'e_residual'])
        dfidx = 0
        angle = ANGULAR_REGION[0]

        while angle < ANGULAR_REGION[1]:
            tke = react_kin[angle]
            # print 'angle: {}; TKE: {}'.format(angle, tke)

            if self.enable_e_degrader:
                e_deg_e_loss = self.espri_e_degrader.e_loss(
                    react_kin.particle_id, tke, angle)
                e_minus_e_deg = tke - e_deg_e_loss
            else:
                e_deg_e_loss = 0.
                e_minus_e_deg = tke

            de = self.espri_plastic.e_loss(
                react_kin.particle_id, e_minus_e_deg)
            e_minus_de = e_minus_e_deg - de
            if e_minus_de < 0:
                e_minus_de = 0
            e_loss_in_nai = self.espri_nai.e_loss(
                react_kin.particle_id, e_minus_de)
            e_residual = e_minus_de - e_loss_in_nai
            # print ('\te_deg_e-loss: {}; de: {}; nai_e-loss: {}; '
            #        'e-residual: {}'.format(
            #            e_deg_e_loss, de, e_loss_in_nai, e_residual))

            df.loc[dfidx] = [angle, tke, e_deg_e_loss, de, e_loss_in_nai,
                             e_residual]

            angle += angle_step
            dfidx += 1
        return df

    def run(self):
        for reaction in self.reaction_kinematics_data:
            res = self.do_reaction(reaction)
            self.results.append(res)
        return self.results


class EspriEdESimResultsPlotter:

    def __init__(self, reaction_kinematics_data, results, name=""):
        self.results = results
        self.reaction_kinematics_data = reaction_kinematics_data
        self.name = name

    def plot_e_de(self):
        plt.figure()
        for (kin, res) in \
            zip(self.reaction_kinematics_data, self.results):
            # plt.scatter(res['nai_e_loss'], res['de'], label=kin.particle_id,
            #             marker=markers[i])
            plt.plot(res['nai_e_loss'], res['de'],
                     label=kin.particle_id, marker='.', markersize=8,
                     linestyle="")
        plt.grid()
        plt.title('E vs. dE ({})'.format(self.name))
        plt.xlabel('E [MeV]')
        plt.ylabel('dE [MeV]')
        plt.ylim(0, 37)
        plt.xlim(0, 220)
        plt.legend()
        plt.tight_layout()
        plt.savefig('e_de({}).png'.format(
            self.name))
        # plt.show()

    def plot_e_de_hist(self):
        plt.figure()
        hist_df = None
        for (kin, res) in \
            zip(self.reaction_kinematics_data, self.results):
            if hist_df is None:
                hist_df = res.copy()
            else:
                hist_df = hist_df.append(res)
        plt.hist2d(hist_df['nai_e_loss'], hist_df['de'], bins=120,
                   range=np.array([(0, 200), (0, 37)]), norm=LogNorm())
        plt.colorbar()
        plt.grid()
        plt.title('E vs. dE ({})'.format(self.name))
        plt.xlabel('E [MeV]')
        plt.ylabel('dE [MeV]')
        plt.ylim(0, 37)
        plt.xlim(0, 220)
        plt.legend()
        plt.tight_layout()
        plt.savefig('e_de_hist({}).png'.format(
            self.name))
        # plt.show()

    def plot_e_aft_deg(self):
        plt.figure()
        for (kin, res) in \
            zip(self.reaction_kinematics_data, self.results):
            plt.plot(res['angle'], res['tke'] - res['e_deg_e_loss'],
                     label=kin.particle_id)
        plt.grid()
        plt.title('E vs. angle ({})'.format(self.name))
        plt.xlabel('Angle deg.')
        plt.ylabel('E [MeV]')
        plt.ylim(0, 200)
        plt.xlim(53, 73)
        plt.legend()
        plt.tight_layout()
        plt.savefig('e_aft_deg({}).png'.format(
            self.name))
        # plt.show()


if __name__ == '__main__':
    print "### ESPRI dE-E simulation ###"
    # angular region of interest in lab deg.
    ANGULAR_REGION = (55., 70.)
    rand_deuteron_kin = RandomDeuteronKinematics([10., 200.])
    rand_tritium_kin = RandomTritiumKinematics([10., 200.])

    bg_sim = EspriEdESim(ANGULAR_REGION,
                         [rand_deuteron_kin, rand_tritium_kin],
                         e_degrader_thickness=0)
    bg_sim.run()

    for t in [40, 60, 80, 100, 140, 180]:
        rand_proton_kin = RandomProtonKinematics([20, t])
        sim = EspriEdESim(ANGULAR_REGION,
                          [rand_proton_kin],
                          e_degrader_thickness=t)
        sim.run()

        results_plotter = EspriEdESimResultsPlotter(
            bg_sim.reaction_kinematics_data, bg_sim.results,
            "E(p) = 20 - {}".format(t))
        results_plotter.reaction_kinematics_data.append(
            sim.reaction_kinematics_data[0])
        results_plotter.results.append(sim.results[0])
        results_plotter.plot_e_aft_deg()
        results_plotter.plot_e_de()
        results_plotter.plot_e_de_hist()
        del results_plotter.reaction_kinematics_data[-1]
        del results_plotter.results[-1]
