#!/usr/bin/env bash
set -euo pipefail
# Project-local toolchain/sysroot provisioned during M0. No upstream source patch.
repo_dir="$(cd "$(dirname "$0")/../.." && pwd)"
spike_dir="${MYAI_M0_DIR:-$(dirname "$repo_dir")/.m0}"
export CARGO_HOME="$spike_dir/toolchain/cargo"
export RUSTUP_HOME="$spike_dir/toolchain/rustup"
export PATH="$CARGO_HOME/bin:$PATH"
export CC="$spike_dir/sysroot/usr/bin/aarch64-linux-gnu-gcc-14"
export CXX="$spike_dir/sysroot/usr/bin/aarch64-linux-gnu-g++-14"
export PKG_CONFIG_PATH="$spike_dir/sysroot/usr/lib/aarch64-linux-gnu/pkgconfig"
export LIBRARY_PATH="$spike_dir/sysroot/usr/lib/aarch64-linux-gnu"
export JAN_ENGINE_BUILD_DIR="$spike_dir/jan-gcc14"
export CARGO_BUILD_JOBS=3
test -x "$CC"
test -x "$CXX"
cd "$repo_dir"
# GCC 13 cannot build upstream's ARM SME variant. GCC 14 does. Jan's late
# archive group comes after libgcc; force these AArch64 helpers to be selected.
cargo rustc --locked \
  --manifest-path src-tauri/plugins/tauri-plugin-llamacpp/Cargo.toml \
  --bin jan-llama-worker --features engine -- \
  -C link-arg=-Wl,-u,__aarch64_swp4_acq_rel,-u,__aarch64_ldset4_relax \
  -C link-arg=-lgcc
