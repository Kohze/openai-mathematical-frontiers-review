"""Exact checks of elementary review illustrations, not proofs of release claims."""
from fractions import Fraction
from pathlib import Path
import json

PAPER = Path(__file__).resolve().parents[1]


def gf4_mul(a, b):
    result = 0
    for _ in range(2):
        if b & 1:
            result ^= a
        b >>= 1
        a <<= 1
        if a & 4:
            a ^= 7  # x^2+x+1
    return result


def main():
    full = punctured = 0
    values = []
    for t in range(4):
        square = gf4_mul(1 ^ t, 1 ^ t)
        values.append(square)
        full ^= square
        if t:
            punctured ^= square
    if full != 0 or punctured != 1:
        raise RuntimeError("Finite-field illustration failed")
    # z=x*Ax for A=[[0,2],[0,0]], ||x||=1, is bounded by 2|x1||x2|<=1.
    # On real unit vectors the equality x1=x2 is witnessed algebraically:
    real_squared_product_at_equality = 4 * Fraction(1, 2) * Fraction(1, 2)
    if real_squared_product_at_equality != 1:
        raise RuntimeError("Jordan numerical-range illustration failed")
    # Hessian of x1*x4+x2*x3: H^2=I and trace(H)=0 give two +1 and two -1 eigenvalues.
    hessian = [[0, 0, 0, 1], [0, 0, 1, 0], [0, 1, 0, 0], [1, 0, 0, 0]]
    square = [[sum(hessian[i][k]*hessian[k][j] for k in range(4))
               for j in range(4)] for i in range(4)]
    identity = [[int(i == j) for j in range(4)] for i in range(4)]
    if square != identity or sum(hessian[i][i] for i in range(4)):
        raise RuntimeError("Common-base Hessian illustration failed")
    # Exact eigenpairs of the four-state negative generator, including the
    # reducible boundary. This checks the full operator, not just a variance formula.
    states = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    state_index = {state: i for i, state in enumerate(states)}
    chain_checks = []
    for tau in (Fraction(0), Fraction(1, 8), Fraction(1), Fraction(2)):
        operator = [[Fraction(0) for _ in states] for _ in states]
        for i, (a, b) in enumerate(states):
            operator[i][i] = 1 + tau
            operator[i][state_index[(-a, b)]] = -1
            operator[i][state_index[(a, -b)]] = -tau
        basis = [[1 for _ in states], [a for a, b in states],
                 [b for a, b in states], [a*b for a, b in states]]
        eigenvalues = [0, 2, 2*tau, 2*(1+tau)]
        for vector, value in zip(basis, eigenvalues):
            image = [sum(operator[i][j]*vector[j] for j in range(4)) for i in range(4)]
            if image != [value*v for v in vector]:
                raise RuntimeError("Restricted-observable generator eigenpair failed")
        chain_checks.append({"tau": str(tau), "eigenvalues": [str(x) for x in eigenvalues],
                             "restricted_energy_for_first_coordinate": "2",
                             "second_coordinate_energy": str(2*tau), "passed": True})
    def mesh_polynomial(t):
        return (t-Fraction(1, 2))**2-Fraction(1, 16)
    mesh_values = [mesh_polynomial(Fraction(t)) for t in (0, 1)]
    midpoint_value = mesh_polynomial(Fraction(1, 2))
    if mesh_values != [Fraction(3, 16), Fraction(3, 16)] or midpoint_value != -Fraction(1, 16):
        raise RuntimeError("Finite mesh versus continuum illustration failed")
    residue_checks = []
    for prime in (2, 3, 5, 7, 11, 13):
        for shift in range(2*prime):
            centered_first = [Fraction(int(u == 0))-Fraction(1, prime) for u in range(prime)]
            centered_shift = [Fraction(int((u+shift) % prime == 0))-Fraction(1, prime) for u in range(prime)]
            shared = sum(a*b for a, b in zip(centered_first, centered_shift))/prime
            independently_resampled = sum(a*b for a in centered_first for b in centered_shift)/(prime*prime)
            stated = Fraction(prime-1 if shift % prime == 0 else -1, prime*prime)
            if shared != stated or independently_resampled != 0:
                raise RuntimeError("Shared versus independently resampled prime residue failed")
            residue_checks.append({"p": prime, "h": shift, "shared_covariance": str(shared),
                                   "independent_covariance": "0", "passed": True})
    result = {
        "scope": "Elementary exposition checks; release theorems are separate",
        "gf4": {"encoding": "0,1,alpha,1+alpha", "squared_interpolant_values": values,
                "full_sum": full, "punctured_sum": punctured, "passed": True},
        "jordan_example": {"matrix": [[0, 2], [0, 0]], "operator_norm": 2,
                           "numerical_radius": 1, "squared_radius_witness": "1", "passed": True},
        "common_base_hessian": {"matrix": hessian, "square_is_identity": True,
                                "trace": 0, "eigenvalues": [1, 1, -1, -1], "passed": True},
        "restricted_observable_chain": {"checks": chain_checks, "passed": True},
        "finite_mesh": {"h": "1", "node_values": [str(x) for x in mesh_values],
                        "midpoint_value": str(midpoint_value), "passed": True},
        "shared_residue_pair": {"checks": residue_checks, "passed": True}
    }
    (PAPER / "audit").mkdir(exist_ok=True)
    (PAPER / "audit/illustrative-examples.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
