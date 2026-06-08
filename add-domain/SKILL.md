---
name: jarvis-add-domain
version: 0.0.1
description: |
  Wire a custom domain to your Jarvis app: Route53 hosted zone, ACM cert (DNS-
  validated), ALB listener rule, Amplify Hosting domain (if frontend), and the
  HTTP-to-HTTPS redirect. Replaces the default jarvis.app subdomain. (jarvis)
allowed-tools: [Bash, Read, Write, Edit, AskUserQuestion]
triggers:
  - jarvis add domain
  - use my domain
  - custom domain
  - add ssl
---

# /jarvis-add-domain — custom domain in one command

The 2026-01-16 ALB HTTPS three-part fix is baked in: HTTPS listener on 443, security group rule for 443 from 0.0.0.0/0, ACM cert in ISSUED state. All three are checked, none are skipped.

## Preamble

```bash
[ ! -f .jarvis/profile.json ] && echo "BLOCKED: not a Jarvis project." && exit 1
CURRENT_DOMAIN=$(jq -r '.domain // ""' .jarvis/profile.json)
echo "CURRENT_DOMAIN: ${CURRENT_DOMAIN:-default jarvis.app subdomain}"
```

## Step 1: Domain check

Ask:

> What domain do you want to use? (e.g., mysaas.com or app.mysaas.com)

After they answer:

```bash
# Where is the domain currently registered?
DOMAIN_NS=$(dig +short NS "$DOMAIN" | head -3)
echo "CURRENT_NS: $DOMAIN_NS"
```

Three paths:

Options:
- A) Domain is on Route53 (or I'm ready to transfer NS to Route53) — recommended
- B) Domain is on Cloudflare/Namecheap/GoDaddy — I'll add CNAME records manually
- C) I want to buy this domain now via Route53 ($12-15/yr)

## Step 2: Spawn the Domain specialist (Networking + Deploy combined)

writes_glob:
- `iac/route53/zone.tf` — hosted zone (option A)
- `iac/route53/records.tf` — A/AAAA aliases to ALB and Amplify
- `iac/acm/cert.tf` — wildcard cert + apex, DNS-validated
- `iac/networking/alb_https_listener.tf` — updates ALB to use new cert
- `iac/networking/alb_https_sg.tf` — security group rule for 443
- `iac/networking/alb_http_redirect.tf` — HTTP -> HTTPS redirect

## Invisible rails

- **Wildcard cert** (`*.example.com` + `example.com`) — covers apex and all subdomains
- **DNS validation** (auto-creates CNAME records when option A) — faster than email validation, no manual click
- **HTTP-to-HTTPS redirect** — port 80 listener redirects 301 to 443 (no plain HTTP traffic ever reaches the app)
- **Security group rule for 443 from 0.0.0.0/0** — explicitly added (the 2026-01-16 missing-rule incident)
- **Both apex and www** — `mysaas.com` and `www.mysaas.com` both work (apex aliases to ALB, www CNAMEs to apex)
- **Amplify custom domain** (if frontend stack) — frontend domain attached to the Amplify Hosting app

## Step 3: For option B (external DNS)

Print the exact records the user must add:

```
TYPE    NAME                    VALUE
CNAME   _acme-xxx.mysaas.com    _acme-yyy.acm-validations.aws
A       mysaas.com              alias -> my-saas-alb-12abc.us-east-1.elb.amazonaws.com
CNAME   www.mysaas.com          mysaas.com
```

Wait for the user to confirm records are added (or use `dig` to verify in a loop, max 10 minutes).

## Step 4: Verify

```bash
curl -sv "https://$DOMAIN" --max-time 10 | head -5
```

Must return a successful TLS handshake and a 2xx/3xx HTTP response. If not, surface which of the three (HTTPS listener / SG rule / cert) is the problem.

## Step 5: Completion

> Domain installed.
>   - Apex: https://{{DOMAIN}}
>   - WWW:  https://www.{{DOMAIN}} (redirects to apex)
>   - Cert: ISSUED (wildcard, auto-renewing)
>   - HTTP -> HTTPS: redirect active
> Cost: $0.50/mo per hosted zone + $12/yr if you bought via Route53.

Update `.jarvis/profile.json` with `domain = "{{DOMAIN}}"`.
