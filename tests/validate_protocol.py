from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "review-interaction.md"
EXPECTED_NORMALIZED_FIXTURE_SHA256 = (
    "1FCE31E8E6DD3E032EB861DC24B12417D17E87BA5461004F12898F3A3B009E5E"
)


def require(text: str, fragment: str, source: str) -> None:
    if fragment not in text:
        raise AssertionError(f"{source} 缺少必要内容：{fragment}")


def main() -> None:
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    workflow = (ROOT / "references" / "decision-workflow.md").read_text(
        encoding="utf-8"
    )
    metadata = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
    fixture_text = FIXTURE.read_text(encoding="utf-8")
    normalized_fixture_bytes = fixture_text.replace("\r\n", "\n").replace(
        "\r", "\n"
    ).encode("utf-8")
    fixture_lines = fixture_text.splitlines()

    for fragment in (
        "# 第一轮：逐问题交互",
        "# 第二轮：计划确认",
        "`文件路径:行号`",
        "`文件路径:起始行-结束行`",
        "一个交互只对应一个问题 ID",
        "收到 P1 的真实回答后才能展示 P2",
        "| ID | 位置 | 动作 | 最终文本 |",
        "不得写文件",
        "多条问题必须按文件分组",
        "同一句或同一最小原文范围存在多个问题时，可以合并",
        "类型：重复词、标点",
        "原文：请在在设置界面配置。。",
        "不得顺带进行语法优化、句式调整、术语替换或表达润色",
        "| 文件 | 问题类型 | 已修复数量 |",
    ):
        require(skill, fragment, "SKILL.md")

    for fragment in (
        "request_user_input",
        "AskUserQuestion",
        "`question`",
        "path/to/file.md:12",
        "path/to/file.md:12-14",
        "每次只询问一个问题",
        "不要在一个工具调用中放入多个 ID",
        "按文件和问题类型统计实际修复处数",
    ):
        require(workflow, fragment, "references/decision-workflow.md")

    require(metadata, "$check-docs", "agents/openai.yaml")
    require(metadata, "两轮", "agents/openai.yaml")
    require(metadata, "行号", "agents/openai.yaml")
    require(metadata, "逐问题", "agents/openai.yaml")

    forbidden_fragments = (
        "# 第一轮：统一决策",
        "采用全部可执行建议 (Recommended)",
        "全部保留并结束",
    )
    combined_protocol = skill + workflow
    for fragment in forbidden_fragments:
        if fragment in combined_protocol:
            raise AssertionError(f"仍包含旧的整体决策文案：{fragment}")

    actual_hash = hashlib.sha256(normalized_fixture_bytes).hexdigest().upper()
    if actual_hash != EXPECTED_NORMALIZED_FIXTURE_SHA256:
        raise AssertionError(
            "测试文档已被修改："
            f"期望 {EXPECTED_NORMALIZED_FIXTURE_SHA256}，实际 {actual_hash}"
        )

    expected_lines = {
        5: "请在在设置界面完成配置。。",
        7: "The servcie returns the current configuration.",
        9: "这个功能非常非常给力，基本上上手就行！",
        11: "为了提升性能，因此系统会缓存结果。",
        13: "该操作会在较短时间内完成。",
        15: "在 OpenHarmony 设置页面中，客户可以点击按钮登录账户。",
    }
    for line_number, expected in expected_lines.items():
        actual = fixture_lines[line_number - 1]
        if actual != expected:
            raise AssertionError(
                f"测试文档第 {line_number} 行不匹配：{actual!r}"
            )

    print("PASS: 第一轮逐问题交互、第二轮统一确认、三 CLI 映射和行号均有效。")
    print(f"PASS: 测试文档规范化换行后的 SHA-256 = {actual_hash}")


if __name__ == "__main__":
    main()
