#!/usr/bin/env python
import os
import time
import pickle

import numpy as np
from ase import Atoms
from ase.io import read, write
from ase.calculators.singlepoint import SinglePointCalculator


def run_opt(pstress, model, mlp_trajname, fmax, mlp_optstep):
    # pstress: GPa
    # 1 eV/A^3 = 160.21766028 GPa
    # 1 / 160.21766028 ~ 0.006242

    print("Start to Optimize Structures using ", model)
    data = {}
    start = time.time()

    atoms = read("caly_ini.xyz")
    atoms.center()
    aim_stress = 1.0 * pstress* 0.01 * 0.6242
    lattice = np.array(atoms.get_cell()).tolist()
    position = np.array(atoms.get_positions())
    force = np.empty(position.shape) + np.nan

    volume = float(atoms.get_volume())
    energy = float(np.nan)
    symbols = atoms.get_chemical_symbols()
    stress = np.array([])

    enthalpy = float(np.nan)

    stop = time.time()
    cost = stop - start

    data["lattice"] = lattice
    data["symbols"] = symbols
    data["cartpos"] = position.tolist()
    data["force"] = force.tolist()
    data["volume"] = volume
    data["energy"] = energy
    data["stress"] = stress
    data["enthalpy"] = enthalpy
    data["opt_setting"] = {}
    data["opt_setting"]["optimizer"] = model
    data["opt_setting"]["fmax"] = fmax
    data["opt_setting"]["mlp_opt_state"] = False

    with open("caly_opt.pkl", "wb") as f:
        pickle.dump(data, f)

    opt_atoms = Atoms(symbols=data.pop('symbols'), positions=data.pop('cartpos'), cell=data.pop('lattice'))
    sg_calc = SinglePointCalculator(opt_atoms, energy=data.pop('energy'), forces=data.pop('force'))
    opt_atoms.calc = sg_calc
    opt_atoms.info = data
    write("caly_opt.xyz", opt_atoms)
    write("traj.traj", opt_atoms)

    print("failed", cost, " seconds for optimizing this structures.")
    
if __name__ == "__main__":
    run_opt(
        pstress=0,    # GPa
        model="chgnet@0.3.0",
        mlp_trajname="traj.traj",
        fmax=0.1,
        mlp_optstep=100,
    )
