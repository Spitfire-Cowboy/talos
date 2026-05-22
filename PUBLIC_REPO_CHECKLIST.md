# Talos Public Repo Checklist

This checklist is for preparing a public repository from the current scaffold.

## Current scaffold decisions

- **Repository style:** docs-first scaffold
- **License:** Apache 2.0
- **CI:** not added
- **Current contents:** repository metadata, contributor docs, templates, and a lightweight audit script

## Scaffold already added

- [x] Replace the prior private license text with a public open-source license
- [x] Add `README.md`
- [x] Add `CONTRIBUTING.md`
- [x] Add `CODE_OF_CONDUCT.md`
- [x] Add `SECURITY.md`
- [x] Add issue and pull request templates
- [x] Add `.gitignore`
- [x] Add `CHANGELOG.md`
- [x] Add `scripts/check-public-safety.sh`

## Before publishing additional files

- [ ] Inventory every file proposed for publication
- [ ] Remove or rewrite non-public names, URLs, comments, screenshots, and documentation
- [ ] Confirm no secrets, credentials, or tokens are present in tracked files
- [ ] Confirm no customer data or proprietary assets are present
- [ ] Update `README.md` so it describes only the files actually being published
- [ ] Replace placeholder values such as the security-policy URL in `.github/ISSUE_TEMPLATE/config.yml`
- [ ] Run `bash scripts/check-public-safety.sh --strict-public`
- [ ] Add CI only if it validates real public content and passes in a clean environment

## Before announcing a public repo

- [ ] Create the public GitHub repository
- [ ] Copy only the selected files into it
- [ ] Review it as an external visitor
- [ ] Perform a final manual check before announcement
