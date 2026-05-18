# Development

Thanks for your interest in contributing to pynetbox! This page covers the project's branch layout, how to propose changes, and where to get help.

## The Code

pynetbox is maintained on [GitHub](https://github.com/netbox-community/pynetbox), which also serves as the project's primary discussion forum. You'll need a (free) GitHub account to file issues or open pull requests. Most contributors begin by forking the repository under their own account.

There are two permanent branches:

- **`master`** — Active development for the next patch release. Pull requests should target this branch unless they introduce breaking changes that must wait for the next major release.
- **`feature`** — New feature work staged for the next major release.

The source tree is organized into the following directories:

- `pynetbox/core/` — Core HTTP, request, response, and endpoint plumbing.
- `pynetbox/models/` — Model classes (custom `Record` subclasses) for the various NetBox apps.
- `tests/` — Unit and integration tests.
- `docs/` — User documentation (this site).

## Proposing Changes

All substantial changes are tracked via GitHub issues. Feature requests, bug reports, and other proposals must be filed as issues and approved by a maintainer before work begins. This keeps the design rationale for each change discoverable in one place.

To file a new feature request or bug report, select the appropriate issue template. Once your issue has been triaged and accepted, you're welcome to submit a pull request implementing the change.

!!! note
    Please avoid starting work on a proposal before it has been accepted. Not every proposal will be approved, and we'd hate for your time to be wasted on a change that isn't merged.

## Getting Help

Two forums are available for development questions:

- [GitHub Discussions](https://github.com/netbox-community/pynetbox/discussions) — The preferred forum for general discussion and support. Ideal for shaping a feature idea before filing an issue.
- [#netbox on the NetDev Community Slack](https://netdev.chat) — Useful for quick chats. Avoid using it for anything that needs to be referenced later, as the chat history is not retained indefinitely.

!!! note
    Don't use GitHub issues to ask for help — those are reserved for proposed code changes only.

## Governance

pynetbox follows the benevolent-dictator model of governance, with the lead maintainer ultimately responsible for all changes to the codebase. Community contributions are welcomed and encouraged, but the lead maintainer's primary role is to ensure the project's long-term maintainability and its continued focus on its core mission.

## Licensing

pynetbox is released under the [Apache 2.0 license](https://www.apache.org/licenses/LICENSE-2.0). This is a permissive license that allows unrestricted redistribution of the code. Note that all submissions to the project are subject to the same license.
