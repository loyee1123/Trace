---
name: cluster-gpu-cuda-constraint
description: 集群 GPU 驱动上限 CUDA 12.9 + glibc 2.28，PyPI 新版 vllm 全不可用，必须走 conda-forge
metadata:
  type: project
---

2026-07-29 实测的集群硬约束（选任何推理框架前先对照）：

- **三个 GPU 分区（a100 / ica100 / l40s）驱动全是 575.51.03**，最高支持 CUDA 12.9；CUDA 13 构建的程序一律报 "NVIDIA driver too old (found version 12090)"
- **系统 glibc 2.28**（CentOS 8）：PyPI 上 vllm 0.12–0.19 的轮子要 glibc≥2.31 装不上；vllm≥0.21 虽然回到 manylinux_2_28 但全改 CUDA 13 构建 → **PyPI 的 vllm 没有任何可用版本**
- **出路：conda-forge**（面向 glibc 2.28 编译且有 cuda129 变体）：`CONDA_OVERRIDE_CUDA=12.9 micromamba install --override-channels -c conda-forge "vllm=0.19.1=cuda129_py311*"`（`--override-channels` 必须加：defaults 频道全量 repodata 会把登录节点解析进程 OOM 杀掉；`CONDA_OVERRIDE_CUDA` 必须加：登录节点无 GPU 缺 `__cuda` 虚拟包）
- conda-forge 的 vllm **不带 CUDA 编译工具链**，GPU 节点上 Triton JIT 会缺件：还要装 `cuda-cudart-dev cuda-driver-dev cuda-nvcc-tools cuda-cuobjdump cuda-nvdisasm`（钉 `cuda-version=12.9`），slurm 里 export PATH / TRITON_PTXAS_PATH / CUDA_HOME 指向 conda env
- conda-forge vllm 0.19.1 仍捆 transformers 5.x，OpenCUA 的 5.x 兼容补丁（tokenizer + processor）依然需要（[[trace-env-opencua]]）
- vLLM 多模态注意：默认 `max_num_batched_tokens=2048` 即 encoder 缓存上限，高分屏截图（>2048 视觉 token）会 400，启动加 `--max-num-batched-tokens 20480`
- 其他备选：singularity 3.8.7 module（可跑 vllm 官方 CUDA12 镜像）；源码编译（未试，代价高）

连带教训：
- slurm 的 `--output` 必须写共享文件系统路径，登录节点的 /tmp 计算节点看不到，日志会静默丢失
- GPU 节点默认 module 的 gcc-9 libstdc++ 缺 CXXABI_1.3.15，slurm 脚本里要 `module purge` + 把 conda env 的 lib 置于 LD_LIBRARY_PATH 最前（[[trace-env-opencua]]）
- 登录节点 /tmp 里有杂散的 types.py，别在 /tmp 下直接起 python
