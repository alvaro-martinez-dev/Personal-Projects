import argparse
import os

import numpy as np
import yaml
from tqdm import tqdm

from physics.Eqns_Motion_3D import Eqnsmotion
from plotting.Plotter_3D import PlotMotion

from physics.Eqns_Motion_Drag3D import EqnsmotionDrag
from plotting.Plotter_Drag3D import PlotMotionDrag


def load_config(path):
    with open(path, "r") as f:
        config = yaml.safe_load(f)
    return config


def run(config_path="config.yml", output_dir="outputs", show=False):

    config = load_config(config_path)
    pend_cfg = config["pendulum"]
    sim_cfg = config["simulation"]
    use_drag = sim_cfg.get("use_drag", False)

    # Pipeline steps: config -> model(s) -> solve -> plots -> animation
    pipeline = tqdm(total=5, desc="Pipeline", unit="step")

    pipeline.set_description("Loading config")
    t_eval = np.linspace(0, sim_cfg["tfinal"], sim_cfg["n_frames"])
    pipeline.update(1)

    # -----------------------------------------------------------------
    # Building model(s)
    # -----------------------------------------------------------------
    pipeline.set_description("Building model(s)")

    pend_ideal = Eqnsmotion(
        H=pend_cfg["H"],
        M=pend_cfg["M"],
        r=pend_cfg["r"],
        m=pend_cfg["m"],
        l=pend_cfg["l"],
        g=pend_cfg.get("g", 9.81),
    )

    if use_drag:
        pend_drag = EqnsmotionDrag(
            H=pend_cfg["H"],
            M=pend_cfg["M"],
            r=pend_cfg["r"],
            m=pend_cfg["m"],
            l=pend_cfg["l"],
            g=pend_cfg.get("g", 9.81),
            k_drag=pend_cfg.get("k_drag", 0.0),
        )
    pipeline.update(1)

    # -----------------------------------------------------------------
    # Solving ODE(s)
    # -----------------------------------------------------------------
    pipeline.set_description("Solving ODE")

    sol_ideal = pend_ideal.solver(
        theta0=sim_cfg["theta0"],
        dtheta0=sim_cfg["dtheta0"],
        phi0=sim_cfg["phi0"],
        dphi0=sim_cfg["dphi0"],
        t_span=(0, sim_cfg["tfinal"]),
        t_eval=t_eval,
    )
    if not sol_ideal.success:
        pipeline.close()
        raise RuntimeError(f"Integration failed (no-drag): {sol_ideal.message}")

    plotter_ideal = PlotMotion(pend_ideal, sol_ideal)

    if use_drag:
        sol_drag = pend_drag.solver_drag(
            theta0=sim_cfg["theta0"],
            dtheta0=sim_cfg["dtheta0"],
            phi0=sim_cfg["phi0"],
            dphi0=sim_cfg["dphi0"],
            t_span=(0, sim_cfg["tfinal"]),
            t_eval=t_eval,
        )
        if not sol_drag.success:
            pipeline.close()
            raise RuntimeError(f"Integration failed (drag): {sol_drag.message}")

        plotter_drag = PlotMotionDrag(pend_drag, sol_drag)

    pipeline.update(1)

    os.makedirs(output_dir, exist_ok=True)

    # -----------------------------------------------------------------
    # Plotting summary
    # -----------------------------------------------------------------
    pipeline.set_description("Plotting summary")

    if use_drag:
        # Superpone drag vs no-drag: theta(t), energia(t) y trayectoria 3D con rozamiento
        fig_summary = plotter_drag.summary_comparison(plotter_ideal, show=show)
        fig_summary.savefig(
            os.path.join(output_dir, "summary_drag.png"), dpi=150
        )
    else:
        fig_summary = plotter_ideal.summary(show=show)
        fig_summary.savefig(os.path.join(output_dir, "summary_nodrag.png"), dpi=150)

    pipeline.update(1)

    # -----------------------------------------------------------------
    # Saving animation
    # -----------------------------------------------------------------
    pipeline.set_description("Saving animation")

    n_frames = sim_cfg["n_frames"]
    fps = sim_cfg["fps"]

    # Animamos la version con rozamiento si use_drag=True (es la trayectoria
    # "real" que nos interesa ver); si no, la version ideal.
    animate_plotter = plotter_drag if use_drag else plotter_ideal

    with tqdm(total=n_frames, desc="Animation frames", unit="frame", leave=False) as frame_bar:
        def report_progress(current_frame, total_frames):
            frame_bar.n = current_frame
            frame_bar.refresh()

        if use_drag:
            animate_plotter.animate(
                save_path=os.path.join(output_dir, "pendulum_drag.gif"),
                progress_callback=report_progress,
                interval=1000 / fps,
                fps=fps,
            )
        else:
            animate_plotter.animate(
                    save_path=os.path.join(output_dir, "pendulum_nodrag.gif"),
                    progress_callback=report_progress,
                    interval=1000 / fps,
                    fps=fps,
            )

    pipeline.update(1)
    pipeline.close()

    print(f"Done. Results written to '{output_dir}/'.")

    if use_drag:
        return pend_ideal, sol_ideal, plotter_ideal, pend_drag, sol_drag, plotter_drag
    else:
        return pend_ideal, sol_ideal, plotter_ideal


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run pendulum simulation from a config file.")
    parser.add_argument("--config", default="config.yml", help="Path to the YAML config file.")
    parser.add_argument("--outdir", default="outputs", help="Directory to write plots/animation to.")
    parser.add_argument("--show", action="store_true", help="Display plots interactively.")
    args = parser.parse_args()

    run(config_path=args.config, output_dir=args.outdir, show=args.show)