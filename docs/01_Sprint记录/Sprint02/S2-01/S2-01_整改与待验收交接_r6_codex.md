# S2-01 整改与待验收交接 r6（当前 r7/r4 证据）

```yaml
issue_id: S2-01
stage: implementation
batch_id: implementation-S2-01-remediation-r4-20260803
design_batch_id: design-plan-S2-01-remediation-r7-20260803
stage_model: gpt-5.6-terra
review_required: false
review_exemption: "当前用户指令：terra模型不需要评审"
evidence_owner: stage-executor
result: pass
handoff: 待验收
```

## 整改结论

`S2-01_设计实施评审_v1_codex.md` 指出的四项问题已逐项关闭，且没有通过补写评审结论掩盖证据缺口：本批次以用户明确的 Terra 免评审指令运行，执行保证 helper 对阶段执行者证据的 `validate`、`verify`、`adjudicate` 均返回 `pass`。r5/r2 曾在 issue worktree 通过，但其 CRLF 原始摘要不能在合并后的 LF checkout 重现；r7/r4 已以 LF 重新冻结并替代它们，并将 pytest 候选命令固定为显式隔离项目未使用 `pytest-subtests` 的环境。历史退出滞留观察不作为已确认因果归因；当前默认自动加载对照也正常退出。

| 原问题 | 整改与证据 | 结论 |
|:---|:---|:---|
| Important-1：质量门禁范围与实际不一致 | `.venv` Ruff 对 `src/custom_logger/manager.py`、目标测试、runtime oracle 执行 `check` 与 `format --check` 均通过 | 已关闭 |
| Minor-2：结构行数保留 `pending_design_review` | 主设计和矩阵记录 `verify_s2_01_contract.py=32`、`manager.py=461`、runtime oracle `=142` 的实际物理行数 | 已关闭 |
| Minor-3：freeze 重复登记同一资产 | r7 freeze 只含四个唯一 oracle 路径，manifest/freeze 摘要一致 | 已关闭 |
| predicate-only runtime 证据不足 | 新增 `verify_s2_01_runtime.py`，直接调用生产 `init_custom_logger_system`，覆盖 display、bad-display、queue、bad-queue | 已关闭 |
| 合并后 raw SHA 漂移 | `verify_display_normalization.py` 以 LF 原始字节 `d33fb9d...` 重算清单和冻结，在 issue 与主仓库都可验证 | 已关闭 |

## 当前证据

- manifest SHA：`bca075e7d4f3389ae1c5ed03a3e6747b62bc60b12a3c01842808c24b3fd9d20d`
- r7 freeze SHA：`ad78c479d6d4e4485d264b3754344741b53bd0c5f0d0e28c7d46f14bcb59c7b7`
- r7 stage-executor evidence SHA：`1b480b565e44b775a2a469855adb31d722e5b46bbd41a855af14700b115e059d`
- r4 implementation evidence SHA：`1010dcdc39d491e12ff81ab3d77be0411db810b92c647b1cee7a34832423de22`
- `validate_execution_assurance.py validate`、`verify`、`adjudicate`：均为 exit `0`、`status=pass`、`errors=[]`。

| 验证范围 | 最新结果 |
|:---|:---|
| S2-01 目标测试 | `9 passed` |
| 队列/普通初始化回归 | `10 passed` |
| 受影响联合回归 | `19 passed` |
| pytest 运行环境 | 候选命令显式 `-p no:subtests`；项目目标用例不使用该外部插件，三条命令与当前默认自动加载对照均正常退出 |
| 直接生产 runtime oracle | display `4` 个边界；queue success/failure 各 `1` |
| 正反控制 | 正控制通过；bad-display、bad-queue、bad-contract 等反控制均预期 exit `1` |
| 质量 | Ruff check 通过；`3 files already formatted` |
| 设计符合性 | 方案 A、约束、AC、涉及文件均为 `pass`；未触及 writer/queue 配置契约、公共 API、ADR、前端或 Skill |

## 残余风险

完整套件的实测结果为 `212 passed, 3 skipped, 13 failed`。13 个失败与历史基线同类：5 项 TC0021 `invalid_level` 序列化配置、7 项 TC0022 固定 `/mnt/ntfs` 子进程导入路径、1 项 Mock logger 类型要求。它们不是本次目录显示、queue 时序、Ruff 整改或 runtime oracle 引入的新增失败，仍须在验收时显式接受或另行登记。

## 待验收范围

验收应确认初始化成功提示中的目录以单一目录分隔符结束、完整日志与 warning 日志文件名仍在消息中、已有尾分隔符不重复、普通与 queue 初始化的成功/失败时序保持。当前 Sprint 运营状态可更新为 `待验收`，但本交接不把 issue 标为 `已完成`。
