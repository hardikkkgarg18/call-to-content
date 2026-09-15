# Sample discovery-call transcript (synthetic)

> This is a fabricated transcript for demonstration only. Real prospect
> transcripts and their extracted insights are not included in this public repo.

---

**Interviewer:** Walk me through how you handle billing for your AI agents today.

**Founder:** Honestly it's held together with spreadsheets. Every customer runs
a different number of agent calls, and each call burns a different amount of
tokens depending on how long the conversation goes. At the end of the month
someone on my team exports usage from three places and stitches it into an
invoice by hand.

**Interviewer:** How long does that take?

**Founder:** Two, three days. And it's wrong often enough that I've stopped
trusting it. Last month we under-charged a customer by almost forty percent
because a metering script had silently stopped logging one event type. Nobody
noticed until the customer's own finance team asked why their bill was so low.

**Interviewer:** What happens if this stays unsolved as you grow?

**Founder:** It doesn't scale. We're onboarding bigger accounts now, enterprise
ones, and they want usage-based pricing with a proper breakdown per department.
I can't do that on a spreadsheet. Either I hire a billing person, or I stop
taking those deals — both are bad. What I actually need is something that meters
every call and every token automatically and shows me margin per customer.

**Interviewer:** Have you looked at existing tools?

**Founder:** Stripe and Chargebee assume old-school SaaS seats. They don't
understand "this customer ran 12,000 agent calls at a variable per-call cost."
We looked, but we'd be bending the tool the whole time.
