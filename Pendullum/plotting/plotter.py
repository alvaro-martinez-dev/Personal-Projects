import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation


class PlotMotion:
    # Class to visualize the results produced by an `eqnsmotion` instance
    # together with the solution returned by its `solver` method.

    def __init__(self, eqns, sol):
        # eqns: instance of eqnsmotion (needed for geometry / energy methods)
        # sol: solution object returned by eqnsmotion.solver (has .t and .y)

        self.eqns = eqns
        self.sol = sol

        self.t = sol.t
        self.theta = sol.y[0]
        self.dtheta = sol.y[1]

        # Precompute derived quantities used across plots
        self.y_cm, self.z_cm = self.eqns.position_cm(self.theta)
        self.kin_en, self.pot_en, self.total_en, self.lagrangian = self.eqns.energy(
            self.theta, self.dtheta
        )

    def plot_angle(self, ax=None, show=True):
        # Plots theta(t) and dtheta(t) on twin y-axes

        created_fig = ax is None
        if created_fig:
            fig, ax = plt.subplots(figsize=(8, 4.5))

        ax.plot(self.t, self.theta, color="tab:blue", label=r"$\theta$ (rad)")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel(r"$\theta$ (rad)", color="tab:blue")
        ax.tick_params(axis="y", labelcolor="tab:blue")

        ax2 = ax.twinx()
        ax2.plot(self.t, self.dtheta, color="tab:red", label=r"$\dot\theta$ (rad/s)")
        ax2.set_ylabel(r"$\dot\theta$ (rad/s)", color="tab:red")
        ax2.tick_params(axis="y", labelcolor="tab:red")

        ax.set_title("Angular position and velocity")
        ax.grid(False)

        if created_fig:
            fig.tight_layout()
            if show:
                plt.show()
            return fig, (ax, ax2)

    def plot_energy(self, ax=None, show=True):
        # Plots kinetic, potential and total energy over time

        created_fig = ax is None
        if created_fig:
            fig, ax = plt.subplots(figsize=(8, 4.5))

        ax.plot(self.t, self.kin_en, label="Kinetic energy", color="tab:orange")
        ax.plot(self.t, self.pot_en, label="Potential energy", color="tab:green")
        ax.plot(self.t, self.total_en, label="Total energy", color="tab:purple",
                linestyle="--")

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

    def plot_trajectory(self, ax=None, show=True):
        # Plots the trajectory of the center of mass in the y-z plane

        created_fig = ax is None
        if created_fig:
            fig, ax = plt.subplots(figsize=(5.5, 5.5))

        ax.plot(self.y_cm, self.z_cm, color="tab:blue")
        ax.scatter(self.y_cm[0], self.z_cm[0], color="green", zorder=5, label="Start")
        ax.scatter(self.y_cm[-1], self.z_cm[-1], color="red", zorder=5, label="End")
        # Pivot point at (0, H)
        ax.scatter(0, self.eqns.H, color="black", marker="^", zorder=5, label="Pivot")

        ax.set_xlabel("y (m)")
        ax.set_ylabel("z (m)")
        ax.set_title("Center of mass trajectory")
        ax.set_aspect("equal", adjustable="box")
        ax.legend()
        ax.grid(False)

        if created_fig:
            fig.tight_layout()
            if show:
                plt.show()
            return fig, ax

    def summary(self, show=True):
        # Convenience method: combines angle, energy and trajectory into one figure

        fig = plt.figure(figsize=(12, 8))
        ax1 = fig.add_subplot(2, 2, 1)
        ax2 = fig.add_subplot(2, 2, 2)
        ax3 = fig.add_subplot(2, 2, (3, 4))

        self.plot_angle(ax=ax1, show=False)
        self.plot_energy(ax=ax2, show=False)
        self.plot_trajectory(ax=ax3, show=False)

        fig.tight_layout()
        if show:
            plt.show()
        return fig

    def animate(self, interval=30, save_path=None, fps=30, progress_callback=None):
        # Creates an animation of the pendulum swinging in the y-z plane.
        # If save_path is given (e.g. "pendulum.gif" or "pendulum.mp4"),
        # the animation is saved to disk instead of only being returned.
        # progress_callback(current_frame, total_frames) is forwarded to
        # matplotlib's anim.save, useful for wiring up a progress bar (e.g. tqdm).

        fig, ax = plt.subplots(figsize=(5.5, 5.5))

        margin = 0.2 * (self.eqns.l + self.eqns.r)
        y_lim = self.eqns.l + self.eqns.r + margin
        ax.set_xlim(-y_lim, y_lim)
        ax.set_ylim(self.eqns.H - 2 * y_lim, self.eqns.H + margin)
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlabel("y (m)")
        ax.set_ylabel("z (m)")
        ax.set_title("Pendulum motion")
        ax.grid(False)

        pivot = (0, self.eqns.H)
        ax.scatter(*pivot, color="black", marker="^", zorder=5)

        string_line, = ax.plot([], [], color="gray", lw=1.5)
        ball_point, = ax.plot([], [], "o", color="tab:blue", markersize=12)
        trace_line, = ax.plot([], [], color="tab:blue", alpha=0.3, lw=1)

        def init():
            string_line.set_data([], [])
            ball_point.set_data([], [])
            trace_line.set_data([], [])
            return string_line, ball_point, trace_line

        def update(frame):
            y, z = self.y_cm[frame], self.z_cm[frame]
            string_line.set_data([pivot[0], y], [pivot[1], z])
            ball_point.set_data([y], [z])
            trace_line.set_data(self.y_cm[: frame + 1], self.z_cm[: frame + 1])
            return string_line, ball_point, trace_line

        anim = animation.FuncAnimation(
            fig, update, frames=len(self.t), init_func=init,
            interval=interval, blit=True
        )

        if save_path is not None:
            save_kwargs = {}
            if progress_callback is not None:
                save_kwargs["progress_callback"] = progress_callback

            if save_path.endswith(".gif"):
                anim.save(save_path, writer="pillow", fps=fps, **save_kwargs)
            else:
                anim.save(save_path, fps=fps, **save_kwargs)

        return anim