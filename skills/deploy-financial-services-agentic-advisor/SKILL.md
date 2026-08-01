---
name: deploy-financial-services-agentic-advisor
description: |
  Deploys the AgenticAdvisor repository for use with the FinServ financial services WealthApp package, using sf.
  Use when the user asks to "deploy the agentic advisor for the financial services package".
---

# deploy-financial-services-agentic-advisor

Pull Salesforce metadata from a git repository and deploy it to a target org using the Salesforce CLI.

This skill does not convert namespaces.

## Workflow

The steps below are for Linux/macOS. If on Windows replace $TMPDIR with %TEMP%

### Step 1: Ensure Salesforce CLI is installed

Check if `sf` or `sfdx` is available on PATH:

```bash
which sf 2>/dev/null || which sfdx 2>/dev/null
sf --version 2>/dev/null || sfdx --version 2>/dev/null
```

If it is missing, show an error message and stop running.

### Step 2: Verify sf version

Confirm `sf --version` returns @salesforce/cli/2.137.7 or higher. If the version is too low run `sf update`.

### Step 3: Get source from git repository

```bash
cd $TMPDIR
git clone https://github.com/salesforce/next-gen-wealth.git
cd next-gen-wealth/AgenticAdvisor
```

If you get an error that the repository already exists, then
```bash
cd $TMPDIR/next-gen-wealth/AgenticAdvisor
git pull
```


### Step 4: Authenticate to the target org

Ask the user for: **Alias** for the org

If the alias does not exist in `sf org list`, then ask the user for **Instance URL** and log in using `sf org login web --instance-url '<Instance URL>' --alias <Alias>`

### Step 5: Deploy the data kit

Before deploying for real, run a validation-only deploy to check for errors without writing changes to the org. This prevents partial deploys that leave the org in a broken state.

```bash
cd $TMPDIR/next-gen-wealth/AgenticAdvisor
sf project deploy start --metadata-dir DataKit --target-org <Alias> --ignore-warnings --wait 30 --dry-run
```

If the dry-run **fails**: report the errors to the user and **do NOT proceed** with the actual deploy. Work with the user to fix the issues first.

If the dry-run **succeeds**: report the results to the user and **ask for explicit confirmation** before proceeding to the actual deploy. The actual deploy is the same command without the --dry-run argument.

Check the output for:
- **Status: Succeeded** — deployment is complete
- **Component errors** — report them to the user with details
- **Test failures** — if tests were run, report results

If there are errors or failures abort the agent workflow.

### Step 6: Enable/install the data streams

Tell the user to complete the following steps on the UI and to notify you when they have done this so that you can move on to the next step:
Click on Data Cloud Setup (from the Setup gear icon menu). Navigate to **Data Spaces > Developer Tools > Data Kits** in the left panel. Click on "FSC Agentic Advisor Package Data Kit", then click the Data Kit Deploy button.

Run `sf org open --target-org <Alias>` to open the URL so that the user can complete the steps manually.

### Step 7: Deploy the package artifacts

Before deploying for real, run a validation-only deploy to check for errors without writing changes to the org. This prevents partial deploys that leave the org in a broken state.

```bash
cd $TMPDIR/next-gen-wealth/AgenticAdvisor
sf project deploy start --metadata-dir PackageResources --target-org <Alias> --ignore-warnings --wait 30 --dry-run
```

If the dry-run **fails**: report the errors to the user and **do NOT proceed** with the actual deploy. Work with the user to fix the issues first.

If the dry-run **succeeds**: report the results to the user and **ask for explicit confirmation** before proceeding to the actual deploy. The actual deploy is the same command without the --dry-run argument.

Check the output for:
- **Status: Succeeded** — deployment is complete
- **Component errors** — report them to the user with details
- **Test failures** — if tests were run, report results

If there are errors or failures abort the agent workflow.

### Step 8: Cleanup

After successful deployment, optionally clean up temporary files. This is how to do it on Linux/macOS, figure out the equivalent if on Windows:

```bash
rm -rf $TMPDIR/next-gen-wealth
```
