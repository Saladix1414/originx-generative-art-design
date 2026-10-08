# OriginX Hardware Detection — Phase 5

## Status

PHASE 5 establishes the hardware-observation and capability-classification boundary for OriginX Generative Art Engine.

Hardware detection is descriptive.

It does not authorize model execution.

```text
HARDWARE AVAILABILITY != EXECUTION AUTHORITY
```

## Canonical versions

- OX-HARDWARE-PROFILE-1
- OX-HARDWARE-DETECTOR-1
- OX-HARDWARE-EVIDENCE-1

## Responsibilities

The hardware layer may observe:

- platform and architecture
- CPU topology and features
- total memory capacity
- swap capacity
- storage capacity
- relevant device nodes
- acceleration API probes
- runtime/tool presence
- local execution capability evidence

The hardware layer may classify:

- LOCAL_CPP
- LOCAL_GPU
- ORIGINX_GPU
- EXTERNAL_PROVIDER

Capability states are:

```text
CONFIRMED
UNAVAILABLE
UNKNOWN
```

UNKNOWN is a valid first-class result and must not be promoted to CONFIRMED without evidence.

## Observation and classification

OriginX separates:

```text
OBSERVATION -> CLASSIFICATION
```

The same observation must always produce the same classification.

Live observations themselves are not required to remain byte-identical across time.

## CPU capability

A supported native architecture with observable CPU and memory evidence may establish descriptive LOCAL_CPP capability.

This still does not authorize model execution.

## GPU capability

A GPU-related device node alone is insufficient evidence for local GPU inference.

```text
DEVICE NODE != GPU INFERENCE PROOF
```

Observing /dev/dri/card0 does not by itself establish a usable Vulkan, OpenCL, CUDA, ROCm or model-inference path.

A successful supported acceleration API probe may establish descriptive GPU capability.

That capability remains separate from execution authority.

## Volatile observations

The following live values are intentionally excluded from the stable PHASE 5 evidence hash:

- memory.availableBytes
- memory.swapFreeBytes
- storage.freeBytes

These values change with system activity and are observations rather than reproducibility anchors.

Total hardware capacities may be retained in closure evidence.

## Runtime packages

Installed runtime packages are descriptive evidence only.

The presence of Torch, TensorFlow, ONNX Runtime, NumPy, Vulkan bindings or similar software does not authorize inference.

PHASE 5 installs no model runtime.

## Remote capability

PHASE 5 does not probe or authorize:

- ORIGINX_GPU
- EXTERNAL_PROVIDER

Absent verified evidence, these remain UNKNOWN.

## Governance

The hardware profile enforces:

```text
policy = LOCAL_FIRST
hardwareAvailabilityGrantsExecutionAuthority = false
executionAllowed = false
```

Hardware detection cannot override Render Plan governance.

## Stable closure evidence

The PHASE 5 hardware snapshot is stored in:

docs/architecture/phase5d-hardware-evidence.json

It records stable closure evidence and explicitly identifies excluded volatile fields.

The snapshot is historical evidence.

It is not a runtime authorization token.

## Explicit non-goals

PHASE 5 does not implement:

- model installation
- model registry
- Stable Diffusion execution
- image generation
- LoRA execution
- ControlNet execution
- provider execution
- automatic GPU enablement
- canonical artwork approval

## Next phase

```text
PHASE 6 — OriginX Local Forge
```

The Local Forge may consume hardware capability evidence, but it must preserve the execution-authority boundary established here.
