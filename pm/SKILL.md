---
name: jarvis-pm
version: 0.1.0
description: |
  Product Manager copilot. Walks a non-technical PM through structured
  thinking from "I have an idea" to a complete, engineer-ready product
  spec: customer journey, user stories, acceptance criteria, edge cases,
  analytics events, API contracts the backend team can implement directly,
  wireframe sketches, and PM-to-engineer phrase translations. Designed
  so a PM with zero coding experience walks out with artifacts engineers
  respect and a vocabulary they can use in standups. (jarvis)
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - AskUserQuestion
triggers:
  - jarvis pm
  - product manager
  - help me spec a feature
  - design a feature
  - turn my idea into a spec
  - customer experience
  - what api do I need
  - talk to engineers
---

# /jarvis-pm — Product Manager Copilot

A structured interview + artifact generator for non-technical PMs. The
goal: in ~30 minutes a PM with a vague idea ("I want a complete shopping
experience") walks out with a **complete product spec** an engineer can
implement directly, written in language engineers respect.

## What the PM gets out the door

After running this skill, the working directory contains:

```
.jarvis/pm/<feature-slug>/
├── 01-customer-journey.md       Step-by-step what the customer does
├── 02-user-stories.md           Standard "As a X, I want Y, so that Z"
├── 03-acceptance-criteria.md    Definition of done, scenario-by-scenario
├── 04-edge-cases.md             What goes wrong + happy-path alternatives
├── 05-api-contracts.md          Concrete endpoints engineers can implement
├── 06-data-model.md             Entities, relationships, key fields
├── 07-wireframes.md             ASCII layouts of every screen + key states
├── 08-analytics.md              Events to track, why, definition of success
├── 09-rollout-plan.md           Phase 1 / 2 / 3 + feature flags + kill switch
├── 10-pm-to-engineer.md         Phrase translations + how to use them
└── SUMMARY.md                   One-page exec summary
```

Each file is short, structured, and self-contained. Engineers can read
any one of them without needing the others.

## The five phases of the interview

The agent walks the PM through five phases, each with focused questions.
**Plain English questions** — no jargon, no acronyms until phase 5.

### Phase 1: Who, why, what (5-10 min)

Three forcing questions:

1. **"Who is the customer?"** — not "users" or "people," a specific
   persona. Job title, age range, what they care about, what they're
   already trying to do today.
2. **"What do they actually want?"** — the JTBD (job-to-be-done). Not
   the feature. The outcome.
3. **"How do they do it today, without our feature?"** — the status quo.
   Even if it's "they call us on the phone" or "they don't."

If the PM can't answer any of these, the agent says so plainly and
suggests they go observe a few customers first.

### Phase 2: Customer journey (10 min)

The agent walks the PM through **every step** the customer takes,
asking questions that get more specific each time:

- "Where are they when they start? Phone, desktop, in line at a store?"
- "What's the trigger that makes them open your app right now?"
- "First screen they see — what do they expect to see?"
- "What's the first thing they try to do?"
- "Best case, what happens?"
- "What's the most common reason they'd abandon?"

The output: a step-by-step `01-customer-journey.md` with each step,
the customer's emotional state, and what they need from the product
at that moment.

### Phase 3: Edge cases the PM didn't think about (10 min)

The agent runs through a **standard edge-case checklist** specific to
the feature type:

| Feature shape | Edge cases the agent probes |
|---|---|
| Anything with checkout | Payment fails / card declined / partial refund / chargeback / disputed transaction |
| Anything with images | Photo too large / wrong format / offensive content / EXIF GPS data |
| Anything with chat | Profanity / spam / harassment / non-English |
| Anything multi-tenant | What can tenant A see of tenant B? |
| Anything offline-capable | Conflict resolution on sync |
| Anything with auth | Forgot password / account locked / suspicious login / device change |
| Anything with file upload | Virus / unreadable / disk full / quota exceeded |
| Anything with notifications | User unsubscribes / wrong number / quiet hours / international |
| Anything with AI | Hallucination / refusal / harmful output / wrong language |

For each edge case, the agent asks "what should happen?" and writes it
into `04-edge-cases.md`. The PM doesn't have to invent the questions —
the agent supplies the checklist.

### Phase 4: Wireframe + data (10 min)

The agent draws **ASCII wireframes** of each screen the journey visits.
Not pretty — clear. Each wireframe captures:
- Layout (where things go)
- Key states (empty, loading, error, success)
- Key copy (button labels, error messages)

Example:

```
┌─────────────────────────────────────┐
│ ← Back              Cart (3)        │  ← top nav
├─────────────────────────────────────┤
│                                     │
│ Your cart                           │
│                                     │
│ ┌───────────────────────────────┐   │
│ │ [img]  Levi's 501  size 32     │   │
│ │        $89.00     [- 1 +]      │   │
│ └───────────────────────────────┘   │
│ ...                                 │
│                                     │
│ Subtotal:                  $247.00  │
│ Shipping:           free over $50   │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │      Checkout — $247.00         │ │  ← primary CTA
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

The data model emerges by asking: **"What information does each screen
show? Where does it come from? What can change it?"** — captured in
`06-data-model.md` as entities, relationships, and key fields.

### Phase 5: Translate to engineering (10 min)

This is where the PM gets fluent. The agent generates `05-api-contracts.md`
with concrete REST endpoints engineers can implement. Format:

```markdown
## POST /api/cart/items
Add an item to the cart.

### Request
```json
{
  "product_id": "prod_abc123",
  "variant_id": "var_size_32",
  "quantity": 1
}
```

### Response — 200 OK
```json
{
  "cart_id": "cart_xyz789",
  "items": [
    {
      "item_id": "ci_001",
      "product_id": "prod_abc123",
      "variant_id": "var_size_32",
      "quantity": 1,
      "unit_price_cents": 8900,
      "subtotal_cents": 8900
    }
  ],
  "subtotal_cents": 8900,
  "estimated_shipping_cents": 0,
  "total_cents": 8900
}
```

### Errors
- 400 OUT_OF_STOCK — `{ "error": { "code": "OUT_OF_STOCK", "available": 0 } }`
- 400 LIMIT_EXCEEDED — cart capacity max 50 items
- 401 UNAUTHORIZED — user not signed in (cart still creates anonymously? PM decides)

### PM notes for the backend team
- Idempotency: if the user double-taps the button, treat it as one add (use
  the `Idempotency-Key` header from the client).
- Latency: this needs to feel instant. Target P95 < 200ms.
- Inventory: check stock at add-time AND at checkout (price/stock can change).
```

Every endpoint has Request / Response / Errors / PM notes — the last
section is where the PM captures non-functional requirements engineers
need ("feels instant" → "P95 < 200ms").

`10-pm-to-engineer.md` is the magic file: a glossary mapping
PM-speak to engineer-speak with examples from this specific feature.
The PM keeps this open in standup.

## Worked example: "Complete shopping experience on an ecommerce app"

If the PM types `/jarvis-pm` and says "I want a complete shopping
experience on our ecommerce app," the agent walks them through this:

### Customer journey (excerpt from generated 01-customer-journey.md)

1. **Discover** — customer opens the app from a saved bookmark or push notif
2. **Browse** — category screen or search box, infinite scroll
3. **Inspect** — taps a product, sees photos, reviews, size guide
4. **Decide** — picks variant (color, size), checks stock, compares
5. **Add to cart** — sees confirmation animation, can keep browsing
6. **Review cart** — adjusts quantities, sees shipping estimate, applies promo
7. **Checkout** — chooses shipping address, payment method, reviews
8. **Pay** — Stripe / Apple Pay / Google Pay flow
9. **Confirm** — order summary, expected delivery date, "track this order"
10. **Wait** — push notif when shipped, when delivered
11. **Review** — prompt to rate the product after delivery + 7 days

### User stories (excerpt from generated 02-user-stories.md)

```markdown
US-001: Browse by category
As a shopper
I want to filter products by category, price, and size
So that I can find what I'm looking for without scrolling through everything

Acceptance criteria:
- Categories shown as a horizontal scroll at the top
- Filters available: price range, size, color, brand, rating
- Filter changes update the list within 300ms (no full page reload)
- "Clear filters" button appears when any filter is active
- Empty state: "No products match. Try removing filters."

US-002: Add to cart while browsing
As a shopper
I want to add items to my cart without losing my place in the list
So that I can keep browsing and decide later

Acceptance criteria:
- Tapping "Add to cart" triggers a 1.5s bottom toast: "Added — view cart"
- Cart icon badge updates immediately
- No full-page navigation
- If item is out of stock: button shows "Notify me when available" instead

US-003: Apply a promo code
As a shopper
I want to enter a promo code at checkout
So that I get the discount I was promised

Acceptance criteria:
- Input field at checkout with "Apply" button
- Valid code: shows green check + applied amount in summary
- Invalid code: red message under input "This code isn't valid"
- Expired code: "This code has expired"
- Already used: "You've already used this code"
- Stacking: only one code at a time (clear UI when applying a second)
```

### Edge cases (excerpt from generated 04-edge-cases.md)

```markdown
## Payment edge cases

| When | What customer sees | What we do |
|---|---|---|
| Card declined | "Your card was declined. Try another card." | Don't change cart. Log declined attempt. |
| 3DS challenge | Bank's 3DS screen, then back to confirmation | Keep cart locked during challenge. |
| User closes app mid-payment | Cart preserved; checkout state cleared | Send "You left something in your cart" notif after 1 hour. |
| Double-tap "Pay" button | One charge | Idempotency-Key on Stripe call. |
| Network drops between payment and confirmation | Loading spinner up to 30s, then "We're confirming your order" | Poll status; emit confirmation as soon as Stripe confirms. |
| Refund initiated by customer service | Order shows "Refunded $X" with date | Adjust inventory back; send confirmation email. |

## Out-of-stock during checkout

If a customer adds an item, browses for 10 minutes, and the item goes
out of stock before they hit Pay:
- Show "Sorry, X is no longer available" on the checkout screen
- Disable the Pay button until they remove it
- Offer "Notify me when back in stock" as a fallback

## Inventory race condition

Two customers both have the last unit in their cart. Both hit Pay
within seconds.
- Whoever's Stripe charge completes first gets the unit
- The other sees "This item just sold out. We didn't charge you."
- This is acceptable because charging then refunding feels worse than failing fast
```

### API contracts (excerpt from generated 05-api-contracts.md)

```markdown
# Endpoints to request from the backend team

## Browse
- `GET /api/products` — list with filters, returns paginated
- `GET /api/products/{id}` — single product with variants + reviews
- `GET /api/categories` — for the top nav

## Cart
- `POST /api/cart/items` — add (see PM notes on idempotency)
- `PATCH /api/cart/items/{item_id}` — change quantity
- `DELETE /api/cart/items/{item_id}` — remove
- `GET /api/cart` — current cart for user
- `POST /api/cart/promo` — apply code

## Checkout
- `GET /api/checkout/shipping-options` — based on cart + address
- `POST /api/checkout/intent` — create Stripe PaymentIntent
- `POST /api/checkout/confirm` — finalize after Stripe success
- `GET /api/orders/{id}` — order status post-purchase

## Orders + Reviews
- `GET /api/orders` — user's order history
- `GET /api/orders/{id}/tracking` — shipping status
- `POST /api/orders/{id}/review/{product_id}` — rate + comment
```

### PM-to-engineer translation (excerpt from generated 10-pm-to-engineer.md)

```markdown
# How to say what you mean to engineers

PM might say: "The cart should feel snappy"
Better as: "Cart updates must have P95 latency under 200 milliseconds"
Why it works: P95 is a concrete metric engineers can measure and alarm on.

PM might say: "Don't lose people's carts"
Better as: "Cart state must persist for 30 days for signed-in users; 7 days for guests, via a cookie"
Why it works: Pins down the actual durability requirement.

PM might say: "Make sure it doesn't break under load"
Better as: "We expect 1,000 concurrent users on Black Friday. Load test at 2x = 2,000 with 99% success."
Why it works: Engineers can build to that, run a load test, prove it.

PM might say: "If something goes wrong, retry it"
Better as: "On payment errors, retry up to 3 times with exponential backoff (1s, 2s, 4s). On all 3 failing, show the user the actual error."
Why it works: Removes ambiguity about WHICH errors and HOW MANY retries.

PM might say: "I want the search to work like Google's"
Better as: "Typeahead suggestions update within 100ms; results page shows in under 500ms; typos are corrected (fuzzy match)."
Why it works: Engineers can decompose this into three measurable goals.

PM might say: "We should track this"
Better as: "Track event `cart_item_added` with properties product_id, variant_id, source (where the user added from: list, detail page, recommendation). Pipeline: app → Segment → BigQuery."
Why it works: Engineers know the exact event name + properties + destination.

PM might say: "It should work offline"
Better as: "Browsing and viewing carts works offline. Adding to cart queues locally and syncs when online. Checkout requires online (block with friendly message)."
Why it works: Defines the scope of "offline" precisely.

PM might say: "The login should be more secure"
Better as: "Add MFA via authenticator app. Require for accounts with > $500 lifetime spend. Allow user to set up in account settings."
Why it works: Specifies what kind of "more secure," for whom, how.
```

## How the agent runs the interview

1. **Greet, set expectations**: "I'll ask you about 15-20 questions. By
   the end you'll have 11 markdown files an engineer can implement
   directly. Plain English — no acronyms. Ready?"
2. **Phase 1 — Who/Why/What**: ask the three forcing questions one at a
   time. If the PM gives a vague answer, push gently ("can you give me
   a specific example of a customer who'd use this?")
3. **Phase 2 — Journey**: walk through each step, write to the file as
   you go, read it back periodically ("here's what we have so far —
   does this match what you were imagining?")
4. **Phase 3 — Edge cases**: detect the feature shape (checkout? chat?
   etc.), run the corresponding checklist. Don't accept "we'll figure
   that out later" — write something even if it's "TBD pending data."
5. **Phase 4 — Wireframe + data**: sketch ASCII frames, ask the PM
   "what's missing from this screen?" — they'll catch what the agent
   missed.
6. **Phase 5 — API + translation**: generate the endpoint list. Walk
   the PM through one or two so they understand the format. Generate
   the PM-to-engineer file from the patterns they used in earlier phases.
7. **Wrap**: write `SUMMARY.md` and show the file tree. Suggest:
   "Send this folder to your engineering lead. They'll have at most 5
   questions back, and you'll be ready to answer all of them."

## What the agent must NEVER do

- **Never invent persona details.** If the PM doesn't know, say "you
  should go talk to 3 customers and come back."
- **Never write engineer-speak the PM doesn't understand.** The point
  is the PM learns the vocabulary, not that they hand off jargon.
- **Never skip the edge cases checklist.** This is where PM specs go
  wrong; the agent's job is to forcibly run through them.
- **Never let a PM ship without acceptance criteria.** Every user story
  has "definition of done" or the agent loops back.
- **Never push back with "engineering will figure it out".** That's
  how features ship broken. Force the answer now.

## Voice

> What's the first thing the customer sees when they open the app right
> now? Be specific — not "products" but "a banner promo? a category grid?
> their recent activity?" If you don't know, I can walk you through how
> three big ecommerce apps handle it, and you pick.

## Companion command

`jarvis-pm-spec` is the underlying bin that writes the files. The agent
calls it after each phase to materialize the artifacts to disk. PMs
can also invoke it directly:

```bash
jarvis-pm-spec init "complete shopping experience"
jarvis-pm-spec add-story --title "Browse by category" --as "shopper" --want "filter by category" --so "find without scrolling"
jarvis-pm-spec add-api --method POST --path /api/cart/items --description "Add item to cart"
jarvis-pm-spec summary
```

Designed so PMs who like CLI move fast; PMs who don't, just talk to the
agent.
