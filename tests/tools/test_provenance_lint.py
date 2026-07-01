from tools.provenance_lint import lint_identity_text, lint_text


def test_allows_normal_commit_message():
    assert lint_text("docs: update governance standard\n\nHuman-authored note.") == []


def test_blocks_ai_coauthor_trailer():
    findings = lint_text(
        "docs: update standard\n\nCo-authored-by: Codex <codex@example.com>"
    )

    assert [finding.rule for finding in findings] == ["ai-coauthor-trailer"]


def test_blocks_generated_by_trailer():
    findings = lint_text("docs: update standard\n\nGenerated-by: Claude")

    assert [finding.rule for finding in findings] == ["generated-by-trailer"]


def test_blocks_ai_credit_line():
    findings = lint_text("docs: update standard\n\nImplemented by Devin")

    assert [finding.rule for finding in findings] == ["ai-credit-line"]


def test_blocks_ai_author_identity():
    findings = lint_identity_text(
        "Claude (agent) <claude@agents.hummbl.io> 1782843919 -0400",
        label="author",
    )

    assert [finding.rule for finding in findings] == ["ai-author-identity"]


def test_allows_human_author_identity():
    findings = lint_identity_text(
        "Reuben Bowlby <reuben@hummbl.io> 1782843919 -0400",
        label="author",
    )

    assert findings == []
