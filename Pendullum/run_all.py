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
    # Overall pipeline progress: config -> model -> solve -> plots -> animation
    pipeline = tqdm(total=5, desc="Pipeline", unit="step")

    pipeline.set_description("Loading config")
    config = load_config(config_path)
    pend_cfg = config["pendulum"]
    sim_cfg = config["simulation"]
    pipeline.update(1)

    pipeline.set_description("Building model")
    pend = Eqnsmotion(
        H=pend_cfg["H"],
        M=pend_cfg["M"],
        r=pend_cfg["r"],
        m=pend_cfg["m"],
        l=pend_cfg["l"],
        g=pend_cfg.get("g", 9.81),
    )
    pipeline.update(1)

    pipeline.set_description("Solving ODE")
    t_eval = np.linspace(0, sim_cfg["tfinal"], sim_cfg["n_frames"])
    sol = pend.solver(
        theta0=sim_cfg["theta0"],
        dtheta0=sim_cfg["dtheta0"],
        phi0=sim_cfg["phi0"],
        dphi0=sim_cfg["dphi0"],
        t_span=(0, sim_cfg["tfinal"]),
        t_eval=t_eval,
    )
    if not sol.success:
        pipeline.close()
        raise RuntimeError(f"Integration failed: {sol.message}")
    pipeline.update(1)

    os.makedirs(output_dir, exist_ok=True)
    plotter = PlotMotion(pend, sol)

    pipeline.set_description("Plotting summary")
    fig_summary = plotter.summary(show=show)
    fig_summary.savefig(os.path.join(output_dir, "summary.png"), dpi=150)
    pipeline.update(1)

    pipeline.set_description("Saving animation")
    n_frames = sim_cfg["n_frames"]
    with tqdm(total=n_frames, desc="Animation frames", unit="frame", leave=False) as frame_bar:
        def report_progress(current_frame, total_frames):
            frame_bar.n = current_frame
            frame_bar.refresh()

        fps = sim_cfg["fps"]

        plotter.animate(
            save_path=os.path.join(output_dir, "pendulum.gif"),
            progress_callback=report_progress,
            interval=1000 / fps,
            fps = fps,
        )
    pipeline.update(1)
    pipeline.close()

    print(f"Done. Results written to '{output_dir}/'.")

    return pend, sol, plotter


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run pendulum simulation from a config file.")
    parser.add_argument("--config", default="config.yml", help="Path to the YAML config file.")
    parser.add_argument("--outdir", default="outputs", help="Directory to write plots/animation to.")
    parser.add_argument("--show", action="store_true", help="Display plots interactively.")
    args = parser.parse_args()

    run(config_path=args.config, output_dir=args.outdir, show=args.show)
