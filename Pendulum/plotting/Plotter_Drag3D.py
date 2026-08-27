import numpy as np
import matplotlib.pyplot as plt

from plotting.Plotter_3D import PlotMotion


class PlotMotionDrag(PlotMotion):
    # Hereda plot_angle, plot_angular_velocity, plot_trajectory,
    # summary, animate... de PlotMotion tal cual.
    # Solo sobreescribe lo relacionado con energia (para usar energy_drag)
    # y anade metodos de comparacion drag vs no-drag.

    def __init__(self, eqns, sol):
        # eqns: instancia de EqnsmotionDrag
        # sol: solucion devuelta por eqns.solver_drag()
        super().__init__(eqns, sol)

        # Sobreescribimos la energia calculada por el __init__ del padre
        # (que usa self.eqns.energy(), sin rozamiento) por la version
        # con rozamiento.
        (self.kin_en,self.pot_en,self.total_en,self.E0,
         ) = self.eqns.energy_drag(
            self.theta,self.dtheta,self.phi,self.dphi,self.t)

    # ---------------------------------------------------------
    # ENERGY (override): misma pinta que el padre, pero anadiendo
    # una linea de referencia en E0 para ver visualmente cuanto
    # se ha disipado.
    # ---------------------------------------------------------

    def plot_energy(self, ax=None, show=True):

        created_fig = ax is None

        if created_fig:
            fig, ax = plt.subplots(figsize=(8, 4.5))

        ax.plot(self.t, self.kin_en, label="Kinetic energy")
        ax.plot(self.t, self.pot_en, label="Potential energy")
        ax.plot(self.t, self.total_en, label="Total energy", linestyle="--")

        ax.axhline(
            self.E0,
            color="gray",
            linestyle=":",
            linewidth=1,
            label="E0 (no drag)",
        )

        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Energy (J)")
        ax.set_title("Energy vs time (with drag)")

        ax.legend()
        ax.grid(False)

        if created_fig:
            fig.tight_layout()

            if show:
                plt.show()

            return fig, ax

    # ---------------------------------------------------------
    # COMPARISON PLOTS
    # ---------------------------------------------------------

    def plot_energy_comparison(
        self,
        other,
        label_self="Con rozamiento",
        label_other="Sin rozamiento",
        ax=None,
        show=True,
    ):
        """
        Superpone la energia total de esta simulacion (con rozamiento)
        con la de otra (tipicamente un PlotMotion sin rozamiento, o
        un PlotMotionDrag con k_drag=0 como test de sanidad).
        """

        created_fig = ax is None

        if created_fig:
            fig, ax = plt.subplots(figsize=(8, 4.5))

        ax.plot(self.t, self.total_en, label=label_self)
        ax.plot(other.t, other.total_en, label=label_other, linestyle="--")

        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Energy (J)")
        ax.set_title("Energy comparison")

        ax.legend()
        ax.grid(False)

        if created_fig:
            fig.tight_layout()

            if show:
                plt.show()

            return fig, ax

    def plot_angle_comparison(
        self,
        other,
        label_self="Con rozamiento",
        label_other="Sin rozamiento",
        ax=None,
        show=True,
    ):
        """
        Superpone theta(t) de esta simulacion con la de otra.
        Es donde mas se nota visualmente el efecto del rozamiento
        (decaimiento de amplitud).
        """

        created_fig = ax is None

        if created_fig:
            fig, ax = plt.subplots(figsize=(8, 4.5))

        ax.plot(self.t, self.theta, label=f"theta ({label_self})")
        ax.plot(
            other.t,
            other.theta,
            label=f"theta ({label_other})",
            linestyle="--",
        )

        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Theta (rad)")
        ax.set_title("Angle comparison")

        ax.legend()
        ax.grid(False)

        if created_fig:
            fig.tight_layout()

            if show:
                plt.show()

            return fig, ax

    def summary_comparison(self, other, show=True):
        """
        Combina angle_comparison y energy_comparison en una sola figura,
        mas la trayectoria 3D propia (con rozamiento) para referencia.
        """

        fig = plt.figure(figsize=(12, 8))

        ax1 = fig.add_subplot(2, 2, 1)
        ax2 = fig.add_subplot(2, 2, 2)
        ax3 = fig.add_subplot(2, 2, (3, 4), projection="3d")

        self.plot_angle_comparison(other, ax=ax1, show=False)
        self.plot_energy_comparison(other, ax=ax2, show=False)
        self.plot_trajectory(ax=ax3, show=False)

        fig.tight_layout()

        if show:
            plt.show()

        return fig