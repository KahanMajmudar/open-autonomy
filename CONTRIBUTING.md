# Contribution Guide.

### Creating A Pull Request
- **Target branch:** double-check the PR is opened against the correct branch before submitting
- **Naming convention:** name of the branch should be in kebab case with not more than two or three words. for example `some-feature` or `feat/some-feature`.
- **Tag relevant ticket/issue:** describe the purpose of the PR properly with relevant ticket/issue. Also attaching a tag such as enhancement/bug/test would help.
- **Include a sensible description:** decriptions help reviewers to understand the purpose and context of the proposed changes.
- **Properly comment non-obvious  code** to avoid confusion during the review and enhance maintainability.
- **Code reviews:** two reviewers will be assigned to a PR.
- **Linters:** make sure every linter and checks pass before making a commit. Linters help us maintain a coherent codebase with a common code style, proper API documentation and will help you catch most errors before even running your code.
- **Tests:** the PR needs to contain tests for the newly added code or updated code. (If a commit is made for sole purpose of the review you can add tests later after review is done and PR is ready to merge)

Also mention potential effects on other branches/code might have from your changes.
### Documentation (Docstrings and inline comments)
- Instead of writing just single line of docstring write more informative docstring. If a method is fairly easy to understand one line of docstring will do but if the method has more complex logic it needs be documented properly.
```python
def some_method(some_arg: Type) -> ReturnType:
    """
    This method does something very complex.

    example:
      >> a = Type("value")
      >> some_method(a)
      output

    :param some_arg: describe argument.
    :return: value of ReturnType

    optional
    - types of exceptions it might raise
    """
```
### Some more suggestions to help you write better code.

- Always use guard clauses where possible. This leads to more efficient code that has less nesting and is much easier to read.
- When developing agent applications raise exceptions for all branches which are currently unhandled and would cause inconsistencies in the app. These exceptions can then be surgically addressed in separate PRs. Example: on the happy path a file is loaded properly, on the unhappy path an exception is raised by the file not being present. In production handling this can get involved. During development it is best to "park" this issue and focus on the happy case. But the unhappy case should raise so we can capture its prevalence in tests. Logging is the worst approach as it hides this issue!
- Agent-based apps must be designed with determinism at their core. During every round, agents must agree upon their execution outputs in order to make progress. Any source of randomness or code inconsistency that leads to not strict determinism will undermine the app's ability to achieve its goal. Avoid using thing like:
    - Non-verifiable randomness libraries.
    - Non deterministic libraries, like ML frameworks that do not guarantee exact same results under the same initial conditions.
    - Using the agent's local time to make decisions along the execution flow. Agents synchronize using the consensus engine, and that's the only reliable source of "time" you should use. Block timestamp is one handy property common to all agents and can be used as a `time.now()` equivalent.
    - Using local resources that are not shared among all agents to make decisions.