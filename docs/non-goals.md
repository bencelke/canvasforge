# Non-Goals

CanvasForge deliberately excludes the following from the current offline App Factory core.

## Product non-goals

- Replacing Microsoft Power Apps Studio
- Guaranteeing pixel-perfect Studio rendering without Studio validation
- Claiming local preview equals the Power Apps runtime
- Supporting every Canvas control, property, or formula in the first release
- Acting as a general Power Platform ALM / DevOps platform
- Building a low-code marketplace or hosted SaaS authoring product
- Requiring AVD, tenant login, or Microsoft API access for core usefulness

## Technical non-goals (current phases)

- Live Microsoft 365 / Power Platform / SharePoint connectivity in core flows
- Authentication, OAuth, CAC, certificate, cookie, or token handling
- Telemetry or analytics collection
- Remote manifest includes or URL imports
- Environment-variable interpolation in manifests
- Arbitrary code execution from manifests
- Publishing, sharing, or overwriting apps
- Creating Power Automate flows
- Managing SharePoint permissions or production connectors
- Hard-coding O-Room Actions terminology into core packages
- Default `.msapp` generation without a validated Microsoft-supported path
- AI inside the work-side Runner

## Safety non-goals

CanvasForge will not:

- Store or request passwords, CAC PINs, certificates, cookies, or secrets
- Accept government/military operational data as sample content
- Silently perform destructive tenant operations in future connected modes
- Ship Deployment Kits containing tenant connections or real data

## Future consideration (explicitly later)

These may be evaluated in later phases only if a Microsoft-supported, validated path exists:

- Deployment Kit builder and Runner (Phases 3B / 8)
- Local graphical preview (Phase 4)
- Expanded Power Fx templates (Phase 6)
- Experimental `.msapp` adapter (Phase 9)
- Studio Compatibility Laboratory fixtures (Phase 10)
- Canvas authoring MCP / connected updates with human approval (optional adapter)

Until those paths are validated and scheduled, CanvasForge remains an offline App Factory centered on manifests, Candidate Code View, and portable kits.
