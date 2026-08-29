# Dollars beside naira, and opening an account

This is a design brief. It is not legal advice. The rules for digital assets in
Nigeria change often, so a lawyer should confirm the limits and the partner
arrangement before anyone builds this.

## Part one. Holding dollars and naira in one app

### The idea

A Nigerian who wants a stablecoin wants dollars that hold their value. They are
not buying a technology. So the product calls the balance **Dollars**. It never
says crypto, or USDT, or blockchain, or network, or gas. None of those words
names the thing the person is buying.

### Two pockets

There are two places money can sit, and nothing else.

- **Everyday.** This holds naira. It is the balance on the home screen. It runs
  on the bank rails the product already uses.
- **Dollars.** This holds a dollar stablecoin. A licensed partner holds it. The
  app never holds a key.

The person moves money between the two on one screen, called Convert. That
screen shows the rate, the fee, and what they will get. It ends with the same
slide control every other payment in the app ends with.

Dollars can also go to another Amana user. They cannot go to an outside wallet
address. That decision is what keeps the product simple. There is no address to
copy, no network to pick, and no way to send money to a place it cannot come
back from. You can open this up later. You cannot easily close it again.

### The naira stablecoin is a rail, not a pocket

The plan holds cNGN as well, but the person never sees it. A naira stablecoin
does not give someone anything that naira in a bank account does not. What it
does give is settlement at two in the morning, on a Sunday, and on a public
holiday. The person feels that as transfers that always work. They never have
to learn its name.

If cNGN were shown as a third balance, every send screen would need a currency
picker, and every person would have to learn a third thing. They would get
nothing back for it.

### What this adds to the app

Three new screens:

- **Dollars.** The balance, today's rate, where the dollars came from, and a
  line saying who holds them.
- **Convert.** Naira in, dollars out, with the rate and the fee on the screen.
- **Converted.** The receipt.

Two screens change:

- **Home** gains one row for Dollars, between the shortcuts and the money health
  score. Someone who never holds a dollar reads one extra line.
- **Settings** already has a Spending limits screen. The dollar limits go there,
  next to the naira ones, rather than in a new place.

### Where the rules land

- A partner registered with the Securities and Exchange Commission holds the
  dollar balance. The Investments and Securities Act of 2025 brought virtual
  assets under that Commission, so the partner needs to be registered under it.
- Naira stays on the bank or microfinance bank rails the product already uses.
  Nothing about the naira side changes.
- Money laundering rules apply to the dollar balance. The partner runs the
  checks, and the app shows the results as limits rather than as forms.
- The Travel Rule applies when digital assets leave for another provider. This
  product does not let them leave, so that obligation does not arise. This is a
  second reason to start closed.
- Converting is the moment that has to be recorded for tax. The app already has
  a History screen, so every conversion appears there with the rate that was
  used.

### What the assistant does here

It watches the rate and says something when the rate moves against the person.
It says when dollars have been sitting still. It says what the same money would
have been worth if it had stayed in naira. This is the same idea as the money
health score, applied to a second currency.

## Part two. Opening an account

### The goal

A working naira account in about ninety seconds. Nobody should have to finish
everything before they can see the app.

### The rule that cannot be avoided

The Central Bank of Nigeria requires a Bank Verification Number or a National
Identity Number on every account. That question is not optional.

The typing is optional. Eleven digits come back with a name and a date of birth
attached. The person confirms what came back instead of filling in a form. This
is the single biggest saving in the flow.

### The eight screens

1. **Start.** What the app is, and what opening it needs. One button.
2. **Number.** The phone number, on a number pad.
3. **Code.** Six digits from the text message.
4. **Nin.** The National Identity Number or the Bank Verification Number.
5. **Who.** The name and date of birth that came back. The person confirms it.
6. **Face.** A photo, checked against the identity record.
7. **Passcode.** Six digits, used to send money later.
8. **Ready.** The account number, and an honest list of what works now and what
   does not.

### How the screens connect

Everything a person answers stays on the screen. Each answered question becomes
a small row with a green tick, and those rows sit above the current question. By
the fifth screen the person is looking at their account being built.

This does the work a progress bar does, and it does more. A progress bar counts
at you. The stack of answered questions lets you check what you gave before the
account exists.

### What waits until later

The Ready screen offers a row called Finish setting up. It is not required and
it does not block anything. It asks for three things:

- Where the person lives.
- A photo of an identity document.
- Where the money comes from.

Finishing those raises the sending limit and opens the Dollars balance. The
person can stop halfway and whatever they finished is kept.

### What each stage allows

These numbers are examples. A lawyer should set the real ones.

After the eight screens:

- Receive money from any Nigerian bank.
- Send up to fifty thousand naira a day.
- Buy airtime and data, and pay bills.

After Finish setting up:

- Send up to one million naira a day.
- Hold dollars.
- Borrow against the account history.

## Open questions for the founder

1. What are the real limits at each stage? These depend on the banking partner
   and on the tier rules, and they should be set before build.
2. Which partner holds the dollar balance, and are they registered?
3. Should the app ever let dollars leave to an outside wallet? The design leaves
   room for it, but adding it means an address, a network, a warning, and the
   Travel Rule fields.
4. What happens to a person who fails the identity check? The screens do not
   cover that case yet.
