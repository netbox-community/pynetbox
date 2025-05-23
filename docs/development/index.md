# Development

Thanks for your interest in contributing to pynetbox! This introduction covers a few important things to know before you get started.

## The Code

pynetbox is maintained on [GitHub](https://github.com/netbox-community/pynetbox). GitHub also serves as one of our primary discussion forums. While all the code and discussion is publicly accessible, you'll need to register for a free GitHub account to engage in participation. Most people begin by forking the pynetbox repository under their own GitHub account to begin working on the code.

There are two permanent branches in the repository:

* `master` - Active development for the upcoming patch release. Pull requests will typically be based on this branch unless they introduce breaking changes that must be deferred until the next major release.
* `feature` - New feature work to be introduced in the next major release.

pynetbox components are arranged into modules:

* `core/` - Core functionality including API interaction, response handling, and query building
* `models/` - Model definitions for different NetBox object types
* `tests/` - Test suite including unit and integration tests
* `docs/` - Documentation files

## Proposing Changes

All substantial changes made to the code base are tracked using GitHub issues. Feature requests, bug reports, and similar proposals must all be filed as issues and approved by a maintainer before work begins. This ensures that all changes to the code base are properly documented for future reference.

To submit a new feature request or bug report for pynetbox, select and complete the appropriate issue template. Once your issue has been approved, you're welcome to submit a pull request containing your proposed changes.

!!! note
    Avoid starting work on a proposal before it has been accepted. Not all proposed changes will be accepted, and we'd hate for you to waste time working on code that might not make it into the project.

## Getting Help

There are two primary forums for getting assistance with pynetbox development:

* [GitHub discussions](https://github.com/netbox-community/pynetbox/discussions) - The preferred forum for general discussion and support issues. Ideal for shaping a feature requests prior to submitting an issue.
* [#netbox on NetDev Community Slack](https://netdev.chat) - Good for quick chats. Avoid any discussion that might need to be referenced later on, as the chat history is not retained indefinitely.

!!! note
    Don't use GitHub issues to ask for help: These are reserved for proposed code changes only.

## Governance

pynetbox follows the benevolent dictator model of governance, with the lead maintainer ultimately responsible for all changes to the code base. While community contributions are welcomed and encouraged, the lead maintainer's primary role is to ensure the project's long-term maintainability and continued focus on its primary functions.

## Licensing

The entire pynetbox project is licensed as open source under the Apache 2.0 license. This is a very permissive license which allows unlimited redistribution of all code within the project. Note that all submissions to the project are subject to the same license. 