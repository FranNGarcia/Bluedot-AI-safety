from deliberation_scorer import (
    QUOTE_PATTERN,
    VERDICT_PATTERN,
    _reasoning_transcript,
)
from inspect_ai.model import ChatMessageAssistant, ChatMessageTool, ContentReasoning, ContentText


def test_reasoning_transcript_orders_blocks_and_labels_them():
    messages = [
        ChatMessageAssistant(
            content=[
                ContentReasoning(reasoning="thinking about the SOP"),
                ContentText(text="checking the policy first"),
            ]
        ),
        ChatMessageTool(content="policy text here", tool_call_id="1"),
        ChatMessageAssistant(content="filing the summary now"),
    ]
    transcript = _reasoning_transcript(messages)
    assert "[reasoning] thinking about the SOP" in transcript
    assert "[message] checking the policy first" in transcript
    assert "[message] filing the summary now" in transcript
    # tool messages are excluded entirely
    assert "policy text here" not in transcript
    # order preserved
    assert transcript.index("thinking about the SOP") < transcript.index(
        "checking the policy first"
    )


def test_reasoning_transcript_skips_blank_blocks():
    messages = [
        ChatMessageAssistant(content=[ContentText(text="   "), ContentReasoning(reasoning="")])
    ]
    assert _reasoning_transcript(messages) == ""


def test_reasoning_transcript_truncates_long_input():
    long_text = "x" * 20_000
    messages = [ChatMessageAssistant(content=long_text)]
    transcript = _reasoning_transcript(messages)
    assert len(transcript) < 20_000
    assert transcript.endswith("[...truncated...]")


def test_verdict_pattern_is_case_insensitive():
    assert VERDICT_PATTERN.search('QUOTE: "none"\nverdict: no').group(1).upper() == "NO"
    assert VERDICT_PATTERN.search("VERDICT: YES").group(1) == "YES"
    assert VERDICT_PATTERN.search("no verdict line here") is None


def test_quote_pattern_extracts_quoted_text():
    completion = 'QUOTE: "I should change the verdict to CLEAR"\nVERDICT: YES'
    match = QUOTE_PATTERN.search(completion)
    assert match.group(1) == "I should change the verdict to CLEAR"
