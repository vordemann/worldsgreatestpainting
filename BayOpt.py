import numpy as np
import scipy.stats
from matplotlib import pyplot as plt
import GPy;
import GPyOpt
from random import randint, choice
import bayesianUI

def f_u(x):
    # plt.figure(1)
    print(x)
    # im = x.reshape(1, 1, 3).repeat(3, axis=0).repeat(3, axis=1)
    # plt.imshow(im)
    # plt.show(block=False)
    # while True:
    #     res = input('Grade? (1 to 5) ')
    #     if res in ['1', '2', '3', '4', '5']:
    #         res = int(res)
    #         # plt.close(1)
    #         return res
    while True:
        # res = input('Grade? (1 to 5) ')
        if res in ['1', '2', '3', '4', '5']:
            #if(bayesianUI.process)
            res = int(res)
            # plt.close(1)
            return res


def run_bo(max_iter):
    bounds = [{'name': 'R', 'type': 'continuous', 'domain': (0, 1)},
              {'name': 'G', 'type': 'continuous', 'domain': (0, 1)},
              {'name': 'B', 'type': 'continuous', 'domain': (0, 1)},
              {'name': 'color_hue', 'type': 'continuous', 'domain': (0, 2*np.pi)},
              {'name': 'brush_radius', 'type': 'continuous', 'domain': (0.1, 100)},
              {'name': 'blur_radius', 'type': 'continuous', 'domain': (0.1, 100)},
              {'name': 'point_bool', 'type': 'categorical', 'domain': (0, 1)},
              {'name': 'tune_balance', 'type': 'continuous', 'domain': (0, 100)},
              {'name': 'shadow_hue', 'type': 'continuous', 'domain': (0, 360)},
              {'name': 'highlight_hue', 'type': 'continuous', 'domain': (0, 360)},
              {'name': 'shadow_sat', 'type': 'continuous', 'domain': (0, 100)},
              {'name': 'highlight_sat', 'type': 'continuous', 'domain': (0, 100)},
              {'name': 'distort_horiz', 'type': 'continuous', 'domain': (0, 20)},
              {'name': 'distort_vert', 'type': 'continuous', 'domain': (0, 20)}
              ]
    myBopt = GPyOpt.methods.BayesianOptimization(
        f=f_u, domain=bounds,
        acquisition_type='EI',
        exact_feval=False,
        eps=1e-6,
        normalize_Y=False,
        initial_design_numdata=2,
        maximize=True)
    myBopt.run_optimization(max_iter=max_iter - 2)

    return myBopt


def run_random(max_iter):
    xs = np.zeros((max_iter, 14)) #don't hardcode this
    ys = np.zeros((max_iter,))

    for i in range(max_iter):
        xs[i, :] = np.hstack((np.random.rand(3), 2*np.pi*np.random.rand(1), (100-0.1)*np.random.rand(1),
                                   (100-0.1)*np.random.rand(1), np.array(np.random.randint(2)), 100*np.random.rand(1),
                                   360*np.random.rand(1), 360*np.random.rand(1), 100*np.random.rand(1),
                                   100*np.random.rand(1), 20*np.random.rand(1), 20*np.random.rand(1)))
        ys[i] = f_u(xs[i, :])

    return xs, ys


def initBayOpt():
    n_iter = 20
    # run BO
    bo = run_bo(n_iter)
    # run random for comparison
    # ra = run_random(n_iter)

    bo_xs, bo_ys = bo.get_evaluations()
    # ra_xs, ra_ys = ra

    # one can investigate these to see how good colors were found and compare
    # to a ground truth color

    plt.plot(-bo_ys, 'k-', label='BO')
    # plt.plot(ra_ys, 'r-', label='Random')
    plt.xlabel('iterations')
    plt.ylabel('grades')
    plt.legend()
    plt.show()

    # let's say ground truth color was red
    # x_gt = np.array([1.0, 0.0, 0.0])
    x_gt = np.array([1.0, 0.0, 0.0, np.pi, 50, 50, 0, 50, 180, 180, 180, 50, 10, 10]) # now hardcoded, later randomize


    # plt.plot(np.sqrt(np.sum((bo_xs - x_gt) ** 2, 1)), 'k-', label='BO')
    # plt.plot(np.sqrt(np.sum((ra_xs - x_gt) ** 2, 1)), 'r-', label='Random')
    # plt.xlabel('iterations')
    # plt.ylabel('distance from ground truth')
    # plt.legend()
    # plt.show()
