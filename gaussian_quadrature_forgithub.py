"""
Class for integration (1D and 2D) using Gaussian Quadrature. 
The docstrings were not written by me, but the code was.
"""

import numpy as np
from scipy import linalg


class GaussianQuadrature:
    """Class for integrating functions on arbitrary intervals using Gaussian
    quadrature with the Legendre polynomials or the Chebyshev polynomials.
    """
    # Problems 1 and 3
    def __init__(self, n, polytype="legendre"):
        """Calculate and store the n points and weights corresponding to the
        specified class of orthogonal polynomial (Problem 3). Also store the
        inverse weight function w(x)^{-1} = 1 / w(x).

        Parameters:
            n (int): Number of points and weights to use in the quadrature.
            polytype (string): The class of orthogonal polynomials to use in
                the quadrature. Must be either 'legendre' or 'chebyshev'.

        Raises:
            ValueError: if polytype is not 'legendre' or 'chebyshev'.
        """
        if polytype not in {"legendre", "chebyshev"}:
            raise ValueError("You must enter 'chebyshev' or 'legendre'.")

        if polytype == "legendre":  # If you have a Legendre Polynomial
            self.w_reciprical = lambda x : 1
        else:                       # If you have a Chebyshev Polynomial
            self.w_reciprical = lambda x : np.sqrt(1 - x**2)

        self.label = polytype
        self.n = n

        self.xint, self.weights = self.points_weights(n) # Defines the x intercept points and weights

    def points_weights(self, n):
        """Calculate the n points and weights for Gaussian quadrature.

        Parameters:
            n (int): The number of desired points and weights.

        Returns:
            points ((n,) ndarray): The sampling points for the quadrature.
            weights ((n,) ndarray): The weights corresponding to the points.
        """
        if self.label == "legendre": # Case for legendre polynomials
            alpha = np.zeros(n)
            beta = (np.arange(1,n)**2)/(4*np.arange(1,n)**2 - 1)
            measure = 2
        else:                        # Case for chebyshev polynomials
            alpha = np.zeros(n)
            beta = np.full(n-1, 1/4)
            beta[0] = 1/2
            measure = np.pi

        offsets = [-1,0,1]
        diagonals = [np.sqrt(beta), alpha, np.sqrt(beta)] # Defines the diagonal entries

        J = np.diag(diagonals[0], offsets[0]) \
        + np.diag(diagonals[1], offsets[1]) \
        + np.diag(diagonals[2], offsets[2]) # Defines the Jacobi
        # print(J)

        evals, evecs = linalg.eig(J)
        x = np.real(evals) # Gets the x intercepts
        w = measure*np.real(evecs[0,:])**2 # Gets the weights

        return x, w


    def basic(self, f):
        """Approximate the integral of a f on the interval [-1,1]."""
        g = lambda x : f(x) * self.w_reciprical(x) # Calculates g
        return np.sum(g(self.xint)*self.weights) # Calculates the integral approximation

    def integrate(self, f, a, b):
        """Approximate the integral of a function on the interval [a,b].

        Parameters:
            f (function): Callable function to integrate.
            a (float): Lower bound of integration.
            b (float): Upper bound of integration.

        Returns:
            (float): Approximate value of the integral.
        """
        h = lambda x : f(x*(b-a)/2 + (b+a)/2) # Gets function from change of variables
        return ((b-a)/2)*self.basic(h)

    def integrate2d(self, f, a1, b1, a2, b2):
        """Approximate the integral of the two-dimensional function f on
        the interval [a1,b1]x[a2,b2].

        Parameters:
            f (function): A function to integrate that takes two parameters.
            a1 (float): Lower bound of integration in the x-dimension.
            b1 (float): Upper bound of integration in the x-dimension.
            a2 (float): Lower bound of integration in the y-dimension.
            b2 (float): Upper bound of integration in the y-dimension.

        Returns:
            (float): Approximate value of the integral.
        """
        h = lambda x, y: f(x*(b1 - a1)/2 + (a1 + b1)/2, y*(b2 - a2)/2 + (a2 + b2)/2)
        g = lambda x, y: h(x,y)*self.w_reciprical(x)*self.w_reciprical(y)

        total = 0
        for i, _ in enumerate(self.weights):
            # Calculates the total by adding up the inner sums
            total += np.sum(self.weights[i]*self.weights*g(np.full_like(self.xint, self.xint[i]),self.xint))
        return total*(b1 - a1)*(b2 - a2)/4 # Multiplies by the change of variable constant
