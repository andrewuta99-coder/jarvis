# 30-Second Demo Script

The screencast that ships with the HN post. No voice-over. Music optional.

## Setup before recording

- Fresh AWS account (or sandbox sub-account) with `aws configure` done
- Claude Code session in an empty directory
- Browser windows pre-positioned:
  - Top half: terminal + Claude Code
  - Bottom half: AWS Console (showing empty resources list)
- Audio: ambient or off — the visual carries the story
- Recording: 1080p, 30fps minimum, ~30 seconds total

## Storyboard

| Time | Frame |
|------|-------|
| 0:00 | **Cold open.** Empty terminal. Empty AWS Console showing 0 ECS services, 0 DynamoDB tables. Text overlay: "Brand new AWS account." |
| 0:03 | Type: `/jarvis-init my-saas` — hit enter |
| 0:05 | 4-question interview: AI SaaS / CRA / FastAPI / us-east-1 (arrow-key selects, fast) |
| 0:12 | **Visible progress bars.** Phase 1 (foundation): networking, infra, data — all three at once. ~3 seconds elapsed time on the speeded-up screen |
| 0:16 | Phase 2 (services): auth, ai, backend, frontend in parallel |
| 0:20 | Phase 3 (integration): email, payments, deploy |
| 0:23 | Phase 4 (ship): "terraform apply" — green checkmarks scroll |
| 0:26 | **Browser opens automatically** to `https://my-saas-12abc.jarvis.app/login` |
| 0:27 | Quick login as `demo@...` with `demo` password |
| 0:28 | Dashboard. Click "Chat" — AI replies. Click "Billing" — Stripe checkout opens |
| 0:30 | **End card**: "AWS-native. No lock-in. MIT. github.com/andrewuta99-coder/jarvis" |

## Key visual moments

1. **Parallel agents** must read visually as parallel. Three progress
   bars filling simultaneously, not sequentially. This is the whole pitch
   in one frame.
2. **Zero AWS console clicks** — the AWS console stays visible the whole
   time, showing resources appearing without anyone touching it.
3. **The live URL** is the climax. The browser opening to a working app
   on a real domain is the "holy shit it works" moment.

## What NOT to show

- Don't show the 4-question interview slowly. Speed it up to ~0.5x — the
  point is "answer 4 questions" not "read 4 questions."
- Don't show the AWS Console deeply. Glances only. The point is "stuff
  appeared" not "look at all this complexity."
- Don't show the chat working in detail. One reply, one frame, move on.
- No voiceover, no music with lyrics. Either ambient bed or pure visual.

## Variants

| Variant | Length | Audience | Differences |
|---|---|---|---|
| HN/Twitter | 30s | Cold | No setup, just the magic moment. End card with URL. |
| Indie Hackers | 60s | Warm | Add a "how it works under the hood" final shot with the constellation diagram |
| YC pitch | 120s | Investor | Adds cost projection ($14/mo idle), Vercel comparison, mention CloudMortgage as validation |
| Conference talk intro | 90s | Engineer | Show the actual generated Terraform afterwards — "this is what your team will maintain" |

## Recording tools

- Mac: Screen Studio (paid, the best quality), CleanShot X (cheaper),
  built-in Cmd+Shift+5 (free, lowest quality)
- Add captions in post if making sound off-friendly
- Export at 1080p H.264, target ~3MB so it autoplays cleanly on Twitter

## Captions for sound-off viewers

Big text overlays at key transitions:
- "Brand new AWS account"
- "4 questions"
- "10 specialists, 4 phases, in parallel"
- "Zero clicks in AWS console"
- "Live URL in 10 minutes"
- End card.

## Status

To record after the first real end-to-end sandbox run (v1.1 gate). The
storyboard is locked; the recording is a 30-minute task once the demo
actually runs clean against a fresh AWS account.
