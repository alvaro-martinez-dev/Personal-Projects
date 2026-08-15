import pandas as pd
import numpy as np
from scipy.integrate import solve_ivp

class Eqnsmotion:

    def __init__(self,H,M,r,m,l,g=9.81):
        # H: Height at which the pendulum is attached in the z-axis (wrt to the surface, ie z=0)
        # M: Mass of the ball
        # r: Radius of the ball
        # m: Mass of the string
        # l: Longitude of the string
        # g: Earth's acceleration on the surface

        self.H = H
        self.M = M
        self.r = r
        self.m = m
        self.l = l
        self.g = g
        #A is a geometric value repeated along calculations
        self.A = (self.M*(self.l + self.r) + self.m*self.l/2) / (self.m + self.M) 
        # I is the moment of inertia
        self.I_ball = self.M*(self.l+self.r)**2 + (2/5)*self.M*self.r**2
        self.I_string = (1/3)*self.m*self.l**2
        self.I = self.I_ball + self.I_string


    def position_cm(self,theta,phi):
        # Function that computes the center of mass position. 
        # Assume initially that we only work on the y-z plane. 

        x_cm = self.A*np.cos(phi)*np.sin(theta)
        y_cm = self.A*np.sin(phi)*np.sin(theta)
        z_cm = self.H - self.A*np.cos(theta)

        return x_cm, y_cm, z_cm


    def velocity_cm(self,theta,dtheta,phi,dphi):
        # Function that computes cm velocity

        dx_cm = self.A*np.cos(phi)*dtheta*np.cos(theta) - self.A*dphi*np.sin(phi)*np.sin(theta)
        dy_cm = self.A*np.sin(phi)*dtheta*np.cos(theta) + self.A*dphi*np.cos(phi)*np.sin(theta)
        dz_cm = self.A*dtheta*np.sin(theta)

        return dx_cm, dy_cm, dz_cm


    def energy(self,theta,dtheta,phi,dphi):
        # Kinetic energy and potential energy

        kin_en = 0.5*self.I*(dtheta**2 + dphi**2)

        _, _, z_cm = self.position_cm(theta,phi)
        pot_en = (self.m + self.M)*self.g*z_cm

        total_en = kin_en + pot_en

        lagrangian = kin_en - pot_en

        return kin_en, pot_en, total_en, lagrangian


    def theta_angular_accel(self,theta):

        if self.I <= 0:
            raise ValueError("Moment of inertia is zero or negative.")
        else:
            return (-(self.m + self.M)*self.A*self.g*np.sin(theta)) / self.I
            
        
    def equations_of_motion(self, t, y):

        theta, dtheta, phi, dphi = y

        ddtheta = self.theta_angular_accel(theta)
        ddphi = 0.0

        return [dtheta, ddtheta, dphi, ddphi]


    def solver(self, theta0, dtheta0, phi0, dphi0, t_span, t_eval=None):

        y0 = [theta0, dtheta0, phi0, dphi0]

        sol = solve_ivp(self.equations_of_motion,t_span,y0,t_eval=t_eval,rtol=1e-9,atol=1e-9)

        return sol