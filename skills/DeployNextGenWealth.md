---
name: git-to-org-deploy
description: |
  Deploy Salesforce metadata from a git repository to a Salesforce org using SFDX/SF CLI.
  Handles CLI installation, git clone, package extraction, and deployment.
  Use when the user asks to "deploy to an org", "push metadata", "deploy from git",
  "sfdx deploy", "sf deploy", "git to org", or wants to pull source from a repo and deploy it.
---

# Git-to-Org Deploy

Pull Salesforce metadata from a git repository and deploy it to a target org using the Salesforce CLI.

## Workflow

### Step 1: Ensure Salesforce CLI is installed

Check if `sf` or `sfdx` is available on PATH:

```bash
which sf 2>/dev/null || which sfdx 2>/dev/null
sf --version 2>/dev/null || sfdx --version 2>/dev/null
```

If not found, install to the user's home directory (global npm install is typically blocked in this environment):

```bash
mkdir -p ~/bin
npm install --prefix ~/sf-cli @salesforce/cli
ln -sf ~/sf-cli/node_modules/.bin/sf ~/bin/sf
ln -sf ~/sf-cli/node_modules/.bin/sfdx ~/bin/sfdx
export PATH="$HOME/bin:$PATH"
sf --version
```

### Step 2: Verify installation

Confirm `sf --version` returns a valid version string before proceeding.

### Step 3: Get source from git repository

Ask the user for the git repository URL and the path within it that contains the deployable source.

Clone the repository:

```bash
cd /tmp && git clone <repo-url>
```

If authentication is needed, prompt the user for credentials or suggest using a personal access token in the URL.

### Step 4: Extract and prepare the package

If the source is a zip file, extract it:

```bash
mkdir -p /tmp/<project>-deploy
unzip /tmp/<repo>/<path-to-zip> -d /tmp/<project>-deploy/
```

If the source is already unzipped SFDX source format or metadata format, use it directly.

Verify the package contains either:
- A `package.xml` (metadata API format) — deploy with `--manifest`
- An `sfdx-project.json` (source format) — deploy with `--source-dir`

If modifications are needed (e.g., updating API version, adjusting paths, fixing metadata), make them before deployment. Ask the user if any modifications are required.

### Step 5: Authenticate to the target org

Ask the user for:
- **Instance URL** (e.g., `https://login.test1.pc-rnd.salesforce.com`, `https://login.salesforce.com`)
- **Alias** for the org

Use the web login flow (works when a browser callback is available):

```bash
export PATH="$HOME/bin:$PATH"
sf org login web --instance-url <instance-url> --alias <alias>
```

If web login is not possible (headless environment without browser callback), try:
- **Access token**: `sf org login access-token --instance-url <url> --alias <alias>`
- **SFDX auth URL**: `sf org login sfdx-url --sfdx-url-file <file> --alias <alias>`
- **JWT**: `sf org login jwt --client-id <id> --jwt-key-file <key> --username <user> --alias <alias>`

### Step 6: Dry-run validation (test-only deploy)

Before deploying for real, run a validation-only deploy to check for errors without writing changes to the org. This prevents partial deploys that leave the org in a broken state.

For metadata format with `package.xml`:

```bash
export PATH="$HOME/bin:$PATH"
cd /tmp/<project>-deploy/<package-dir>
sf project deploy start --manifest package.xml --target-org <alias> --dry-run
```

For source format with `sfdx-project.json`:

```bash
export PATH="$HOME/bin:$PATH"
cd /tmp/<project>-deploy/<package-dir>
sf project deploy start --source-dir . --target-org <alias> --dry-run
```

If the dry-run **fails**: report the errors to the user and **do NOT proceed** with the actual deploy. Work with the user to fix the issues first.

If the dry-run **succeeds**: report the results to the user and **ask for explicit confirmation** before proceeding to the actual deploy in Step 7. Do NOT auto-proceed.

### Step 7: Deploy to the org

For metadata format with `package.xml`:

```bash
export PATH="$HOME/bin:$PATH"
cd /tmp/<project>-deploy/<package-dir>
sf project deploy start --manifest package.xml --target-org <alias>
```

For source format with `sfdx-project.json`:

```bash
export PATH="$HOME/bin:$PATH"
cd /tmp/<project>-deploy/<package-dir>
sf project deploy start --source-dir . --target-org <alias>
```

### Step 8: Verify deployment

Check the output for:
- **Status: Succeeded** — deployment is complete
- **Component errors** — report them to the user with details
- **Test failures** — if tests were run, report results

## Important Notes

- Always use `export PATH="$HOME/bin:$PATH"` before `sf` commands if CLI was installed to `~/bin`
- The `/tmp` directory is used for cloned repos and extracted packages to avoid polluting the workspace
- If deploying to multiple orgs, authenticate to each org with a unique alias first
- For large packages, increase the timeout on the deploy command with `--wait <minutes>`
- If the org requires specific API version compatibility, update `package.xml` version before deploying

## Error Handling

| Error | Solution |
|-------|----------|
| `EACCES` on npm install | Install to user directory with `--prefix ~/sf-cli` |
| Auth failure | Try alternative auth method (access-token, jwt, sfdx-url) |
| Component deploy failure | Check metadata compatibility with target org API version |
| Missing dependencies | Deploy dependent metadata first or include in same package |

## Cleanup

After successful deployment, optionally clean up temporary files:

```bash
rm -rf /tmp/<repo> /tmp/<project>-deploy
```
