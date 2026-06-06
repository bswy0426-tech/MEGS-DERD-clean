# Depth Estimation Error Experiment

This note describes the experiment for checking how DERD-Net depth errors affect
the final MEGS reconstruction.

## Goal

The purpose is to show whether MEGS is robust when the depth prior is imperfect.
DERD-Net depth is used as a pseudo-depth prior, so the paper should not imply
that it is ground-truth depth. This experiment perturbs the estimated depth and
then compares rendering quality and trajectory accuracy.

## Experiment Variables

Use the same dataset sequence, random seed, and training schedule as the main
experiment. Change only the `depth_error_exp` field in the YAML config.

### Relative Gaussian Noise

```yaml
depth_error_exp:
  enable: true
  mode: gaussian_rel
  sigma: 0.05
```

Run several levels, for example `0.05`, `0.10`, and `0.20`.

### Scale Bias

```yaml
depth_error_exp:
  enable: true
  mode: scale
  scale_factor: 1.10
```

Run both under-estimation and over-estimation, for example `0.90`, `1.10`, and
`1.20`.

### Depth Dropout

```yaml
depth_error_exp:
  enable: true
  mode: dropout
  dropout_ratio: 0.30
```

Run several missing-depth levels, for example `0.10`, `0.30`, and `0.50`.

## Recommended Table

Report PSNR, SSIM, LPIPS, and ATE.

| Setting | PSNR up | SSIM up | LPIPS down | ATE down |
| --- | ---: | ---: | ---: | ---: |
| Clean DERD-Net depth |  |  |  |  |
| Gaussian noise 5% |  |  |  |  |
| Gaussian noise 10% |  |  |  |  |
| Gaussian noise 20% |  |  |  |  |
| Scale 0.90 |  |  |  |  |
| Scale 1.10 |  |  |  |  |
| Dropout 30% |  |  |  |  |

## Paper Wording

Use conservative wording:

> We perturb DERD-Net depth estimates with relative noise, scale bias, and
> random dropout to evaluate sensitivity to depth-prior errors. The results show
> that moderate perturbations mainly degrade trajectory stability, while severe
> depth corruption can also reduce rendering quality. This confirms that
> DERD-Net depth is useful as a geometric regularizer, but MEGS remains sensitive
> to the quality and weighting of the pseudo-depth prior.

Avoid saying that the depth prior completely solves scale drift or guarantees
metric accuracy.
