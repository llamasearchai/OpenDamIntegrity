"""3D visualization using VTK if available, otherwise matplotlib."""
from __future__ import annotations

from pathlib import Path
from typing import Tuple

import numpy as np

try:
    import vtk  # type: ignore
    VTK_AVAILABLE = True
except Exception:  # pragma: no cover - optional
    VTK_AVAILABLE = False

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401


def _make_surface(width: int = 100, depth: int = 60, height: int = 30) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    x = np.linspace(0, width, 60)
    y = np.linspace(0, depth, 40)
    X, Y = np.meshgrid(x, y)
    Z = height - (height / width) * X + 1.0 * np.sin(Y / 3.0)  # simple sloped surface with ripples
    Z = np.clip(Z, 0, None)
    return X, Y, Z


def render_dam_surface_png(output_path: str | Path, width: int = 100, depth: int = 60, height: int = 30) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    X, Y, Z = _make_surface(width, depth, height)

    if VTK_AVAILABLE:
        # Minimal VTK offscreen rendering
        points = vtk.vtkPoints()
        polys = vtk.vtkCellArray()
        nx, ny = X.shape
        for i in range(nx):
            for j in range(ny):
                points.InsertNextPoint(float(X[i, j]), float(Y[i, j]), float(Z[i, j]))
        # Build quads
        for i in range(nx - 1):
            for j in range(ny - 1):
                id0 = i * ny + j
                id1 = (i + 1) * ny + j
                id2 = (i + 1) * ny + (j + 1)
                id3 = i * ny + (j + 1)
                quad = vtk.vtkQuad()
                quad.GetPointIds().SetId(0, id0)
                quad.GetPointIds().SetId(1, id1)
                quad.GetPointIds().SetId(2, id2)
                quad.GetPointIds().SetId(3, id3)
                polys.InsertNextCell(quad)
        polydata = vtk.vtkPolyData()
        polydata.SetPoints(points)
        polydata.SetPolys(polys)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        renderer = vtk.vtkRenderer()
        renderer.AddActor(actor)
        renderer.SetBackground(1.0, 1.0, 1.0)

        renwin = vtk.vtkRenderWindow()
        renwin.OffScreenRenderingOn()
        renwin.AddRenderer(renderer)
        renwin.SetSize(1024, 768)
        renwin.Render()

        w2i = vtk.vtkWindowToImageFilter()
        w2i.SetInput(renwin)
        w2i.Update()
        writer = vtk.vtkPNGWriter()
        writer.SetFileName(str(output_path))
        writer.SetInputData(w2i.GetOutput())
        writer.Write()
        return output_path

    # Fallback: matplotlib 3D
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_surface(X, Y, Z, cmap="viridis", linewidth=0, antialiased=True)
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.set_zlabel("Z (m)")
    ax.set_title("Dam Surface Model (fallback)")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path

