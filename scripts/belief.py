import numpy as np
from scipy.stats import multivariate_normal
from sympy import *
from sympy.geometry import *


class Belief():
    def __init__(self, mu=None, cov=None, particles = [], walls = [], action=None, siblings=[]):
        n_particles = 5
        if mu is None:
            assert(particles is not None)
            assert(isinstance(particles[0], Particle))
            particle_poses = np.vstack([part.pose for part in particles])
            mu = np.mean(particle_poses, axis = 0)
            cov = np.cov(particle_poses)
            self.particles = particles
        if len(particles) == 0:
            assert mu is not None
            mvn = multivariate_normal(mean=mu, cov=cov)
            self.particles = [Particle(mvn.rvs()) for n in range(n_particles)]
            mu = mvn.mean
            cov = mvn.cov
        self.walls = walls
        self._mean = mu
        self.connected = False
        self._cov = cov
        self.action = action
        self.siblings = siblings
    def mean(self):
        return self._mean
    def siblings(self):
        return self.siblings()
    def cov(self):
        return self._cov
    def get_action(self):
        return self.action
    """
    Check for inconsistencies in the belief state representation,
    - all q must be in free space OR in contact with the same pair of surfaces
    - if there are contacts, the contact must be in a link with a contact sensor (null for pt robot)
    """
    def is_valid(self):
        return not self.any_collisions()

    def any_collisions(self):
        return bool(len(self.find_collisions().keys()))
    """
    walls that collide with some number of particles. 
    A collision is NOT the same as a contact. Contacts are expected and planned for
    dict mapping wall with particles
    """
    def find_collisions(self):
        wall_i_to_colliding_parts = {}
        for wall, i in zip(self.walls, range(len(self.walls))):
            parts_in_collision = wall.get_particles_in_collision(self)
            for part in parts_in_collision:
                if wall.endpoints not in part.world_contact_surfaces():
                    if i not in wall_i_to_colliding_parts.keys():
                        wall_i_to_colliding_parts[i] = [part]
                    else:
                        wall_i_to_colliding_parts[i].append(part)
        return wall_i_to_colliding_parts


class Wall():
    """
    line going from e1 to e2
    """
    def __init__(self, e1, e2):
        self.line = Line(Point(*e1), Point(*e2))
        self.endpoints = (e1, e2)
    """
    if there is a 96% probability that the belief will 
    coincide with the line 
    returns idxs
    """
    def get_particles_in_collision(self, belief):
        #start integrating from the center out
        def func(pt):
            #inside_wall = #on opposite side of wall, best we have now is mean is on the
            #side inside. Does pt cross line?
            seg = Segment(Point(*belief.mean()), pt)
            inside_wall = bool(len(intersection(seg, self.line)))
            return int(inside_wall)
        parts_in_collision = [part for part in belief.particles if func(part.pose)]
        return parts_in_collision


class Particle():
    def __init__(self, pose):
        self.pose = pose
        self.contacts = [] #tuples of (robot_surface, world_surface)
    def world_contact_surfaces(self):
        return [x[1] for x in self.contacts]

