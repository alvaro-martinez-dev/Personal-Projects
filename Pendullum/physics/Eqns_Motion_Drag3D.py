import numpy as np
from scipy.integrate import cumulative_trapezoid
from scipy.integrate import solve_ivp

from physics.Eqns_Motion_3D import Eqnsmotion


class EqnsmotionDrag(Eqnsmotion):
    # Hereda __init__, position_cm, velocity_cm, energy,
    # theta_angular_accel, equations_of_motion, solver...
    # de Eqnsmotion tal cual, sin reescribir nada.

    def __init__(self, H, M, r, m, l, g=9.81, k_drag=0.0):
        super().__init__(H, M, r, m, l, g)
        self.k_drag = k_drag


    def omega_perp(self, theta, dtheta, dphi):
        wperp = np.sqrt(dtheta**2 + np.sin(theta)**2 * dphi**2)
        k_wperp = self.k_drag * self.A**2 * wperp

        return wperp, k_wperp


    def Q_energy_loss(self,theta,dtheta,dphi):

        _, k_wperp = self.omega_perp(theta, dtheta, dphi)

        Q_theta = -k_wperp * dtheta
        Q_phi = -k_wperp * dphi * np.sin(theta)**2

        return Q_theta, Q_phi


    def energy_drag(self, theta, dtheta, phi, dphi, t):

        # nd = no_drag
        kin_en, pot_en, tot_en_nd = self.energy(theta, dtheta, phi, dphi)

        # dE/dt = sum_i Q_i * q_i_dot = Q_theta*dtheta + Q_phi*dphi
        Q_theta, Q_phi = self.Q_energy_loss(theta,dtheta,dphi)
        disip_power = Q_theta * dtheta + Q_phi * dphi

        energia_perdida = cumulative_trapezoid(-disip_power, x=t, initial=0)

        E0 = tot_en_nd[0]
        tot_en = E0 - energia_perdida

        return kin_en, pot_en, tot_en, E0


    def angular_accel_drag(self, theta, dtheta, dphi):
        # Modified E-L for loss of energy
        # d/dt(\partial L / \partial \cdot{q_i}) - (\partial L / \partial q_i) = Q_i
        if self.I <= 0:
            raise ValueError("Moment of inertia is zero or negative.")
        else:

            #nd = no drag
            ddtheta_nd, ddphi_nd = self.angular_accel(theta,dtheta,dphi)

            Q_theta, Q_phi = self.Q_energy_loss(theta,dtheta,dphi)

            ddtheta = ddtheta_nd + (Q_theta / self.I)
            ddphi = ddphi_nd + (Q_phi / (self.I * np.sin(theta)**2))

            return ddtheta, ddphi


    def equations_of_motion_drag(self, t, y):
    
            theta, dtheta, phi, dphi = y
    
            ddtheta, ddphi = self.angular_accel_drag(theta,dtheta,dphi)
    
            return [dtheta, ddtheta, dphi, ddphi] 


    def solver_drag(self, theta0, dtheta0, phi0, dphi0, t_span, t_eval=None):
    
            y0 = [theta0, dtheta0, phi0, dphi0]
    
            sol = solve_ivp(self.equations_of_motion_drag,t_span,y0,t_eval=t_eval,rtol=1e-9,atol=1e-9)
    
            return sol
