# Launch Day Checklist

T-minus checklist for the v1.3.0 public launch.

## T-7 days

- [ ] Pull request a fresh AWS sandbox account, run `/jarvis-init` end to end.
      Document any issues. Fix them.
- [ ] Record the 30-second screencast per `DEMO_SCRIPT.md`. Export 1080p.
- [ ] Buy 5 minutes of cloud time to verify `jarvis-doctor` + `/jarvis-eject`
      both work against live resources.
- [ ] Pre-write 12 tweets for the thread, attach the demo video to tweet 1.

## T-1 day

- [ ] Repo description, topics, social-preview image set on GitHub
- [ ] CHANGELOG.md proofread
- [ ] README hero block (the magic moment) reads well on mobile
- [ ] `curl ... | bash` install verified from a fresh laptop one more time
- [ ] HN account warm (some karma, not a fresh account)

## T-0 (launch day)

- [ ] **6:00 AM PT** — HN submit. Title: "Show HN: Jarvis – From blank
      AWS account to deployed SaaS in 10 minutes"
- [ ] **6:02 AM PT** — Post on Twitter/X (the 12-tweet thread)
- [ ] **6:05 AM PT** — Email Corey Quinn (`COREY_QUINN_PITCH.md`)
- [ ] **6:10 AM PT** — Post on r/aws, r/devops, r/SaaS
- [ ] **6:30 AM PT** — Post on Indie Hackers
- [ ] **9:00 AM PT** — Post on Product Hunt
- [ ] **Throughout the day** — Reply to every HN comment within 30 min.
      Be honest about limitations. The good-faith engagement is the launch.

## T+1 day

- [ ] Triage GitHub issues. Reply to every one within 24h.
- [ ] If HN landed front page: don't sleep on the comments. Reply to top
      objections personally.
- [ ] If it didn't: that's fine. Iterate, ship v1.4 with the most-requested
      fix, try again in 30 days. HN is a fickle audience; the work is the
      same either way.

## T+7 days

- [ ] Retro: what landed, what didn't. Update README hero based on what
      objections came up the most.
- [ ] If install count > 100: open an Issue template for "report your
      install experience" — community feedback compounds.
- [ ] Update `MILESTONES.md` with the next 3 months of work.

## Anti-checklist (things NOT to do)

- ❌ Don't post on every platform on the same day. HN + Twitter + Corey
     same day is enough. r/aws and PH spread across the week.
- ❌ Don't argue with HN trolls. State your case once, then mute the
     thread. Hours spent arguing = hours not building v1.4.
- ❌ Don't promise features in comments. Acknowledge requests; deliver
     in commits, not promises.
- ❌ Don't compare to YC / gstack / Garry Tan more than once in the
     post. The comparison is flattering for v1.0 but becomes a crutch.
     Stand on the work.

## Distribution metrics to track

- HN: position over time, comment count, hours on front page
- Twitter: impressions, link clicks, follows gained
- GitHub: stars per hour, forks, issues, first 10 external installs
- Install: count of unique IPs hitting `install.sh` (CDN logs)
- Long tail: organic Google traffic to the repo over the next 90 days

The goal isn't the launch-day spike. The goal is the third-month
trickle of installs from someone finding it via a "SES connect timeout"
Google search and realizing the fix has been sitting in a template
for two years.
