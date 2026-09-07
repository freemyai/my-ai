# ADR 0004 — Build the upstream Jan worker with a scoped ARM64 toolchain

Status: accepted for M0 CPU spike, not a shipping packaging decision.

Jan main's native engine builds all ARM CPU variants, including SME. On Spark's
Ubuntu 24.04 GCC 13, compilation fails on the `sme` architecture modifier.
Project-local GCC 14.2.0 compiles these variants without changing upstream code.
The final Rust executable initially fails to link two outline atomic helpers:
`__aarch64_swp4_acq_rel` and `__aarch64_ldset4_relax`. The native archive group is
emitted after libgcc. Explicit linker undefined-symbol flags plus `-lgcc` resolve
this; the executable then loads the ARMv8.6 CPU backend and serves a real model.

Use `scripts/m0/build-jan-worker.sh`. Keep root Jan source, native shim and pinned
llama.cpp unchanged. Build dependencies were downloaded as Ubuntu packages and
extracted into `../.m0/sysroot`, not installed system-wide. Rust is project-local.
The WebKit development metadata is 2.44.0, while installed runtime libraries are
newer: this is a development workaround, not a redistributable sysroot.

Evidence: local `../.m0/jan-worker-link2.log` and its result JSON; real inference
fingerprint `b10621-c1d0e7a004015f23bc0233470b747b596f29b264`.

This proves worker feasibility, not the complete Jan desktop build, installer,
GPU backend or long-running stability. Do not present CPU smoke throughput as a
product benchmark. Production needs a supported toolchain matrix and packaging
review; an upstream issue/PR may be proposed separately, not silently submitted.
