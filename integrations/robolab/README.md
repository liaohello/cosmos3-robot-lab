<!-- SPDX-FileCopyrightText: Copyright (c) 2026 Xiangyu Li. -->
<!-- SPDX-License-Identifier: OpenMDW-1.1 -->

# RoboLab integration patches

This directory stores focused patches for an external RoboLab checkout. It does not contain the RoboLab source tree.

## Supported base

- Repository: [NVlabs/RoboLab](https://github.com/NVlabs/RoboLab)
- Release: `v0.3.1`
- Base commit: `9db0aaf`
- Apply in order:
  1. `patches/0001-bounded-cpu-streaming-image-recorder.patch`
  2. `patches/0002-Add-training-ready-Cosmos-DROID-trajectory-export.patch`

The patches were carried from the Cosmos Lite integration snapshot and are distributed under the upstream `OpenMDW-1.1` terms. The patch author attribution is retained; the source email address was removed from the patch metadata. The full license text is in [`LICENSE-OpenMDW-1.1.txt`](LICENSE-OpenMDW-1.1.txt).

Apply only to a clean checkout at the pinned base. The stage A runner does not apply patches automatically:

```bash
git -C "$ROBOLAB_DIR" switch --detach 9db0aaf
git -C "$ROBOLAB_DIR" apply --check /path/to/cosmos3-robot-lab/integrations/robolab/patches/0001-bounded-cpu-streaming-image-recorder.patch
git -C "$ROBOLAB_DIR" apply /path/to/cosmos3-robot-lab/integrations/robolab/patches/0001-bounded-cpu-streaming-image-recorder.patch
git -C "$ROBOLAB_DIR" apply --check /path/to/cosmos3-robot-lab/integrations/robolab/patches/0002-Add-training-ready-Cosmos-DROID-trajectory-export.patch
git -C "$ROBOLAB_DIR" apply /path/to/cosmos3-robot-lab/integrations/robolab/patches/0002-Add-training-ready-Cosmos-DROID-trajectory-export.patch
```

The first patch bounds image-recording memory and streams recording copies to CPU. The second exports successful DROID trajectories in LeRobot v3 format. Recheck the base commit and run the upstream recorder, schema, and trajectory validation before using either patch on another RoboLab release.
