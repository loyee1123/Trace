# UI-TARS-1.5-7B 集群部署 + 本地桌面客户端

三步把 UI-TARS 跑起来：集群出 GPU 算力，笔记本上的 UI-TARS Desktop 通过 SSH 隧道连过来。

## 1. 集群端：启动模型服务

```bash
sbatch /scratch4/kding1/Trace/uitars/serve_uitars.slurm
squeue -u yluo62                     # 等 R 状态
grep "on node" logs/vllm-<jobid>.log  # 拿到 GPU 节点名，如 gpu07
tail -f logs/vllm-<jobid>.log         # 看到 "Application startup complete" 即就绪（首次加载约 2-3 分钟）
```

## 2. 笔记本端：开 SSH 隧道

```bash
ssh -N -L 8000:<GPU节点名>:8000 yluo62@<集群登录节点地址>
```

保持这个终端开着。验证：浏览器打开 http://localhost:8000/v1/models 能看到 `ui-tars-1.5-7b`。

## 3. 笔记本端：装 UI-TARS Desktop 并连接

1. 从 https://github.com/bytedance/UI-TARS-desktop/releases 下载安装（Windows .exe / macOS .dmg）。
2. 打开 Settings，VLM 配置填：
   - **VLM Provider**: 兼容 OpenAI 的选项（vLLM / Hugging Face for UI-TARS-1.5）
   - **VLM Base URL**: `http://localhost:8000/v1`
   - **VLM API Key**: 随便填（如 `empty`，vLLM 不校验）
   - **VLM Model Name**: `ui-tars-1.5-7b`
3. 授予屏幕录制/辅助功能权限（macOS 会弹窗），然后用自然语言下任务。

## 注意

- 模型权重在共享 HF 缓存（HF_HOME=/scratch4/kding1/huggingface/hf-home），不入 git。
- slurm 任务默认 8 小时后释放 GPU；用完 `scancel <jobid>`。
- 若 vLLM 报 `--limit-mm-per-prompt` 参数格式错误，改成 `--limit-mm-per-prompt image=10`（旧版语法）。
- 首次任务建议低风险：让它开浏览器查天气之类；不可逆操作（发送/删除/支付）开确认。
