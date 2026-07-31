# Agentic Advisor Suite for Financial Services Cloud

Deploy the Agentic Advisor Suite into a Financial Services Cloud org. This installs the full suite even if you only plan to use some features.

## Contents

- [What's in This Repository](#whats-in-this-repository)
- [Before You Start](#before-you-start)
- [Deploy the Metadata](#deploy-the-metadata)
- [After You Deploy](#after-you-deploy)

## What's in This Repository

Use these metadata artifacts to enable Agentic Advisor Suite features in your org:

- **Run My Day** — Daily task and meeting summaries tailored to wealth advisors
- **Client Detail Pages** — AI-powered client insights and summaries
- **Meeting Concierge** — Meeting preparation, discussion guides, and follow-up automation
- **Households** — ARC graph to visualize Household relationships

This repository includes:

- **Meeting Playbook Definitions** — Pre-configured playbooks for client meetings (Annual Review)
- **GenAI Prompt Templates** — AI prompts for client summaries and preparation briefs
- **Flows** — Automation for meeting creation, goal tracking, and summaries

## Before You Start

Make sure you have:

- Financial Services Cloud (FinServ) managed package installed in your org
- System Administrator profile to deploy metadata and create custom objects
- Salesforce CLI (`sf`) installed ([download here](https://developer.salesforce.com/tools/salesforcecli))

To verify your org meets these requirements and others required to install the Agentic Advisor Suite, go to **Setup > Feature Settings > Financial Services > Agentic Advisor** and run the preflight checks.

## Deploy the Metadata

Every deployment method follows the same three-step sequence:

1. Deploy the datakit
2. Enable the data streams in Setup
3. Deploy the package resources

Pick the method that fits your environment:

- **[Salesforce CLI](#option-1-salesforce-cli-recommended)** — fastest if you already have `sf`; recommended for developers.
- **[Workbench](#option-2-workbench)** — browser-based; no CLI needed.
- **[Claude Skill](#option-3-claude-skill-in-development)** — automated via a Claude skill (still in development).

### Option 1: Salesforce CLI (Recommended)

After every deploy step, verify it succeeded before moving on — look for `Status: Succeeded`.

1. Download this repository to your computer:

   ```bash
   git clone https://github.com/salesforce/next-gen-wealth.git
   cd next-gen-wealth/NextGenWealth
   ```

2. Log in to your org:

   ```bash
   sf org login web --instance-url 'https://login.salesforce.com' --alias myalias
   ```

   Replace `myalias` with a name you'll remember (like `fsc-sandbox`). Start with a sandbox before deploying to production — for a sandbox, use `-r https://test.salesforce.com`; for a custom My Domain, use `-r https://<mydomain>.my.salesforce.com`.

3. Deploy the datakit:

   ```bash
   sf project deploy start --metadata-dir DataKit --target-org myalias --ignore-warnings --wait 30
   ```

4. Click on Data Cloud Setup (from the Setup gear icon menu).  Navigate to **Data Spaces > Developer Tools > Data Kits** in the left panel.  Click on "FSC Agentic Advisor Package Data Kit", then click the Data Kit Deploy button.

5. Deploy the package resources:

   ```bash
   sf project deploy start --metadata-dir PackageResources --target-org myalias --ignore-warnings --wait 30
   ```

### Option 2: Workbench

After every deploy step, verify it succeeded before moving on — look for a `Succeeded` result in the deploy status table.

1. Download or clone this repository to your computer.

2. Prepare the deployment package:

   ```bash
   python3 CloneNextGenWealth.py
   ```

   This creates a folder named `ClonedNextGenWealth` inside your system temp directory (`$TMPDIR` on macOS/Linux, `%TEMP%` on Windows). The script prints the full path to the folder, along with the paths to `DataKitSinglePackage.zip` and `PackageResourcesSinglePackage.zip` — copy them from the script's output.

3. Install Workbench:

   - Get it from the [Chrome Web Store](https://chromewebstore.google.com/detail/workbench/konbmllgicfccombdckckakhnmejjoei?hl=en)
   - Open Workbench and log in to your org

4. Deploy the datakit:

   - Go to **Deploy > Deploy/Retrieve**
   - Click **Deploy**
   - Upload `ClonedNextGenWealth/DataKitSinglePackage.zip`
   - Check **Single Package**
   - Click **Run**

5. Enable the data streams in Setup (see TODO above).

6. Deploy the package resources:

   - Go to **Deploy > Deploy/Retrieve**
   - Click **Deploy**
   - Upload `ClonedNextGenWealth/PackageResourcesSinglePackage.zip`
   - Check **Single Package**
   - Click **Run**

### Option 3: Claude Skill (In Development)

> ⚠️ This option is still in development and not yet ready for general use.

Add the [deploy-next-gen-wealth](https://github.com/salesforce/next-gen-wealth/blob/main/skills/deploy-next-gen-wealth/SKILL.md) skill to Claude Code or simply ask Claude to read this file, then run:

> Deploy the NextGenWealth package resources

To deploy to a different namespace use a command like the following:

> Deploy the NextGenWealth package resources to namespace FSC9gs0

## After You Deploy

### Configure Run My Day

In Data Cloud, manually map the `FinAssetPortfolioTgtAlloc` DMO and the `FinancialAccountBalance.EndDate` field.

### Configure Action Plan Templates

The Meeting Playbook Definition (`Annual_Review_FSC_Package`) doesn't include action plan templates by default. Add them manually:

1. Go to **Setup > Action Plan Template Settings**
2. Deploy these templates:
   - `Annual Review Pre Meeting Template`
   - `Annual Review Post Meeting Template`
3. Click each of these 2 templates and press the Publish button.
4. Edit the `Annual_Review_FSC_Package` meeting playbook definition
5. Attach the templates:
   - **Meeting Preparation Tasks**: Choose "Annual Review Pre Meeting Template"
   - **Meeting Follow-Up Tasks**: Choose "Annual Review Post Meeting Template"
