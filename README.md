# next-gen-wealth

Source for the **FSC Agentic Advisor** managed-package payload that powers the Next Gen Wealth experience inside Salesforce Financial Services Cloud (FSC).

The repo is the staging ground for the public mirror at <https://github.com/salesforce/next-gen-wealth>; the `NextGenWealth/` and `NextGenWealthDataKit/` folders are eventually copied there.

## What the package gives a wealth advisor

Once installed, the package layers an agentic, AI-assisted workflow on top of an FSC org:

- **Two custom Account record pages** (one for Household accounts, one for Person accounts) that surface client context, the household relationship graph, an AUM/last-interaction summary card, financial accounts, meetings, and recommended actions.
- **A Client Pulse capability** that, given an Account, generates an at-a-glance narrative of the client's current financial state, what has changed since the last interaction, and what the advisor should prioritize next.
- **An Annual Review Meeting Playbook** that drives the full meeting lifecycle (pre-meeting research, in-session discussion guide, post-meeting follow-up), composing GenAI prompt templates from this package and from `meetingcenter_wealth` / `meetingcenter`.
- **Post-meeting automations** that turn the meeting transcript / notes into structured Salesforce work: creating or updating Financial Goals, creating Tasks, creating Person Life Events, and updating the Household.

Underneath, a **Data Cloud data kit** wires the FSC Sales/Service Cloud data into 16 streams plus an Individual identity-resolution ruleset, so the prompt-grounding flows can reason over a unified household view.

## Repository layout

| Folder | What it contains |
|---|---|
| [`NextGenWealth/`](./NextGenWealth) | Salesforce metadata package (API 67.0): Lightning record pages, prompt-grounding & automation flows, GenAI prompt templates, the Annual Review meeting playbook, and the household relationship graph. |
| [`NextGenWealthDataKit/`](./NextGenWealthDataKit) | Data Cloud data kit (API 67.0): data streams, data lake objects, data source / field maps, data transforms, and the FSC Individual identity-resolution ruleset. |
| `LICENSE.txt`, `how_to_license.md` | Apache License 2.0. |
| `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md` | Community / governance / security docs. |

---

## `NextGenWealth/` -- the metadata package

`NextGenWealth/package.xml` declares the deployable manifest (API `67.0`). Five metadata types ship in it:

### Lightning record pages -- `flexipages/`

Both pages have `sobjectType = Account`.

#### `NextGenWlthMgmt_HshldAcct_Pkg_rec_L` -- *Agentic Advisor Household Record Page For Package*

The household record page composes:

- `force:highlightsPanel` (header), `force:detailPanel` (details tab)
- `runtime_industries_client360:clientProfileCard` -- shows the primary household member's `Name`, `PersonEmail`, `Phone` alongside the household's `FinServ__AUM__c` and `FinServ__LastInteraction__c`
- `runtime_industries_arcgraph:arcGraph` -- renders the `Household_Graph_for_Managed_Package` relationship graph
- `runtime_industries_client360:financialPortfolioContainer` -- portfolio summary
- `runtime_industries_client360:recommendedActions` -- AI-driven next-best-action surface
- `runtime_industries_meetingengagement:meetingList` -- household-scoped meetings list
- `runtime_sales_activities:activityPanel`, `FinServ:FinancialAccountList`, `force:relatedListContainer`, `runtime_omnistudio:flexcard`, tabset / tabs

#### `NextGenWlthMgmt_PersonAcct_Pkg_rec_L` -- *Agentic Advisor Person Account Record Page For Package*

Same building blocks as the household page **minus** `arcGraph` and the household-specific `clientProfileCard` configuration (a person account has no group graph to draw).

### Flows -- `flows/` (all `apiVersion = 67.0`)

| Flow | Purpose |
|---|---|
| **`Client_Summary_FSC_Package`** | Prompt-grounding flow for the *Create Annual Review Client Summary* prompt template. Input is a `MeetingPlaybookStage`; the flow walks the household / person account, financial accounts, financial goals, cases, and prior meetings, and emits a structured `$Output.Prompt` text block consumed by the LLM. |
| **`Create_Meeting_from_Event_FSC_package`** | Creates a Meeting record from an Event when an advisor schedules an Annual Review (or Prospecting) Meeting. Surfaces a fault path with an explicit error if the Annual Review / Prospecting templates aren't found, and includes a *Have Household?* decision so household and person flows diverge cleanly. |
| **`Create_Person_Life_Event_FSC_Package`** | Post-meeting automation. Invokes an AI action to suggest a Life Event from the meeting-playbook stage notes (`Get Life Event Suggestion`), then routes through a *Person or Household Account?* decision to set the correct Contact / Primary Member Account, and creates the `PersonLifeEvent` record. |
| **`GetAcctDtlClntPulsePkg`** | Prompt-grounding flow for the *Client Pulse* prompt templates. Validates the input Account, classifies it (Person vs. Household via `FinServ__GroupRecordTypeMapper__mdt`), and assembles a single prompt block of Account, Financial Goals, Financial Account Roles, Person Life Events, Open Cases, and last Meeting / Call interaction. Standard-world counterpart lives in `core/next-gen-wealth-impl/flows/nextgenwealth/GetAcctDtlForClntPulse-1.flow`. |
| **`Periodic_Create_New_Goals_Or_Update_Existing_Goals_FSC_Package`** | Post-meeting automation. Calls an AI prompt to extract new financial-goal suggestions from the post-meeting notes, parses the JSON one index at a time (`Get Goal By Index`, `Increment Goal Index`, `Store Current Goal JSON`), and creates or updates `FinServ__FinancialGoal__c` records under the correct primary member. |
| **`Prep_Brief_Summary_FSC_Package`** | Prompt-grounding flow for the *Create Annual Review Preparation Brief* prompt template. Gathers per-account financial holdings, financial accounts, financial goals, cases, document summaries, and prior client summary into the prompt context. |

### GenAI prompt templates -- `genAiPromptTemplates/`

All four templates run on the `sfdc_ai__DefaultBedrockAnthropicClaude45Sonnet` primary model and ship in `Published` status.

| Template | Input | Backing grounding flow | Output shape |
|---|---|---|---|
| **`Create_Annual_Review_Client_Summary_FSC_Package`** | `SOBJECT://MeetingPlaybookStage` | `flow://Client_Summary_FSC_Package` | 120-130 word client summary with a bold header (name, age, AUM, risk profile) and up to five bullets labelled **Goals**, **Financial Context**, **Sentiment**, **Risk Sensitivity**, **Advisor Priority**. |
| **`Create_Annual_Review_Preparation_Brief_FSC_Package`** | `SOBJECT://MeetingPlaybookStage` | `flow://Prep_Brief_Summary_FSC_Package` | 220-250 word meeting-specific prep brief with ## sections **Since Last Meeting**, **Portfolio**, **What's Changed**, **Suggested Agenda**, **Meeting Priorities**. |
| **`GenerateClientPulseForHouseholdMngPkg`** | `SOBJECT://Account` (household) | `flow://GetAcctDtlClntPulsePkg` | Four-section household insight card: **Summary**, **What changed since the Last interaction date**, **Why it matters**, **Key Data Points**, all anchored against the last Meeting / Call `LastModifiedDate`. |
| **`GenerateClientPulseForPersonAccountMngPkg`** | `SOBJECT://Account` (person) | `flow://GetAcctDtlClntPulsePkg` | Person-account variant of the same Client Pulse output. |

All templates use a `fileDroppingStrategy` that drops the oldest grounding files first when context is over budget.

### Meeting playbook -- `meetingPlaybookDefinitions/Annual_Review_FSC_Package`

> *"Ideal for quarterly or annual check-ins with existing clients. Includes pre-meeting research, in-session discussion guide, and post-meeting follow-up."*

A three-stage playbook composing prompts from this package and from sibling FSC packages (`meetingcenter_wealth`, `meetingcenter`):

| Stage | Capabilities (in `capabilityOrder`) |
|---|---|
| **PreMeeting** (`stageOrder=1`) | `ClientSummary` → `Create_Annual_Review_Client_Summary_FSC_Package`; `MeetingPrepBrief` → `Create_Annual_Review_Preparation_Brief_FSC_Package`; `DocumentSummaryPrompt` → `meetingcenter_wealth__DocumentSummaryPrompt`. |
| **InSession** (`stageOrder=2`) | `MeetingDiscussionGuide` → `meetingcenter_wealth__PeriodicDiscussionGuidePrompt`; `VoiceRecordPrompt` → `meetingcenter__TranscriptSummaryPrompt`; `DocumentSummaryPrompt`; `TakeMeetingNotesPrompt` → `meetingcenter__TakeMeetingNotesPrompt`. |
| **PostMeeting** (`stageOrder=3`) | `FollowupSummaryPrompt` → `meetingcenter_wealth__PeriodicPostMeetingPrompt`; **Generate Follow-up Email** (`meetingcenter_wealth__PeriodicClientEmailPrompt`); **Create or Update Goal** (`Periodic_Create_New_Goals_Or_Update_Existing_Goals_FSC_Package`, `isAllowMultipleUse=true`); **Create Tasks** (`meetingcenter_wealth__PrdCreateTask`); **Create Life Event** (`Create_Person_Life_Event_FSC_Package`); **Update Household** (`meetingcenter_wealth__GetHshldUpdtMtg`). |

The playbook ships with `isActive=false` so admins can review / enable per-org.

### Relationship graph -- `relationshipGraphDefinitions/Household_Graph_for_Managed_Package`

A `HorizontalHierarchy` graph (`isActive=true`, `styleVariant=NextGen`) used by the household record page's `arcGraph` component. The graph models:

- **Root** -- `Account` (the household).
- **Members** -- `Contact` via `AccountContactRelation`. Displays `Title`, `FinServ__Age__c`, `Phone`; marks the primary member via `FinServ__Primary__c` with a `utility:favorite` indicator.
- **Related Contacts** -- `Contact` via `FinServ__ContactContactRelation__c` -- per-member related contacts.
- **Member Accounts** -- `Account` via `AccountContactRelation` filtered by `FinServ__IncludeInGroup__c = true`.
- **Related Groups** -- `Account` via `FinServ__AccountAccountRelation__c` where `RecordType.DeveloperName = IndustriesHousehold`.
- **Related Accounts** -- `Account` via `FinServ__AccountAccountRelation__c` where `RecordType.DeveloperName != IndustriesHousehold`.

---

## `NextGenWealthDataKit/` -- the Data Cloud data kit

`NextGenWealthDataKit/package.xml` declares the Data Cloud manifest (API `67.0`).

The data kit definition `FSCAgenticAdvisorPackageDataKit` is the entry point:

> *"This data kit includes data streams, data lake objects, data transforms, field mappings, and identity resolution for Financial Services Cloud."*

Deployment order from the kit's `<deploymentOrder>`:

1. **`FSCAgenticAdvisorPackageDataBundle`** (`DataStream` bundle) -- the Salesforce Sales & Service Cloud source bundle.
2. **`FinServ_FinancialAccountBalance_c_Home`** (`MktDataLakeObject`) -- the Financial Account Balance DLO.
3. **`FSCAgenticAdvisorFADataTransforms`** (`MktDataTransform`) -- data transforms.
4. **`Individual_FSC`** (`IdentityResolution`) -- the *FSC Individual Ruleset*: *"Ruleset to perform identity resolution for Individual records from BridgeFT and CRM"*. Resolves on `ssot__Individual__dlm` and unifies into `UnifiedssotIndividualFsc__dlm` using match rules over Last Name, First Name, Email, Birth Date, Address Line 1, City, Country, etc.

### What each subfolder holds

| Folder | Contents |
|---|---|
| `dataKitObjectTemplates/` | `FSCAgenticAdvisorFADataTransforms` (data transforms) and `Individual_FSC` (the FSC Individual identity-resolution ruleset). |
| `dataPackageKitDefinitions/` | The top-level kit definition `FSCAgenticAdvisorPackageDataKit`. |
| `DataPackageKitObjects/` | ~37 DMO/DLO object declarations referenced by the kit (`FSCAgenticAdvisorPackageDataKit1`..`92` plus two timestamped variants). |
| `dataSourceBundleDefinitions/` | `FSCAgenticAdvisorPackageDataBundle` -- the Salesforce Sales & Service Cloud data bundle. |
| `dataSourceObjects/` | Source-object descriptors for each data stream below, plus `FinServ_FinancialAccountBalance_c_Home`. |
| `dataSrcDataModelFieldMaps/` | Several hundred field-level mappings: source CRM/FSC object → DMO. Examples include `DataSrcDataModelFinAccSrcIdMap`, `DataSrcDataModelGoalPartyToGoalMap`, `DataSrcDataModelFCAIdMap`, and the `PartyProfileKitSalesforce_Home*` / `ExportPackageKitSalesforce_Home*` / `ExtractDataKit*` families. |
| `dataStreamTemplates/` | 16 stream templates (see below). |
| `mktDataSources/` | Underlying `mktDataSource` records: `FinServ_FinancialAccountBalance_c_Home`, `Salesforce_00Dxx00sfmZGtKO`. |

### Data streams (16)

`refreshFrequency = BATCH`, `refreshMode = UPSERT`, all tied to the `FSCAgenticAdvisorPackageDataBundle` bundle:

`Account`, `AccountContactRelation`, `Contact`, `Financial_Account`, `Financial_Account_Role`, `Financial_Custodian`, `Financial_Custodian_Advisor`, `Financial_Goal`, `Financial_Holding`, `Financial_Plan`, `Lead`, `Party_Profile`, `Person_Life_Event`, `Referral`, `Securities`, `User`.

---

## How the pieces fit together at runtime

```
                           ┌─────────────────────────────────────┐
   Advisor opens Account ─►│  NextGenWlthMgmt_*_Pkg_rec_L page   │
                           │   - clientProfileCard               │
                           │   - arcGraph (household only)       │◄─ relationshipGraphDefinitions/
                           │   - financialPortfolioContainer     │   Household_Graph_for_Managed_Package
                           │   - meetingList                     │
                           │   - recommendedActions              │
                           │   - generateSummaryWrapper          │
                           └────────────────┬────────────────────┘
                                            │
                                            ▼  Client Pulse / Annual Review
                ┌───────────────────────────────────────────────────────┐
                │  GenAiPromptTemplate (Claude 4.5 Sonnet via Bedrock)  │
                │   - GenerateClientPulseFor{Household,PersonAccount}…  │
                │   - Create_Annual_Review_Client_Summary_FSC_Package   │
                │   - Create_Annual_Review_Preparation_Brief_FSC_Package│
                └────────────────────┬─────────────────────────────────┘
                                     │ flow://… data provider
                                     ▼
                ┌───────────────────────────────────────────────────────┐
                │  Grounding flows (apiVersion 67.0)                    │
                │   - GetAcctDtlClntPulsePkg   (Client Pulse)           │
                │   - Client_Summary_FSC_Package     (Annual Review)    │
                │   - Prep_Brief_Summary_FSC_Package (Annual Review)    │
                └────────────────────┬─────────────────────────────────┘
                                     │ SOQL via FSC managed-package objects
                                     ▼
                ┌───────────────────────────────────────────────────────┐
                │  FSC data model                                       │
                │   Account, AccountContactRelation,                    │
                │   FinServ__GroupRecordTypeMapper__mdt,                │
                │   FinServ__FinancialGoal__c, FinServ__FinancialAccount,│
                │   FinServ__FinancialAccountRole__c,                   │
                │   PersonLifeEvent, Case, Event ...                    │
                └───────────────────────────────────────────────────────┘

   Annual Review Meeting Playbook (Annual_Review_FSC_Package):
   PreMeeting  ─► ClientSummary + PrepBrief + DocumentSummary
   InSession   ─► DiscussionGuide + TranscriptSummary + TakeMeetingNotes
   PostMeeting ─► Follow-up Email
                  + Periodic_Create_New_Goals_Or_Update_Existing_Goals_FSC_Package
                  + Create Tasks
                  + Create_Person_Life_Event_FSC_Package
                  + Update Household
```

The Data Cloud kit feeds the same FSC objects via `Account_Data_Stream`, `Financial_*_Data_Stream`, `Person_Life_Event_Data_Stream`, etc., and the `Individual_FSC` ruleset unifies people into a single profile so household-level queries return a coherent picture.

---

## Deploying

Both packages are metadata-API format with a top-level `package.xml`. Deploy each from the repo root with the Salesforce CLI:

```bash
# Salesforce metadata package
sf project deploy start --metadata-dir NextGenWealth

# Data Cloud data kit (requires a Data Cloud-enabled org)
sf project deploy start --metadata-dir NextGenWealthDataKit
```

Notes:
- Both packages target API version `67.0`.
- The metadata package assumes the org has the FSC managed package installed (every flow and flexipage references `FinServ__*` objects / fields).
- The data kit's `FSCAgenticAdvisorPackageDataKit` ships with `isDeployed=false` and `isEnabled=false`; enable it in the Data Cloud Data Kit UI after deploy.
- The Annual Review playbook ships with `isActive=false`; activate per-org in the Meeting Playbook setup.

## Repository docs

- **License:** Apache License, Version 2.0 -- see [`LICENSE.txt`](./LICENSE.txt) and [`how_to_license.md`](./how_to_license.md).
- **Contributing:** see [`CONTRIBUTING.md`](./CONTRIBUTING.md).
- **Code of conduct:** see [`CODE_OF_CONDUCT.md`](./CODE_OF_CONDUCT.md).
- **Security:** report vulnerabilities via <https://www.sfdc.co/SubmitVuln> (also documented in [`SECURITY.md`](./SECURITY.md)).

## Status

This is a temporary internal staging repository. The eventual public home for the `NextGenWealth/` and `NextGenWealthDataKit/` packages is the public repo at <https://github.com/salesforce/next-gen-wealth>.
