# next-gen-wealth

Source for the **FSC Agentic Advisor** managed-package payload that powers the Next Gen Wealth experience inside Salesforce Financial Services Cloud (FSC). The repo is the staging ground for the public mirror at <https://github.com/salesforce/next-gen-wealth>; the `NextGenWealth/` and `NextGenWealthDataKit/` folders are eventually copied there.

It ships two deployable Salesforce metadata packages (API 67.0):

| Folder | What it contains |
|---|---|
| [`NextGenWealth/`](./NextGenWealth) | Lightning record pages, screen and prompt flows, GenAI prompt templates, the Annual Review meeting playbook, and the household relationship graph. |
| [`NextGenWealthDataKit/`](./NextGenWealthDataKit) | A Data Cloud data kit: data streams, data lake objects, data source/field maps, transforms, and the FSC identity-resolution ruleset. |

## NextGenWealth — FSC Agentic Advisor package

`NextGenWealth/package.xml` declares the deployable manifest (API version `67.0`).

### Lightning record pages (`flexipages/`)

Two FlexiPages override the standard `Account` record page when the package is installed:

- **`NextGenWlthMgmt_HshldAcct_Pkg_rec_L`** — *Agentic Advisor Household Record Page For Package* (rendered for household accounts).
- **`NextGenWlthMgmt_PersonAcct_Pkg_rec_L`** — *Agentic Advisor Person Account Record Page For Package* (rendered for person accounts).

### Flows (`flows/`)

| Flow | Purpose |
|---|---|
| `Client_Summary_FSC_Package` | Data-grounding flow for the **Create Annual Review Client Summary** prompt template. Assembles client/household details, financial accounts, goals, life events, and cases into the prompt context. |
| `Create_Meeting_from_Event_FSC_package` | Creates a Meeting record from an Event, wired to the Annual Review playbook templates. Surfaces a friendly error when the Annual Review or Prospecting template can't be found. |
| `Create_Person_Life_Event_FSC_Package` | Invokes an AI action that suggests a Person Life Event from the in-meeting stage notes, then creates the `PersonLifeEvent` record against the contact. |
| `GetAcctDtlClntPulsePkg` | Data-grounding flow for the **Client Pulse** prompt template (managed-package variant). Classifies the input Account (Person vs. Household via `FinServ__GroupRecordTypeMapper__mdt`) and gathers Account, Financial Goals, Financial Account Roles, Person Life Events, Open Cases, and last interaction Event into the prompt context. |
| `Periodic_Create_New_Goals_Or_Update_Existing_Goals_FSC_Package` | After a meeting, invokes an AI prompt to extract new financial-goal suggestions from the post-meeting notes; iterates the JSON response by index and creates / updates `FinServ__FinancialGoal__c` records. |
| `Prep_Brief_Summary_FSC_Package` | Data-grounding flow for the **Create Annual Review Preparation Brief** prompt template. Aggregates financial-account IDs and per-holding data into the prompt context. |

### GenAI prompt templates (`genAiPromptTemplates/`)

| Template | Description (from `<description>`) | Backing flow |
|---|---|---|
| `Create_Annual_Review_Client_Summary_FSC_Package` | "Creates a comprehensive summary brief for annual client reviews, including portfolio performance, key strategic decisions, and relationship history." | `Client_Summary_FSC_Package` |
| `Create_Annual_Review_Preparation_Brief_FSC_Package` | "Creates a preparation brief for annual client reviews, including financial data, prior interactions, and open items." | `Prep_Brief_Summary_FSC_Package` |
| `GenerateClientPulseForHouseholdMngPkg` | "Generates a summary of a household's current financial state, changes since the last interaction, and their implications." | `GetAcctDtlClntPulsePkg` |
| `GenerateClientPulseForPersonAccountMngPkg` | "Generates a summary of a person account's current financial state, changes since the last interaction, and their implications." | `GetAcctDtlClntPulsePkg` |

### Meeting playbook (`meetingPlaybookDefinitions/`)

- **`Annual_Review_FSC_Package`** — *"Ideal for quarterly or annual check-ins with existing clients. Includes pre-meeting research, in-session discussion guide, and post-meeting follow-up."* Three-stage playbook:
  - **PreMeeting** — invokes `Create_Annual_Review_Client_Summary_FSC_Package`, `Create_Annual_Review_Preparation_Brief_FSC_Package`, and `meetingcenter_wealth__DocumentSummaryPrompt`.
  - **InMeeting** — invokes `meetingcenter_wealth__PeriodicDiscussionGuidePrompt` and `meetingcenter__TranscriptSummaryPrompt`.
  - **PostMeeting** — wires the post-meeting follow-up actions.

### Relationship graph (`relationshipGraphDefinitions/`)

- **`Household_Graph_for_Managed_Package`** — a `HorizontalHierarchy` graph visualizing a household account, its members (via `AccountContactRelation`), per-contact related contacts (via `FinServ__ContactContactRelation__c`), member sub-accounts (filtered by `FinServ__IncludeInGroup__c = true`), related groups (`RecordType.DeveloperName = IndustriesHousehold` on `FinServ__AccountAccountRelation__c`), and other related accounts.

## NextGenWealthDataKit — Data Cloud data kit

`NextGenWealthDataKit/package.xml` declares the Data Cloud manifest (API version `67.0`).

> "This data kit includes data streams, data lake objects, data transforms, field mappings, and identity resolution for Financial Services Cloud." — `FSCAgenticAdvisorPackageDataKit.dataPackageKitDefinition`

Deployment order (per the data-kit definition):
1. `FSCAgenticAdvisorPackageDataBundle` (DataStream bundle)
2. `FinServ_FinancialAccountBalance_c_Home` (Mkt Data Lake Object)
3. `FSCAgenticAdvisorFADataTransforms` (Mkt Data Transform)
4. `Individual_FSC` (Identity Resolution ruleset — *"Ruleset to perform identity resolution for Individual records from BridgeFT and CRM"*)

### What's inside

| Folder | Contents |
|---|---|
| `dataKitObjectTemplates/` | `FSCAgenticAdvisorFADataTransforms` (data transforms) and `Individual_FSC` (the FSC Individual identity-resolution ruleset). |
| `dataPackageKitDefinitions/` | The top-level kit definition `FSCAgenticAdvisorPackageDataKit`. |
| `DataPackageKitObjects/` | DMO/DLO declarations referenced by the kit. |
| `dataSourceBundleDefinitions/` | `FSCAgenticAdvisorPackageDataBundle` -- the Salesforce Sales & Service Cloud data bundle. |
| `dataSourceObjects/` | Source-object descriptors for each data stream listed below. |
| `dataSrcDataModelFieldMaps/` | Field-level mappings from data-source objects to DMOs. |
| `dataStreamTemplates/` | 16 stream templates: Account, AccountContactRelation, Contact, Financial Account, Financial Account Role, Financial Custodian, Financial Custodian Advisor, Financial Goal, Financial Holding, Financial Plan, Lead, Party Profile, Person Life Event, Referral, Securities, User. |
| `mktDataSources/` | Underlying `mktDataSource` records (`FinServ_FinancialAccountBalance_c_Home`, `Salesforce_00Dxx00sfmZGtKO`). |

## Deploying

Deploy each folder as a Salesforce Metadata API package from the repo root.

```bash
sf project deploy start --metadata-dir NextGenWealth
sf project deploy start --metadata-dir NextGenWealthDataKit
```

The data kit (`NextGenWealthDataKit`) targets a Data Cloud–enabled org and must be deployed in addition to the metadata package; both packages target API 67.0.

## Repository

- **License:** Apache License, Version 2.0 — see [`LICENSE.txt`](./LICENSE.txt) and [`how_to_license.md`](./how_to_license.md).
- **Contributing:** see [`CONTRIBUTING.md`](./CONTRIBUTING.md).
- **Code of conduct:** see [`CODE_OF_CONDUCT.md`](./CODE_OF_CONDUCT.md).
- **Security:** report vulnerabilities via <https://www.sfdc.co/SubmitVuln> (also documented in [`SECURITY.md`](./SECURITY.md)).

## Notes

This is a temporary internal staging repository. The eventual public home for the `NextGenWealth/` and `NextGenWealthDataKit/` packages is the public repo at <https://github.com/salesforce/next-gen-wealth>.
