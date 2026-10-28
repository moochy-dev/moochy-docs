# Moochy Credits

> **Not available yet.** Moochy Credits is built but switched off. This page describes how it will work when it opens.

Moochy Credits lets you give AI tokens without your own API key. You pay with a card. Your payment becomes credits. Moochy's own computers spend the credits on AI tokens for the projects or the people you choose.

"Add credits to give AI tokens without your own API key. Moochy keeps nothing. The card fee (Stripe, 2.9% + 30¢) and the provider's fee for buying tokens (OpenRouter, 5.5%) come out of your payment, and the rest becomes credits: $20 → $18.12 of tokens. Every request your credits pay for has a public receipt. Unused credits are refunded after 12 months, or any time you ask."

"Moochy is 100% free. Credits are optional and at cost." "This is not a tax-deductible donation."

## Add credits

1. Sign in on moochy.dev and open **Credits** (`https://moochy.dev/credits`).
2. Choose $10, $25, $50 or $100, or type an amount from $5 to $500.
3. Press **Add credits**. Moochy sends you to Stripe Checkout. You type your card there. Moochy never sees your card.
4. After the payment, the credits show as **held** for 72 hours. Then you can spend them.

From the terminal, `moochy credits add 20` opens the same page in your browser. You type card details only in the browser.

Limits: $5 to $500 for each payment, 3 payments a day, and a balance of $1,000 at most. You need a confirmed email address.

## How much you get

Your credits are your payment minus the card fee and the provider's fee. Moochy uses the real Stripe fee of your payment. For a $20 payment:

| Step | Amount |
|---|---|
| Payment | $20.00 |
| Stripe fee (2.9% + 30¢) | −$0.88 |
| OpenRouter fee (5.5% on top of the tokens it buys) | −$1.00 |
| Credits | $18.12 |

## Spend credits

You spend credits when you donate them or when you give them as a gift:

```sh
moochy donate --credits 20 --repo owner/name       # a one-off total of $20 from your credits
moochy donate --credits 10 --org github/acme
moochy donate --credits 10 --person github/alice
moochy gift create 20 --credits                    # a gift link paid from your credits
```

On the web, choose **Pay with: my credits** on a donate form or on **Gift tokens**. See [Give AI tokens with a link or a QR code](gift-tokens.md) for gifts.

- Each spend is an allocation. It ends 12 months after you make it.
- The owner of a project accepts Moochy Credits one time. After that, new credits for that project start at once.
- You cannot give credits to a project, an organisation or a profile that you own or maintain, or to your own account.

## Who serves your credits

Moochy Credits is a donor account (handle `credits`) that Moochy runs. "Moochy Credits is served by Moochy's own computers with Moochy's own provider key. Like any donor's computer, they see the requests they serve; Moochy's relay still sees only ciphertext."

"Your API keys stay on your machine. Credits are spent by Moochy's own computers with Moochy's own provider key, never stored on the servers that route requests."

The servers that route requests hold the Stripe keys and never the provider key. The computers that serve credits hold the provider key and never the Stripe keys.

## See where your credits go

```sh
moochy credits              # balance, held, purchases with fees, allocations with used and left
moochy credits --json
```

`https://moochy.dev/credits` shows the same, with a receipt link for each request. There you can **Stop** an allocation, **Refund unused** credits, **Add credits** and **Gift credits**.

The public ledger `https://moochy.dev/credits/ledger` shows all money in, Stripe fees, provider fees, credits issued, used, held and refunded, the provider top-ups and the monthly reconciliation. It does not name payers unless they chose **Show my handle**.

## Refunds

| Case | What happens |
|---|---|
| The target declines, or does not answer in 30 days | The credits go back to your balance |
| You stop an allocation | The unused part goes back to your balance |
| An allocation is not used for 12 months | The unused part goes back to your balance |
| You press **Refund unused** | Moochy refunds your oldest payments first. Stripe keeps its fee. |
| A payment is 12 months old | Moochy refunds its unused part and sends you an email |

## Card disputes and fraud

A card dispute or a fraud warning removes the unused credits of that payment and freezes the credits of the account. A fraud warning also refunds the unused part. `moochy credits` then shows: "Your credits are frozen (a card dispute or fraud warning): nothing new can be spent."
