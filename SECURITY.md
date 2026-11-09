# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 3.0.x   | ✅ |

## Reporting a vulnerability

If you discover a security issue in PACIF (for example, unsafe deserialization of audit inputs, path traversal in report writers, or dependency risks):

1. **Do not** open a public GitHub issue.
2. Email **for.smirnov.maks@gmail.com** with:
   - Description of the issue
   - Steps to reproduce
   - Affected version / commit
   - Any known exploitability constraints

We aim to acknowledge reports within 5 business days and to provide a remediation timeline after triage.

## Scope notes

PACIF is primarily a statistical library. It does not implement authentication, multi-tenant isolation, or network services by default. Security-sensitive deployments (SaaS audit pipelines, regulated environments) should apply standard controls around data access, logging, and supply chain independently of this repository.
