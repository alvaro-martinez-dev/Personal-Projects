import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation


class PlotMotion:
    # Class to visualize the results produced by an Eqnsmotion instance
    # together with the solution returned by its solver method.

    def __init__(self, eqns, sol):
        # eqns: instance of Eqnsmotion
        # sol: solution object returned by eqns.solver()
        # sol.y = [theta, dtheta, phi, dphi]

        self.eqns = eqns
        self.sol = sol

        self.t = sol.t

        # Angular variables
        self.theta = sol.y[0]
        self.dtheta = sol.y[1]
        self.phi = np.mod(sol.y[2], 2 * np.pi)
        self.dphi = sol.y[3]

        # Center of mass position
        self.x_cm, self.y_cm, self.z_cm = self.eqns.position_cm(
            self.theta,
            self.phi
        )

        # Energy
        (
            self.kin_en,
            self.pot_en,
            self.total_en
        ) = self.eqns.energy(
            self.theta,
            self.dtheta,
            self.phi,
            self.dphi
        )

    # ---------------------------------------------------------
    # ANGLES
    # ---------------------------------------------------------

    def plot_angle(self, ax=None, show=True):
        """
        Plot theta and phi as functions of time.
        """

        created_fig = ax is None

        if created_fig:
            fig, ax = plt.subplots(figsize=(8, 4.5))

        ax.plot(
            self.t,
            self.theta,
            label=r"$\theta$ (rad)"
        )

        ax.plot(
            self.t,
            self.phi,
            label=r"$\phi$ (rad)"
        )

        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Angle (rad)")
        ax.set_title("Angular coordinates")

        ax.legend()
        ax.grid(False)

        if created_fig:
            fig.tight_layout()

            if show:
                plt.show()

            return fig, ax

    # ---------------------------------------------------------
    # ANGULAR VELOCITIES
    # ---------------------------------------------------------

    def plot_angular_velocity(self, ax=None, show=True):
        """
        Plot dtheta and dphi as functions of time.
        """

        created_fig = ax is None

        if created_fig:
            fig, ax = plt.subplots(figsize=(8, 4.5))

        ax.plot(
            self.t,
            self.dtheta,
            label=r"$\dot{\theta}$ (rad/s)"
        )

        ax.plot(
            self.t,
            self.dphi,
            label=r"$\dot{\phi}$ (rad/s)"
        )

        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Angular velocity (rad/s)")
        ax.set_title("Angular velocities")

        ax.legend()
        ax.grid(False)

        if created_fig:
            fig.tight_layout()

            if show:
                plt.show()

            return fig, ax

    # ---------------------------------------------------------
    # ENERGY
    # ---------------------------------------------------------

    def plot_energy(self, ax=None, show=True):
        """
        Plot kinetic, potential and total energy.
        """

        created_fig = ax is None

        if created_fig:
            fig, ax = plt.subplots(figsize=(8, 4.5))

        ax.plot(
            self.t,
            self.kin_en,
            label="Kinetic energy"
        )

        ax.plot(
            self.t,
            self.pot_en,
            label="Potential energy"
        )

        ax.plot(
            self.t,
            self.total_en,
            label="Total energy",
            linestyle="--"
        )

        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Energy (J)")
        ax.set_title("Energy vs time")

        ax.legend()
        ax.grid(False)

        if created_fig:
            fig.tight_layout()

            if show:
                plt.show()

            return fig, ax

    # ---------------------------------------------------------
    # 3D TRAJECTORY
    # ---------------------------------------------------------

    def plot_trajectory(self, ax=None, show=True):
        """
        Plot the 3D trajectory of the center of mass.
        """

        created_fig = ax is None

        if created_fig:
            fig = plt.figure(figsize=(7, 6))
            ax = fig.add_subplot(111, projection="3d")

        ax.plot(
            self.x_cm,
            self.y_cm,
            self.z_cm,
            label="CM trajectory"
        )

        # Start point
        ax.scatter(
            self.x_cm[0],
            self.y_cm[0],
            self.z_cm[0],
            label="Start"
        )

        # End point
        ax.scatter(
            self.x_cm[-1],
            self.y_cm[-1],
            self.z_cm[-1],
            label="End"
        )

        # Pivot
        ax.scatter(
            0,
            0,
            self.eqns.H,
            marker="^",
            label="Pivot"
        )

        ax.set_xlabel("x (m)")
        ax.set_ylabel("y (m)")
        ax.set_zlabel("z (m)")
        ax.set_title("Center of mass trajectory")

        ax.legend()

        if created_fig:
            fig.tight_layout()

            if show:
                plt.show()

            return fig, ax

    # ---------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------

    def summary(self, show=True):
        """
        Combine angle, energy and 3D trajectory plots.
        """

        fig = plt.figure(figsize=(12, 8))

        ax1 = fig.add_subplot(2, 2, 1)
        ax2 = fig.add_subplot(2, 2, 2)

        ax3 = fig.add_subplot(
            2,
            2,
            (3, 4),
            projection="3d"
        )

        self.plot_angle(
            ax=ax1,
            show=False
        )

        self.plot_energy(
            ax=ax2,
            show=False
        )

        self.plot_trajectory(
            ax=ax3,
            show=False
        )

        fig.tight_layout()

        if show:
            plt.show()

        return fig

    # ---------------------------------------------------------
    # 3D ANIMATION
    # ---------------------------------------------------------

    def animate(
        self,
        interval=30,
        save_path=None,
        fps=30,
        progress_callback=None
    ):
        """
        Animate the 3D pendulum motion.
        """

        fig = plt.figure(figsize=(7, 6))

        ax = fig.add_subplot(
            111,
            projection="3d"
        )

        # -----------------------------------------------------
        # Axis limits
        # -----------------------------------------------------

        margin = 0.2 * (self.eqns.l + self.eqns.r)

        limit = self.eqns.l + self.eqns.r + margin

        ax.set_xlim(-limit, limit)
        ax.set_ylim(-limit, limit)

        ax.set_zlim(
            self.eqns.H - 2 * limit,
            self.eqns.H + margin
        )

        ax.set_xlabel("x (m)")
        ax.set_ylabel("y (m)")
        ax.set_zlabel("z (m)")

        ax.set_title("3D Pendulum motion")

        # -----------------------------------------------------
        # Pivot
        # -----------------------------------------------------

        pivot_x = 0
        pivot_y = 0
        pivot_z = self.eqns.H

        ax.scatter(
            pivot_x,
            pivot_y,
            pivot_z,
            color="black",
            marker="^",
            zorder=5
        )

        # -----------------------------------------------------
        # Pendulum elements
        # -----------------------------------------------------

        string_line, = ax.plot(
            [],
            [],
            [],
            color="gray",
            lw=1.5
        )

        ball_point, = ax.plot(
            [],
            [],
            [],
            "o",
            color="tab:blue",
            markersize=12
        )

        trace_line, = ax.plot(
            [],
            [],
            [],
            color="tab:blue",
            alpha=0.3,
            lw=1
        )

        # -----------------------------------------------------
        # Initialization
        # -----------------------------------------------------

        def init():

            string_line.set_data([], [])
            string_line.set_3d_properties([])

            ball_point.set_data([], [])
            ball_point.set_3d_properties([])

            trace_line.set_data([], [])
            trace_line.set_3d_properties([])

            return (
                string_line,
                ball_point,
                trace_line
            )

        # -----------------------------------------------------
        # Frame update
        # -----------------------------------------------------

        def update(frame):

            x = self.x_cm[frame]
            y = self.y_cm[frame]
            z = self.z_cm[frame]

            # String / rod
            string_line.set_data(
                [pivot_x, x],
                [pivot_y, y]
            )

            string_line.set_3d_properties(
                [pivot_z, z]
            )

            # Ball
            ball_point.set_data(
                [x],
                [y]
            )

            ball_point.set_3d_properties(
                [z]
            )

            # Trajectory
            trace_line.set_data(
                self.x_cm[:frame + 1],
                self.y_cm[:frame + 1]
            )

            trace_line.set_3d_properties(
                self.z_cm[:frame + 1]
            )

            return (
                string_line,
                ball_point,
                trace_line
            )

        # -----------------------------------------------------
        # Animation
        # -----------------------------------------------------

        anim = animation.FuncAnimation(
            fig,
            update,
            frames=len(self.t),
            init_func=init,
            interval=interval,
            blit=True
        )

        # -----------------------------------------------------
        # Save animation
        # -----------------------------------------------------

        if save_path is not None:

            save_kwargs = {}

            if progress_callback is not None:
                save_kwargs["progress_callback"] = progress_callback

            if save_path.endswith(".gif"):

                anim.save(
                    save_path,
                    writer="pillow",
                    fps=fps,
                    **save_kwargs
                )

            else:

                anim.save(
                    save_path,
                    fps=fps,
                    **save_kwargs
                )

        return anim