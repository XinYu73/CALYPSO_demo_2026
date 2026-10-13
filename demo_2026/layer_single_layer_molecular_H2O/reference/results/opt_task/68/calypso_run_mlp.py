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
from ase.optimize import FIRE

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
        "check_cuda_mem": False,
        "on_isolated_atoms": "warn",
        "stress_weight": 0.006241509125883258,
    },
)


print("Optimization Running with fix Layer Group")
from ase.constraints import FixConstraint
from ase.stress import full_3x3_to_voigt_6_stress, voigt_6_to_full_3x3_stress
import spglib


def prep_symmetry(atoms, layer_group_number=None):
    if layer_group_number is not None:
        dataset = layer_group_information[layer_group_number]
        rotations = [
            np.linalg.inv(dataset["conventional_to_primitive_trans_matrix"])
            @ item[:3, :3]
            @ dataset["conventional_to_primitive_trans_matrix"]
            for item in dataset["affine_matrixes"][0]
        ]
        translations = [
            np.linalg.inv(dataset["conventional_to_primitive_trans_matrix"])
            @ item[:3, -1]
            for item in dataset["affine_matrixes"][0]
        ]
    else:
        dataset = spglib.get_symmetry_dataset(
            (atoms.get_cell(), atoms.get_scaled_positions(), atoms.get_atomic_numbers())
        )
        rotations = dataset["rotations"]
        translations = dataset["translations"]

    symm_map = []
    scaled_pos = atoms.get_scaled_positions()
    for rot, trans in zip(rotations, translations):
        this_op_map = [-1] * len(atoms)
        for i_at in range(len(atoms)):
            new_p = rot @ scaled_pos[i_at, :] + trans
            dp = scaled_pos - new_p
            dp -= np.round(dp)
            i_at_map = np.argmin(np.linalg.norm(dp, axis=1))
            this_op_map[i_at] = i_at_map
        symm_map.append(this_op_map)
    return (rotations, translations, symm_map)


def symmetrize_rank1(lattice, inv_lattice, forces, rot, trans, symm_map):
    scaled_symmetrized_forces_T = np.zeros(forces.T.shape)

    scaled_forces_T = np.dot(inv_lattice.T, forces.T)
    for r, t, this_op_map in zip(rot, trans, symm_map):
        transformed_forces_T = np.dot(r, scaled_forces_T)
        scaled_symmetrized_forces_T[:, this_op_map] += transformed_forces_T
    scaled_symmetrized_forces_T /= len(rot)
    symmetrized_forces = (lattice.T @ scaled_symmetrized_forces_T).T

    return symmetrized_forces


def symmetrize_rank2(lattice, lattice_inv, stress_3_3, rot):
    scaled_stress = np.dot(np.dot(lattice, stress_3_3), lattice.T)

    symmetrized_scaled_stress = np.zeros((3, 3))
    for r in rot:
        symmetrized_scaled_stress += np.dot(np.dot(r.T, scaled_stress), r)
    symmetrized_scaled_stress /= len(rot)

    sym = np.dot(np.dot(lattice_inv, symmetrized_scaled_stress), lattice_inv.T)
    return sym


class FixSymmetryLayer(FixConstraint):
    def __init__(
        self,
        atoms,
        symprec=0.01,
        layer_group_number=None,
        adjust_positions=True,
        adjust_cell=True,
        verbose=False,
    ):
        self.atoms = atoms.copy()
        self.symprec = symprec
        self.verbose = verbose
        sym = prep_symmetry(atoms, layer_group_number)
        self.rotations, self.translations, self.symm_map = sym
        self.do_adjust_positions = adjust_positions
        self.do_adjust_cell = adjust_cell

    def adjust_cell(self, atoms, cell):
        if not self.do_adjust_cell:
            return
        # stress should definitely be symmetrized as a rank 2 tensor
        # UnitCellFilter uses deformation gradient as cell DOF with steps
        # dF = stress.F^-T quantity that should be symmetrized is therefore dF .
        # F^T assume prev F = I, so just symmetrize dF
        cur_cell = atoms.get_cell()
        cur_cell_inv = atoms.cell.reciprocal().T

        # F defined such that cell = cur_cell . F^T
        # assume prev F = I, so dF = F - I
        delta_deform_grad = np.dot(cur_cell_inv, cell).T - np.eye(3)

        # symmetrization doesn't work properly with large steps, since
        # it depends on current cell, and cell is being changed by deformation
        # gradient
        max_delta_deform_grad = np.max(np.abs(delta_deform_grad))
        if max_delta_deform_grad > 0.25:
            raise RuntimeError(
                "FixSymmetry adjust_cell does not work properly"
                " with large deformation gradient step {} > 0.25".format(
                    max_delta_deform_grad
                )
            )
        elif max_delta_deform_grad > 0.15:
            warnings.warn(
                "FixSymmetry adjust_cell may be ill behaved with"
                " large deformation gradient step {}".format(max_delta_deform_grad)
            )

        symmetrized_delta_deform_grad = symmetrize_rank2(
            cur_cell, cur_cell_inv, delta_deform_grad, self.rotations
        )
        cell[:] = np.dot(cur_cell, (symmetrized_delta_deform_grad + np.eye(3)).T)

    def adjust_positions(self, atoms, new):
        if not self.do_adjust_positions:
            return
        # symmetrize changes in position as rank 1 tensors
        step = new - atoms.positions
        symmetrized_step = symmetrize_rank1(
            atoms.get_cell(),
            atoms.cell.reciprocal().T,
            step,
            self.rotations,
            self.translations,
            self.symm_map,
        )
        new[:] = atoms.positions + symmetrized_step

    def adjust_forces(self, atoms, forces):
        # symmetrize forces as rank 1 tensors
        # print('adjusting forces')
        forces[:] = symmetrize_rank1(
            atoms.get_cell(),
            atoms.cell.reciprocal().T,
            forces,
            self.rotations,
            self.translations,
            self.symm_map,
        )

    def adjust_stress(self, atoms, stress):
        # symmetrize stress as rank 2 tensor
        raw_stress = voigt_6_to_full_3x3_stress(stress)
        symmetrized_stress = symmetrize_rank2(
            atoms.get_cell(), atoms.cell.reciprocal().T, raw_stress, self.rotations
        )
        stress[:] = full_3x3_to_voigt_6_stress(symmetrized_stress)

    def index_shuffle(self, atoms, ind):
        if len(atoms) != len(ind) or len(set(ind)) != len(ind):
            raise RuntimeError(
                "FixSymmetry can only accomodate atom"
                " permutions, and len(Atoms) == {} "
                "!= len(ind) == {} or ind has duplicates".format(len(atoms), len(ind))
            )

        ind_reversed = np.zeros((len(ind)), dtype=int)
        ind_reversed[ind] = range(len(ind))
        new_symm_map = []
        for sm in self.symm_map:
            new_sm = np.array([-1] * len(atoms))
            for at_i in range(len(ind)):
                new_sm[ind_reversed[at_i]] = ind_reversed[sm[at_i]]
            new_symm_map.append(new_sm)

        self.symm_map = new_symm_map

    def todict(self):
        return {
            "name": "FixSymmetryLayer",
            "kwargs": {
                "atoms": self.atoms,
                "symprec": self.symprec,
                "adjust_positions": self.do_adjust_positions,
                "adjust_cell": self.do_adjust_cell,
                "verbose": self.verbose,
            },
        }


def run_opt(pstress, model, mlp_trajname, fmax, mlp_optstep, layer_group_number=None):
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
        atoms.set_constraint(FixSymmetryLayer(atoms, layer_group_number))

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
            ucf = UnitCellFilter(
                atoms,
                scalar_pressure=aim_stress,
                mask=[[1, 1, 1], [1, 1, 1], [0, 0, 0]],
            )
            ss = SaveState(atoms)

            opt = FIRE(ucf, trajectory=mlp_trajname)
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
        mlp_optstep=1000,
        layer_group_number=None,
    )
