# Repo Descriptor Guide

This repository publishes the starter semantic layer for the broader SourceOS / AgentOS / SocioProphet topology.

## What this starter pack contains

- `semantic/context.jsonld` — JSON-LD context for repository descriptors
- `semantic/repo-ontology.jsonld` — role vocabulary / concept graph
- `schemas/repo_descriptor.schema.json` — JSON Schema for machine-readable repo descriptors
- `examples/repo-descriptor.*.jsonld` — concrete examples for the current topology

## Why this exists

READMEs are for humans. Repo descriptors are for machines.

Every important repository should eventually ship a small machine-readable descriptor so that:

- agents can resolve role and adjacency without scraping prose
- tooling can build topology maps automatically
- documentation sites can embed structured metadata
- policy and orchestration systems can reason over repo classes and relationships directly

## Recommended placement in downstream repos

Each repo should eventually publish:

- `semantic/repo.jsonld`

The descriptor should reference this shared context and vocabulary rather than redefining terms locally.

## Minimal descriptor skeleton

```json
{
  "@context": "https://raw.githubusercontent.com/SourceOS-Linux/sourceos-spec/main/semantic/context.jsonld",
  "@id": "urn:sourceos:repo:ORG:REPO",
  "@type": ["RepoDescriptor", "Repository"],
  "name": "repo-name",
  "description": "One-sentence role statement.",
  "repositoryFullName": "ORG/repo-name",
  "repoUrl": "https://github.com/ORG/repo-name",
  "organization": "ORG",
  "defaultBranch": "main",
  "semanticDescriptorVersion": "0.1.0",
  "topologyRole": "roleTypedContractRegistry",
  "connectsTo": [],
  "notThisRepo": []
}
```

## Current canonical role set

- `rolePlatformWorkspaceController`
- `roleLinuxIntegrationSpine`
- `roleTypedContractRegistry`
- `roleWorkstationConformanceLane`
- `roleAutomationCommons`
- `roleOSSubstrate`
- `rolePublicDocsSurface`
- `roleStarterScaffold`

## Current rule of use

- prefer one primary topology role per repo
- use `connectsTo` for explicit adjacency
- use `notThisRepo` to block common category mistakes
- use `consumesVocabularyFrom` when the repo imports the canonical vocabulary from this repo

## Near-term follow-up

Next we should add one real `semantic/repo.jsonld` file to each core repo:

- `SociOS-Linux/agentos-spine`
- `SocioProphet/sociosphere`
- `SociOS-Linux/workstation-contracts`
- `SociOS-Linux/SourceOS`
- `SociOS-Linux/socios`
- `SociOS-Linux/socioslinux-web`
