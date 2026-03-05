# Runbook: Incident Response (Reduce MTTR, Make Failures Boring)

## Trigger
- Alerts firing for critical services (error rate, latency, crash loops)
- SLO burn rate indicates impending breach
- Customer impact reported

## Immediate actions (first 15 minutes)
1. Declare incident severity and assign roles (Incident Commander, Comms, Ops).
2. Confirm observability signals are available (logs/metrics/traces) for the affected service.
3. Stabilize: mitigate blast radius (rollback, disable feature flag, scale up/down).
4. Communicate: acknowledge impact, give next update time, keep a timeline.

## Diagnosis
- Identify the failing dependency or recent change (deploy, config, infra drift).
- Use dashboards + traces to find the top error/latency contributor.
- Validate alert routing and escalation are working.

## Remediation
- Apply the smallest safe change to restore service.
- Capture “what we learned” while context is fresh.

## Prevention
- Ensure every service has SLOs, alerts, and a runbook path in the service catalog.
- Run game days and validate incident readiness periodically (automate checks in CI).

