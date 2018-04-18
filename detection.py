import numpy as np
from initialize import *


def multivariate_gaussian(x, meu, cov):
    """calculates multivariate gaussian matrix from mean and covariance matrices"""
    det = np.linalg.det(cov)
    val = np.exp(-0.5 * np.dot(np.dot((x - meu).T, np.linalg.inv(cov)), (x - meu)))
    try:
        val /= np.sqrt(((2 * np.pi) ** 12) * det)
    except:
        print('Matrix is not positive, semi-definite')
    if np.isnan(val):
        val = np.finfo(float).eps
    return val


def initialize(chroma, templates, nested_cof):
    """initialising PI with equal probabilities"""
    """initialize the emission, transition and initialisation matrices for HMM in chord recognition
    PI - initialisation matrix, #A - transition matrix, #B - observation matrix"""
    PI = np.ones(24) / 24
    """initialising A based on nested circle of fifths"""
    eps = 0.01
    A = np.empty((24, 24))
    for chord in chords:
        ind = nested_cof.index(chord)
        t = ind
        for i in range(24):
            if t >= 24:
                t = t % 24
            A[ind][t] = (abs(12 - i) + eps) / (144 + 24 * eps)
            t += 1

    """initialising based on tonic triads - Mean matrix; Tonic with dominant - 0.8,
    tonic with mediant 0.6 and mediant-dominant 0.8, non-triad diagonal	elements 
    with 0.2 - covariance matrix"""

    nFrames = np.shape(chroma)[1]
    B = np.zeros((24, nFrames))
    meu_mat = np.zeros((24, 12))
    cov_mat = np.zeros((24, 12, 12))
    meu_mat = np.array(templates)
    offset = 0

    for i in range(24):
        if i == 12:
            offset = 0
        tonic = offset
        if i < 12:
            mediant = (tonic + 4) % 12
        else:
            mediant = (tonic + 3) % 12
        dominant = (tonic + 7) % 12

        # weighted diagonal
        cov_mat[i, tonic, tonic] = 0.8
        cov_mat[i, mediant, mediant] = 0.6
        cov_mat[i, dominant, dominant] = 0.8

        # off-diagonal - matrix not positive semidefinite, hence determinant is negative
        # for n in [tonic,mediant,dominant]:
        # 	for m in [tonic, mediant, dominant]:
        # 		if (n is tonic and m is mediant) or (n is mediant and m is tonic):
        # 			cov_mat[i,n,m] = 0.6
        # 		else:
        # 			cov_mat[i,n,m] = 0.8

        # filling non zero diagonals
        for j in range(12):
            if cov_mat[i, j, j] == 0:
                cov_mat[i, j, j] = 0.2
        offset += 1

    """observation matrix B is a multivariate Gaussian calculated from mean vector and 
    covariance matrix"""

    for m in range(nFrames):
        for n in range(24):
            B[n, m] = multivariate_gaussian(chroma[:, m], meu_mat[n, :], cov_mat[n, :, :])

    return PI, A, B


def viterbi(PI, A, B):
    """Viterbi algorithm to find Path with highest probability - dynamic programming"""
    (nrow, ncol) = np.shape(B)
    path = np.zeros((nrow, ncol))
    states = np.zeros((nrow, ncol))
    path[:, 0] = PI * B[:, 0]

    for i in range(1, ncol):
        for j in range(nrow):
            s = [(path[k, i - 1] * A[k, j] * B[j, i], k) for k in range(nrow)]
            (prob, state) = max(s)
            path[j, i] = prob
            states[j, i - 1] = state

    return path, states
