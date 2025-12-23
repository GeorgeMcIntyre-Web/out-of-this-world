"""
Manim animations for 30-second investor "wow" video.
Renders high-quality explainer animation.
"""

from __future__ import annotations

import subprocess
import shutil
from pathlib import Path

import numpy as np
from manim import *  # noqa: F403


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


class CosmicCompassExplainer(Scene):  # noqa: F405
    def construct(self):
        # === SCENE 1: Title (0-3s) ===
        self.camera.background_color = "#0a0a0a"

        title = Text("Cosmic Compass", font_size=72, color=BLUE, weight=BOLD)  # noqa: F405
        subtitle = Text(
            "Autonomous Navigation via Gravitational Sensing",
            font_size=32,
            color=WHITE,  # noqa: F405
        ).next_to(title, DOWN, buff=0.5)  # noqa: F405

        self.play(Write(title), run_time=1.5)  # noqa: F405
        self.play(FadeIn(subtitle), run_time=1)  # noqa: F405
        self.wait(0.5)
        self.play(FadeOut(title), FadeOut(subtitle))  # noqa: F405

        # === SCENE 2: Problem Statement (3-8s) ===
        problem_text = Text("Deep space navigation is blind", font_size=48, color=RED)  # noqa: F405
        self.play(Write(problem_text), run_time=1.5)  # noqa: F405
        self.wait(1)

        # Show spacecraft icon with question marks
        asset_svg = _repo_root() / "demos" / "assets" / "spacecraft_icon.svg"
        if asset_svg.exists():
            spacecraft = SVGMobject(str(asset_svg)).scale(0.8)  # noqa: F405
        else:
            spacecraft = Circle(radius=0.5, color=YELLOW, fill_opacity=1)  # noqa: F405
        spacecraft.move_to(ORIGIN)  # noqa: F405

        question_marks = VGroup(  # noqa: F405
            *[
                Text("?", font_size=48, color=YELLOW).move_to(  # noqa: F405
                    spacecraft.get_center()
                    + 1.5 * np.array([np.cos(theta), np.sin(theta), 0.0])
                )
                for theta in np.linspace(0, 2 * np.pi, 8, endpoint=False)
            ]
        )

        self.play(FadeOut(problem_text))  # noqa: F405
        self.play(FadeIn(spacecraft))  # noqa: F405
        self.play(LaggedStart(*[FadeIn(q) for q in question_marks], lag_ratio=0.1), run_time=2)  # noqa: F405
        self.wait(0.5)
        self.play(FadeOut(spacecraft), FadeOut(question_marks))  # noqa: F405

        # === SCENE 3: Solution (8-15s) ===
        solution_text = Text("Detect gravitational signatures", font_size=48, color=GREEN)  # noqa: F405
        self.play(Write(solution_text), run_time=1.5)  # noqa: F405
        self.wait(0.5)
        self.play(solution_text.animate.to_edge(UP))  # noqa: F405

        # Show neutron star and spacecraft
        neutron_star = Circle(  # noqa: F405
            radius=0.4, color=BLUE, fill_opacity=1, stroke_width=3, stroke_color=BLUE_C  # noqa: F405
        )
        neutron_star.set_sheen_direction(UP)  # noqa: F405
        neutron_star.move_to(2 * RIGHT)  # noqa: F405

        ns_label = Text("Neutron Star", font_size=20, color=BLUE_C).next_to(  # noqa: F405
            neutron_star, DOWN, buff=0.3  # noqa: F405
        )

        if asset_svg.exists():
            spacecraft2 = SVGMobject(str(asset_svg)).scale(0.3)  # noqa: F405
        else:
            spacecraft2 = Circle(radius=0.2, color=YELLOW, fill_opacity=1)  # noqa: F405
        spacecraft2.move_to(5 * LEFT)  # noqa: F405

        self.play(FadeIn(neutron_star), FadeIn(ns_label))  # noqa: F405
        self.play(FadeIn(spacecraft2))  # noqa: F405

        # Gravity field visualization
        gravity_waves = VGroup()  # noqa: F405
        for i in range(5):
            circle = Circle(  # noqa: F405
                radius=0.4 + i * 0.5,
                color=BLUE,  # noqa: F405
                stroke_width=2,
                stroke_opacity=max(0.15, 0.6 - i * 0.1),
            )
            circle.move_to(neutron_star.get_center())
            gravity_waves.add(circle)

        self.play(Create(gravity_waves), run_time=1.5)  # noqa: F405

        # Spacecraft trajectory
        path = ArcBetweenPoints(  # noqa: F405
            spacecraft2.get_center(),
            neutron_star.get_center() + 0.8 * DOWN,  # noqa: F405
            angle=-TAU / 6,  # noqa: F405
        )

        # Measurement points
        measurement_dots = VGroup(  # noqa: F405
            *[Dot(point=path.point_from_proportion(t), color=GREEN, radius=0.05) for t in np.linspace(0, 1, 12)]  # noqa: F405,E501
        )

        self.play(
            MoveAlongPath(spacecraft2, path),  # noqa: F405
            Create(measurement_dots, lag_ratio=0.05),  # noqa: F405
            run_time=3,
        )

        self.wait(0.5)
        self.play(FadeOut(VGroup(neutron_star, ns_label, spacecraft2, gravity_waves, measurement_dots, solution_text)))  # noqa: F405,E501

        # === SCENE 4: Technology (15-22s) ===
        tech_title = Text("Quantum Sensor Technology", font_size=48, color=YELLOW).to_edge(UP)  # noqa: F405,E501
        self.play(Write(tech_title), run_time=1)  # noqa: F405

        # Atom interferometer simplified diagram
        atom = Circle(radius=0.1, color=RED, fill_opacity=1)  # noqa: F405
        atom.move_to(3 * LEFT)  # noqa: F405

        laser1 = Line(start=ORIGIN + 3 * UP, end=ORIGIN, color=PURE_RED, stroke_width=4)  # noqa: F405,E501
        laser_label = Text("Laser Pulse", font_size=20, color=PURE_RED).next_to(  # noqa: F405
            laser1, RIGHT, buff=0.2  # noqa: F405
        )

        self.play(FadeIn(atom))  # noqa: F405
        self.play(Create(laser1), FadeIn(laser_label))  # noqa: F405

        # Atom splits (two paths)
        atom_up = atom.copy().move_to(2 * UP + RIGHT)  # noqa: F405
        atom_down = atom.copy().move_to(2 * DOWN + RIGHT)  # noqa: F405
        self.play(Transform(atom, VGroup(atom_up, atom_down)), run_time=1)  # noqa: F405

        # Atoms recombine with phase shift
        interference = Circle(  # noqa: F405
            radius=0.15, color=GREEN, fill_opacity=0.8, stroke_width=3, stroke_color=GREEN_C  # noqa: F405
        )
        interference.move_to(3 * RIGHT)  # noqa: F405

        phase_label = Text("Phase Shift ∝ Gravity", font_size=24, color=GREEN).next_to(  # noqa: F405
            interference, DOWN, buff=0.3  # noqa: F405
        )

        self.play(atom_up.animate.move_to(interference.get_center()), atom_down.animate.move_to(interference.get_center()), run_time=1)  # noqa: F405,E501
        self.play(FadeIn(interference), FadeIn(phase_label))  # noqa: F405

        self.wait(1)
        self.play(FadeOut(VGroup(atom_up, atom_down, laser1, laser_label, interference, phase_label, tech_title)))  # noqa: F405,E501

        # === SCENE 5: Performance Stats (22-27s) ===
        stats_title = Text("Performance", font_size=56, color=BLUE).to_edge(UP)  # noqa: F405
        self.play(Write(stats_title), run_time=0.8)  # noqa: F405

        stats = VGroup(  # noqa: F405
            Text("10⁶× better than traditional IMU", font_size=36, color=WHITE),  # noqa: F405
            Text("100 km → 100 m accuracy", font_size=36, color=GREEN),  # noqa: F405
            Text("Autonomous deep space navigation", font_size=36, color=YELLOW),  # noqa: F405
        ).arrange(DOWN, buff=0.6, center=True)  # noqa: F405

        for stat in stats:
            self.play(FadeIn(stat, shift=UP * 0.3), run_time=0.8)  # noqa: F405
            self.wait(0.5)

        self.wait(1)
        self.play(FadeOut(stats), FadeOut(stats_title))  # noqa: F405

        # === SCENE 6: Call to Action (27-30s) ===
        cta = VGroup(  # noqa: F405
            Text("OutOfThisWorld", font_size=64, color=BLUE, weight=BOLD),  # noqa: F405
            Text("GPS for Deep Space", font_size=40, color=WHITE),  # noqa: F405
        ).arrange(DOWN, buff=0.4, center=True)  # noqa: F405

        self.play(FadeIn(cta, scale=1.2), run_time=1.5)  # noqa: F405
        self.wait(1.5)


def render_animation():
    """Render the animation via the manim CLI."""
    root = _repo_root()
    out_dir = root / "demos" / "outputs" / "videos"
    out_dir.mkdir(parents=True, exist_ok=True)

    print("Rendering Manim animation...")
    print("This can take a few minutes depending on environment.")

    cmd = [
        "manim",
        "-qh",
        str(Path(__file__).resolve()),
        "CosmicCompassExplainer",
        "-o",
        "cosmic_compass_explainer.mp4",
        "--media_dir",
        str(out_dir),
    ]
    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        raise RuntimeError("manim CLI not found. Install manim or skip animation.") from None

    # Copy to a friendly top-level path for presentations.
    expected = out_dir / "videos" / "manim_animations" / "1080p60" / "cosmic_compass_explainer.mp4"
    if expected.exists():
        shutil.copy2(expected, out_dir / "cosmic_compass_explainer.mp4")

    print(f"✅ Animation rendered under {out_dir}")


if __name__ == "__main__":
    render_animation()

