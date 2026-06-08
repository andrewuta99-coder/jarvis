---
name: jarvis-add-email
version: 0.0.1
description: |
  Add transactional email via AWS SES: verified sender identity, VPC endpoint
  for SES (prevents the connect-timeout class of bugs), bounce/complaint SNS
  topics, suppression list management, and the IAM policy. Includes templates
  for welcome / password-reset / notification. (jarvis)
allowed-tools: [Bash, Read, Write, Edit, AskUserQuestion]
triggers:
  - jarvis add email
  - add ses
  - send email
  - transactional email
---

# /jarvis-add-email — transactional email done right

The SES connect-timeout bug from CloudMortgage 2026-12-22 is permanently solved here. The VPC endpoint for SES ships with this feature — not as a separate step the user has to remember.

## Preamble

```bash
[ ! -f .jarvis/profile.json ] && echo "BLOCKED: not a Jarvis project." && exit 1
DOMAIN=$(jq -r '.domain // ""' .jarvis/profile.json)
[ -z "$DOMAIN" ] && echo "DOMAIN: none (will use jarvis.app subdomain)"
```

## Cost projection

> About to add: SES (verified sender, VPC endpoint, bounce/complaint SNS, IAM)
> Cost projection:
>   Idle:               +$0/mo (SES free up to 62k emails/month)
>   62k emails/mo:      +$0/mo (free tier)
>   100k emails/mo:     +$3.80/mo
>   VPC endpoint:       +$7.30/mo (2 AZs - required for private subnets)
>
> Proceed?

(Note: VPC endpoint cost is the trade — it prevents the connect-timeout class of incidents that took CloudMortgage half a day to debug.)

## Step 1: Sender identity

Ask:

Options:
- A) Use a subdomain of my jarvis.app domain (recommended for first-time — works in ~60s)
- B) Use my custom domain (requires DNS records — will print MX/TXT/CNAME for you to add)

If B, the user must add records to their DNS provider. Print the records, wait for confirmation. Re-check verification via `aws ses get-identity-verification-attributes` until verified or 5 minutes elapse.

## Step 2: SES sandbox escape

Check if the account is in sandbox mode:

```bash
aws sesv2 get-account --output json | jq '.ProductionAccessEnabled'
```

If false (sandbox), tell the user:

> Your SES account is in sandbox mode — you can only send to verified addresses.
>
> For production, you need to request production access from AWS (24-48hr approval).
> This is a one-time AWS account thing, not Jarvis.
>
> Want me to:
>   A) Open the AWS request page in your browser now (recommended)
>   B) Continue in sandbox for testing — I'll add your test addresses to verified list
>   C) Skip — set this up later

## Step 3: Spawn the Email specialist

writes_glob:
- `iac/ses/identity.tf`
- `iac/ses/vpc_endpoint.tf`            <- the invisible rail
- `iac/ses/sns_bounce_complaint.tf`    <- the invisible rail
- `iac/iam/email_policy.tf`
- `backend/email/*.py` (or .ts/.js)
- `backend/email/templates/*.html`      <- welcome, password-reset, notification
- `tests/integration/test_email.py`

## Invisible rails

- VPC endpoint `com.amazonaws.{region}.email` — prevents `Connect timeout on email.{region}.amazonaws.com` failure mode
- SNS bounce + complaint topics, subscribed to a Lambda that maintains a suppression list
- Suppression list checked before every send — no more sending to known-bouncing addresses
- DKIM enabled (3 CNAME records for sender domain)
- Configuration set with event publishing (CloudWatch) — observability for free
- Send rate cap as a sanity guard (1 email/sec default, raisable)
- Templates use Jinja-style `{{var}}` substitution, escaped HTML by default

## Step 4: Test send

Send a test email to the user's own address (the AWS account owner). If it lands within 30 seconds, the IAM, VPC endpoint, identity, and code are all wired correctly. If not, surface where the failure occurred.

## Step 5: Completion

> Email installed.
>   - Sender: noreply@{{DOMAIN}} (verified, DKIM on)
>   - VPC endpoint: vpce-xxx (SES reachable from private subnets)
>   - Bounce + complaint SNS topics: live, suppression list active
>   - 3 templates ready: welcome, password-reset, notification
>   - send_email() helper imported in backend/email/__init__.py
> Cost: $0/mo at <62k emails (SES free tier) + $7.30/mo for VPC endpoint.
