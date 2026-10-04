# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
import json


class WebClaimVerifier(gl.Contract):
    claim: str
    source_url: str
    verdict: str
    explanation: str

    def __init__(self, claim: str, source_url: str):
        self.claim = claim
        self.source_url = source_url
        self.verdict = "UNVERIFIED"
        self.explanation = ""

    @gl.public.write
    def verify(self):
        """
        Verify whether a factual claim is supported by an external web source.

        The leader and validators independently fetch the source and ask an
        LLM for a structured decision. Consensus compares the decision fields,
        while allowing natural-language explanations to differ.
        """

        claim = self.claim
        source_url = self.source_url

        def evaluate_source():
            response = gl.nondet.web.get(source_url)

            if response.status_code >= 400:
                raise gl.UserError(
                    f"Source returned HTTP {response.status_code}"
                )

            source_text = response.body.decode("utf-8")

            # Keep the prompt bounded and deterministic in shape.
            source_text = source_text[:30000]

            prompt = f"""
You are a source-grounded claim verifier.

CLAIM:
{claim}

SOURCE URL:
{source_url}

SOURCE CONTENT:
{source_text}

Determine whether the source directly supports the claim.

Return JSON with exactly these fields:
{{
  "verdict": "SUPPORTED" | "NOT_SUPPORTED" | "INCONCLUSIVE",
  "explanation": "brief explanation based only on the supplied source"
}}

Rules:
- SUPPORTED means the source provides sufficient evidence for the claim.
- NOT_SUPPORTED means the source contradicts the claim or clearly does not support it.
- INCONCLUSIVE means the source does not contain enough information.
- Do not use outside knowledge.
- Keep the explanation concise.
"""

            result = gl.nondet.exec_prompt(
                prompt,
                response_format="json",
            )

            if not isinstance(result, dict):
                raise gl.UserError("LLM returned an invalid response format")

            verdict = result.get("verdict")
            explanation = result.get("explanation")

            if verdict not in (
                "SUPPORTED",
                "NOT_SUPPORTED",
                "INCONCLUSIVE",
            ):
                raise gl.UserError("LLM returned an invalid verdict")

            if not isinstance(explanation, str) or not explanation.strip():
                raise gl.UserError("LLM returned an invalid explanation")

            return {
                "verdict": verdict,
                "explanation": explanation[:1000],
            }

        def validator_fn(leader_result):
            if not isinstance(leader_result, gl.vm.Return):
                return False

            try:
                validator_result = evaluate_source()
            except Exception:
                return False

            leader_data = leader_result.calldata

            if not isinstance(leader_data, dict):
                return False

            leader_verdict = leader_data.get("verdict")
            validator_verdict = validator_result.get("verdict")

            # Reasoning text can legitimately differ between LLMs.
            # The substantive classification must agree exactly.
            return leader_verdict == validator_verdict

        result = gl.vm.run_nondet_unsafe(
            evaluate_source,
            validator_fn,
        )

        self.verdict = result["verdict"]
        self.explanation = result["explanation"]

    @gl.public.view
    def get_result(self) -> dict:
        return {
            "claim": self.claim,
            "source_url": self.source_url,
            "verdict": self.verdict,
            "explanation": self.explanation,
        }
