# S2-01 设计实施评审报告（v1 codex）

## 评审结论

**结论：⚠️ 需修复后合并/交接。**

S2-01 的生产实现行为与批准方案一致，目标测试和受影响回归均通过；但当前执行保证清单无法通过仓库现行的确定性校验，且缺少可定位的冻结侧车文件。现有 `S2-01_设计评审_r2_codex.md` 与 `S2-01_实施评审_r3c_codex.md` 中的 `pass`/`frozen` 不能作为当前阶段门禁证据。应先修复设计批次的 assurance 资产并重新冻结，再进行一次新的 implementation recheck；本报告不更新 Sprint 状态，也不替代用户验收。

## 问题（findings first）

### Important-1：执行保证清单未通过确定性 schema/门禁校验，当前阶段不能放行

- **位置**：
  - `docs/01_Sprint记录/Sprint02/S2-01/S2-01_执行保证清单.json:2-12`：没有 `contract_version`，`risk_modifiers` 也没有对应的 `risk_sources[].source_locator`。
  - `.../S2-01_执行保证清单.json:14-85`：AC-S2-01-01 至 AC-S2-01-03 的 `evidence_grade_required` 为 `business_outcome`，但缺少契约要求的 `positive_control`；`baseline.applicable=false` 使用了 `reason`，而当前校验器要求非空 `not_applicable_reason`。
  - `.../S2-01_执行保证清单.json:87-104`：AC-S2-01-04 的 `oracle_assets` 为空，当前校验器要求每条 oracle 都有非空资产列表。
- **证据**：在 issue worktree 使用其隔离解释器执行：

  ```text
  ./.venv/Scripts/python.exe D:/Tony/ubuntu_settings/.claude/skills/resources/helpers/validate_execution_assurance.py validate \
    --root D:/Tony/projects2025/custom_logger/.worktrees/S2-01 \
    --manifest docs/01_Sprint记录/Sprint02/S2-01/S2-01_执行保证清单.json
  ```

  返回码为 `2`（`protocol_failure`）。输出明确列出：`contract_version` 缺失、风险修正项缺少 `source_locator`、AC-01~03 缺少 `positive_control`、三项 baseline 缺少 `not_applicable_reason`、AC-04 `oracle_assets` 为空。主路径执行同一校验同样返回 `2`，另外报告了 CRLF 造成的资产摘要不一致。
- **影响**：当前 `S2-01_设计.md:125-139`、`S2-01_实施记录.md:18-30`、`S2-01_验收标准追踪矩阵.md:25-38` 所声明的 assurance freeze/batch gate 无法由现行确定性执行器验证；根据执行保证契约，不能继续 acceptance handoff、合并或将其视为“可验收”。
- **修复建议**：回到 design-plan 创建新的设计批次，补齐上述字段和可执行正向控制，统一使用 `not_applicable_reason`，为 AC-04 提供稳定的 oracle 资产并记录 digest。先运行 `validate`、正向控制和反向控制，通过后生成新的 freeze 侧车；不要在 implementation 阶段直接同步修改已冻结清单。

### Important-2：冻结资产的侧车与所有权证据缺失，且实施记录显示可能在 implementation 阶段改写 oracle

- **位置**：
  - `docs/01_Sprint记录/Sprint02/S2-01/S2-01_设计评审_r2_codex.md:151-164` 只在 Markdown 中嵌入 `assurance_freeze` 摘要；仓库中没有与该批次对应的冻结 JSON 侧车或 Reviewer-owned execution-evidence 文件。
  - `docs/01_Sprint记录/Sprint02/S2-01/S2-01_实施记录.md:18-30` 将 manifest/oracle 标为 `frozen`，但 `:33-40` 又把 `S2-01_执行保证清单.json`、`S2-01_验收标准追踪矩阵.md` 和 `技术验证/verify_s2_01_oracles.py` 列为 implementation 范围内的“补齐”产物。
  - Git 证据：提交 `1cd1283` 同时新增执行保证清单和 `verify_s2_01_oracles.py`，而当前实现阶段记录引用同一批次的 freeze 输入。
- **契约依据**：`D:/Tony/ubuntu_settings/.claude/skills/references/execution-assurance-contract.md:140-157` 要求设计 Reviewer 用 `freeze` 生成只写一次的侧车；清单、解析器、反例和 oracle 资产由 design-plan 所有，implementation 只能只读消费，不能回写冻结清单或 oracle 资产。放行还要求实际 freeze、所有 digest 一致以及 Reviewer 重跑 `verify`/`adjudicate`（同文件 `:204-215`）。
- **影响**：当前 `status: frozen` 只有文档摘要，没有可复核的冻结对象；如果清单/资产是在 implementation 闭环中补写，implementation 的输入边界和设计冻结顺序不可证明，现有 `blocking_count: 0` 属于治理证据不足而不是已验证通过。
- **修复建议**：由 design-plan 生成新的、版本化且不存在同名覆盖的 freeze 侧车及设计执行证据，保留 manifest/oracle 的最终 digest；随后以新的 implementation recheck 批次只读消费它们，执行 `verify`、全部候选正向/反向命令和 `adjudicate`，并在矩阵/台账中引用侧车路径和摘要。

### Important-3：冻结摘要对换行格式敏感，主路径无法复现 issue worktree 的声明 digest

- **位置/证据**：当前 Git 配置 `core.autocrlf=true`。主路径文件为 CRLF，直接 `sha256sum` 得到：

  | 资产 | 文档/issue worktree 声明 | 主路径实际字节摘要 |
  |---|---|---|
  | `S2-01_执行保证清单.json` | `9be1a1e6f2538a1b719020fac20fd9a17e3352ef8e319a0abaac417b8582d994` | `048c9122e20ee45458d76c1336ee3a6a0c145dbf5c8d5b4748872cd57dbaa685` |
  | `技术验证/verify_s2_01_oracles.py` | `55b582ef53ada7d9008a41579dff992f3149f0d2137c05b62b0883363f3760cf` | `ef8cfd0678503e1f545fe16c57fb701944066851ba4da828cce320560c7ca6d4` |
  | `S2-01_设计评审_r2_codex.md` | `532b49137e4d62d8300612502b9ebd30d76491a72d31c23b330c3e6f561258a9` | `aa94b9a7ea90c66e2acb3d0e53f78d6ac52768d1d0e81e48e96ac43d018b05a8` |
  | `S2-01_实施评审_r3c_codex.md` | `665473fce6f226c006a220a3f048712617955d2fb935d82b97ce904c5bd65998` | `5863eae6503dbcaf0ca5a00069110053be6105397f288f549179445024c2ccbd` |

  `cmp` 证明生产文件和目标测试在主路径与 issue worktree 内容相同；差异来自文本换行字节。issue worktree 的 LF 字节摘要与 Git blob 一致，主路径 CRLF 摘要则不同。
- **影响**：功能行为不受 CRLF/LF 影响，但直接按工作树字节计算的 digest 会因 checkout 方式变化，导致主路径 implementation gate 误报 digest mismatch，无法稳定复核冻结证据。
- **修复建议**：在契约/校验器中明确摘要的规范化方式（例如对 UTF-8 文本先统一为 LF，或对 Git blob 计算摘要），并让报告、manifest、freeze 侧车和校验器统一使用该算法；随后在新设计批次中重新计算所有依赖摘要。不要只把主路径摘要手工替换成“看起来一致”的值。

### Minor-1：前置测试的全局状态/资源清理不是失败安全的

- **位置**：`tests/01_unit_tests/test_tc0030_init_log_path.py:15-52`、`:54-84`、`:86-120` 在断言前直接重置 `_initialized`，清理代码位于断言之后且没有 `try/finally`。同文件新增的参数化和 queue E2E 用例 `:147-159`、`:200-204` 已使用失败安全的清理方式，但前三个历史用例仍可能留下 writer 状态或文件句柄。
- **影响**：单个断言失败时，后续测试可能继承错误的全局 logger 状态，造成顺序相关或资源泄漏；本次 `9/9` 绿测不能证明失败路径下的隔离性。
- **修复建议**：为整个测试类提供统一 fixture，在 setup 前调用 teardown/reset，在 fixture finalizer 中无条件关闭 writer/queue 并恢复 `_initialized`/`_queue_mode`；至少将前三个用例的初始化和断言包在 `try/finally` 中。

## 通过项与验证证据

### 业务行为与范围

- 方案决策 `#5/#6/#8/#10` 与当前代码一致：`src/custom_logger/manager.py:117-121` 仅在成功提示边界生成 `str(log_dir).rstrip("/\\") + os.sep`，原始 `log_dir` 仍传给 writer/receiver，`logger.info`、两个文件名和错误处理未被移动。
- 主路径与 issue worktree 的 `manager.py`、`test_tc0030_init_log_path.py` 内容相同；当前工作树其他 `config.py`、`logger.py`、测试和文档变更属于用户已有的非 S2-01 修改，本报告未将其归因于本 issue。

### 新鲜命令结果

| 检查 | 命令/环境 | 结果 |
|---|---|---|
| 目标 E2E | `/d/anaconda3/envs/base_python3.12/python.exe -m pytest tests/01_unit_tests/test_tc0030_init_log_path.py -q -p no:cacheprovider`（主路径） | `9 passed` |
| 队列/普通回归 | 同一解释器运行 `test_tc0018_enable_queue_mode_config.py` | `10 passed` |
| 联合回归 | 两个目标测试文件联合运行 | `19 passed` |
| 正向 oracle | `verify_s2_01_oracles.py --mode display`、`--mode queue` | 分别 `display_cases=4`、`queue_success=1 queue_failure=1`，退出码 `0` |
| 反向控制 | `--mode bad-display`、`--mode bad-queue` | 均退出码 `1`，反例按预期失败 |
| 显示规范化脚本 | `verify_display_normalization.py` | `display_normalization=PASS` |
| Ruff | `python.exe -m ruff check ...manager.py ...test_tc0030...` | `All checks passed`，Ruff `0.15.11` |
| 格式 | `python.exe -m ruff format --check ...` | `2 files already formatted` |
| 差异空白 | `git diff --check`（目标生产/测试文件） | 退出码 `0` |
| 完整套件 | issue worktree `.venv/Scripts/python.exe -m pytest tests -q -p no:cacheprovider` | `212 passed, 3 skipped, 13 failed`；失败与 S2-01 目标行为无关，但仍是 acceptance 残余风险 |
| 确定性 assurance 校验 | issue worktree `.venv/Scripts/python.exe validate_execution_assurance.py validate ...` | 退出码 `2`，见 Important-1 |

## 问题汇总

- Critical：`0`
- Important：`3`
- Minor：`1`

## 下一步

1. 由 design-plan 新建 remediation 设计批次，修复 manifest schema、正向控制、baseline 字段、资产摘要算法和风险来源定位。
2. 使用确定性执行器成功完成 `validate`、正/反向控制和 `freeze`，将版本化 freeze 侧车与 Reviewer-owned execution evidence 纳入 issue 目录。
3. 由 implementation 只读消费新的 freeze，运行 `verify`、候选正向/反向命令、正式规模检查和 `adjudicate`；重新读取完整设计与实施差异后再评审。
4. 修复或隔离 `test_tc0030` 的失败安全清理；完整套件的 13 个既有失败继续作为 acceptance 风险单独记录，不得改写成全套通过。

## 评审结构化结果

```text
=== 代码评审完成 ===

评审执行者：main-agent-inline
评审范围：主路径已合并 S2-01（HEAD 151ee74，S2-01 生产/测试与 issue 证据目录）；排除工作树中与 S2-01 无关的既有修改
变更文件：S2-01 目标生产/测试 2 个，issue 设计/实施/验收/验证证据全量读取

评审结论：⚠️ 需修复后合并

问题汇总：
- Critical: 0
- Important: 3
- Minor: 1

验证证据：目标 `9/9`、队列回归 `10/10`、联合 `19/19`；正向 oracle 退出 `0`；反向控制退出 `1`；Ruff check/format 退出 `0`；完整套件 `212/3/13`；确定性 assurance validate 退出 `2`。
下一步：修复新的 design batch/冻结证据后，重新执行 implementation recheck；当前不能交接 acceptance。
```
