# Contributing to PACIF

Thank you for your interest in contributing to PACIF. Algorithmic transparency should be a public good. We welcome contributions of all kinds — code, documentation, tests, examples, and ideas.

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How to Contribute

### 1. Reporting Bugs

- Check existing [issues](https://github.com/ppiiyo/pacif-framework/issues) first.
- Open a new issue with a clear title and description.
- Include: Python version, OS, minimal reproducible example, expected vs actual behavior.

### 2. Suggesting Enhancements

- Open an issue with the `enhancement` label.
- Describe the use case, why it matters for predictive alignment / audit workflows, and any proposed API shape.

### 3. Pull Requests

1. Fork the repository.
2. Create a feature branch from `main` (`git checkout -b feature/your-feature`).
3. Make your changes with clear, focused commits.
4. Add or update tests if applicable.
5. Ensure the code follows existing style (we use ruff + type hints where practical).
6. Update documentation (README, docstrings) if the public API or behavior changes.
7. Open a Pull Request against `main` with a clear description of *what* and *why*.

### Development Setup

```bash
git clone https://github.com/ppiiyo/pacif-framework.git
cd pacif-framework
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev,demo,causal]"
```

### Coding Guidelines

- Prefer clarity and explicitness over cleverness.
- Public functions should have type hints and docstrings.
- Keep statistical claims precise. PACIF measures **predictive alignment**, not causality or wellbeing.
- Avoid introducing heavy dependencies into the core package.
- New metrics or diagnostics should include reliability considerations and clear interpretation guidance.

### Areas We Especially Welcome

- Additional bias-correction methods and comparative benchmarks
- Stronger anti-gaming checks in the audit reporter
- Integration examples (Kafka, BigQuery, Snowflake, pandas pipelines)
- Improved drift detection variants and evaluation
- Documentation, tutorials, and real-world (or high-quality synthetic) case studies
- Packaging, CI, and developer experience improvements

## Questions?

Open a [Discussion](https://github.com/ppiiyo/pacif-framework/discussions) or reach out via the enterprise contact in the README.

Thank you for helping make algorithmic accountability more rigorous and accessible.
