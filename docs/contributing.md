# Contributing

Use Python 3.11+ and the standard library. Keep canonical agent definitions platform neutral; adapter output should derive from them so fixes do not diverge between products. Preserve existing stable IDs; add new roles consistently to catalog, routing, memory and adapters with migration tests. No runtime server or mandatory external service is needed.

```sh
python3 scripts/dat.py validate
python3 -m unittest discover -s tests -v
git diff --check
```

Installer and memory tests must use temporary directories. Test clean and repeated installs, project/global scope, unmanaged files, locally edited files, upgrade conflicts, dry runs, uninstall and rollback. Never use a real home directory as a test fixture. Add focused regression cases for behavioral changes, rather than duplicating implementation details.

Policy tests are deterministic contract/simulation tests. They cover explicit specialist selection, fallback, risk gates, protocol validation, conflict routing and recovery. They do not measure agent intelligence, prove native delegation or replace host smoke tests. New native testing evidence must name the product surface, version, operating system, tool invocation, observed result and limitation. Never promote capability matrix statuses based solely on generated files or unit tests.

When changing platform formats, consult current official documentation, update [platform sources](platform-sources.md), regenerate adapters through the maintained mechanism and run validation. Keep unavailable integrations visibly untested. Do not pin models without an explicit compatibility reason.

Public documentation is English with maintained PT-PT usage guidance. Keep examples synthetic and free of secrets, user data and local machine paths. Do not add planning files to consumer projects. Review generated output and public content before publication.

Use Semantic Versioning: MAJOR for incompatible contracts or installation behavior, MINOR for compatible features, PATCH for compatible fixes. Release versions must match the published files and installer metadata. A proposed change does not authorize a consumer commit, push, pull request, paid resource or deployment; preserve those approval boundaries. Contributions are distributed under the repository's MIT License.
