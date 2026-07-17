# check_skill
`check-docs` 是一个面向 Markdown 技术资料的文档质量检查 Skill。它最鲜明的设计不是“大范围润色”，而是将问题严格拆成两类：

| 处理方式                     | 问题类型                                                     |
| ---------------------------- | ------------------------------------------------------------ |
| 高置信度，直接修改原文件     | 中文错别字、英文拼写错误、输入造成的重复字词、中文语句中的多余空格、明显标点错误 |
| 涉及语义或表达判断，仅给建议 | 冗余表达、口语化、语句不通顺、模糊词、术语和大小写不一致、OpenHarmony 规范问题 |

核心原则可以概括为：

> 确定的低级错误直接修；存在表达偏好、上下文判断或技术语义风险的问题，先报告，再由用户决定。

## 工作流程

主流程定义在 [SKILL.md](D:\\codexprojects\\skill_learning\\docs-prompt\\skills\\check-docs\\SKILL.md)：

1. 确认用户授权范围，只处理 Markdown 文件。
2. 读取总体行为准则。
3. 按直接修改规则修复高置信度低级错误。
4. 按审查规则记录需要用户确认的问题。
5. 口语化检查必须读取完整的口语化规则，不能简单依靠关键词。
6. 涉及 OpenHarmony、术语、缩略语或大小写时，再加载术语规则。
7. 修改后检查差异，避免影响 Markdown、代码、命令、URL 和技术含义。
8. 汇总直接修改结果，逐条列出待确认问题。
9. 用户确认后，才修改第二类问题，并重新检查。

这实际上形成了一个“自动修复 → 人工确认 → 二次修改验证”的闭环。

## 规则体系

Skill 采用了模块化结构：

- [behavior-principles.md](D:\\codexprojects\\skill_learning\\docs-prompt\\skills\\check-docs\\references\\behavior-principles.md)：统一规定高置信度、最小修改、语义等价、Markdown 保护和工作区变更保护。
- [direct-fix-rules.md](D:\\codexprojects\\skill_learning\\docs-prompt\\skills\\check-docs\\references\\direct-fix-rules.md)：规定哪些低级错误可以直接修改。
- [review-rules.md](D:\\codexprojects\\skill_learning\\docs-prompt\\skills\\check-docs\\references\\review-rules.md)：统一管理需要用户决定的问题。
- [colloquial-rules.md](D:\\codexprojects\\skill_learning\\docs-prompt\\skills\\check-docs\\references\\colloquial-rules.md)：详细限定口语化问题的类型、排除项、判定流程和示例。
- [terminology-rules.md](D:\\codexprojects\\skill_learning\\docs-prompt\\skills\\check-docs\\references\\terminology-rules.md)：处理一般术语一致性和 OpenHarmony 专用规范。
- [openai.yaml](D:\\codexprojects\\skill_learning\\docs-prompt\\skills\\check-docs\\agents\\openai.yaml)：提供“资料检查”的界面名称和默认提示，不参与实际运行逻辑。

这种结构使主文件保持为“流程编排层”，详细判断规则放在 references 中，维护和扩展都比较方便。

## 安全边界

这个 Skill 对“不要改什么”规定得很严格：

- 不验证技术事实、产品能力、业务逻辑、接口定义和参数含义。
- 不检查或修改代码块、行内代码、URL、邮箱、路径、命令、参数、日志、报错信息和占位符。
- 不随意修改品牌名、包名、库名、产品名和代码标识符。
- 不把中英文之间是否留空格当作错误。
- 不跨句重写，不调整信息顺序，不补充未经原文支持的事实。
- OpenHarmony 专用规则只适用于 OpenHarmony 资料，不强加给其他项目。
- 修改前需要注意工作区已有变更，防止覆盖用户内容。

因此，它更像一个“保守型技术文档校对器”，不是一个自由改写工具。

## 相对原始 prompts 的主要优化

根据仓库根目录保留的原始分类 prompts，你的版本主要做了这些整合和改进：

1. 从多个独立 prompt 变成统一 Skill

原来的错别字、拼写、标点、冗余、口语化、模糊词和一致性检查彼此分散；现在由一个入口统一编排，同时仍保留模块化规则。

2. 从“只输出 JSON 建议”升级为实际工作流

原始 prompts 主要接收带行号的文本，然后输出 JSON。现在 Skill 可以直接处理文件、目录或 Git 变更，对确定问题直接落盘，并检查修改差异。

3. 引入清晰的人机决策边界

低级错误自动修复，可能涉及表达偏好或技术含义的问题必须由用户确认。这比所有问题都直接修改或所有问题都只报告更适合真实资料维护。

4. 强化防误改约束

新增并反复强调：

- 高置信度
- 最小更改
- 语义等价
- 不新增事实
- 不破坏 Markdown
- 不覆盖已有修改
- 修改后必须检查差异

5. 修正“建议中编造事实”的风险

原始口语化示例会把“挺方便、上手就行”改成“提供默认配置并附带说明文档”，但原文并没有这些事实。新版本明确禁止这种补写，并要求在信息不足时建议作者补充依据。

6. 缩小 OpenHarmony 规范的误用范围

原始一致性 prompt 容易把 OpenHarmony 推荐词应用到所有资料；新版本明确规定只对 OpenHarmony 相关内容应用，其他资料只检查自身上下文一致性。

7. 改善交付结果的可读性

默认不再输出 JSON，而是给出：

- 按文件汇总的直接修复数量；
- 文件路径和行号；
- 原文；
- 必要时的参考依据；
- 具体原因；
- 最小修改建议。

这更适合人与 Agent 协作审阅。
