import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib import rcParams
from matplotlib.collections import LineCollection
import evo.core.trajectory as traj
import evo.core.sync as sync
import evo.core.metrics as metrics
from evo.tools import file_interface

GT_FILE = 'pose_file_gt_BA_f006_whole.txt'#you can change your pose.txt
EST_FILE = 'pose_file_est_BA_f006_whole.txt'#you can change your pose.txt

def main():
    print("🚀 loading...")
    path_ref = file_interface.read_kitti_poses_file(GT_FILE)
    path_est = file_interface.read_kitti_poses_file(EST_FILE)
    traj_ref = traj.PoseTrajectory3D(
        positions_xyz=path_ref.positions_xyz,
        orientations_quat_wxyz=path_ref.orientations_quat_wxyz,
        timestamps=np.arange(path_ref.num_poses, dtype=np.float64)
    )
    
    traj_est = traj.PoseTrajectory3D(
        positions_xyz=path_est.positions_xyz,
        orientations_quat_wxyz=path_est.orientations_quat_wxyz,
        timestamps=np.arange(path_est.num_poses, dtype=np.float64)
    )

    print("🔄  (Umeyama Alignment)...")
    traj_ref, traj_est = sync.associate_trajectories(traj_ref, traj_est)
    traj_est.align(traj_ref, correct_scale=True, correct_only_scale=False)
    print("📊  (APE)...")
    data = (traj_ref, traj_est)
    ape_metric = metrics.APE(metrics.PoseRelation.translation_part)
    ape_metric.process_data(data)
    errors = ape_metric.error  
    print("🎨 1:1 ")
    rcParams['font.family'] = 'serif'
    rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif', 'serif']
    rcParams['mathtext.fontset'] = 'cm'  
    rcParams['axes.linewidth'] = 1.2     
    xyz_ref = traj_ref.positions_xyz
    xyz_est = traj_est.positions_xyz
    
    horiz_ref, vert_ref = xyz_ref[:, 1], xyz_ref[:, 0]
    horiz_est, vert_est = xyz_est[:, 1], xyz_est[:, 0]
    horiz_offset = horiz_ref[0]
    vert_offset = vert_ref[0]
    horiz_ref -= horiz_offset
    vert_ref -= vert_offset
    horiz_est -= horiz_offset
    vert_est -= vert_offset
    fig, ax = plt.subplots(figsize=(7, 6), dpi=300)
    
    ax.plot(horiz_ref, vert_ref, '--', color='#666666', label='reference', linewidth=2.0, zorder=1)

    ax.plot(horiz_ref[0], vert_ref[0], 'o', color='#666666', markersize=5, zorder=3)
    ax.plot(horiz_ref[-1], vert_ref[-1], 'x', color='#666666', markersize=5, markeredgewidth=1.5, zorder=3)

    points = np.array([horiz_est, vert_est]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    norm = plt.Normalize(errors.min(), errors.max())
    lc = LineCollection(segments, cmap='jet', norm=norm, zorder=2)
    lc.set_array(errors)
    lc.set_linewidth(2.0)
    line = ax.add_collection(lc)

    ax.set_title('APE w.r.t. translation part (m)\n(with Sim(3) Umeyama alignment)', fontsize=12, pad=10)
    
    ax.set_xlabel('$y$ (m)', fontsize=12)
    ax.set_ylabel('$x$ (m)', fontsize=12)
    
    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.3f'))
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.3f'))

    ax.legend(loc='upper left', fontsize=10, framealpha=1.0, edgecolor='#CCCCCC')

    ax.grid(True, linestyle='-', color='#E0E0E0', linewidth=1.2)
    ax.set_axisbelow(True)
    
    for spine in ax.spines.values():
        spine.set_edgecolor('#A0A0A0')

    ax.set_aspect('equal', adjustable='datalim')

    cbar = fig.colorbar(line, ax=ax, fraction=0.03, pad=0.04)
    cbar.outline.set_edgecolor('#A0A0A0')
    cbar.outline.set_linewidth(1.2)
    cbar.ax.tick_params(labelsize=10)
    cb_min, cb_max = errors.min(), errors.max()
    cb_mid = (cb_min + cb_max) / 2
    cbar.set_ticks([cb_min, cb_mid, cb_max])
    cbar.ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.3f'))

    plt.tight_layout()
    output_name = 'paper_style_trajectory.png'
    plt.savefig(output_name, bbox_inches='tight')
    
    print(f"✅ save: {output_name}")
    print(f"📈 average error: {np.mean(errors):.6f} m, maximum error: {np.max(errors):.6f} m")

if __name__ == '__main__':
    main()