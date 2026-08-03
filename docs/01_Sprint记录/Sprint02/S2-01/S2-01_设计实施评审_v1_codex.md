# S2-01 设计实施评审报告（v1 codex）

## 评审结论

**结论：需修复后合并/交接。**

S2-01 的生产实现行为与批准方案一致，目标测试和受影响回归均通过；但当前执行保证清单无法通过确定性校验，且缺少可定位的冻结侧车文件。旧版设计/实施报告中的 `pass`/`frozen` 不能作为当前阶段门禁证据。应先修复 design-plan 的 assurance 资产并重新冻结，再进行新的 implementation recheck；本报告不更新 Sprint 状态，也不替代用户验收。

## 问题（findings first）

### Important-1：执行保证清单未通过确定性 schema/门禁校验

- `S2-01_执行保证清单.json` 缺少 `contract_version`，风险修正项没有对应的 `risk_sources[].source_locator`。
- AC-S2-01-01 至 AC-S2-01-03 声明为 `business_outcome`，但缺少契约要求的 `positive_control`；不可用 baseline 使用了 `reason` 而非 `not_applicable_reason`。
- AC-S2-01-04 的 `oracle_assets` 为空，校验器要求每条 oracle 有非空资产列表。
- 在 issue worktree 执行 `validate_execution_assurance.py validate` 返回 `2`（`protocol_failure`）。

**影响**：设计、实施和验收矩阵中声明的 assurance freeze/batch gate 无法由确定性执行器验证，不能继续 acceptance handoff、合并或将批次视为可验收。

**修复建议**：回到 design-plan 创建新的批次，补齐 manifest schema、正向控制、baseline 字段和 AC-04 稳定 oracle，先通过 `validate`、正向控制和反向控制，再生成新的 freeze 侧车；implementation 不得直接回写冻结清单或 oracle。

### Important-2：冻结侧车与 Reviewer-owned 证据缺失

- 旧设计报告只在 Markdown 中嵌入 `assurance_freeze` 摘要，仓库中没有该批次的冻结 JSON 侧车或 Reviewer-owned execution-evidence 文件。
- 旧实施记录将 manifest/oracle 标为 `frozen`，同时又把它们列为 implementation 阶段的补齐产物，无法证明冻结先于实施。
- 执行保证契约要求 design Reviewer 用 `freeze` 生成只写一次的侧车；implementation 只能只读消费 manifest、解析器、反例和 oracle 资产，并由独立 Reviewer 重新运行 `verify`/`adjudicate`。

**修复建议**：由 design-plan 生成版本化、不可覆盖的 freeze 侧车和设计执行证据，记录最终 digest；随后以新的 implementation recheck 只读消费，并重新运行所有命令。

### Important-3：冻结摘要受 CRLF/LF 换行影响

主路径与 issue worktree 的文本内容相同，但在 `core.autocrlf=true` 下工作树字节不同，直接对工作树原始字节计算 SHA-256 会产生不同摘要，导致主路径 implementation gate 误报 digest mismatch。

**修复建议**：明确 UTF-8 raw bytes 与 LF 的摘要政策，使用 `.gitattributes` 固定 S2-01 manifest、oracle 和设计证据行尾，并让 manifest、freeze 侧车和 Reviewer 使用同一算法重新计算摘要。

### Minor-1：前三个测试用例的资源清理不是失败安全的

`tests/01_unit_tests/test_tc0030_init_log_path.py` 的前三个历史用例在断言后才清理，未使用 `try/finally`；断言失败可能留下 writer 状态或文件句柄，造成后续测试顺序依赖。新增参数化和 queue E2E 已使用失败安全清理。

**修复建议**：至少将前三个用例的初始化和断言包在 `try/finally` 中，在 finally 中无条件关闭 writer/queue 并恢复全局状态。

## 通过项与验证证据

- `src/custom_logger/manager.py:117-121` 与批准方案一致：只在成功提示边界生成 `str(log_dir).rstrip("/\\") + os.sep`，原始目录仍传给 writer/receiver。
- 目标测试 `9 passed`，队列/普通回归 `10 passed`，联合命令 `19 passed`。
- `verify_s2_01_oracles.py --mode display` 与 `--mode queue` 退出 `0`；反向 `bad-display` 与 `bad-queue` 均退出 `1`。
- `verify_display_normalization.py` 通过；Ruff check/format 通过；`git diff --check` 通过。
- 完整套件为 `212 passed, 3 skipped, 13 failed`，失败属于既有配置/跨平台残余风险，不得改写为全套通过。
- 原始 assurance `validate` 返回 `2`，因此旧报告的 freeze 声明不能满足当前门禁。

## 问题汇总

- Critical：0
- Important：3
- Minor：1

## 下一步

1. 由 design-plan 新建 remediation 批次，修复 manifest schema、正向控制、baseline 字段、摘要算法和风险来源定位。
2. 使用确定性执行器通过 `validate`、正/反向控制和 `freeze`，并将版本化侧车与 Reviewer-owned execution evidence 纳入 issue 目录。
3. 由 implementation 只读消费新的 freeze，运行 `verify`、候选正/反向命令、正式规模检查和 `adjudicate`，再独立评审。
4. 修复 `test_tc0030` 的失败安全清理；完整套件的 13 个既有失败继续作为 acceptance 风险单独记录。
