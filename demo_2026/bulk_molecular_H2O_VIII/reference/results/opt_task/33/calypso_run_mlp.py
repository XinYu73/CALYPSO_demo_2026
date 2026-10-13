#!/usr/bin/env python
import io
import sys
import time
import pickle
import warnings
import contextlib

import numpy as np
from ase.io import read, write
from ase import Atoms
from ase.calculators.singlepoint import SinglePointCalculator
from ase.optimize import LBFGS

try:
    from ase.filters import UnitCellFilter
    from ase.spacegroup.symmetrize import FixSymmetry
except:
    from ase.constraints import UnitCellFilter, FixSymmetry

from chgnet.model import CHGNet
from chgnet.model import CHGNetCalculator as MLP

chgnet = CHGNet.load(model_name="0.3.0")
calc = MLP(
    model=chgnet,
    **{
        "check_cuda_mem": True,
        "on_isolated_atoms": "warn",
        "stress_weight": 0.006241509125883258,
    },
)


def run_opt(pstress, model, mlp_trajname, fmax, mlp_optstep, keep_sym=False):
    # pstress: GPa
    # 1 eV/A^3 = 160.21766028 GPa
    # 1 / 160.21766028 ~ 0.006242

    verbose = True
    stream = sys.stdout if verbose else io.StringIO()
    with contextlib.redirect_stdout(stream):
        print("Start to Optimize Structures using ", model)
        data = {}
        start = time.time()

        atoms = read("caly_ini.xyz")
        atoms.write("POSCAR")
        if keep_sym:
            atoms.set_constraint(
                FixSymmetry(atoms, symprec=0.1, adjust_positions=True, adjust_cell=True)
            )

        if len(atoms) == 1:
            from ase.build import make_supercell

            atoms = make_supercell(atoms, [[2, 0, 0], [0, 2, 0], [0, 0, 1]])

        dis_mtx = atoms.get_all_distances(mic=True)
        row, col = np.diag_indices_from(dis_mtx)
        dis_mtx[row, col] = np.nan
        min_dis = np.nanmin(dis_mtx)

        volume = float(atoms.get_volume())
        force = np.array(atoms.get_scaled_positions()).tolist()
        energy = np.nan
        stress = [np.nan] * 6
        enthalpy = np.nan

        if min_dis > 0.6:
            atoms.calc = calc
            aim_stress = 1.0 * pstress * 0.01 * 0.6242
            ucf = UnitCellFilter(atoms, scalar_pressure=aim_stress)
            ss = SaveState(atoms)

            opt = LBFGS(ucf, trajectory=mlp_trajname)
            opt.attach(ss, 1, pstress, fmax)

            opt.run(
                fmax=fmax,
                steps=mlp_optstep,
            )
            atoms.center()
            volume = float(atoms.get_volume())
            force = np.array(atoms.get_forces()).tolist()
            max_force = np.linalg.norm(np.array(ucf.get_forces()), axis=1).max()
            energy = float(atoms.get_potential_energy())
            stress = np.array(
                atoms.get_stress(voigt=True) * 160.21766028
            ).tolist()  # eV/A^3 to GPa
            enthalpy = energy + pstress * volume * 0.01 * 0.6242
            mlp_opt_state = True
            dis_mtx = atoms.get_all_distances(mic=True)
            row, col = np.diag_indices_from(dis_mtx)
            dis_mtx[row, col] = np.nan
            min_dis = np.nanmin(dis_mtx)
            if min_dis < 0.6 or max_force > fmax:
                mlp_opt_state = False
                energy = np.nan
                stress = [np.nan] * 6
                enthalpy = np.nan
        else:
            mlp_opt_state = False
            warnings.warn(f"The minimum distance of two atoms is {min_dis}, too close.")
            atoms.write("traj.traj")

        symbols = atoms.get_chemical_symbols()
        lattice = np.array(atoms.get_cell()).tolist()
        position = np.array(atoms.get_positions()).tolist()

        stop = time.time()
        cost = stop - start

        data["lattice"] = lattice
        data["symbols"] = symbols
        data["cartpos"] = position
        data["force"] = force
        data["volume"] = volume
        data["energy"] = energy
        data["stress"] = stress
        data["enthalpy"] = enthalpy
        data["pullay_stress"] = pstress
        data["opt_setting"] = {}
        data["opt_setting"]["optimizer"] = model
        data["opt_setting"]["fmax"] = fmax
        data["opt_setting"]["mlp_opt_state"] = mlp_opt_state
        data["opt_setting"]["time_consuming"] = cost
        data["opt_setting"]["converge"] = (
            True if np.max(np.abs(force)) <= fmax else False
        )

        with open("caly_opt.pkl", "wb") as f:
            pickle.dump(data, f)

        opt_atoms = Atoms(
            symbols=data.pop("symbols"),
            positions=data.pop("cartpos"),
            cell=data.pop("lattice"),
        )
        sg_calc = SinglePointCalculator(
            opt_atoms,
            energy=data.pop("energy"),
            forces=data.pop("force"),
            stress=data.pop("stress"),
        )
        opt_atoms.calc = sg_calc
        opt_atoms.info = data
        write("caly_opt.xyz", opt_atoms)
        write("CONTCAR", opt_atoms)

        print("opt done! cost ", cost, " seconds.")


class SaveState:
    def __init__(self, atoms):
        self.atoms = atoms
        self.atoms.center()

    def __call__(self, pstress, fmax):
        data = {}
        symbols = self.atoms.get_chemical_symbols()
        lattice = np.array(self.atoms.get_cell()).tolist()
        position = np.array(self.atoms.get_positions()).tolist()

        volume = float(self.atoms.get_volume())
        force = np.array(self.atoms.get_forces()).tolist()
        energy = float(self.atoms.get_potential_energy())
        stress = np.array(self.atoms.get_stress(voigt=True) * 160.21766028).tolist()
        enthalpy = energy + pstress * volume * 0.01 * 0.6242

        data["lattice"] = lattice
        data["symbols"] = symbols
        data["cartpos"] = position
        data["force"] = force
        data["volume"] = volume
        data["energy"] = energy
        data["stress"] = stress
        data["enthalpy"] = enthalpy
        data["pullay_stress"] = pstress
        data["opt_setting"] = {}
        data["opt_setting"]["fmax"] = fmax
        data["opt_setting"]["converge"] = (
            True if np.max(np.abs(force)) <= fmax else False
        )

        with open("caly_opt.pkl", "wb") as f:
            pickle.dump(data, f)

        opt_atoms = Atoms(
            symbols=data.pop("symbols"),
            positions=data.pop("cartpos"),
            cell=data.pop("lattice"),
        )
        sg_calc = SinglePointCalculator(
            opt_atoms,
            energy=data.pop("energy"),
            forces=data.pop("force"),
            stress=data.pop("stress"),
        )
        opt_atoms.calc = sg_calc
        opt_atoms.info = data

        write("caly_opt.xyz", opt_atoms)


if __name__ == "__main__":
    run_opt(
        pstress=0.001,  # GPa
        model="chgnet@0.3.0",
        mlp_trajname="traj.traj",
        fmax=0.01,
        mlp_optstep=100,
        keep_sym=True,
    )
