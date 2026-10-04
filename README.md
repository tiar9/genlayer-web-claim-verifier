# Web Claim Verifier — GenLayer Intelligent Contract

A reusable Intelligent Contract primitive for verifying whether a factual
claim is supported by an external web source.

## What it demonstrates

- External web access through `gl.nondet.web.get`
- Structured LLM output with `response_format="json"`
- Custom consensus validation with `gl.vm.run_nondet_unsafe`
- Independent leader/validator execution
- Deterministic state updates only after consensus
- A reusable pattern for source verification and evidence-based workflows

## Contract flow

1. The user supplies a claim and a source URL.
2. The leader fetches the source and asks an LLM to classify the claim.
3. The validator independently fetches the same source and repeats the
   evaluation.
4. Consensus accepts the result only when the substantive `verdict` agrees.
5. The final verdict and explanation are stored after consensus.

The explanation is intentionally not compared character-for-character because
LLM reasoning can be expressed differently while reaching the same decision.

## Verdicts

- `SUPPORTED` — the source provides sufficient evidence for the claim.
- `NOT_SUPPORTED` — the source contradicts the claim or clearly does not support it.
- `INCONCLUSIVE` — the source does not contain enough information.

## Example

Constructor:

```text
claim:
GenLayer supports non-deterministic operations in Intelligent Contracts.

source_url:
https://docs.genlayer.com/developers/intelligent-contracts/features/non-determinism
```

Then call:

```text
verify()
```

Read the result with:

```text
get_result()
```

## Design / security notes

The contract does not trust the leader's LLM output by itself. The validator
re-runs the source retrieval and evaluation independently and compares the
decision field.

External web content is inherently variable, so the contract compares a
stable classification rather than requiring identical free-form explanations.

Storage writes happen only after `run_nondet_unsafe` returns the consensus
result.

## Repository layout

```text
genlayer-web-claim-verifier/
├── contracts/
│   └── web_claim_verifier.py
├── tests/
│   └── test_contract_structure.py
├── README.md
└── LICENSE
```

## Intended contribution

This is designed as a reusable Intelligent Contract primitive rather than a
hello-world example. The same consensus pattern can be adapted to:

- source-backed fact verification
- research workflows
- content validation
- compliance evidence checks
- dispute/evidence workflows
- real-world web information verification

## License

MIT
