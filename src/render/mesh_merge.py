# Copyright (c) 2026 Renaud Guillon
"""Merge a model's still meshes into one mesh per material (ENG-106, PERF-02).

A model built of many small parts (the player ship: over 300 meshes) costs a draw call per part,
and as many again in every layer that draws it (a glow layer). Its parts that never move against
each other and share a material and how they are drawn can be one mesh: the same triangles, the
same frames, a draw call each. Parts that an animation moves, scales or fades are kept apart by
the code that animates them (`keep_apart`), with everything under them.
"""

from org.transcrypt.stubs.browser import __pragma__

# isort: split
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


def keep_apart(node: Any) -> None:
    """Keep `node`'s meshes, and those of every node under it, out of `merge_still_meshes`.

    The node is marked (`__keptApart`): moved or faded by animations.
    """
    __pragma__("js", "{}", "node.__keptApart = true;")


def merge_still_meshes(root: Any) -> int:
    """Merge the meshes under `root` that share a material and their drawing state; return how many.

    Only plain, visible, fully opaque-visibility meshes with one opaque material are merged, not
    those kept apart or under a node kept apart, nor instanced ones. See-through meshes stay apart:
    they are drawn sorted by their own centre's distance, which a merge would move. An unevenly
    scaled mesh's normals are first set so the merge turns them as Babylon's shader did (by its
    matrix's inverse transpose), so it shades the same. Each group of two or more becomes one
    mesh under `root` (in its frame, wherever it stands), with the group's drawing state (rendering
    group, alpha index, shadows, layer mask); the vertex attributes are those the group shares.
    Their transform nodes stay, empty.
    """
    __pragma__(
        "js",
        "{}",
        """
        const isApart = (mesh) => {
            for (let node = mesh; node && node !== root; node = node.parent) {
                if (node.__keptApart) return true;
            }
            return false;
        };
        const groups = new Map();
        root.computeWorldMatrix(true);
        for (const mesh of root.getChildMeshes(false)) {
            mesh.computeWorldMatrix(true);
            const material = mesh.material;
            if (mesh.getClassName() !== 'Mesh' || !material || mesh.skeleton
                || material.getClassName() === 'MultiMaterial' || mesh.instances.length > 0
                || mesh.hasThinInstances || !mesh.isVisible || mesh.visibility !== 1
                || !mesh.isEnabled(false) || mesh.getTotalVertices() === 0 || isApart(mesh)
                || material.needAlphaBlendingForMesh(mesh) || material.needAlphaTesting()) {
                continue;
            }
            const key = [material.uniqueId, mesh.renderingGroupId, mesh.alphaIndex,
                mesh.receiveShadows, mesh.layerMask, mesh.isPickable].join('|');
            if (!groups.has(key)) groups.set(key, []);
            groups.get(key).push(mesh);
        }
        // An unevenly scaled mesh's normals are drawn turned by its matrix's inverse transpose
        // (A^-T, A its world matrix's 3x3), but merged they are turned by A itself: they are
        // first set to (A^T A)^-1 n, which A turns into A^-T n, the direction the shader drew.
        const evenNormals = (mesh) => {
            const normals = mesh.getVerticesData(BABYLON.VertexBuffer.NormalKind);
            if (!normals) return;
            const m = mesh.getWorldMatrix().m;
            // A[i][j] = m[j * 4 + i] (Babylon's matrices act on row vectors).
            const a = [[m[0], m[4], m[8]], [m[1], m[5], m[9]], [m[2], m[6], m[10]]];
            const g = [[0, 0, 0], [0, 0, 0], [0, 0, 0]];
            for (let i = 0; i < 3; i++) {
                for (let j = 0; j < 3; j++) {
                    g[i][j] = a[0][i] * a[0][j] + a[1][i] * a[1][j] + a[2][i] * a[2][j];
                }
            }
            const det = g[0][0] * (g[1][1] * g[2][2] - g[1][2] * g[2][1])
                - g[0][1] * (g[1][0] * g[2][2] - g[1][2] * g[2][0])
                + g[0][2] * (g[1][0] * g[2][1] - g[1][1] * g[2][0]);
            if (det === 0) return;
            const inv = [
                [(g[1][1] * g[2][2] - g[1][2] * g[2][1]) / det,
                 (g[0][2] * g[2][1] - g[0][1] * g[2][2]) / det,
                 (g[0][1] * g[1][2] - g[0][2] * g[1][1]) / det],
                [(g[1][2] * g[2][0] - g[1][0] * g[2][2]) / det,
                 (g[0][0] * g[2][2] - g[0][2] * g[2][0]) / det,
                 (g[0][2] * g[1][0] - g[0][0] * g[1][2]) / det],
                [(g[1][0] * g[2][1] - g[1][1] * g[2][0]) / det,
                 (g[0][1] * g[2][0] - g[0][0] * g[2][1]) / det,
                 (g[0][0] * g[1][1] - g[0][1] * g[1][0]) / det],
            ];
            const out = new Float32Array(normals.length);
            for (let k = 0; k < normals.length; k += 3) {
                const x = normals[k];
                const y = normals[k + 1];
                const z = normals[k + 2];
                const nx = inv[0][0] * x + inv[0][1] * y + inv[0][2] * z;
                const ny = inv[1][0] * x + inv[1][1] * y + inv[1][2] * z;
                const nz = inv[2][0] * x + inv[2][1] * y + inv[2][2] * z;
                const length = Math.hypot(nx, ny, nz) || 1;
                out[k] = nx / length;
                out[k + 1] = ny / length;
                out[k + 2] = nz / length;
            }
            mesh.setVerticesData(BABYLON.VertexBuffer.NormalKind, out, false);
        };
        root.computeWorldMatrix(true);
        const toRoot = root.getWorldMatrix().clone().invert();
        let made = 0;
        for (const group of groups.values()) {
            if (group.length < 2) continue;
            const first = group[0];
            let kinds = first.getVerticesDataKinds();
            for (const mesh of group) {
                const own = mesh.getVerticesDataKinds();
                kinds = kinds.filter((kind) => own.indexOf(kind) >= 0);
            }
            for (const mesh of group) {
                for (const kind of mesh.getVerticesDataKinds()) {
                    if (kinds.indexOf(kind) < 0) mesh.removeVerticesData(kind);
                }
                mesh.computeWorldMatrix(true);
                if (mesh.nonUniformScaling) evenNormals(mesh);
            }
            const state = [first.renderingGroupId, first.alphaIndex, first.receiveShadows,
                first.layerMask, first.isPickable];
            const name = root.name + '-merged-' + first.material.name;
            const merged = BABYLON.Mesh.MergeMeshes(group, true, true);
            if (!merged) continue;
            merged.name = name;
            merged.bakeTransformIntoVertices(toRoot);
            merged.parent = root;
            merged.renderingGroupId = state[0];
            merged.alphaIndex = state[1];
            merged.receiveShadows = state[2];
            merged.layerMask = state[3];
            merged.isPickable = state[4];
            made += 1;
        }
        return made;
        """,
    )
    return 0
