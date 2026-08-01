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
- Salesforce CLI (`sf`) installed ([download here](https://developer.salesforce.com/tools/salesforcecli)) if you plan to use Option 1 or Option 2
- python3 installed if you plan to use Option 3

To verify your org meets these requirements and others required to install the Agentic Advisor Suite, go to **Setup > Feature Settings > Financial Services > Agentic Advisor** and run the preflight checks.

## Deploy the Metadata

Every deployment method follows the same three-step sequence:

1. Deploy the datakit
2. Enable the data streams in Setup
3. Deploy the package resources

Pick the method that fits your environment:

- **[Salesforce CLI](#option-1-salesforce-cli)** — fastest if you already have `sf`; recommended for developers.
- **[Claude Skill](#option-2-claude-skill)** — automated via a Claude skill.
- **[Workbench](#option-3-workbench)** — browser-based; no CLI needed.

### Option 1: Salesforce CLI

After every deploy step, verify it succeeded before moving on — look for `Status: Succeeded`.

1. Download this repository to your computer:

   ```bash
   git clone https://github.com/salesforce/next-gen-wealth.git
   cd next-gen-wealth/AgenticAdvisor
   ```

2. Log in to your org:

   ```bash
   sf org login web --instance-url 'https://login.salesforce.com' --alias myalias
   ```

   Replace `myalias` with the alias to your org. Start with a sandbox before deploying to production — for a sandbox, use `--instance-url https://test.salesforce.com`; for a custom My Domain, use `--instance-url https://<mydomain>.my.salesforce.com`.

3. Deploy the datakit:

   ```bash
   sf project deploy start --metadata-dir DataKit --target-org myalias --ignore-warnings --wait 30
   ```

4. Click on Data Cloud Setup (from the Setup gear icon menu). Navigate to **Data Spaces > Developer Tools > Data Kits** in the left panel. Click on "FSC Agentic Advisor Package Data Kit", then click the Data Kit Deploy button.

5. Deploy the package resources:

   ```bash
   sf project deploy start --metadata-dir PackageResources --target-org myalias --ignore-warnings --wait 30
   ```

### Option 2: Claude Skill

Add the [deploy-financial-services-agentic-advisor](https://github.com/salesforce/next-gen-wealth/blob/main/skills/deploy-financial-services-agentic-advisor/SKILL.md) skill to an AI tool like Claude Code or Cursor or AI Suite, or simply ask the AI tool to read this file, then run:

> Deploy the agentic advisor for the financial services package


### Option 3: Workbench

After every deploy step, verify it succeeded before moving on — look for a `Succeeded` result in the deploy status table.

1. Download or clone this repository to your computer.

   ```bash
   git clone https://github.com/salesforce/next-gen-wealth.git
   cd next-gen-wealth
   ```
2. Prepare the deployment package:

   ```bash
   python3 tools/CreateClone.py
   ```

   If your package uses a namespace other than FinServ you may specify it, for example:
   ```bash
   python3 tools/CreateClone.py --namespace FSC1
   ```

   This creates a folder named `ClonedAgenticAdvisorForFinancialServices` inside your system temp directory (`$TMPDIR` on macOS/Linux, `%TEMP%` on Windows). The script prints the full path to the folder, along with the paths to `DataKitSinglePackage.zip` and `PackageResourcesSinglePackage.zip`.

3. Install Workbench:

   - Get it from the [Chrome Web Store](https://chromewebstore.google.com/detail/workbench/konbmllgicfccombdckckakhnmejjoei?hl=en)
   - Open Workbench and log in to your org

4. Deploy the datakit:

   - Go to **Deploy > Deploy/Retrieve**
   - Click **Deploy**
   - Upload `ClonedAgenticAdvisorForFinancialServices/DataKitSinglePackage.zip` from the `$TMPDIR` or `%TEMP%` folder
   - Check **Single Package**
   - Click **Run**

5. Enable the data streams in Setup as in step 4 of Option 1.

6. Deploy the package resources:

   - Go to **Deploy > Deploy/Retrieve**
   - Click **Deploy**
   - Upload `ClonedAgenticAdvisorForFinancialServices/PackageResourcesSinglePackage.zip` from the `$TMPDIR` or `%TEMP%` folder
   - Check **Single Package**
   - Click **Run**

## After You Deploy

### Configure Run My Day

In Data Cloud, manually map the `FinAssetPortfolioTgtAlloc` DMO and the `FinancialAccountBalance.EndDate` field.

### Configure Action Plan Templates

The Meeting Playbook Definition (`Annual_Review_FSC_Package`) doesn't include action plan templates by default. Add them manually:

1. Go to **Setup > Action Plan Template Settings**
2. Deploy these templates:
   - `Annual Review Pre Meeting Template`
   - `Annual Review Post Meeting Template`
3. For both templates, press the Publish button.
4. Edit the `Annual_Review_FSC_Package` meeting playbook definition
5. Attach the templates:
   - **Meeting Preparation Tasks**: Choose "Annual Review Pre Meeting Template"
   - **Meeting Follow-Up Tasks**: Choose "Annual Review Post Meeting Template"
