# S2-01 设计实施评审报告（r5 codex）

## 评审结论

**结论：⚠️ 需修复后合并/验收。**

S2-01 的业务实现本身符合批准方案：初始化成功提示在 Windows 与当前目标环境下追加一个目录分隔符，已有尾分隔符不重复，配置原值、普通/队列初始化参数和成功/失败时序保持不变。正式 issue worktree 中目标测试、队列回归和联合回归均通过。

但是，设计阶段明确冻结的质量检查范围包含 `src/custom_logger/manager.py`，而正式 `issue/S2-01` worktree 使用的 Ruff 0.16.1 对该文件报告 10 个错误；实施记录只检查了目标测试文件，并将质量结果写成通过。因此当前“设计/实施质量门禁全部通过”的结论不可在正式 worktree 中复现，必须先修正质量门禁口径或补齐代码质量整改，再作为完整评审通过交接验收。

## Findings First

### Important-1：设计质量检查范围与实施证据不一致，正式 issue worktree 的 manager 检查失败

- **位置**：`docs/01_Sprint记录/Sprint02/S2-01/S2-01_设计.md:228-233` 要求质量层执行 `ruff check src/custom_logger/manager.py tests/01_unit_tests/test_tc0030_init_log_path.py`；`docs/01_Sprint记录/Sprint02/S2-01/S2-01_实施记录.md:79-92` 却把 `quality_scope` 缩为 `tests/01_unit_tests/test_tc0030_init_log_path.py`。
- **独立证据**：在正式 `D:/Tony/projects2025/custom_logger/.worktrees/S2-01` 中执行 `.venv/Scripts/python.exe -m ruff check src/custom_logger/manager.py tests/01_unit_tests/test_tc0030_init_log_path.py`，Ruff `0.16.1` 返回码 `1`，报告 10 个错误，涉及 import 排序、裸 `except`/吞异常、Optional 类型标注和无效 `global` 声明（`manager.py:2-10,132-136,154,285,303,353`）。同一 worktree 的 format check 返回 `0`；只检查目标测试文件返回 `0`。
- **影响**：设计文档中的质量门禁和实施报告中的“质量检查通过”不是同一范围/解释器下的可复核事实。虽然这些 lint 错误大多是 `manager.py` 的既有基线问题，未造成 S2-01 目标行为失败，但它们使当前批次不能声称满足设计 §9 的完整质量判据，也使主工作树使用 Ruff `0.15.11` 得到的 `0` 与 issue worktree 的正式结果发生工具版本漂移。
- **修复建议**：在 issue 级别固定 Ruff 版本和质量范围；二选一并写回设计、实施记录、验收矩阵和评审证据：
  1. 按设计范围修复/抑制 `manager.py` 的 10 个 lint 问题，并在 issue worktree 重新执行 check/format；或
  2. 明确 S2-01 只对本批次实际修改的目标测试执行质量门禁，把 `manager.py` 的既有 lint 基线列为独立残余风险，不再把设计 §9 写成包含 manager 的通过结论。
  任何选择都需要重新生成受影响的评审证据摘要；不能用另一解释器的通过结果替代正式 issue worktree 结果。

### Minor-1：主设计仍保留已过期的结构行数占位

- **位置**：`docs/01_Sprint记录/Sprint02/S2-01/S2-01_设计.md:318-335` 对 `verify_s2_01_contract.py` 保留 `actual_lines: pending_design_review` 和 `delta_lines: pending_design_review`，并写着“实施阶段回填”。
- **影响**：当前实现和实施评审已经结束，但设计结构证据仍是不完整占位；实际脚本为 32 行，不能与结构质量“complete”声明形成闭环。
- **修复建议**：回填真实物理行数与差值（或明确标记该字段不适用），并同步需要引用该设计摘要的证据文件；随后重跑确定性校验。

### Minor-2：freeze sidecar 对同一个 oracle 资产重复登记三次

- **位置**：`docs/01_Sprint记录/Sprint02/S2-01/技术验证/freeze/design-plan-S2-01-remediation-r4-20260803.freeze.json:11-27` 中 `verify_s2_01_oracles.py` 出现三条完全相同的 `path`/`sha256` 记录。
- **影响**：`validate`/`verify` 当前仍返回 `0`，功能和摘要一致性没有被破坏；但侧车没有 criterion 标识，重复项无法区分是 AC-01/02/03 的引用还是误写，降低审计可读性并增加后续摘要漂移风险。
- **修复建议**：由 freeze 生成器去重资产路径，或保留每个 AC 的引用 ID 而不是无标签重复项；修改后重新计算 freeze/evidence digest 并重跑 `verify`/`adjudicate`。

### Minor-3：正向 oracle 主要验证复制的局部谓词，不直接执行生产 manager

- **位置**：`docs/01_Sprint记录/Sprint02/S2-01/技术验证/verify_s2_01_oracles.py:18-24` 重新实现 `normalize_display`/`raw_display`，`33-39` 重新构造成功提示，`41-72` 只对该本地 prompt factory 做 queue 正反控制。
- **影响**：这些控制能区分已知的 raw-display/bad-queue 反例，但 oracle 自身不调用 `src/custom_logger/manager.py`；若生产调用点、logger 级别或路径传递发生其他偏离，oracle 仍可能通过。目标 pytest 的 9/10/19 真实测试弥补了主要行为证据，因此该问题不阻断功能合并，但不应把 oracle 单独描述为生产实现的独立证明。
- **修复建议**：保留当前 predicate 作为纯逻辑控制时，在验收矩阵中明确其 `predicate-only` 性质；另增加一个不 mock 生产初始化的轻量 oracle，或让静态 oracle 至少校验实际调用点/参数契约。

## 评审范围

- **实现基线**：当前主工作树 `sprint02` 的 `HEAD=89c7f25`（S2-01 合并提交）；实现历史包含 `788c240` 的生产改动和 `e71c5ac` 的失败安全清理整改。
- **正式实施目标**：`D:/Tony/projects2025/custom_logger/.worktrees/S2-01`，分支 `issue/S2-01`，解释器 `.venv/Scripts/python.exe`（Python 3.12.9）。
- **读取内容**：S2-01 原始需求、方案决策、主设计、实施记录、验收追踪矩阵、闭环台账、冻结 manifest/freeze/evidence、生产 `manager.py`、目标/回归测试、三个验证脚本和历史评审报告。
- **当前主工作树脏改动**：`config.py`、`logger.py`、`test_tc0022*`、`test_tc0023*`、旧文档、缓存及未跟踪文件均未触及 S2-01 生产文件或 `test_tc0030`；它们只作为完整套件环境背景检查，不归因于 S2-01。

## 需求与实现核对

| 检查项 | 结果 | 证据 |
|---|---|---|
| 显示规范化 | pass | `src/custom_logger/manager.py:117-121` 使用 `str(log_dir).rstrip("/\\") + os.sep`，仅用于成功提示 |
| 原始配置/路径契约 | pass | `manager.py:80/99/104/108` 仍把原始 `log_dir` 传给 receiver/writer；目标参数化测试比较配置值未改变 |
| 普通/队列成功失败时序 | pass | 目标 queue success/failure E2E 和既有 `tc0018` 回归均通过 |
| 固定日志契约 | pass | `logger.info`、`full.log`、`warning.log` 和失败消息仍存在；contract oracle 正向通过、bad-contract 反向失败 |
| 测试失败安全清理 | pass（本批次范围） | `test_tc0030` 前三个历史用例在 `try/finally` 中 teardown；目标/联合命令通过 |
| 设计结构证据 | ⚠️ | `verify_s2_01_contract.py` 行数仍为 pending，占位需回填 |
| 质量门禁 | ⚠️ | 正式 issue worktree 对设计声明的 manager+test 范围 Ruff check 失败；目标测试单文件 check 通过 |

## 新鲜验证证据

以下命令均在本轮重新执行并读取退出码：

| 验证 | 命令/环境 | 结果 |
|---|---|---|
| 目标测试 | `.worktrees/S2-01/.venv/Scripts/python.exe -m pytest tests/01_unit_tests/test_tc0030_init_log_path.py -q -p no:cacheprovider` | `9 passed` |
| 队列/普通回归 | 同一解释器运行 `test_tc0018_enable_queue_mode_config.py` | `10 passed` |
| 联合回归 | 两个目标文件联合执行 | `19 passed` |
| 显示规范化脚本 | `verify_display_normalization.py` | exit `0`，四种输入均输出一个 native separator |
| display oracle | `verify_s2_01_oracles.py --mode display` | exit `0`，`display_cases=4` |
| queue oracle | `verify_s2_01_oracles.py --mode queue` | exit `0`，`queue_success=1 queue_failure=1` |
| contract oracle | `verify_s2_01_contract.py --mode contract --root .` | exit `0`，`contract_patterns=4` |
| 反向控制 | `--mode bad-display`、`--mode bad-queue`、`--mode bad-contract` | 均按预期 exit `1` |
| assurance validate | `validate_execution_assurance.py validate` | exit `0`，manifest digest `17e01d8a...` |
| assurance verify | `validate_execution_assurance.py verify` | exit `0`，`errors=[]` |
| assurance adjudicate | `validate_execution_assurance.py adjudicate` | exit `0`，`reviewed_batch_id=implementation-S2-01-remediation-r1-20260803` |
| 正式 issue Ruff | `.venv/Scripts/python.exe -m ruff check manager.py test_tc0030...` | exit `1`，10 个 manager 基线错误（见 Important-1） |
| 正式 issue format | `.venv/Scripts/python.exe -m ruff format --check manager.py test_tc0030...` | exit `0` |
| 完整套件（主工作树脏状态） | `PYTHONDONTWRITEBYTECODE=1 D:/anaconda3/envs/base_python3.12/python.exe -m pytest tests -q -p no:cacheprovider` | exit `1`，`230 passed, 3 skipped, 14 failed`；失败涉及脏工作树中的配置、线程清理、Mock、warning stack trace，不归因于 S2-01 |

## 评审汇总

- Critical: `0`
- Important: `1`
- Minor: `3`
- 业务功能：通过。
- 设计/实施质量门禁：需修复后重新评审；不能把主工作树 Ruff 通过或历史报告中的 `212/3/13` 当作当前正式 issue worktree 的完整证据。
- 当前阶段：保持 `待验收`，在 Important-1 的质量口径/实现整改和 Minor 文档修复完成前，不应更新为 `已完成`。

## 结构化结果

```text
=== 代码评审完成 ===

评审执行者：main-agent-inline
评审范围：HEAD 89c7f25 的 S2-01 合并实现 + issue/S2-01 完整设计/实施证据；当前工作树无关改动仅作残余风险背景
变更文件：S2-01 生产/测试 2 个，issue 设计/实施/验证资产全量读取

评审结论：⚠️ 需修复后合并

问题汇总：
- Critical: 0
- Important: 1
- Minor: 3

验证证据：目标 9/9、队列 10/10、联合 19/19；正向 oracle exit 0；反向控制 exit 1；assurance validate/verify/adjudicate exit 0；正式 issue manager+test Ruff exit 1；完整套件 230/3/14（主工作树脏状态）
下一步：统一并修复正式 issue worktree 的质量门禁口径，回填设计结构字段、整理 freeze 资产，再重新执行完整评审后交接 acceptance。
```
