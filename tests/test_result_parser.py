from mr_review_agent.checks.result_parser import parse_lint_output, strip_ansi


def test_strip_ansi_removes_terminal_color_codes():
    raw = "\x1b[31mInvalid Option:\x1b[39m bad config"

    assert strip_ansi(raw) == "Invalid Option: bad config"


def test_parse_lint_output_groups_problems_by_file_and_rule():
    raw = """
\x1b[31mInvalid Option:\x1b[39m Invalid option name "ignoreUnits"

src/components/DataList/index.vue
  \x1b[2m266:5\x1b[22m  \x1b[31m✖\x1b[39m  Expected "margin-top" to come before "margin-bottom"  \x1b[2morder/properties-order\x1b[22m
  \x1b[2m278:9\x1b[22m  \x1b[31m✖\x1b[39m  Unexpected empty line before declaration              \x1b[2mdeclaration-empty-line-before\x1b[22m

src/pages/hr/clock/approve-list.vue
  \x1b[2m1060:9\x1b[22m  \x1b[31m✖\x1b[39m  Expected "right" to come before "left"  \x1b[2morder/properties-order\x1b[22m

\x1b[31m✖\x1b[39m 3 problems (\x1b[31m3 errors\x1b[39m, \x1b[33m0 warnings\x1b[39m)
  1 error potentially fixable with the "--fix" option.
"""

    summary = parse_lint_output(raw)

    assert summary.total_problems == 3
    assert summary.fixable_count == 1
    assert summary.by_file["src/components/DataList/index.vue"] == 2
    assert summary.by_file["src/pages/hr/clock/approve-list.vue"] == 1
    assert summary.by_rule["order/properties-order"] == 2
    assert summary.by_rule["declaration-empty-line-before"] == 1
