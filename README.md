# Zoopla UK Property API: Sold House Prices and Live UK Listings from Python or MCP

This repo shows two ways to use the [Zoopla UK Property API](https://apify.com/johnvc/zoopla-property-api?fpr=9n7kx3) on Apify: a Python quick start managed with `uv`, and MCP install guides for five AI clients. Those are [Claude Cowork Desktop](https://claude.ai/referral/uIlpa7nPLg) and [Claude Code](https://claude.ai/referral/uIlpa7nPLg), both of which you can start on a free trial, plus Claude on the web, Cursor, and ChatGPT.

**Actor page:** [apify.com/johnvc/zoopla-property-api](https://apify.com/johnvc/zoopla-property-api?fpr=9n7kx3)
**Input schema:** [apify.com/johnvc/zoopla-property-api/input-schema](https://apify.com/johnvc/zoopla-property-api/input-schema?fpr=9n7kx3)

Give the API a UK town, city, borough, or postcode area, like `Rochdale` or `OL11`, and it returns live property listings as structured JSON: asking price and a parsed numeric value, bedrooms, bathrooms, reception rooms, tenure, agent, features, photos, floor plans, the UPRN, and a dated `listingHistory` that records what the property last sold for and when. No listing URL is needed, which matters because UK listings come down fast once a property is sold or let, and a link saved a few weeks ago often points at a dead page.

## Video walkthrough

[![Apify MCP setup walkthrough](https://img.youtube.com/vi/jREWahDGhJM/maxresdefault.jpg)](https://www.youtube.com/watch?v=jREWahDGhJM)

### Text walkthrough

Looking up **sold house prices** normally means clicking through one property page at a time, and the official Zoopla API has been closed to new developers for years, so there is no easy programmatic route to the same data. This Actor takes the search route instead. The main input is `locations`, a list of up to 20 UK place names or postcode areas, with `propertyType` choosing the listing type and `maxResultsPerSearch` acting as your cost cap. Every example in this repo uses `For sale`, because that is where the sale history lives. The main outputs per property are `price` and `priceValue`, `bedrooms`, `bathrooms`, `receptions`, `tenure`, `uprn`, `agentName`, and the `listingHistory` array, whose `Sold` entries carry a date and a price in pounds; `lastSoldPrice`, `lastSoldDate`, and `lastSoldValue` lift the most recent sale out so you do not have to walk the array. A concrete run: search `OL11`, cap the results at three, and you get back three Rochdale properties with their full price trail, for example one that listed at £125,000 in July 2013, sold for £118,000 that September, and is back on the market at £200,000 in May 2026. Because `uprn` comes through on ordinary housing stock, those rows join straight onto Land Registry and council datasets without any fuzzy address matching. Run the same search weekly and diff it, and you have a local market monitor that catches new listings and price reductions the week they happen.

## Python quick start

### Prerequisites

- Python 3.11 or higher
- An Apify account and API key ([get a free key here](https://apify.com?fpr=9n7kx3))

1. **Clone the repository**

   ```bash
   git clone https://github.com/johnisanerd/Apify-Zoopla-Property-API.git
   cd Apify-Zoopla-Property-API
   ```

2. **Install dependencies with uv**

   ```bash
   # Install uv if you do not have it:
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Install project dependencies:
   uv sync
   ```

3. **Configure your API key**

   ```bash
   cp .env.example .env
   # Edit .env and paste your Apify API token
   # Get your free API key at: https://apify.com?fpr=9n7kx3
   ```

4. **Run the example**

   ```bash
   uv run python zoopla-property-api-example.py
   ```

The default run pulls three for-sale listings from one town, so your first call costs about a penny. The other recipes:

```bash
uv run python zoopla-property-api-example.py --example sold-prices
uv run python zoopla-property-api-example.py --example by-url \
    --url https://www.zoopla.co.uk/for-sale/details/70012345/
```

### Alternative: set the API key directly

```bash
export APIFY_API_TOKEN="your_api_key_here"
uv run python zoopla-property-api-example.py
```

## Why use this API

**Sold prices arrive with the listing, not as a separate lookup.** Every property row carries its own dated history, so the asking price and the previous sale price sit on the same record. No second call, no address matching.

**Search by place, not by URL.** UK listings are pulled down within weeks of a sale or let. A pipeline built on saved listing URLs decays; a pipeline built on `locations` keeps returning whatever is live today.

**UPRN is the join key.** The Unique Property Reference Number is the UK government's identifier for an address. It comes through on ordinary housing stock, which makes these rows joinable to Land Registry, council tax, and planning data.

**You control the bill.** Charging is per listing returned, and `maxResultsPerSearch` caps how many listings a run can produce. A listing that has already been removed is reported as an error row and is not charged.

**It is MCP ready.** The same Actor is a tool for Claude, Cursor, and ChatGPT through the hosted Apify MCP server, so an agent can answer "what did houses on this road last sell for" without you writing a client.

### Features

- Dated `listingHistory` per property: Listed, Reduced, and Sold events, each with the price as published and a parsed numeric value
- `lastSoldPrice`, `lastSoldDate`, and `lastSoldValue` for the most recent sale
- `uprn` on ordinary housing stock, for joining to UK government property datasets
- Price as displayed plus `priceValue` and `currency` for sorting and filtering
- Bedrooms, bathrooms, reception rooms, property type, and tenure where the listing publishes it
- Agent name, the full agent description text, bullet `features`, `images`, and `floorPlans`
- A one-line plain-language `summary` per row, so an agent can read a record without post-processing
- Error rows instead of silence: a search or URL that returns nothing produces `result_type: "error"` with a readable `error_message`

## Recipes in this repo

Each recipe is a `--example` flag on the same script. All of them keep `maxResultsPerSearch` at 3 and use one location, so a run stays around a penny.

### Sold house prices for a postcode area

```bash
uv run python zoopla-property-api-example.py --example sold-prices
```

Searches `OL11`, then prints each property's `uprn` and its full dated price trail rather than the asking-price summary. This is the recipe to copy when you are building a comparable-sales table.

### Live listings in a town

```bash
uv run python zoopla-property-api-example.py
```

Searches `Rochdale` and prints the headline fields per property: type, price, room counts, tenure, UPRN, agent, features, and the last sale.

### One listing you already hold

```bash
uv run python zoopla-property-api-example.py --example by-url \
    --url https://www.zoopla.co.uk/for-sale/details/70012345/
```

URL mode, for the case where you already have a live listing link. Pass your own URL; a listing that has since been removed comes back as an error row and is not charged.

**Schedule tip:** save any of these inputs as a task in the Apify Console and put it on a weekly [schedule](https://apify.com/johnvc/zoopla-property-api?fpr=9n7kx3). Diff consecutive runs on `listingUrl` to catch new listings, and on `priceValue` to catch reductions, without running anything by hand.

## Usage examples

### Basic input

```json
{
  "mode": "search",
  "locations": ["Rochdale"],
  "propertyType": "For sale",
  "maxResultsPerSearch": 3
}
```

### Advanced input

```json
{
  "mode": "search",
  "locations": ["OL11", "OL12", "OL16", "Manchester"],
  "propertyType": "For sale",
  "maxResultsPerSearch": 200
}
```

### URL mode

```json
{
  "mode": "url",
  "listingUrls": [
    "https://www.zoopla.co.uk/for-sale/details/70012345/"
  ]
}
```

## Input parameters

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `mode` | `str` | YES | `search` | `search` finds listings from a location and needs no URL. `url` collects specific listing pages you already hold. |
| `locations` | `list[str]` | in search mode | `["London"]` | UK towns, cities, boroughs, or postcode areas. Up to 20 per run. |
| `propertyType` | `str` | no | `For sale` | `For sale` or `to rent`. Used in search mode. |
| `maxResultsPerSearch` | `int` | no | `50` | Listings returned per location, 1 to 2000. This is your cost control, since charging is per listing. |
| `listingUrls` | `list[str]` | in url mode | - | Specific listing URLs, up to 500 per run. A listing that has been sold or let is reported and not charged. |

## Output format

One row per property. This is a real row from a run of the default recipe, trimmed for length (`description`, `images`, and `floorPlans` are long and are cut here):

```json
{
  "result_type": "listing",
  "searchLabel": "Rochdale (For sale)",
  "listingUrl": "https://www.zoopla.co.uk/for-sale/details/69940539/",
  "propertyTitle": "Egremont Road, Milnrow, Rochdale OL16, 2 bed semi-detached bungalow for sale, £225,000",
  "propertyType": "2 bed semi-detached bungalow for sale",
  "address": "Egremont Road, Milnrow, Rochdale OL16",
  "price": "£225,000.00",
  "priceValue": 225000,
  "currency": "GBP",
  "bedrooms": 2,
  "bathrooms": 1,
  "receptions": 2,
  "tenure": "freehold",
  "availability": "true",
  "features": ["Semi-Detached", "True Bungalow", "Spacious Corner Plot", "No Chain"],
  "uprn": "23081271",
  "listingHistory": [
    { "event": "Listed", "date": "March 2026", "price": "£225,000", "priceValue": 225000 },
    { "event": "Listed", "date": "October 2025", "price": "£215,000", "priceValue": 215000 },
    { "event": "Sold", "date": "December 2014", "price": "£154,950", "priceValue": 154950 },
    { "event": "Listed", "date": "May 2014", "price": "£154,950", "priceValue": 154950 }
  ],
  "lastSoldPrice": "£154,950",
  "lastSoldDate": "December 2014",
  "lastSoldValue": 154950,
  "countryCode": "GB",
  "agentName": "Reside",
  "summary": "2 bed semi-detached bungalow for sale at Egremont Road, Milnrow, Rochdale OL16 listed at £225,000.00. Last sold for £154,950 in December 2014.",
  "fetched_at": "2026-08-07T17:46:23.556477+00:00"
}
```

Full field list: `result_type`, `searchLabel`, `propertyId`, `listingUrl`, `propertyTitle`, `propertyType`, `address`, `price`, `priceValue`, `currency`, `bedrooms`, `bathrooms`, `receptions`, `propertySize`, `tenure`, `availability`, `listingLabel`, `features`, `tags`, `description`, `images`, `floorPlans`, `uprn`, `deposit`, `serviceCharge`, `groundRent`, `listingHistory`, `lastSoldPrice`, `lastSoldDate`, `lastSoldValue`, `agentName`, `agentPhone`, `countryCode`, `summary`, `fetched_at`, plus `error_message` and `error_type` on error rows. Fields that depend on what the agent published, such as `propertySize`, `tenure`, `deposit`, `serviceCharge`, and `groundRent`, are present when the listing carries them.

The raw `listingHistory` array also contains a few layout fragments from the source page with no `date` and a price of zero. Keep the entries that have a `date`, as `_price_events()` in the example script does, and you are left with the Listed, Reduced, and Sold events.

## People also search for

### How do I check sold house prices for an area?

Run a search on the town or postcode area, then read `listingHistory` on each returned property. Any `Sold` entry gives the sale price and the month it completed. `lastSoldPrice` and `lastSoldDate` hold the most recent one. The `sold-prices` recipe in this repo prints exactly that view.

### Is the Zoopla API accessible?

Zoopla's own developer API has been closed to new applicants for a long time, which is why "zoopla api" is still a live search with no good answer. This Actor is the practical route: no application process, no key from Zoopla, one Apify token and a location string.

### Is this a Zoopla scraper or an API?

You call it like an API: JSON in, JSON out, from Python, from `curl`, or from an MCP client. Under the hood it reads public listing pages, which is what people mean when they search for a Zoopla scraper, so the same Actor covers both phrasings.

### Can I get the current Zoopla estimate through this API?

No. There is no valuation or estimate field in the output. What you get is the published asking price, the full dated price history, and the last recorded sale price, which is the raw material most people actually want when they go looking for an estimate.

### Does it return property market stats?

Not as a precomputed block. It returns the per-property inputs you would compute stats from: `priceValue` on every live listing and `lastSoldValue` plus dates on the sold ones. Pull a whole postcode area at a higher `maxResultsPerSearch` and you can work out median asking price, median sold price, and the spread between them yourself.

### How do I get leads from this data?

Every listing carries `agentName` and the `listingUrl`, so you can group a postcode area by agent and see who is winning instructions. Combine that with `listingHistory` to see whose listings are sitting long enough to be reduced.

### How far back does the sale history go?

It depends on the property and on what the source holds. In live testing on ordinary housing stock, price events went back to the early 2010s and earlier. New builds and unusual properties often have no recorded sale at all, in which case `lastSoldPrice` is absent.

### How do I use this from Python?

Clone this repo, set `APIFY_API_TOKEN` in `.env`, and run `uv run python zoopla-property-api-example.py`. See the Python quick start above. The example uses the official `apify-client` package, so it is a handful of lines to adapt.

### Can I run it on a schedule or through MCP?

Yes to both. Save the input as a task in the Apify Console and schedule it, or add the Actor to Claude, Cursor, or ChatGPT with the five install sections below.

---

The Actor's MCP server URL, used in all five install sections below:

```
https://mcp.apify.com/?tools=actors,docs,johnvc/zoopla-property-api
```

The `actors` and `docs` tools let the assistant discover and read Apify docs, while preloading just this one Actor keeps the tool list small. Auth is either OAuth in the browser when offered, or your Apify API token (the same `APIFY_API_TOKEN` secret used by the Python example). Get a token at https://console.apify.com/settings/integrations and a free Apify account at https://apify.com?fpr=9n7kx3 .

## Install in Claude Cowork Desktop

![Install in Claude Cowork Desktop](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_claude_desktop.png)

Cowork is the desktop app's automation mode. To give it the Zoopla UK Property API as a tool, add the Apify MCP server as a connector.

1. Open the Claude desktop app and go to **Settings → Connectors** (or **Settings → Developer → Edit Config** to edit `claude_desktop_config.json` directly).
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
2. Add the Apify MCP server, preloaded with only this Actor:

```json
{
  "mcpServers": {
    "apify": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://mcp.apify.com/?tools=actors,docs,johnvc/zoopla-property-api"
      ]
    }
  }
}
```

3. Restart the app. When Cowork first calls the tool, complete the OAuth prompt in your browser, or add your Apify API token in the connector settings to skip OAuth.
4. In a Cowork chat, confirm the tool is available and ask it to run the Zoopla UK Property API.

Download the desktop app and start a free trial: https://claude.ai/referral/uIlpa7nPLg
More help: https://docs.apify.com/platform/integrations/claude-desktop

## Install in Claude Code

![Install in Claude Code](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_claude_code.png)

Claude Code is the command-line tool. Add the Actor's MCP server with one command:

```bash
claude mcp add --transport http apify \
  "https://mcp.apify.com/?tools=actors,docs,johnvc/zoopla-property-api"
```

To use a token instead of browser OAuth:

```bash
claude mcp add --transport http apify \
  "https://mcp.apify.com/?tools=actors,docs,johnvc/zoopla-property-api" \
  --header "Authorization: Bearer YOUR_APIFY_TOKEN"
```

Then verify with `claude mcp list`, or run `/mcp` inside a session. Ask Claude Code to call the Zoopla UK Property API, for example "what did houses on Edenfield Road in Rochdale last sell for".

Try Claude Code free: https://claude.ai/referral/uIlpa7nPLg
Claude Code MCP docs: https://code.claude.com/docs/en/mcp

## Install in Claude (website)

![Install in Claude (website)](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_claude_ai.png)

On claude.ai you add Apify as a connector, then enable just this Actor's tool.

1. Go to **Settings → Connectors → Browse connectors** and search for **Apify MCP server**. Install it (enable or update if prompted).
2. When connecting, authenticate with your Apify API token, and enable the tool `johnvc/zoopla-property-api`.
3. In any chat, open **+ → Connectors** and turn on **Apify**.
4. Alternatively, choose **Add custom connector** and paste the full MCP URL `https://mcp.apify.com/?tools=actors,docs,johnvc/zoopla-property-api`, using OAuth when prompted.
5. Ask Claude to run the Zoopla UK Property API.

Open Claude on the web: https://claude.ai

## Install in Cursor

![Install in Cursor](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_cursor.png)

Cursor reads MCP servers from a project file at `.cursor/mcp.json`.

1. In your project, create `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "apify": {
      "url": "https://mcp.apify.com/?tools=actors,docs,johnvc/zoopla-property-api"
    }
  }
}
```

2. If you prefer token auth over browser OAuth, add a header:

```json
{
  "mcpServers": {
    "apify": {
      "url": "https://mcp.apify.com/?tools=actors,docs,johnvc/zoopla-property-api",
      "headers": { "Authorization": "Bearer YOUR_APIFY_TOKEN" }
    }
  }
}
```

3. Open **Cursor → Settings → MCP** and confirm the **apify** server is connected (green dot).
4. In Composer or Chat, ask Cursor to call the Zoopla UK Property API.

New to Cursor? Get it here: https://cursor.com/referral?code=XQP4VBLI3NNX

## Install in ChatGPT

![Install in ChatGPT](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_ChatGPT.png)

ChatGPT connects to the Apify MCP server through Developer mode (available on ChatGPT Pro, Plus, Business, Enterprise, and Education plans).

1. Click your profile icon, then go to **Settings > Apps**. If you do not see a **Create app** button, open **Advanced settings** and enable **Developer mode**.
2. Click **Create app** and fill out the form:
   - **Name:** Apify
   - **MCP Server URL:** `https://mcp.apify.com/?tools=actors,docs,johnvc/zoopla-property-api`
   - **Authentication:** OAuth
3. Click **Create** and authorize the connection with Apify.
4. To use the app in a conversation, click **+** in the chat, choose **Developer mode**, and select **Apify**.

More help: https://docs.apify.com/platform/integrations/mcp

---

## 🌐 About Alpha OSINT

This example repo is part of [Alpha OSINT](https://www.alphaosint.com), toolset of financial and operations data sources and APIs.
For support or requests for this actor, please start a ticket [directly on our support page](https://apify.com/johnvc/zoopla-property-api/issues/open?fpr=9n7kx3).

---

[**Made with care**](https://apify.com/johnvc?fpr=9n7kx3)

*Use the Zoopla UK Property API to put sold house prices and live UK listings into your own pipeline.*

Last Updated: 2026.08.08
