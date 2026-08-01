# Non-Goals

CanvasForge Phase 0/1 and V1 deliberately exclude the following.

## Product non-goals

- Replacing Microsoft Power Apps Studio
- Guaranteeing pixel-perfect Studio rendering without Studio validation
- Supporting every Canvas control, property, or formula in the first release
- Acting as a general Power Platform ALM / DevOps platform
- Building a low-code marketplace or hosted SaaS authoring product in Phase 1

## Technical non-goals (Phase 1)

- Power Apps YAML / Code View generation
- `.msapp` package generation or reverse-engineering
- MCP server
- VS Code or Cursor extension
- React or browser preview application
- TypeScript / Node.js monorepo
- Network access in offline mode
- Microsoft 365 / Power Platform / SharePoint connectivity
- Authentication, OAuth, CAC, certificate, cookie, or token handling
- Telemetry or analytics collection
- Remote manifest includes or URL imports
- Environment-variable interpolation in manifests
- Arbitrary code execution from manifests
- Publishing, sharing, or overwriting apps
- Creating Power Automate flows
- Managing SharePoint permissions or production connectors
- Hard-coding O-Room Actions terminology into core packages

## Safety non-goals

CanvasForge will not:

- Store or request passwords, CAC PINs, certificates, cookies, or secrets
- Accept government/military operational data as sample content
- Silently perform destructive tenant operations in future connected modes

## Future consideration (explicitly later)

These may be evaluated in later phases only if a Microsoft-supported, validated path exists:

- Code View YAML adapters
- Canvas authoring MCP integration
- Verified source/package workflows
- Controlled connected updates with human approval
- Importable artifacts where technically supported

Until those paths are validated, CanvasForge remains an offline manifest and planning tool.
