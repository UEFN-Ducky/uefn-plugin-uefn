---
description: "Wang tile texturing (the default for every repeating PBR surface): 16-tile atlas generation from any seamless map, the math-node master graph that picks matching tiles by hashed edges, and the failures that bring the grid back"
metadata:
  order: 7
  label: "Wang tiles"
  default_enabled: false
  load_condition: "Any repeating surface: ground, asphalt, walls, brick, carpet, tile, wood, concrete, or the user says tiling, repeating pattern, grid, or Wang"
---

# Wang tiles: no visible repeat, ever

**HARD: every repeating PBR texture uses this.** One texture tiled by plain UV shows a
grid at distance. A Wang set is 16 tiles whose edges only ever meet a matching edge, and
the material picks the tile per cell from a hash, so the surface never repeats and has
no seams. Skip it only for a texture that covers a surface once (signs, posters, UI,
unique baked props).

## Shape of the setup

| Piece | What it is |
|-------|------------|
| Atlas | 4 x 4 grid of tiles, same map layout for Base, Rough and Normal |
| Edge colours | 2 per edge axis: top/bottom pair and left/right pair |
| Tile slot | `col = left + 2*right`, `row = top + 2*bottom` (bits are 0 or 1) |
| Tile size `T` | source width / 4, so texel density is unchanged |
| Parameters | `Base`, `Rough`, `Normal`, `Tile`, `CellX`, `CellY` |

A plain instance has `CellX = CellY = 4`, so `Tile` keeps its old meaning (one source
repeat). Atlas sides stay a power of two so mips and streaming work.

## Build the atlas (Blender Python with numpy)

Read every map as `Non-Color`, top-down, wrapping. Make these sampled patches from
random offsets into the seamless source, each `T x T`, with one set of offsets shared by
all maps of the set:

- `H[0], H[1]` horizontal edge patches. Top edge samples at `(i, j)`, bottom edge at
  `(i, j - T)`, so a bottom row continues the next tile's top row.
- `V[0], V[1]` vertical edge patches, left at `(i, j)`, right at `(i - T, j)`.
- `C` one corner patch, sampled relative to the nearest corner, shared by all tiles.
- **`centre[t,b,l,r]` a different random offset for each of the 16 tiles.** This is
  what removes the repeat.

Blend, per pixel, with `d` the distance to each edge and `dm` the nearest:

```python
band = T * 0.14                                    # edge influence stays narrow
we = smoothstep(clip(1 - dm / band, 0, 1))
w = [1 / max(d, .5)**4 for d in (dt, db, dl, dr)]  # normalise; 1 exactly on its edge
wc = smoothstep(clip(1 - dist_to_nearest_corner / (T * .12), 0, 1))
edge = (sum(p * x for p, x in zip((top, bottom, left, right), w))) * (1 - wc) + corner * wc
pixel = centre * (1 - we) + edge * we
```

On normal maps renormalise after blending: `n = v*2-1; n /= |n|; v = (n+1)*.5`.

### Bricks, planks, panels, floor tile (anything on a grid)

Offsets must land on the pattern's grid or the mortar lines tear.

1. Find the period per axis from the base map autocorrelation: FFT of luminance, take
   the first peak at lag `>= S/24` that is over 0.32 and within 0.8 of the highest peak.
   No peak on that axis means organic: use any offset.
2. Snap: `n = max(1, round(T / P))`, `P2 = T / n`, sample rate `s = P / P2`. Sample with
   `(i * s + offset)` and bilinear filtering, wrapping. Every offset is a multiple of `P`.
3. Give the instance `CellX = 4 / sx`, `CellY = 4 / sy`. Without this the pattern
   stretches by the snap factor.

## The master graph (UEFN math nodes, no Custom/HLSL)

```
P      = TexCoord * Tile * Append(CellX, CellY)
cell   = Floor(P)          f = Frac(P)
bit(v, a, b, seed) = Floor(Frac(Sine(Dot(v, (a, b)) + seed; Period 6.2831853) * 43758.5453) * 2)
top    = bit(cell,        127.1, 311.7, 0.13)
bottom = bit(cell+(0,1),  127.1, 311.7, 0.13)
left   = bit(cell,        269.5, 183.3, 0.71)
right  = bit(cell+(1,0),  269.5, 183.3, 0.71)
index  = Append(left + 2*right, top + 2*bottom)
atlasUV = (f * 0.996 + 0.002 + index) * 0.25
```

Three `TextureSampleParameter2D` nodes (`Base` Color, `Rough` Masks, `Normal` Normal):
`UVs = atlasUV`, `MipValueMode = Derivative`, `DDX(UVs) = DDX(P * 0.25)`,
`DDY(UVs) = DDY(P * 0.25)`. Rough uses the R output. About 90 expressions and 230
instructions, well inside the 500 budget.

**Single-input nodes (Floor, Frac, DDX, DDY, Sine):** connect with an empty pin name
(`''`). A named pin silently stays empty and blocks launch.

Texture settings: Base `TC_DEFAULT` sRGB on, Rough `TC_MASKS` sRGB off, Normal
`TC_NORMALMAP` sRGB off. Validate with Epic `ValidateAssets`, then look at the surface
from far away and from eye height.

## What brings the grid back

| Symptom | Cause | Fix |
|---------|-------|-----|
| Regular rows of the same streaks | Edge bands too wide, so 2 strips dominate | Add per-tile centres, keep `band` near 14% of `T` |
| Same tile pattern every few cells | `Sine` left at Period 1 turns the hash periodic | Period `6.2831853` |
| Thin lines on tile borders | No explicit derivatives or no inset | Derivative mip mode, `0.996` inset |
| Mortar lines broken | Offset not on the period | Snap offsets, set `CellX/CellY` |
| Stretched bricks or planks | Snapped atlas without compensation | `CellX = 4 / sx`, `CellY = 4 / sy` |
| Black or flat surface after launch | Single-input pin given a name | Connect with `''` |

## Related

- Instances and parameters: `pbr_master_instances`
- Texture settings: `texture_import`
