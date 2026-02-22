# Scout Data Pipeline Research: Comprehensive Data Sources for SMB Acquisition & Due Diligence

**Author**: Research Analyst
**Date**: February 19, 2026
**Version**: 1.0
**Purpose**: Identify and evaluate all possible data sources for deal sourcing and due diligence in SMB acquisitions

---

## Executive Summary

### Key Findings

This research identifies **50+ data sources** across deal sourcing and due diligence categories, ranging from free public records to premium enterprise APIs. The SMB acquisition data landscape is fragmented but rich, with opportunities to create unique insights through data fusion.

**Most Valuable Data Sources for Scout:**
1. **Google Maps API** - Universal business directory (200M+ businesses globally)
2. **Franchise Disclosure Documents (FDD)** - Rare transparent financial data for franchises
3. **Secretary of State APIs** - Authoritative business registration data
4. **Public Reviews (Google, Yelp, Trustpilot)** - Quality and sentiment signals
5. **BizBuySell/BizQuest** - Active deal flow marketplaces
6. **Job Postings APIs** - Leading indicator of business growth
7. **Court Records/PACER** - Risk signals (liens, lawsuits, bankruptcies)
8. **Reddit Communities** - Operator sentiment and deal sourcing strategies
9. **Business License Databases** - Comprehensive local business data
10. **Technology Stack APIs (BuiltWith/Wappalyzer)** - Sophistication signals

### Biggest Gaps

- **Private company financials** (except franchises with FDD filings) - No public database exists for most SMBs
- **Owner intentions** - Hard to detect if owners are thinking about selling
- **Customer concentration** - Requires direct access to customer lists
- **Debt obligations** - Not publicly available for private companies
- **Actual cash flow** - Financial reporting not required for most SMBs

### Recommended Priorities

**Phase 1 (Months 1-2) - Quick Wins:**
- Google Maps API integration (business universe)
- Reddit scraping for sentiment (free)
- Secretary of State bulk downloads (free/low-cost)
- FDD data collection (free via state portals)
- Review aggregation (Google/Yelp APIs)

**Phase 2 (Months 3-4) - Paid APIs:**
- Sourcescrub or Grata (deal sourcing platform)
- Job postings API (hiring signals)
- Court records/PACER (risk signals)
- Technology stack data (BuiltWith/Wappalyzer)

**Phase 3 (Months 5-6) - Advanced Features:**
- Data fusion algorithms
- Proprietary scoring models
- Real-time monitoring and alerts
- Competitive intelligence dashboard

---

## 1. Deal Sourcing Data Sources

### 1.1 Online Marketplaces

#### **BizBuySell**

- **Description**: The Internet's largest marketplace for buying and selling businesses, founded in 1996
- **Data Available**:
  - 40,000-45,000 active listings at any given time
  - 65,000+ annual listings across 16 industries
  - Business financials (asking price, revenue, cash flow)
  - Location data
  - Industry classifications
  - Seller descriptions
- **Access Method**: Web scraping (no public API), paid listings required for detailed data
- **Cost**: Free to browse, listing fees $200-$2,000+ for sellers
- **Coverage**: Comprehensive US coverage, all industries, focus on established businesses
- **Use Cases**:
  - Primary deal flow monitoring
  - Market pricing benchmarks
  - Seller sentiment analysis
  - Competitive intelligence
- **Feasibility**: Medium (scraping required, no official API)
- **Priority**: HIGH
- **Sources**: [BizBuySell Learning Center](https://www.bizbuysell.com/learning-center/article/where-to-find-a-business-for-sale/), [BizBuySell Insight Report](https://www.bizbuysell.com/insight-report/)

#### **Flippa**

- **Description**: Long-established open marketplace for digital businesses, founded in 2009
- **Data Available**:
  - Mostly digital businesses (websites, e-commerce, SaaS)
  - Most listings under $50,000
  - Traffic data, revenue metrics
  - Connected financial data (Stripe, Shopify, Google Analytics)
  - Historical performance data
- **Access Method**: Web scraping, some API access for partners
- **Cost**: $29 listing fee + 3-15% commission on sales
- **Coverage**: Global, focused on online businesses
- **Use Cases**:
  - Digital business deal flow
  - Micro-acquisition opportunities
  - Market trend analysis
- **Feasibility**: Medium (scraping, limited API)
- **Priority**: MEDIUM
- **Sources**: [Flippa vs Acquire.com Comparison](https://todaytesting.com/flippa-vs-acquire-comparison-buy-sell-online-businesses-2025/)

#### **Acquire.com (formerly MicroAcquire)**

- **Description**: Curated marketplace for startup and SaaS acquisitions, launched in 2020
- **Data Available**:
  - Vetted SaaS and tech startups
  - Connected financial metrics (Stripe, analytics)
  - Revenue, growth rates, tech stack
  - Anonymous listings until buyer qualification
- **Access Method**: Paid subscription required ($390-$780/year for buyers), web scraping
- **Cost**: Premium $390/year, Platinum $780/year for buyers
- **Coverage**: US/global, focus on tech/SaaS businesses
- **Use Cases**:
  - High-quality tech business deal flow
  - SaaS acquisition opportunities
- **Feasibility**: Low (requires paid subscription, strict terms)
- **Priority**: LOW (not focused on traditional SMBs)
- **Sources**: [Acquire.com Buyers](https://acquire.com/buyers/), [Flippa vs Acquire.com](https://todaytesting.com/flippa-vs-acquire-best-marketplace-to-buy-sell-online-business-2025/)

#### **SMB.co**

- **Description**: Small business marketplace with data-backed valuations, launched 2023+
- **Data Available**:
  - Business listings with valuation data
  - Expert support and tools
  - Market data for pricing
- **Access Method**: Platform access, unknown API availability
- **Cost**: Unknown, likely paid tiers
- **Coverage**: US SMB focus
- **Use Cases**:
  - SMB-focused deal flow
  - Valuation benchmarking
- **Feasibility**: Unknown (new platform)
- **Priority**: MEDIUM
- **Sources**: [SMB.co](https://smb.co/)

#### **BusinessesForSale.com**

- **Description**: US business-for-sale marketplace
- **Data Available**: 57,943+ businesses from brokers and independent sellers
- **Access Method**: Web scraping
- **Cost**: Free to browse
- **Coverage**: Comprehensive US coverage
- **Use Cases**: Additional deal flow source
- **Feasibility**: Medium (scraping)
- **Priority**: MEDIUM
- **Sources**: [BusinessesForSale.com](https://us.businessesforsale.com)

#### **BizQuest.com**

- **Description**: Business marketplace founded in 1994
- **Data Available**: 1,500+ active listings
- **Access Method**: Web scraping
- **Cost**: Free for buyers
- **Coverage**: US businesses, smaller catalog
- **Use Cases**: Supplemental deal flow
- **Feasibility**: Medium (scraping)
- **Priority**: LOW
- **Sources**: [Best Places to Find Business to Buy](https://www.midstreet.com/blog/top-online-sites-buy-business)

#### **DealStream**

- **Description**: Marketplace for businesses and investment opportunities
- **Data Available**: 20,000+ listings including businesses for sale
- **Access Method**: Web scraping
- **Cost**: Unknown
- **Coverage**: US businesses and franchises
- **Use Cases**: Deal flow aggregation
- **Feasibility**: Medium
- **Priority**: LOW
- **Sources**: [Best Places to Find Business](https://www.midstreet.com/blog/top-online-sites-buy-business)

#### **BusinessBroker.net**

- **Description**: Business and franchise marketplace
- **Data Available**: 28,000+ businesses and franchises
- **Access Method**: Web scraping
- **Cost**: Free to browse
- **Coverage**: US, searchable by industry and location
- **Use Cases**: Broker network, deal flow
- **Feasibility**: Medium
- **Priority**: LOW
- **Sources**: [Where to Find Business for Sale](https://www.bizbuysell.com/learning-center/article/where-to-find-a-business-for-sale/)

#### **Kumo**

- **Description**: AI-driven deal sourcing platform launched recently
- **Data Available**:
  - 815,291+ listings from thousands of brokers
  - Aggregated from multiple marketplaces worldwide
  - $538B+ in annual revenue represented
- **Access Method**: Platform subscription (likely required)
- **Cost**: Unknown, likely paid
- **Coverage**: Global, comprehensive aggregation
- **Use Cases**:
  - Mega-aggregator for deal flow
  - Unified search across platforms
- **Feasibility**: Low (requires subscription, expensive likely)
- **Priority**: MEDIUM (if cost-effective)
- **Sources**: [KUMO Top 10 Deal Sources](https://www.withkumo.com/blog/top-10-deal-sources-to-find-smb-listings-online)

### 1.2 Business Directories & Local Data

#### **Google Maps API / Google Places API**

- **Description**: Universal business directory with 200M+ businesses globally
- **Data Available**:
  - Business name, address, phone (NAP)
  - Categories and industry classifications
  - Operating hours
  - Reviews and ratings (star ratings, review counts)
  - Photos
  - Website URLs
  - Geographic coordinates
  - Attributes (delivery, dine-in, etc.)
- **Access Method**: Official Google Places API, or scraping tools (Outscraper, Apify, ScrapingDog)
- **Cost**:
  - Google Places API: Free tier (limited), then paid per query
  - Scraping services: $50-500/month depending on volume
- **Coverage**: 200M+ businesses globally, 4,000+ industry sectors
- **Use Cases**:
  - Universal business discovery
  - Building target lists by location and industry
  - Review sentiment analysis
  - Market saturation analysis
  - Competitive density mapping
- **Feasibility**: HIGH (official API available, many scraping alternatives)
- **Priority**: HIGH
- **Sources**: [Google Maps Scraper - Outscraper](https://outscraper.com/google-maps-scraper/), [Apify Google Maps Scraper](https://apify.com/compass/crawler-google-places), [Google Maps Scraping Guide 2025](https://scrap.io/google-maps-scraping-complete-guide-business-data-leads-2025)

#### **Yelp Fusion API**

- **Description**: Business directory focused on consumer services with user reviews
- **Data Available**:
  - Business name, address, phone
  - Categories
  - Star ratings, review counts
  - Up to 3-7 review excerpts (160 chars each, depending on plan)
  - Price levels
  - Photos
  - Operating hours
- **Access Method**: Official Yelp Fusion API (Places API)
- **Cost**:
  - 5,000 free API calls during 30-day trial
  - Paid plans per API call (pricing varies)
  - Plus plan: 3 reviews/business
  - Enterprise: 7 reviews/business
- **Coverage**: Millions of businesses across 32 countries
- **Use Cases**:
  - Consumer-facing business discovery
  - Review sentiment for quality signals
  - Restaurant, retail, service business targeting
- **Feasibility**: HIGH (official API)
- **Priority**: HIGH
- **Sources**: [Yelp Places API](https://business.yelp.com/data/products/places-api/), [Yelp Developers](https://www.yelp.com/developers)

#### **Better Business Bureau (BBB) Data**

- **Description**: Business accreditation and complaint tracking organization
- **Data Available**:
  - BBB ratings and accreditation status
  - Customer complaints and resolutions
  - Business profiles
  - Years in business
  - Complaint statistics by industry
- **Access Method**: Official BBB API (developer.bbb.org), or scraping services (ScrapingBee)
- **Cost**: Unknown for official API, scraping services ~$50-200/month
- **Coverage**: US businesses that engage with BBB (not comprehensive)
- **Use Cases**:
  - Risk screening
  - Reputation assessment
  - Complaint history analysis
- **Feasibility**: MEDIUM (API exists but access requirements unclear)
- **Priority**: MEDIUM
- **Sources**: [BBB API](https://developer.bbb.org/), [BBB Scraper API - ScrapingBee](https://www.scrapingbee.com/scrapers/better-business-bureau-api/)

### 1.3 Business Registry & Public Records

#### **Secretary of State Business Registries**

- **Description**: Official state business registration databases (all 50 US states)
- **Data Available**:
  - Legal business name
  - Registration number
  - Entity type (LLC, Corp, etc.)
  - Registration date
  - Business address
  - Registered agent
  - Active/inactive status
  - Officers and directors (varies by state)
  - Filing history
- **Access Method**:
  - State-by-state APIs (Iowa, California have public APIs)
  - Third-party aggregators (Middesk, Cobalt Intelligence)
  - Bulk downloads from some states
  - Manual lookup portals
- **Cost**:
  - Many states: FREE (bulk downloads or API)
  - Third-party APIs: $500-5,000+/month
  - Middesk: Unknown pricing (enterprise)
- **Coverage**: All US businesses (required by law to register)
- **Use Cases**:
  - Business verification and validation
  - Owner/officer identification
  - Age of business (establishment date)
  - Entity structure analysis
  - Compliance checking
- **Feasibility**: HIGH (many free state sources, aggregators available)
- **Priority**: HIGH
- **Sources**: [Secretary of State API - Middesk](https://www.middesk.com/blog/secretary-of-state-api), [Secretary of State API Solutions 2026](https://cobaltintelligence.com/blog/post/top-secretary-of-state-api-solutions-for-verifying-businesses), [Iowa SOS API](https://api.sos.iowa.gov/), [California Business Registry 2025](https://www.kyckr.com/blog/california-business-register-2025-update)

#### **Business License & Permit Databases**

- **Description**: State and local business licenses and permits (public records)
- **Data Available**:
  - License type and status
  - Issue and expiration dates
  - Business name and contact info
  - License conditions and restrictions
  - Inspection records (in some jurisdictions)
- **Access Method**:
  - Data.gov datasets
  - Local government APIs (varies by city/county)
  - License Lookup API services
  - Manual searches on jurisdiction websites
- **Cost**: Mostly FREE (public records), API services ~$100-500/month
- **Coverage**: Varies by jurisdiction, major cities have good coverage
- **Use Cases**:
  - Business verification
  - Compliance status
  - Operational activity signals
  - Industry identification
- **Feasibility**: MEDIUM (fragmented by jurisdiction)
- **Priority**: MEDIUM
- **Sources**: [Business License Search API](https://apis.licenselookup.org/business-license-search-api/), [Data.gov Licenses](https://catalog.data.gov/dataset?tags=licenses), [Are Business Licenses Public Record?](https://www.doola.com/blog/are-business-licenses-public-record/)

#### **OpenCorporates**

- **Description**: Largest open database of company information globally
- **Data Available**:
  - 204M companies from 170 jurisdictions
  - Basic company info (name, registration #, status)
  - Company filings and documents
  - Officer/director information
  - Corporate relationships and networks
  - Industry classifications
- **Access Method**: Official OpenCorporates API
- **Cost**:
  - FREE for open data projects (share-alike license)
  - Paid API accounts remove restrictions
  - Pricing not publicly disclosed
- **Coverage**: Global, 204M companies
- **Use Cases**:
  - Global business discovery
  - Corporate structure mapping
  - Director network analysis
  - International due diligence
- **Feasibility**: HIGH (public API, free tier available)
- **Priority**: MEDIUM
- **Sources**: [OpenCorporates API](https://api.opencorporates.com/), [Getting Started with OpenCorporates API](https://blog.opencorporates.com/2025/02/13/getting-started-with-the-opencorporates-api/), [Bellingcat Guide to OpenCorporates](https://www.bellingcat.com/resources/2023/08/24/following-the-money-a-beginners-guide-to-using-the-opencorporates-api/)

### 1.4 AI-Powered Deal Sourcing Platforms

#### **Grata**

- **Description**: AI-powered private company search engine
- **Data Available**:
  - 16M+ private businesses
  - Revenue ranges, business models, funding history
  - Industries and sectors
  - AI-powered "lookalike" search
  - Executive contact data
  - Company websites as primary data source
- **Access Method**: Platform subscription
- **Cost**: Unknown, likely $10,000-50,000+/year (enterprise pricing)
- **Coverage**: 16M+ US private companies
- **Use Cases**:
  - Proprietary deal sourcing
  - Target list building
  - Market intelligence
  - Lookalike company discovery
- **Feasibility**: LOW (expensive, requires subscription)
- **Priority**: MEDIUM (if budget allows)
- **Sources**: [Grata + Sourcescrub](https://grata.com/grata-and-sourcescrub), [Grata vs Sourcescrub Comparison](https://otio.ai/blog/grata-vs-sourcescrub), [How to Win Deals in 2026 with AI](https://grata.com/resources/private-equity-deal-flow)

#### **Sourcescrub**

- **Description**: Market-leading deal sourcing platform with expert-in-the-loop AI
- **Data Available**:
  - 15M+ companies
  - 150,000+ information sources aggregated
  - Profile+ standard (7+ data categories, 9 growth signals)
  - Founder-owned business focus
  - Events, directories, industry sources
  - Executive contact information
- **Access Method**: Platform subscription
- **Cost**: Unknown, likely $10,000-50,000+/year (enterprise)
- **Coverage**: 15M+ US companies, especially founder-owned
- **Use Cases**:
  - Proprietary deal sourcing
  - Founder-owned business discovery
  - Outbound campaign targeting
  - Sector-specific outreach
- **Feasibility**: LOW (expensive, enterprise sales)
- **Priority**: MEDIUM (88% prefer over Grata per 2024 study)
- **Sources**: [Sourcescrub vs Grata](https://webflow.sourcescrub.com/uk/competitors/sourcescrub-vs-grata), [Why Choose Sourcescrub](https://www.sourcescrub.com/why-sourcescrub), [What is Deal Sourcing Platform](https://www.sourcescrub.com/post/what-is-a-deal-sourcing-platform)

#### **Inven / Udu**

- **Description**: AI-native "lookalike" search platforms for private companies
- **Data Available**:
  - Train AI with examples of target companies
  - Find similar companies based on patterns
  - Superior for niche theses vs. standard industry codes
- **Access Method**: Platform subscription
- **Cost**: Unknown
- **Coverage**: Unknown
- **Use Cases**:
  - Niche market discovery
  - Pattern-based targeting
  - Similar company identification
- **Feasibility**: LOW (new platforms, unknown access)
- **Priority**: LOW
- **Sources**: [Deal Sourcing for Search Funds 2025](https://searcherinsights.com/the-real-guide-to-deal-sourcing-for-your-search-fund-2025/)

### 1.5 Job Posting Data (Hiring Signals)

#### **Indeed API**

- **Description**: Job posting platform with API for job data
- **Data Available**:
  - Job postings by company
  - Job titles and descriptions
  - Posting dates
  - Location data
  - Employer information
- **Access Method**: Indeed Partner API (requires partnership approval)
- **Cost**: Unknown, likely partner/revenue share agreements
- **Coverage**: Extensive US job postings
- **Use Cases**:
  - Hiring = growth signal
  - Business expansion detection
  - Staffing level estimation
  - Department growth tracking
- **Feasibility**: LOW (requires partnership)
- **Priority**: MEDIUM
- **Sources**: [Indeed Documentation](https://docs.indeed.com/)

#### **LinkedIn Job Posting API**

- **Description**: Professional network job postings API
- **Data Available**:
  - Company job postings
  - Role levels and functions
  - Department growth signals
  - Historical hiring trends
- **Access Method**: LinkedIn API (requires approval, ATS partnerships)
- **Cost**: Unknown, requires business relationship with LinkedIn
- **Coverage**: Professional jobs, tech and corporate focus
- **Use Cases**:
  - Executive hiring = strategic shifts
  - Department expansion tracking
  - Buying signals for B2B
  - Company growth phase detection
- **Feasibility**: LOW (restricted API access)
- **Priority**: MEDIUM
- **Sources**: [LinkedIn Job Posting API](https://learn.microsoft.com/en-us/linkedin/talent/job-postings/api/overview?view=li-lts-2025-10), [Scrape LinkedIn for Hiring Signals](https://n8n.io/workflows/3580-scrape-linkedin-job-listings-for-hiring-signals-and-prospecting-with-bright-data/)

#### **TheirStack Job Postings API**

- **Description**: Third-party job postings aggregator
- **Data Available**:
  - Job postings from multiple sources
  - Company hiring trends
  - Job market intelligence
- **Access Method**: API subscription
- **Cost**: Unknown, likely $500-2,000/month
- **Coverage**: Aggregated from multiple job boards
- **Use Cases**:
  - Hiring signals without direct job board APIs
  - Growth tracking
  - Market intelligence
- **Feasibility**: MEDIUM
- **Priority**: MEDIUM
- **Sources**: [TheirStack Job Postings API](https://theirstack.com/en/job-posting-api)

### 1.6 Technology & Web Intelligence

#### **BuiltWith**

- **Description**: Website technology profiler
- **Data Available**:
  - Technology stack (CMS, ecommerce platform, analytics, etc.)
  - Millions of websites tracked
  - Historical technology usage
  - Competitor technology analysis
- **Access Method**: BuiltWith API
- **Cost**: $295/month Basic, $995/month Team (includes API credits)
- **Coverage**: Millions of websites globally
- **Use Cases**:
  - Technology sophistication scoring
  - Ecommerce platform identification
  - Tech stack modernization opportunities
  - Competitive intelligence
- **Feasibility**: MEDIUM (paid API, moderate cost)
- **Priority**: MEDIUM
- **Sources**: [BuiltWith vs Wappalyzer](https://www.wappalyzer.com/articles/builtwith-alternative/)

#### **Wappalyzer**

- **Description**: Website technology profiler with 3M daily users
- **Data Available**:
  - Technology stack detection
  - Company details, verified emails, phone numbers
  - Social media profiles
  - Keywords and metadata
  - Near-instant or real-time analysis
- **Access Method**: Wappalyzer API
- **Cost**: Lower than BuiltWith, mid-tier Business plan includes API
- **Coverage**: Millions of websites, 3M daily browser extension users contribute data
- **Use Cases**:
  - Similar to BuiltWith but lower cost
  - Technology stack analysis
  - Company enrichment
- **Feasibility**: MEDIUM (paid API, lower cost than BuiltWith)
- **Priority**: MEDIUM
- **Sources**: [Wappalyzer API](https://www.wappalyzer.com/api/), [How to Check Website Technology 2026](https://popupsmart.com/blog/check-website-technology)

#### **SimilarWeb API**

- **Description**: Website traffic and analytics intelligence
- **Data Available**:
  - Total visits (desktop + mobile)
  - Engagement metrics (bounce rate, pages/visit, duration)
  - Traffic sources
  - Geographic distribution
  - Competitor benchmarking
  - 37 months historical data
- **Access Method**: SimilarWeb API (subscription add-on)
- **Cost**: Enterprise pricing, "Data Credits" model (pay for data received)
- **Coverage**: Millions of websites globally
- **Use Cases**:
  - Website traffic as growth/decline signal
  - Market share analysis
  - Competitive intelligence
  - Business health assessment
- **Feasibility**: LOW (expensive enterprise pricing)
- **Priority**: LOW (nice-to-have, not essential)
- **Sources**: [SimilarWeb API](https://developers.similarweb.com/docs/similarweb-web-traffic-api), [API Solutions](https://www.similarweb.com/corp/daas/api/)

#### **WHOIS Domain Data**

- **Description**: Domain registration and ownership information
- **Data Available**:
  - Domain owner name (if not privacy-protected)
  - Registration date
  - Expiration date
  - Registrar
  - Contact information (email, phone, address)
  - Nameservers
- **Access Method**: WHOIS lookup APIs (WhoisXML API, ICANN Lookup), free lookup tools
- **Cost**: FREE (manual lookups), API ~$50-500/month for bulk
- **Coverage**: All registered domains globally
- **Use Cases**:
  - Business age verification (domain age)
  - Contact information discovery
  - Owner identification
  - Domain portfolio analysis
- **Feasibility**: HIGH (many free and paid options)
- **Priority**: LOW (limited value, often privacy-protected)
- **Sources**: [Whois.com](https://www.whois.com/whois/), [ICANN Lookup](https://lookup.icann.org/), [WhoisXML API](https://whois.whoisxmlapi.com/lookup)

### 1.7 Business Intelligence & Data Enrichment

#### **ZoomInfo**

- **Description**: Leading B2B data intelligence platform
- **Data Available**:
  - 200M+ B2B contacts
  - Company firmographics
  - Technologies used
  - Corporate hierarchies
  - Funding details
  - News alerts and scoops
  - Intent signals
- **Access Method**: ZoomInfo Enterprise API
- **Cost**: Enterprise pricing (expensive, $10,000-50,000+/year)
- **Coverage**: 200M+ contacts, comprehensive B2B coverage
- **Use Cases**:
  - Company enrichment
  - Contact discovery
  - Firmographic data
  - Technographic data
- **Feasibility**: LOW (expensive enterprise sales)
- **Priority**: LOW (too expensive for early stage)
- **Sources**: [ZoomInfo API](https://api-docs.zoominfo.com/), [ZoomInfo Enterprise API](https://www.zoominfo.com/solutions/data-as-a-service/enterprise-api)

#### **Clearbit**

- **Description**: B2B data enrichment platform
- **Data Available**:
  - 50M+ companies
  - 100+ firmographic and technographic attributes
  - Real-time enrichment
  - IP intelligence (Reveal API)
  - Email-based enrichment
- **Access Method**: Clearbit API (Enrichment API, Reveal API)
- **Cost**: Unknown, likely $5,000-25,000+/year
- **Coverage**: 50M companies globally
- **Use Cases**:
  - Company data enrichment
  - Firmographic attributes
  - Website visitor identification
  - Technographic data
- **Feasibility**: MEDIUM (API available, moderate-high cost)
- **Priority**: LOW
- **Sources**: [Clearbit Enrichment](https://clearbit.com/platform/enrichment), [Clearbit API](https://clearbit.com/resources/guides/Twilio-Segment-enrichment)

#### **Crunchbase API**

- **Description**: Startup and private company database
- **Data Available**:
  - 600+ API endpoints
  - Funding rounds and investment data
  - Company firmographics
  - Revenue estimates, valuations
  - Founder information
  - Funding predictions (AI-powered)
- **Access Method**: Crunchbase API
- **Cost**: Paid tiers (significant cost for comprehensive access)
- **Coverage**: Millions of companies, focus on funded startups
- **Use Cases**:
  - Startup acquisition targets
  - Funding history analysis
  - Investor identification
  - Growth trajectory assessment
- **Feasibility**: MEDIUM (API available, paid)
- **Priority**: LOW (focused on VC-backed companies, not typical SMBs)
- **Sources**: [Crunchbase Data](https://data.crunchbase.com/docs/welcome-to-crunchbase-data), [Crunchbase API Guide](https://nubela.co/blog/crunchbase-api-guide/)

#### **D&B (Dun & Bradstreet)**

- **Description**: Business credit and risk intelligence
- **Data Available**:
  - Business credit reports
  - D&B PAYDEX score
  - Payment history
  - Credit ratings
  - Financial stability metrics
  - Failure risk scores
- **Access Method**: D&B Direct+ API, Credit Information B2B API
- **Cost**: Enterprise pricing (expensive)
- **Coverage**: Comprehensive US business credit data
- **Use Cases**:
  - Credit risk assessment
  - Financial stability analysis
  - Payment behavior tracking
  - Due diligence screening
- **Feasibility**: LOW (expensive, enterprise sales)
- **Priority**: LOW (expensive for early stage)
- **Sources**: [D&B Credit Information API](https://www.dnb.com/en-gb/developers/credit-information-b2b-api.html), [D&B Business Credit Reports](https://www.dnb.com/en-us/smb/resources/credit-scores/how-to-read-dun-and-bradstreet-business-credit-reports.html)

#### **Apollo.io**

- **Description**: Sales intelligence and B2B contact database
- **Data Available**:
  - 220M+ people database
  - Emails, phone numbers, job titles, social profiles
  - 7-step email verification (91% accuracy)
  - 35M global companies
  - Built-in CRM and email campaigns
- **Access Method**: Apollo.io API
- **Cost**: Paid plans starting ~$49-99/month
- **Coverage**: 220M contacts, 35M companies globally
- **Use Cases**:
  - Contact discovery for outreach
  - Email finding and verification
  - Owner/executive identification
- **Feasibility**: HIGH (accessible API, reasonable pricing)
- **Priority**: MEDIUM
- **Sources**: [Apollo.io Email Finder](https://www.apollo.io/tools/email-finder), [Apollo vs Hunter.io](https://www.bookyourdata.com/blog/hunter-io-vs-apollo-io)

#### **Hunter.io**

- **Description**: Email finder and verification tool
- **Data Available**:
  - Professional email addresses
  - Confidence scores for emails
  - Source attribution (where email was found)
  - Domain email patterns
- **Access Method**: Hunter.io API
- **Cost**: $49/month and up
- **Coverage**: Extensive email database
- **Use Cases**:
  - Owner/executive email discovery
  - Contact enrichment
  - Outreach campaigns
- **Feasibility**: HIGH (accessible API, reasonable pricing)
- **Priority**: LOW
- **Sources**: [Hunter.io API](https://hunter.io/api-documentation/v2), [Hunter.io Email Finder API](https://hunter.io/api/email-finder)

### 1.8 Local Business Networks & Associations

#### **International Franchise Association (IFA)**

- **Description**: World's largest franchising organization
- **Data Available**:
  - 733,000 franchise establishments
  - Franchising Economic Outlook (annual)
  - State-by-state franchise data
  - Industry growth projections
  - Economic impact data (jobs, GDP)
- **Access Method**: Reports and publications (no API), partnership with U.S. Census Bureau and FRANdata
- **Cost**: Likely paid reports/membership
- **Coverage**: US franchise systems across 300+ industries
- **Use Cases**:
  - Franchise industry intelligence
  - Market growth trends
  - Regional expansion patterns
  - Economic forecasting
- **Feasibility**: MEDIUM (reports available, no API)
- **Priority**: MEDIUM (valuable for franchise focus)
- **Sources**: [International Franchise Association](https://www.franchise.org/), [IFA Franchising Economic Outlook](https://www.franchise.org/franchising-economic-outlook/)

#### **Local Business Associations & Chambers**

- **Description**: City and regional business associations
- **Data Available**:
  - Member directories
  - Local business news
  - Economic development reports
  - Business events and activity
- **Access Method**: Manual directory scraping, newsletter subscriptions
- **Cost**: FREE to low-cost memberships
- **Coverage**: Varies by region
- **Use Cases**:
  - Local business discovery
  - Community engagement
  - Networking opportunities
- **Feasibility**: LOW (highly fragmented, manual effort)
- **Priority**: LOW
- **Sources**: N/A (local sources)

### 1.9 News & Media Intelligence

#### **Business Journals (Regional)**

- **Description**: Regional business news publications (e.g., Worcester Business Journal, Hartford Business Journal, Crain's)
- **Data Available**:
  - M&A announcements
  - Business news and profiles
  - Local economic trends
  - Executive moves
  - Expansion announcements
- **Access Method**: RSS feeds, web scraping, newsletter subscriptions
- **Cost**: FREE to ~$100/year subscriptions
- **Coverage**: Regional, major metro areas
- **Use Cases**:
  - M&A trend monitoring
  - Local market intelligence
  - Deal announcement tracking
  - Owner profile discovery
- **Feasibility**: MEDIUM (RSS/scraping possible)
- **Priority**: MEDIUM
- **Sources**: [Worcester Business Journal](https://wbjournal.com/), [Hartford Business Journal](https://hartfordbusiness.com/), [Crain's Chicago Business](https://www.chicagobusiness.com/)

#### **Business Wire / PR Newswire**

- **Description**: Press release distribution services
- **Data Available**:
  - M&A announcements
  - Partnership news
  - Business milestones
  - Executive appointments
- **Access Method**: RSS feeds, web scraping, paid API access
- **Cost**: FREE (basic access), paid for full archives
- **Coverage**: National and global business announcements
- **Use Cases**:
  - M&A monitoring
  - Business activity tracking
  - Deal announcement alerts
- **Feasibility**: HIGH (public RSS feeds)
- **Priority**: LOW
- **Sources**: [Business Wire M&A News](https://www.businesswire.com/newsroom/subject/merger-acquisition)

### 1.10 Social Media & Community Intelligence

#### **LinkedIn Company Pages**

- **Description**: Professional network company profiles
- **Data Available**:
  - Company size (employee count)
  - Headcount growth over time
  - Department distribution
  - Employee function growth
  - New hire counts
  - Company descriptions and updates
- **Access Method**: LinkedIn Premium Insights, scraping (PhantomBuster, etc.), limited official API
- **Cost**:
  - Premium: $30-120/month
  - Scraping services: $50-500/month
  - Official API: Restricted access
- **Coverage**: Millions of companies globally
- **Use Cases**:
  - Headcount growth = expansion signal
  - Department hiring = strategic priorities
  - Employee engagement tracking
  - Company size verification
- **Feasibility**: MEDIUM (scraping possible, official API restricted)
- **Priority**: MEDIUM
- **Sources**: [LinkedIn Company Insights API](https://saleleads.ai/blog/linkedin-company-insights-api), [LinkedIn Premium Insights](https://www.linkedin.com/help/linkedin/answer/a565340/premium-insights-on-linkedin-pages-overview?lang=en)

#### **Reddit Communities**

- **Description**: Discussion forums with acquisition and SMB operator communities
- **Data Available**:
  - Deal sourcing strategies
  - Acquisition success/failure stories
  - Due diligence tips
  - Operator sentiment
  - Market insights
  - Pain points and opportunities
- **Key Subreddits**:
  - r/sweatystartup - Service business operators and acquirers
  - r/Entrepreneur - Business acquisition discussions
  - r/smallbusiness - Owner perspectives
  - r/Search - Search fund community (if exists)
  - r/financialindependence - SMB acquisition path discussions
- **Access Method**: Reddit API, web scraping, manual monitoring
- **Cost**: FREE (Reddit API free with rate limits)
- **Coverage**: Active communities with thousands of members
- **Use Cases**:
  - Qualitative market research
  - Deal sourcing strategy insights
  - Due diligence best practices
  - Sentiment analysis
  - Operator pain points discovery
- **Feasibility**: HIGH (free API, easy scraping)
- **Priority**: HIGH (unique qualitative insights)
- **Sources**: [r/sweatystartup](https://www.sweatystartup.com/), [EtA FAQ](https://investors.club/entrepreneurship-through-acquisition-faq/)

#### **Facebook Business Pages**

- **Description**: Social media business profiles
- **Data Available**:
  - Reviews and ratings
  - Check-ins (for local businesses)
  - Posts and engagement
  - Response rates
- **Access Method**: Facebook Graph API (restricted), scraping
- **Cost**: FREE (API with restrictions)
- **Coverage**: Millions of business pages
- **Use Cases**:
  - Additional review data
  - Engagement signals
  - Local business activity
- **Feasibility**: LOW (API restrictions, scraping challenges)
- **Priority**: LOW
- **Sources**: N/A

---

## 2. Due Diligence Data Sources

### 2.1 Financial Data Sources

#### **Franchise Disclosure Documents (FDD)**

- **Description**: Required financial disclosures for franchise systems (23 items)
- **Data Available**:
  - Item 19: Financial Performance Representations (revenue, expenses, profits)
  - Franchise fees and costs
  - Franchisee litigation history
  - Franchisor background
  - Territory information
  - Training and support details
  - Actual franchisee performance data (average revenue, top/bottom performers)
- **Access Method**:
  - **FREE State Portals**: California, Indiana, Minnesota, Wisconsin SOS websites
  - **Paid Databases**: FRANdata (40,000+ FDDs, 25 years), FranChimp (18,000+ FDDs)
  - **FDD Exchange**: Community-sourced database
  - Direct from franchisors (required disclosure)
- **Cost**:
  - State portals: FREE
  - FRANdata: Unknown (enterprise pricing)
  - FranChimp: Subscription required
  - FDD Exchange: Unknown
- **Coverage**: 3,500+ franchise systems with FDDs
- **Use Cases**:
  - Franchise unit financial benchmarking
  - Revenue and profitability analysis
  - Risk assessment (litigation)
  - Franchise system evaluation
  - Location performance comparison
- **Feasibility**: HIGH (free state sources available)
- **Priority**: HIGH (rare public financial data for SMBs)
- **Sources**: [FDD Exchange](https://fddexchange.com/), [FRANdata FDDs](https://frandata.com/products-solutions/fdds-franchise-disclosure-documents/), [FranChimp FDDs](https://www.franchimp.com/?page=fdd), [Where to Find Free FDDs](https://www.oakscale.com/post/franchise-basics-where-to-find-free-franchise-disclosure-documents-fdds), [FTC FDD Deep Dive](https://www.ftc.gov/business-guidance/blog/2023/05/franchise-fundamentals-taking-deep-dive-franchise-disclosure-document)

#### **Business Valuation Benchmarks**

- **Description**: Industry financial benchmarks and valuation multiples
- **Data Available**:
  - Revenue multiples by industry
  - EBITDA multiples
  - Financial ratios (profit margins, etc.)
  - Industry statistics
  - Valuation ranges
- **Key Sources**:
  - **RMA eStatement Studies**: Risk Management Association, manufacturing/wholesale/retail/service/contracting composites
  - **Key Business Ratios (KBR)**: D&B database, 14 key ratios for 800 lines of business
  - **Business Valuation Resources (BVR)**: Pratt's Stats database, thousands of private company deals
  - **BizBuySell Valuation Reports**: Service business multiples and benchmarks
  - **IBISWorld**: Industry reports with financial metrics
- **Access Method**: Paid subscriptions, library access, consulting firm reports
- **Cost**: $500-5,000+/year for data access
- **Coverage**: Comprehensive industry coverage
- **Use Cases**:
  - Business valuation
  - Deal pricing analysis
  - Financial health benchmarking
  - Industry comparison
- **Feasibility**: MEDIUM (paid subscriptions required)
- **Priority**: MEDIUM
- **Sources**: [Business Valuation Resources](https://www.bvresources.com/), [BVR Benchmarking Platform](https://www.bvresources.com/products/valuation-benchmarking-platform), [BizBuySell Service Business Valuation](https://www.bizbuysell.com/learning-center/valuation-benchmarks/service-business/), [4 Industry Benchmark Tips](https://www.nacva.com/content.asp?contentid=322)

#### **IBISWorld Industry Reports**

- **Description**: Comprehensive industry market research and financial data
- **Data Available**:
  - 723 US industries (all NAICS codes)
  - Trends, statistics, market analysis
  - Industry revenue, growth rates
  - Market share of competitors
  - Barriers to entry, cost structure
  - 5-year forecasts
  - Approximately 25-30 pages per report
- **Access Method**: Subscription (ibisworld.com or library access)
- **Cost**: Unknown (enterprise/institutional pricing), often available via university libraries
- **Coverage**: All US industries, selected China and global industries
- **Use Cases**:
  - Industry analysis
  - Market opportunity assessment
  - Competitive landscape
  - Financial benchmarking
- **Feasibility**: MEDIUM (expensive, may access via libraries)
- **Priority**: MEDIUM
- **Sources**: [IBISWorld](https://www.ibisworld.com/), [IBISWorld Guide - Stanford](https://libguides.stanford.edu/library/ibisworld)

#### **QuickBooks / Xero API (Seller-Granted Access)**

- **Description**: Accounting software APIs for accessing actual business financials
- **Data Available**:
  - Invoices, expenses, payments
  - Revenue, profit & loss
  - Cash flow statements
  - Accounts payable/receivable
  - Full financial reports
- **Access Method**: Official APIs (QuickBooks Online API, Xero Accounting API) with seller authorization (OAuth)
- **Cost**: FREE API access (with seller permission), rate limits apply
- **Coverage**: Businesses using these platforms (millions)
- **Use Cases**:
  - Due diligence financial verification
  - Real-time financial data access
  - Cash flow analysis
  - Revenue validation
- **Feasibility**: HIGH (if seller grants access)
- **Priority**: HIGH (for due diligence phase)
- **Sources**: [Xero API](https://developer.xero.com/documentation/api/accounting/overview), [QuickBooks API](https://www.apideck.com/blog/exploring-the-quickbooks-online-accounting-api), [Xero API Integration Guide](https://www.chift.eu/blog/build-xero-api-integration)

#### **Stripe Revenue Recognition API (Seller-Granted)**

- **Description**: Payment processor financial data access
- **Data Available**:
  - Transaction data
  - Revenue recognition reports
  - Accrual accounting data
  - Journal entries (ASC 606 compliant)
  - Real-time payment flows
- **Access Method**: Stripe API with seller authorization
- **Cost**: FREE API access (with seller permission)
- **Coverage**: Businesses using Stripe
- **Use Cases**:
  - Due diligence revenue verification
  - Payment trend analysis
  - Real-time financial monitoring
- **Feasibility**: HIGH (if seller grants access)
- **Priority**: MEDIUM
- **Sources**: [Stripe Revenue Recognition API](https://www.hubifi.com/blog/stripe-revenue-recognition-api), [Stripe Revenue Recognition](https://docs.stripe.com/revenue-recognition/api)

#### **US Census Bureau Economic Data**

- **Description**: Government economic statistics and business data
- **Data Available**:
  - Economic Indicator Time Series (monthly/quarterly)
  - Annual Business Survey (ABS)
  - Economic Census data (2002-2022)
  - Business counts by county
  - Employment, wages, establishments by industry
  - Quarterly Workforce Indicators
  - Business Dynamics Statistics
- **Access Method**: Census Bureau APIs (free, 500 calls/day without key, more with API key)
- **Cost**: FREE
- **Coverage**: Comprehensive US business and economic data
- **Use Cases**:
  - Market sizing
  - Industry trends
  - Regional economic analysis
  - Workforce data
- **Feasibility**: HIGH (free public API)
- **Priority**: MEDIUM
- **Sources**: [Census Bureau APIs](https://www.census.gov/data/developers/data-sets.html), [Economic Indicators API](https://www.census.gov/data/developers/data-sets/economic-indicators.html), [Small Business API](https://www.census.gov/topics/business-economy/small-business/data/api.html)

### 2.2 Quality & Reputation Signals

#### **Google Reviews (via Google Places API)**

- **Description**: Customer reviews and ratings from Google Maps
- **Data Available**:
  - Star ratings (1-5)
  - Number of reviews
  - Review text and sentiment
  - Review dates and trends
  - Reviewer information
  - Business responses
- **Access Method**: Google Places API
- **Cost**: Free tier + paid per query
- **Coverage**: 200M+ businesses globally
- **Use Cases**:
  - Quality assessment
  - Customer satisfaction analysis
  - Sentiment trend monitoring
  - Reputation risk screening
- **Feasibility**: HIGH (official API)
- **Priority**: HIGH
- **Sources**: [Google Places API](https://developers.google.com/maps/documentation/places/web-service/overview)

#### **Yelp Reviews (via Yelp Fusion API)**

- **Description**: Consumer reviews focused on local services and restaurants
- **Data Available**:
  - Star ratings
  - Review counts
  - 3-7 review excerpts (160 chars) depending on plan
  - Review sentiment
- **Access Method**: Yelp Fusion API
- **Cost**: 5,000 free trial calls, then paid per call
- **Coverage**: Millions of businesses in 32 countries
- **Use Cases**:
  - Consumer-facing business quality assessment
  - Sentiment analysis
  - Reputation tracking
- **Feasibility**: HIGH (official API)
- **Priority**: HIGH
- **Sources**: [Yelp Reviews API](https://docs.developer.yelp.com/reference/v3_business_reviews)

#### **Trustpilot Reviews API**

- **Description**: Consumer review platform focused on online businesses
- **Data Available**:
  - Star ratings and distributions
  - Review content and dates
  - Consumer profiles
  - Review counts and trends
- **Access Method**: Trustpilot API (Service Reviews API, Product Reviews API, Consumer API)
- **Cost**: Unknown (likely paid for API access)
- **Coverage**: Extensive online business coverage
- **Use Cases**:
  - E-commerce business reputation
  - Customer satisfaction tracking
  - Service quality assessment
- **Feasibility**: MEDIUM (API available, cost unclear)
- **Priority**: LOW (less relevant for most SMBs)
- **Sources**: [Trustpilot Service Reviews API](https://developers.trustpilot.com/service-reviews-api/), [Trustpilot API](https://developers.trustpilot.com/)

#### **Glassdoor Reviews API**

- **Description**: Employee reviews and workplace ratings
- **Data Available**:
  - Overall company ratings
  - Culture and values ratings
  - Work-life balance ratings
  - Senior management ratings
  - Compensation and benefits ratings
  - CEO approval ratings
  - Interview experiences
  - Salary data
- **Access Method**:
  - Official Glassdoor Company API
  - Third-party APIs (Bright Data, OpenWeb Ninja, Wextractor)
  - Scraping (Apify)
- **Cost**:
  - Third-party: ~$250/100K records (Bright Data)
  - Official API pricing unknown
- **Coverage**: Extensive company coverage
- **Use Cases**:
  - Employee satisfaction assessment
  - Workplace culture evaluation
  - Compensation benchmarking
  - Management quality signals
- **Feasibility**: MEDIUM (APIs available, moderate cost)
- **Priority**: MEDIUM
- **Sources**: [Glassdoor Reviews Dataset - Bright Data](https://brightdata.com/products/datasets/glassdoor/reviews), [Glassdoor Company API](https://www.glassdoor.com/developer/companiesApiActions.htm), [OpenWeb Ninja Glassdoor API](https://www.openwebninja.com/api/real-time-glassdoor-data)

### 2.3 Risk & Legal Signals

#### **PACER (Federal Court Records)**

- **Description**: Public Access to Court Electronic Records (federal courts)
- **Data Available**:
  - Federal court case filings
  - Civil litigation records
  - Bankruptcy filings
  - Case dockets and documents
  - 1 billion+ documents
- **Access Method**: PACER online portal
- **Cost**: $0.10 per page (capped at $3 per document), fee waivers for low usage
- **Coverage**: All US federal courts
- **Use Cases**:
  - Litigation risk screening
  - Bankruptcy history check
  - Legal dispute identification
  - Compliance verification
- **Feasibility**: HIGH (public system, low cost)
- **Priority**: HIGH
- **Sources**: [PACER](https://pacer.uscourts.gov/), [Find a Case PACER](https://www.uscourts.gov/court-records/find-a-case-pacer)

#### **State & County Court Records**

- **Description**: Civil and criminal court records (state level)
- **Data Available**:
  - State court case filings
  - Judgments and liens
  - Small claims cases
  - Local litigation
- **Access Method**: State-by-state court portals, county clerk offices, aggregators
- **Cost**: Varies (often FREE to low-cost)
- **Coverage**: State and local courts (fragmented)
- **Use Cases**:
  - Local litigation screening
  - Judgment lien discovery
  - Legal risk assessment
- **Feasibility**: MEDIUM (fragmented by jurisdiction)
- **Priority**: MEDIUM
- **Sources**: [StateRecords.org](https://staterecords.org/)

#### **Lien & Judgment Databases**

- **Description**: Public records of liens, judgments, and encumbrances
- **Data Available**:
  - UCC liens (Uniform Commercial Code)
  - Federal and state tax liens
  - Judgment liens
  - Mechanic's liens
  - Property liens
- **Key Sources**:
  - **Experian Business**: 27M+ US businesses, lien data
  - **Wolters Kluwer Lien Solutions**: Nationwide UCC, tax liens, bankruptcies
  - **IRS Automated Lien System**: Federal tax liens
  - County recorders (property liens)
- **Access Method**: Public records portals, paid databases, county clerk offices
- **Cost**: FREE (public records) to paid services ($100-1,000/month)
- **Coverage**: Nationwide with county-level data
- **Use Cases**:
  - Financial encumbrance discovery
  - Debt obligation screening
  - Secured creditor identification
  - Risk assessment
- **Feasibility**: MEDIUM (mix of free and paid sources)
- **Priority**: HIGH
- **Sources**: [Experian Business Public Records](https://www.experian.com/small-business/business-public-records), [Lien Solutions - Wolters Kluwer](https://www.wolterskluwer.com/en/solutions/lien-solutions/ucc-filing-and-public-records-search/public-records-search), [StateRecords Liens](https://staterecords.org/liens/)

#### **UCC Filing Search**

- **Description**: Uniform Commercial Code filings (secured transactions)
- **Data Available**:
  - Secured party information
  - Collateral descriptions
  - Filing dates and status
  - Debtor information
- **Access Method**: Secretary of State UCC search portals (state-by-state), paid aggregators
- **Cost**: Mostly FREE (state portals), paid for bulk/API access
- **Coverage**: All US states
- **Use Cases**:
  - Secured debt discovery
  - Asset encumbrance identification
  - Lender relationship mapping
- **Feasibility**: HIGH (public records)
- **Priority**: MEDIUM
- **Sources**: State Secretary of State websites

#### **BBB Complaint Data**

- **Description**: Better Business Bureau complaints and resolutions
- **Data Available**:
  - Complaint counts by year
  - Complaint types
  - Resolution status
  - BBB rating factors
- **Access Method**: BBB API or scraping
- **Cost**: Unknown for API, scraping ~$50-200/month
- **Coverage**: US businesses engaging with BBB
- **Use Cases**:
  - Customer complaint screening
  - Dispute resolution tracking
  - Reputation risk assessment
- **Feasibility**: MEDIUM
- **Priority**: MEDIUM
- **Sources**: [BBB Complaint Statistics](https://www.bbb.org/all/bbb-complaint-statistics)

### 2.4 Operational & Compliance Data

#### **Business License Verification**

- **Description**: Business license status and compliance
- **Data Available**: (see Deal Sourcing section 1.3)
- **Use Cases**:
  - Compliance verification
  - License expiration monitoring
  - Operational legitimacy check
- **Priority**: MEDIUM (for due diligence)

#### **Health Inspection Records (Restaurants)**

- **Description**: Public health inspection reports and violations
- **Data Available**:
  - Inspection dates and scores
  - Violation types and severity
  - Corrective actions
  - Re-inspection results
- **Access Method**: Local health department websites, aggregators (in some markets)
- **Cost**: FREE (public records)
- **Coverage**: Varies by jurisdiction (major cities have online portals)
- **Use Cases**:
  - Restaurant operational quality assessment
  - Health code compliance
  - Risk screening for food businesses
- **Feasibility**: MEDIUM (fragmented by jurisdiction)
- **Priority**: LOW (specific to restaurants only)
- **Sources**: Local health departments

#### **Building Permits & Inspections**

- **Description**: Construction permits and inspection records
- **Data Available**:
  - Permit applications and approvals
  - Inspection records
  - Violation notices
  - Certificate of occupancy
- **Access Method**: City/county building department portals
- **Cost**: FREE (public records)
- **Coverage**: Local jurisdiction level
- **Use Cases**:
  - Facility investment tracking
  - Code compliance verification
  - Expansion activity detection
- **Feasibility**: MEDIUM (fragmented)
- **Priority**: LOW
- **Sources**: Local building departments

### 2.5 Market & Competitive Intelligence

#### **Market Research Reports**

- **Description**: Industry analysis and market intelligence (see IBISWorld in section 2.1)
- **Use Cases**:
  - Competitive landscape
  - Market sizing
  - Growth trends
- **Priority**: MEDIUM

#### **Competitor Analysis**

- **Description**: Using aggregated data sources to profile competitors
- **Data Sources**:
  - Google Maps (competitor locations)
  - Reviews (comparative quality)
  - Job postings (competitor hiring)
  - Technology stack (competitor sophistication)
  - Traffic data (competitor website performance)
- **Use Cases**:
  - Competitive positioning
  - Market saturation analysis
  - Differentiation opportunities
- **Feasibility**: HIGH (combining existing sources)
- **Priority**: MEDIUM

### 2.6 Sentiment & Community Intelligence

#### **Reddit Operator Discussions**

- **Description**: SMB operator communities sharing experiences
- **Key Subreddits**:
  - r/sweatystartup
  - r/smallbusiness
  - r/Entrepreneur
- **Data Available**:
  - Acquisition due diligence tips
  - Operator challenges and pain points
  - Industry-specific insights
  - Success/failure stories
- **Use Cases**:
  - Qualitative due diligence
  - Industry pain point discovery
  - Operator sentiment analysis
  - Best practice identification
- **Feasibility**: HIGH (free API and scraping)
- **Priority**: HIGH
- **Sources**: [Reddit API](https://www.reddit.com/dev/api/)

#### **Industry Forums & Communities**

- **Description**: Industry-specific online forums
- **Examples**:
  - Franchise forums
  - Restaurant owner forums
  - Service business communities
- **Data Available**:
  - Operator experiences
  - Industry trends
  - Challenge discussions
- **Use Cases**:
  - Industry insight
  - Operator sentiment
  - Pain point discovery
- **Feasibility**: MEDIUM (manual monitoring or scraping)
- **Priority**: LOW

---

## 3. Data Source Comparison Matrix

| Source | Type | Cost | Coverage | Feasibility | Priority | Primary Use Case |
|--------|------|------|----------|-------------|----------|------------------|
| **Google Maps API** | Directory | Free + Paid | 200M businesses | HIGH | HIGH | Universal business discovery |
| **FDD Filings** | Financial | FREE | 3,500 franchises | HIGH | HIGH | Franchise financial benchmarks |
| **Secretary of State APIs** | Registry | FREE/Low | All US businesses | HIGH | HIGH | Business verification, owner data |
| **BizBuySell** | Marketplace | Free browse | 40K+ listings | MEDIUM | HIGH | Active deal flow monitoring |
| **Yelp Fusion API** | Reviews | Trial + Paid | Millions | HIGH | HIGH | Quality & sentiment signals |
| **Reddit Communities** | Sentiment | FREE | Active communities | HIGH | HIGH | Operator insights, strategies |
| **PACER** | Legal | $0.10/page | All federal courts | HIGH | HIGH | Litigation & bankruptcy risk |
| **Job Postings APIs** | Growth Signal | Varies | Extensive | LOW-MED | MEDIUM | Hiring = growth indicator |
| **BBB API** | Reputation | Unknown | US businesses | MEDIUM | MEDIUM | Complaint screening |
| **Business Licenses** | Compliance | FREE | By jurisdiction | MEDIUM | MEDIUM | License verification |
| **Sourcescrub** | AI Platform | $10K-50K/yr | 15M companies | LOW | MEDIUM | Proprietary deal sourcing |
| **Grata** | AI Platform | $10K-50K/yr | 16M companies | LOW | MEDIUM | Private company search |
| **IBISWorld** | Market Research | $1K-5K/yr | 723 US industries | MEDIUM | MEDIUM | Industry analysis |
| **BuiltWith/Wappalyzer** | Technology | $300-1K/yr | Millions of websites | MEDIUM | MEDIUM | Tech sophistication signal |
| **LinkedIn Company Pages** | Growth Signal | $30-500/mo | Millions | MEDIUM | MEDIUM | Headcount growth tracking |
| **OpenCorporates** | Registry | FREE + Paid | 204M global | HIGH | MEDIUM | Global business data |
| **Court Records (State)** | Legal | FREE/Low | By state | MEDIUM | MEDIUM | Local litigation screening |
| **UCC Filings** | Financial | FREE | All states | HIGH | MEDIUM | Secured debt discovery |
| **Glassdoor** | Reputation | $250/100K | Extensive | MEDIUM | MEDIUM | Employee satisfaction |
| **ZoomInfo** | Data Enrichment | $10K-50K/yr | 200M contacts | LOW | LOW | Contact enrichment (expensive) |
| **Crunchbase** | Funding Data | Paid | Millions | MEDIUM | LOW | Startup focus (not SMB) |
| **QuickBooks/Xero API** | Financial | FREE (auth) | Millions | HIGH | HIGH | Due diligence financials (seller-granted) |
| **Stripe API** | Financial | FREE (auth) | Stripe users | HIGH | MEDIUM | Payment verification (seller-granted) |
| **Census Bureau APIs** | Economic | FREE | US comprehensive | HIGH | MEDIUM | Market sizing, trends |
| **Trustpilot API** | Reviews | Unknown | E-commerce focus | MEDIUM | LOW | Online business reputation |
| **SimilarWeb** | Traffic | Enterprise | Millions | LOW | LOW | Website traffic (expensive) |

---

## 4. Reddit Insights

### Key Findings from Reddit Research

While specific Reddit threads were difficult to retrieve via web search, I found valuable insights from the broader Reddit ecosystem and related sources:

#### **r/sweatystartup Community Insights**

**What is "Sweaty Startup"?**
- Service-based and physical businesses (cleaning, junk removal, storage, moving, landscaping)
- Focus on businesses that require manual labor
- Community of operators and acquirers sharing strategies

**Key Insights:**
- "If it's on Zillow you are too late" - applies to business marketplaces too; need competitive advantage
- Call businesses acting like a customer to assess quality and capacity
- Nick Huber (founder) runs business brokerage at nickhuber.com/buy
- Community shares deal breakdowns and success stories

**Deal Sourcing Strategies:**
- Go beyond public marketplaces (BizBuySell, etc.)
- Build relationships with business brokers
- Network in local business communities
- Look for off-market opportunities
- Find businesses through tax lien cleanups, foreclosures (in real estate context)

**Quote**: *"You have to find a competitive advantage. You can't just rely on what's publicly listed."*

**Sources**: [Sweaty Startup](https://www.sweatystartup.com/), [Sweaty Startup Deal Breakdowns](https://sweatystartup.com/deal-breakdowns/page/8/)

#### **Entrepreneurship Through Acquisition (ETA) Community**

**Growth Trends:**
- ETA has surged in popularity at business schools (Harvard, Stanford, Wharton, Kellogg, Darden)
- "Silver Tsunami" - baby boomers retiring, creating acquisition opportunities
- Search fund model gaining mainstream adoption

**Deal Sourcing Reality:**
- "Platform Myth" - high-quality acquisitions aren't waiting on public dashboards
- Success requires systematic, relentless proprietary outreach
- Volume matters: "If 1 in 100 companies would make a good acquisition, seeing 1,000 companies surfaces ~10 viable targets"

**Buyer Positioning:**
- "If you look like every other first-time buyer with a Gmail and no capital plan, brokers will ghost you"
- Need: professional bio, financing prequalification, deal thesis

**Reddit Discussions - Buyer Challenges:**
- Hardest part is sourcing truly great businesses (not raising capital)
- Due diligence, operational skill, and grit separate successful searchers
- Many buyers struggle with broker relationships

**Sources**: [EtA FAQ - Investors Club](https://investors.club/entrepreneurship-through-acquisition-faq/), [Reddit Q&A - Clearly Acquired](https://www.clearlyacquired.com/blog/reddit-q-a-for-those-buying-a-business--hows-your-search-and-deal-process-going-what-challenges-are-you-running-into-in-in-this-market)

#### **r/smallbusiness Due Diligence Insights**

Based on general small business acquisition research and community discussions:

**Financial Due Diligence (30-90 days typical):**
- Request 3-5 years financial statements
- Verify against bank records (not just seller-provided financials)
- Check tax returns (personal and corporate)
- Analyze revenue trends, gross margins
- Review accounts receivable/payable aging

**Legal & Compliance:**
- Articles of incorporation, bylaws, shareholder agreements
- Employee contracts
- Litigation history
- IP rights verification
- Regulatory licenses
- Lease agreements (critical for retail/restaurants)

**Operational "Soft" Due Diligence:**
- Interview management team
- Assess employee satisfaction
- Evaluate supplier relationships
- Understand customer concentration
- Check for "key person" dependency

**Red Flags Discussed:**
- Declining revenue trends
- Customer concentration (>20% from single customer)
- Owner doing all the work (key person risk)
- Poor bookkeeping/financial records
- Legal issues or pending lawsuits
- Lease problems or expiration

**Sources**: [Due Diligence Checklist - Security Banks](https://www.security-banks.com/blog/due-diligence-checklist-for-small-business-acquisitions), [Due Diligence Guide - Quiet Light](https://quietlight.com/your-guide-to-due-diligence-when-buying-a-small-business/)

### Key Takeaways for Scout

1. **Proprietary outreach beats marketplace searching** - Volume and systematic process matter
2. **Buyer positioning is critical** - Professional presentation opens doors
3. **Relationships unlock off-market deals** - Network with brokers, operators, associations
4. **Financial verification is essential** - Always verify against bank records, not just provided statements
5. **"Sweaty" businesses are underserved** - Service businesses get less tech/data attention
6. **Community intelligence is valuable** - Reddit provides qualitative insights not available in structured data

---

## 5. Competitive Analysis

### 5.1 Existing Deal Sourcing Platforms

#### **Sourcescrub**

**What They Do:**
- Market-leading deal sourcing platform for M&A professionals
- Multi-source AI with "expert-in-the-loop" human validation
- 150,000+ information sources → 15M companies

**Data Approach:**
- Profile+ standard: 7+ data categories, 9 growth signals per company
- Focus on founder-owned businesses (unique dataset)
- Events, directories, industry sources aggregated
- Human validation ensures quality

**Pricing & Access:**
- Enterprise sales model
- Likely $10,000-50,000+/year
- Target: PE firms, search funds, M&A advisors

**Gaps:**
- Expensive for individual searchers or early-stage platforms
- Focused on deal professionals, not democratized

#### **Grata**

**What They Do:**
- AI-powered private company search
- 16M+ companies, fully automated ML/AI
- "Deep search" using company websites as primary source

**Data Approach:**
- Web scraping company websites
- AI/ML to extract and structure data
- "Lookalike" search using AI training
- No human validation (pure automation)

**Strengths:**
- Good for niche thesis discovery
- AI-native approach
- Lookalike functionality

**Gaps:**
- Less accurate for bootstrapped/founder-owned companies vs. Sourcescrub (88% prefer Sourcescrub - 2024 study)
- Lacks granular data for smaller companies
- Website-only approach misses offline businesses

**Recent Development:**
- Grata and Sourcescrub appear to be joining forces (per multiple sources)

#### **Axial**

**What They Do:**
- Online marketplace model (not pure data)
- Connects private companies, advisors, and buyers
- Middle-market M&A focused

**Approach:**
- Community/network approach
- Member profiles and deal postings
- Relationship-driven platform

**Gaps:**
- Marketplace model (not comprehensive database)
- Requires membership and engagement
- More manual/relationship-based vs. data-driven

#### **PitchBook**

**What They Do:**
- M&A and private equity data platform
- Focus on larger deals ($10M+)
- Comprehensive financial data, valuations, fund info

**Gaps for SMB:**
- Focused on institutional PE, not SMBs
- Expensive ($10K-30K+/year)
- Limited coverage of sub-$10M businesses
- Overkill for search fund / SMB acquirer needs

#### **DealRoom**

**What They Do:**
- M&A project management and deal execution
- Virtual data room for due diligence
- Workflow and collaboration tools

**Gaps:**
- Not a deal sourcing tool (deals already identified)
- Focused on execution phase, not discovery

### 5.2 What Scout Can Do Differently

#### **Democratization**
- **Existing platforms**: Enterprise pricing ($10K-50K/year), sales-driven
- **Scout opportunity**: Affordable access for individual searchers, search funds, small PE

#### **Data Fusion**
- **Existing platforms**: Single data approach (Grata = websites, Sourcescrub = aggregation)
- **Scout opportunity**: Combine multiple free/low-cost sources into unique insights
  - Google Maps + Reviews + Job Postings + Technology Stack + Reddit sentiment
  - Create composite "acquisition readiness" scores

#### **SMB Focus**
- **Existing platforms**: Broad business focus or middle-market
- **Scout opportunity**: Laser focus on <$10M businesses, "sweaty startups," franchises
  - FDD database for franchise benchmarking
  - Service business specialization

#### **Qualitative + Quantitative**
- **Existing platforms**: Pure quantitative data
- **Scout opportunity**: Layer in Reddit sentiment, operator challenges, qualitative signals
  - What are operators complaining about in r/sweatystartup?
  - What industries are "hot" in acquisition discussions?

#### **Transparency**
- **Existing platforms**: Black box algorithms, proprietary data
- **Scout opportunity**: Show data sources, scoring methodology, confidence levels
  - Build trust with methodology transparency

#### **Real-Time Signals**
- **Existing platforms**: Static databases updated periodically
- **Scout opportunity**: Real-time monitoring of:
  - New BizBuySell listings
  - Job posting changes (hiring surge/decline)
  - Review trends (sentiment shifts)
  - Reddit discussion volume

---

## 6. First Principles Strategy

### Question: What are the 5 most valuable data sources for Scout?

#### **1. Google Maps API (Business Universe)**
**Why:**
- 200M+ businesses = comprehensive universe
- Geographic targeting built-in
- Reviews + ratings included
- Free/low-cost API access
- Foundation for all other data enrichment

**Value:** This is Scout's "master business list" - the starting point for discovering all businesses in target industries/locations.

#### **2. Franchise Disclosure Documents (FDD) (Financial Transparency)**
**Why:**
- RARE public financial data for SMBs
- Actual revenue, expenses, profit data
- Performance by location/franchisee
- FREE via state portals (CA, IN, MN, WI)
- 3,500+ franchise systems

**Value:** Franchises are undervalued acquisition targets with transparent financials. FDD is Scout's "secret weapon" - financial data that competitors don't have.

#### **3. Secretary of State Registries (Verification & Owner Data)**
**Why:**
- Authoritative business registration data
- Owner/officer names (for outreach)
- Business age (establishment date)
- Entity structure
- Mostly FREE

**Value:** Verify businesses exist, get owner names for direct outreach, filter by business age (established = lower risk).

#### **4. Review Aggregation (Quality Signals)**
**Why:**
- Google Reviews + Yelp = quality proxy
- Sentiment analysis = operational health
- Review trends = trajectory (improving/declining)
- Customer satisfaction signal

**Value:** Eliminate bad businesses early. Identify high-quality operators. Track reputation over time.

#### **5. Reddit Communities (Qualitative Intelligence)**
**Why:**
- Operator sentiment and pain points
- Deal sourcing strategies from practitioners
- Industry-specific insights
- FREE to scrape/monitor
- Unique data no other platform has

**Value:** Understand the "soft" factors - what makes businesses attractive, what are red flags, what are market trends from operators themselves.

### Data Fusion Opportunities

**Combination 1: "Hidden Gems"**
- Google Maps (universe) + High reviews (quality) + Low web traffic (undermarketed) + Older domain (established) = Businesses ripe for improvement

**Combination 2: "Growth Signals"**
- Business age (SOS) + Recent job postings (hiring) + Increasing review count (growing) + Positive review sentiment = Expanding business

**Combination 3: "Distressed"**
- Declining review trend + No recent job postings + UCC filings (debt) + Court records (litigation) = Potential distressed opportunity

**Combination 4: "Franchise Opportunity Score"**
- FDD financials (benchmarks) + Individual unit reviews (quality) + Territory analysis (saturation) + Owner age (retirement signal) = Franchise acquisition readiness

**Combination 5: "Technology Gap"**
- Service business (Google Maps) + Low tech stack sophistication (BuiltWith) + High revenue (FDD or estimated) = Modernization opportunity

### Quick Wins vs. Long-Term Investments

#### **Quick Wins (Months 1-2):**

1. **Google Maps Scraping**
   - Use Outscraper or Apify ($50-200/month)
   - Build business universe for target industries/locations
   - Extract reviews, ratings, basic data

2. **Reddit Monitoring**
   - Set up Reddit API scraping (FREE)
   - Monitor r/sweatystartup, r/smallbusiness, r/Entrepreneur
   - Build sentiment database and keyword extraction

3. **FDD Collection**
   - Scrape California, Indiana, Minnesota, Wisconsin SOS sites (FREE)
   - Build franchise financial benchmark database
   - Create franchise valuation models

4. **Secretary of State Bulk Downloads**
   - Download business registration data from states offering bulk data (FREE)
   - Build business verification database
   - Extract owner names for outreach lists

5. **BizBuySell Monitoring**
   - Scrape BizBuySell listings daily
   - Track new listings, price changes, sold businesses
   - Build deal flow alert system

#### **Medium-Term (Months 3-4):**

1. **Job Postings Integration**
   - Integrate TheirStack or similar API ($500-2,000/month)
   - Track hiring as growth signal
   - Build hiring trend database

2. **Court Records / PACER**
   - Set up PACER access ($0.10/page)
   - Build litigation/bankruptcy screening
   - Create risk alert system

3. **Technology Stack Data**
   - Subscribe to Wappalyzer API (~$300-500/month)
   - Analyze tech sophistication
   - Identify modernization opportunities

4. **Review Sentiment Analysis**
   - Build NLP pipeline for review analysis
   - Track sentiment trends over time
   - Create quality scores

5. **Business License Data**
   - Aggregate license data from major cities
   - Build compliance verification
   - Track license renewals

#### **Long-Term (Months 5-6):**

1. **AI Scoring Models**
   - Build proprietary "acquisition attractiveness" scores
   - Combine all data sources into composite signals
   - Train ML models on successful acquisitions

2. **Real-Time Monitoring**
   - Set up webhooks and alerts for data changes
   - Monitor listing changes, review spikes, hiring surges
   - Build notification system

3. **Competitive Intelligence**
   - Market saturation analysis by location
   - Competitive density mapping
   - Whitespace identification

4. **Seller Intent Prediction**
   - Model likelihood of sale based on signals
   - Business age + owner age + declining reviews + no job postings = high likelihood
   - Proactive outreach to predicted sellers

5. **Data Marketplace**
   - Consider selling access to enriched data
   - API for developers
   - Data-as-a-service model

### What's Feasible in 6 Months?

**Definitely Achievable:**
- Google Maps business universe (50K-100K businesses)
- FDD financial database (3,500 franchises)
- Reddit sentiment database (continuous monitoring)
- Secretary of State verification database (all 50 states)
- BizBuySell deal flow tracker (daily scraping)
- Review aggregation and sentiment (Google + Yelp)
- Basic search and filtering interface
- Email alert system for new opportunities

**Stretch Goals:**
- Job postings integration (depends on API access/cost)
- Court records screening (manual effort required)
- Technology stack analysis (depends on budget)
- AI scoring models (requires data science resources)

**Not Feasible Yet:**
- Sourcescrub/Grata competitor (requires $millions in funding)
- Real-time monitoring at scale (infrastructure costs)
- Proprietary contact enrichment (expensive data)

---

## 7. Data Pipeline Architecture

### Proposed Approach

#### **Phase 1: Foundation (Months 1-2)**

**Data Sources to Integrate:**
1. Google Maps API / Outscraper
2. State FDD Portals (CA, IN, MN, WI)
3. Reddit API (r/sweatystartup, r/smallbusiness, r/Entrepreneur)
4. Secretary of State Bulk Downloads (prioritize major states: CA, TX, FL, NY)
5. BizBuySell web scraping

**Integration Strategy:**
- **Google Maps**: Outscraper API ($200/month) → Daily scraping of target industries
- **FDD**: Custom scraper for state portals → Quarterly updates
- **Reddit**: Reddit API → Daily monitoring, keyword extraction
- **SOS**: Bulk downloads → Quarterly updates
- **BizBuySell**: Custom scraper → Daily monitoring

**Data Storage:**
- **PostgreSQL** for structured business data (name, address, financials, registration)
- **MongoDB** for semi-structured (reviews, Reddit posts, FDD documents)
- **S3** for raw documents (FDD PDFs, court records)

**Data Model:**
```
businesses
  - id (UUID)
  - name
  - address (normalized)
  - industry (NAICS codes)
  - source (google_maps, bizbuysell, etc.)
  - created_at, updated_at

reviews
  - business_id (FK)
  - source (google, yelp)
  - rating (1-5)
  - text
  - date
  - sentiment_score

listings
  - business_id (FK)
  - source (bizbuysell, flippa)
  - asking_price
  - revenue
  - cash_flow
  - listing_date
  - status (active, sold, expired)

registrations
  - business_id (FK)
  - state
  - registration_number
  - entity_type
  - registration_date
  - officers (JSONB)

fdd_data
  - franchise_system
  - year
  - item_19_data (JSONB) - financial performance
  - units_count
  - fees
  - litigation_count

reddit_posts
  - id
  - subreddit
  - title
  - text
  - date
  - keywords (array)
  - sentiment_score
```

**Update Frequency:**
- Google Maps: Weekly (for target lists), On-demand (for enrichment)
- FDD: Quarterly (updated annually by law)
- Reddit: Daily
- SOS: Quarterly
- BizBuySell: Daily
- Reviews: Monthly (for existing businesses)

#### **Phase 2: Enrichment (Months 3-4)**

**Additional Data Sources:**
1. Yelp Fusion API
2. Job postings (TheirStack or scraping)
3. PACER court records (manual + API)
4. Wappalyzer technology stack
5. BBB complaints

**Integration:**
- **Yelp**: Official API → Monthly updates for businesses in system
- **Job Postings**: TheirStack API ($1,000/month) → Weekly updates
- **PACER**: Manual searches + API → On-demand during due diligence
- **Wappalyzer**: API ($500/month) → Monthly scans
- **BBB**: Scraping → Quarterly updates

**Enhanced Data Model:**
```
hiring_signals
  - business_id (FK)
  - job_title
  - posted_date
  - source (indeed, linkedin)
  - department

technology_stack
  - business_id (FK)
  - technologies (array) - [wordpress, shopify, stripe]
  - sophistication_score

legal_records
  - business_id (FK)
  - court
  - case_number
  - case_type (lawsuit, bankruptcy)
  - filing_date
  - status

complaints
  - business_id (FK)
  - source (bbb)
  - complaint_count
  - resolution_rate
```

#### **Phase 3: Intelligence (Months 5-6)**

**Advanced Features:**
1. AI scoring models
2. Real-time monitoring
3. Predictive analytics
4. Competitive intelligence

**Algorithms:**
- **Acquisition Attractiveness Score**: Weighted composite of:
  - Financial health (revenue estimate, review count as proxy)
  - Quality (review rating, sentiment)
  - Growth (review trend, hiring activity)
  - Risk (legal records, complaints)
  - Opportunity (tech stack gap, market saturation)

- **Seller Intent Prediction**: Logistic regression on:
  - Business age (older = higher likelihood)
  - Review trends (declining = higher)
  - Hiring (no recent postings = higher)
  - Owner age (if available via SOS or LinkedIn)

- **Franchise Opportunity Score**: For franchises with FDD data:
  - Unit financial performance vs. system average
  - Review quality vs. franchise average
  - Territory saturation
  - Franchisor litigation history

### Cost Estimates

#### **Phase 1 (Months 1-2):**
- Outscraper (Google Maps): $200/month
- Web scraping infrastructure: $50/month (proxies, servers)
- Database hosting (PostgreSQL + MongoDB): $100/month
- Storage (S3): $20/month
- **Total: ~$370/month**

#### **Phase 2 (Months 3-4):**
- Phase 1 costs: $370/month
- Yelp API: $100/month (estimated)
- TheirStack Job Postings: $1,000/month
- Wappalyzer: $500/month
- PACER: $50/month (average usage)
- Additional infrastructure: $100/month
- **Total: ~$2,120/month**

#### **Phase 3 (Months 5-6):**
- Phase 2 costs: $2,120/month
- ML infrastructure (model training, inference): $200/month
- Enhanced monitoring/alerting: $100/month
- **Total: ~$2,420/month**

#### **First 6 Months Total Cost:**
- Months 1-2: $370 × 2 = $740
- Months 3-4: $2,120 × 2 = $4,240
- Months 5-6: $2,420 × 2 = $4,840
- **Total: ~$9,820 for 6 months**

#### **Annual Run-Rate (Post Month 6):**
- ~$2,420/month × 12 = **~$29,000/year**

**Note:** Does NOT include:
- Developer time/salary
- Premium APIs (Sourcescrub, Grata) if added later
- Enterprise data sources (ZoomInfo, etc.)
- Legal fees for data usage compliance

---

## 8. Gaps & Risks

### Data That's Hard or Impossible to Get

#### **1. Private Company Financials**
**Gap:** Most SMBs don't publish financial statements

**Workarounds:**
- FDD data for franchises (transparent)
- Seller-granted access (QuickBooks/Xero APIs during due diligence)
- Estimate revenue from:
  - Employee count × industry revenue-per-employee
  - Square footage × sales per square foot (retail)
  - Review count as activity proxy
  - Job postings (hiring = growth)

#### **2. Owner Intentions**
**Gap:** Can't directly know if owner wants to sell

**Workarounds:**
- Predictive signals:
  - Business age (20+ years = retirement age)
  - Review trends (declining = losing interest)
  - No recent hiring (not investing in growth)
  - Owner age (LinkedIn, public records)
- Proactive outreach to likely sellers

#### **3. Customer Concentration**
**Gap:** Customer lists are private

**Workarounds:**
- Review analysis (do reviews mention specific customers/projects?)
- LinkedIn connections (employees' connections reveal customers)
- Industry knowledge (some industries inherently concentrated)
- Due diligence phase: direct disclosure

#### **4. Actual Debt Obligations**
**Gap:** Private companies don't report debt levels

**Workarounds:**
- UCC filings (secured debt)
- Court records (judgments)
- Credit reports (D&B, Experian Business) - paid
- Due diligence phase: financial statement analysis

#### **5. Key Person Dependency**
**Gap:** Hard to quantify owner's role

**Workarounds:**
- Employee count (1-2 employees = likely owner-dependent)
- Reviews mentioning owner by name
- Job postings (no manager roles = owner does everything)
- Glassdoor reviews (if available)
- Due diligence interviews

#### **6. Technology & Systems**
**Gap:** Internal systems not visible

**Workarounds:**
- BuiltWith/Wappalyzer for web tech
- Job postings (software experience required reveals systems)
- Industry standards (most restaurants use POS X, etc.)
- Due diligence site visit

### Legal & Compliance Risks

#### **Web Scraping Legal Issues**

**Risk:** Terms of Service violations, CFAA (Computer Fraud and Abuse Act) concerns

**Mitigation:**
- Focus on public data only
- Respect robots.txt
- Use official APIs when available
- Don't access behind logins without permission
- Consult legal counsel on specific scraping activities
- Use third-party services (Outscraper, Apify) that handle compliance

#### **Data Privacy (GDPR, CCPA)**

**Risk:** Personal data collection and storage regulations

**Mitigation:**
- Focus on business data, not personal data
- If collecting personal data (owner names, emails):
  - Implement data minimization
  - Provide opt-out mechanisms
  - Document legal basis for processing
  - Implement data retention policies
- Consult privacy attorney

#### **API Terms of Service**

**Risk:** Violating API ToS (e.g., Google, Yelp) by using data improperly

**Mitigation:**
- Read and comply with all API ToS
- Don't store data longer than allowed
- Don't resell raw API data (value-add only)
- Monitor for ToS changes

### Data Quality Risks

#### **Stale Data**
**Risk:** Data becomes outdated (businesses close, info changes)

**Mitigation:**
- Regular refresh cycles (quarterly for slow-changing, monthly for reviews)
- Last-updated timestamps on all data
- Validation checks during enrichment
- User-reported corrections

#### **Incomplete Data**
**Risk:** Missing key fields for many businesses

**Mitigation:**
- Track data completeness scores
- Prioritize enrichment for high-value targets
- Show confidence levels in UI
- Progressive enrichment (start broad, deepen over time)

#### **Inaccurate Data**
**Risk:** Wrong information (outdated, incorrect)

**Mitigation:**
- Cross-reference multiple sources
- Show data sources in UI (transparency)
- User feedback mechanisms
- Verification workflows for critical data

---

## 9. Recommendations

### Phase 1: Months 1-2 (Foundation)

**Goal:** Build comprehensive business universe + basic enrichment

**Priorities:**
1. ✅ **Google Maps Integration** - Business universe foundation
   - Start with 3-5 target industries (e.g., HVAC, plumbing, car washes, dry cleaners, self-storage)
   - 3-5 target markets (e.g., Texas, Florida, Arizona)
   - Build initial database of 10K-50K businesses

2. ✅ **FDD Data Collection** - Financial benchmark database
   - Scrape California, Indiana, Minnesota, Wisconsin portals
   - Parse FDD Item 19 financial data
   - Build franchise financial benchmark models

3. ✅ **Reddit Monitoring** - Sentiment intelligence
   - Daily scraping of r/sweatystartup, r/smallbusiness, r/Entrepreneur
   - Keyword extraction (deal sourcing, due diligence, [industry names])
   - Build sentiment and topic database

4. ✅ **Secretary of State Data** - Verification foundation
   - Bulk download from CA, TX, FL, NY
   - Parse registration data, extract owner names
   - Build verification database

5. ✅ **BizBuySell Scraper** - Active deal flow
   - Daily scraping of new listings
   - Track pricing, industries, locations
   - Build comp database

**Deliverables:**
- Database with 10K-50K businesses
- Basic search interface (industry, location, size)
- FDD financial benchmark tool (for franchises)
- Deal flow alerts (new BizBuySell listings)
- Reddit insight dashboard

**Success Metrics:**
- 10,000+ businesses in database
- 100+ FDDs parsed
- 500+ Reddit posts analyzed
- 50+ states SOS data integrated
- Daily BizBuySell monitoring active

### Phase 2: Months 3-4 (Enrichment)

**Goal:** Add quality, growth, and risk signals

**Priorities:**
1. ✅ **Review Aggregation** - Quality signals
   - Integrate Yelp Fusion API
   - Aggregate Google + Yelp reviews
   - Build sentiment analysis pipeline
   - Track review trends over time

2. ✅ **Job Postings Integration** - Growth signals
   - Integrate TheirStack or scrape Indeed/LinkedIn
   - Track hiring activity by business
   - Build hiring trend database
   - Create growth alerts

3. ✅ **Court Records** - Risk signals
   - Set up PACER access
   - Build litigation/bankruptcy screening
   - Integrate state court records (major markets)
   - Create risk alerts

4. ✅ **Technology Stack** - Sophistication signals
   - Integrate Wappalyzer API
   - Scan websites for tech stack
   - Build sophistication scoring
   - Identify modernization opportunities

5. ✅ **Data Enrichment Pipeline**
   - Automated enrichment workflows
   - Prioritize high-value targets
   - Cross-reference data across sources
   - Build data quality scores

**Deliverables:**
- Enhanced business profiles (quality + growth + risk scores)
- Review sentiment dashboard
- Hiring trend tracking
- Risk screening reports
- Technology gap analysis

**Success Metrics:**
- 80%+ businesses have review data
- 50%+ businesses have hiring data
- Risk screening for top 1,000 businesses
- Technology stack data for businesses with websites

### Phase 3: Months 5-6 (Intelligence)

**Goal:** Build proprietary insights and predictive models

**Priorities:**
1. ✅ **Acquisition Attractiveness Scoring**
   - Weighted composite model
   - Combine quality + growth + risk + opportunity
   - Calibrate against successful acquisitions (if data available)
   - Build scoring dashboard

2. ✅ **Seller Intent Prediction**
   - Logistic regression model
   - Features: age, review trends, hiring, owner age
   - Predict likelihood of sale
   - Prioritize outreach lists

3. ✅ **Competitive Intelligence**
   - Market saturation analysis
   - Competitor density mapping
   - Whitespace identification
   - Competitive positioning insights

4. ✅ **Real-Time Monitoring**
   - New listing alerts (BizBuySell)
   - Review spike alerts (sentiment shift)
   - Hiring surge alerts (growth signal)
   - Price change alerts (marketplace)

5. ✅ **Data Marketplace** (Optional)
   - Consider API access for developers
   - Enriched data export
   - Custom reports

**Deliverables:**
- Acquisition attractiveness scores for all businesses
- Seller intent predictions
- Competitive intelligence reports
- Real-time alert system
- API documentation (if pursuing marketplace)

**Success Metrics:**
- Scoring model with 70%+ predictive accuracy
- Real-time alerts active for key signals
- Competitive analysis for 10+ markets/industries
- API usage (if launched)

### Long-Term Roadmap (Post Month 6)

**Months 7-12:**
- Expand to all 50 states comprehensively
- Add more data sources (Glassdoor, LinkedIn scraping)
- Build proprietary contact enrichment
- Launch API for developers
- Expand industry coverage (retail, healthcare, franchises beyond FDD)

**Year 2:**
- Build Sourcescrub/Grata competitor (with funding)
- Real-time monitoring at scale
- AI-powered deal matching
- Mobile app
- Community features (deal sharing, collaboration)

**Year 3:**
- International expansion
- M&A advisory services
- Transaction facilitation
- Financing marketplace integration

---

## 10. Conclusion

### Summary

This research identifies **50+ data sources** for SMB acquisition deal sourcing and due diligence, ranging from free public records to premium enterprise platforms. The opportunity for Scout is to **democratize access** to acquisition intelligence by combining free and low-cost data sources into unique insights that currently only expensive platforms like Sourcescrub and Grata provide.

**The Scout advantage:**
1. **Focus**: Laser-focused on <$10M SMBs, "sweaty startups," and franchises
2. **Affordability**: $10K-30K/year vs. $30K-50K+ for competitors
3. **Data Fusion**: Combine quantitative (Google Maps, FDD, SOS) + qualitative (Reddit sentiment)
4. **Transparency**: Show data sources and methodology (build trust)
5. **Franchise Expertise**: FDD financial database is a unique asset

**First 6 months are achievable** with ~$10K budget:
- Build 10K-50K business database
- Integrate 10-15 core data sources
- Create basic scoring models
- Launch MVP with search, alerts, and enrichment

**The biggest competitive moats:**
1. **FDD financial database** - No one else focuses on this
2. **Reddit sentiment intelligence** - Qualitative edge
3. **Data fusion algorithms** - Proprietary scoring
4. **SMB focus** - Underserved market vs. PE/VC focus

**Success metrics for Year 1:**
- 100K+ businesses in database
- 1,000+ active users
- 50+ deals facilitated
- $500K ARR (at $500-1,000/year per user)

The data landscape is fragmented but accessible. With systematic execution, Scout can become the **go-to platform for SMB acquirers** by aggregating public data, adding intelligence, and providing actionable insights at a fraction of the cost of existing enterprise platforms.

---

## Sources

### Deal Sourcing
- [SMB.co](https://smb.co/)
- [KUMO Top 10 Deal Sources](https://www.withkumo.com/blog/top-10-deal-sources-to-find-smb-listings-online)
- [BizBuySell Learning Center](https://www.bizbuysell.com/learning-center/article/where-to-find-a-business-for-sale/)
- [BusinessesForSale.com](https://us.businessesforsale.com)
- [Acquire.com Buyers](https://acquire.com/buyers/)
- [Best Places to Find Business to Buy](https://www.midstreet.com/blog/top-online-sites-buy-business)
- [Deal Sourcing for Search Funds 2025](https://searcherinsights.com/the-real-guide-to-deal-sourcing-for-your-search-fund-2025/)
- [Mastering Deal Sourcing - 4Degrees](https://www.4degrees.ai/blog/mastering-the-art-of-deal-sourcing-a-comprehensive-guide-for-investment-professionals)
- [Deal Sourcing Processes for Search Funds](https://www.insightscrm.com/article/deal-sourcing-processes-strategies-tools-for-search-funds)

### AI Platforms
- [Grata + Sourcescrub](https://grata.com/grata-and-sourcescrub)
- [Grata vs Sourcescrub Comparison](https://otio.ai/blog/grata-vs-sourcescrub)
- [Sourcescrub vs Grata](https://webflow.sourcescrub.com/uk/competitors/sourcescrub-vs-grata)
- [Why Choose Sourcescrub](https://www.sourcescrub.com/why-sourcescrub)
- [Private Equity Deal Flow 2026](https://grata.com/resources/private-equity-deal-flow)

### Business Directories
- [Google Maps Scraper - Outscraper](https://outscraper.com/google-maps-scraper/)
- [Apify Google Maps Scraper](https://apify.com/compass/crawler-google-places)
- [Google Maps Scraping Guide 2025](https://scrap.io/google-maps-scraping-complete-guide-business-data-leads-2025)
- [Yelp Places API](https://business.yelp.com/data/products/places-api/)
- [Yelp Developers](https://www.yelp.com/developers)

### Public Records
- [Secretary of State API - Middesk](https://www.middesk.com/blog/secretary-of-state-api)
- [Secretary of State API Solutions 2026](https://cobaltintelligence.com/blog/post/top-secretary-of-state-api-solutions-for-verifying-businesses)
- [OpenCorporates API](https://api.opencorporates.com/)
- [Getting Started with OpenCorporates API](https://blog.opencorporates.com/2025/02/13/getting-started-with-the-opencorporates-api/)
- [Business License Search API](https://apis.licenselookup.org/business-license-search-api/)
- [Data.gov Licenses](https://catalog.data.gov/dataset?tags=licenses)

### Financial Data
- [FDD Exchange](https://fddexchange.com/)
- [FRANdata FDDs](https://frandata.com/products-solutions/fdds-franchise-disclosure-documents/)
- [FranChimp FDDs](https://www.franchimp.com/?page=fdd)
- [Where to Find Free FDDs](https://www.oakscale.com/post/franchise-basics-where-to-find-free-franchise-disclosure-documents-fdds)
- [FTC FDD Deep Dive](https://www.ftc.gov/business-guidance/blog/2023/05/franchise-fundamentals-taking-deep-dive-franchise-disclosure-document)
- [Business Valuation Resources](https://www.bvresources.com/)
- [BizBuySell Service Business Valuation](https://www.bizbuysell.com/learning-center/valuation-benchmarks/service-business/)
- [IBISWorld](https://www.ibisworld.com/)

### APIs & Technology
- [Indeed Documentation](https://docs.indeed.com/)
- [LinkedIn Job Posting API](https://learn.microsoft.com/en-us/linkedin/talent/job-postings/api/overview?view=li-lts-2025-10)
- [TheirStack Job Postings API](https://theirstack.com/en/job-posting-api)
- [Wappalyzer API](https://www.wappalyzer.com/api/)
- [BuiltWith vs Wappalyzer](https://www.wappalyzer.com/articles/builtwith-alternative/)
- [SimilarWeb API](https://developers.similarweb.com/docs/similarweb-web-traffic-api)
- [WHOIS Lookup](https://www.whois.com/whois/)

### Data Enrichment
- [ZoomInfo API](https://api-docs.zoominfo.com/)
- [ZoomInfo Enterprise API](https://www.zoominfo.com/solutions/data-as-a-service/enterprise-api)
- [Clearbit Enrichment](https://clearbit.com/platform/enrichment)
- [Crunchbase Data](https://data.crunchbase.com/docs/welcome-to-crunchbase-data)
- [D&B Credit Information API](https://www.dnb.com/en-gb/developers/credit-information-b2b-api.html)
- [Apollo.io Email Finder](https://www.apollo.io/tools/email-finder)
- [Hunter.io API](https://hunter.io/api-documentation/v2)

### Reviews & Reputation
- [Yelp Reviews API](https://docs.developer.yelp.com/reference/v3_business_reviews)
- [Trustpilot Service Reviews API](https://developers.trustpilot.com/service-reviews-api/)
- [Glassdoor Reviews Dataset - Bright Data](https://brightdata.com/products/datasets/glassdoor/reviews)
- [BBB API](https://developer.bbb.org/)

### Legal & Court Records
- [PACER](https://pacer.uscourts.gov/)
- [Experian Business Public Records](https://www.experian.com/small-business/business-public-records)
- [Lien Solutions - Wolters Kluwer](https://www.wolterskluwer.com/en/solutions/lien-solutions/ucc-filing-and-public-records-search/public-records-search)
- [StateRecords.org](https://staterecords.org/)

### Accounting & Financial APIs
- [Xero API](https://developer.xero.com/documentation/api/accounting/overview)
- [QuickBooks API](https://www.apideck.com/blog/exploring-the-quickbooks-online-accounting-api)
- [Stripe Revenue Recognition API](https://www.hubifi.com/blog/stripe-revenue-recognition-api)
- [Census Bureau APIs](https://www.census.gov/data/developers/data-sets.html)

### Social & Community
- [LinkedIn Company Insights API](https://saleleads.ai/blog/linkedin-company-insights-api)
- [International Franchise Association](https://www.franchise.org/)
- [Sweaty Startup](https://www.sweatystartup.com/)
- [EtA FAQ - Investors Club](https://investors.club/entrepreneurship-through-acquisition-faq/)
- [Reddit Q&A - Clearly Acquired](https://www.clearlyacquired.com/blog/reddit-q-a-for-those-buying-a-business--hows-your-search-and-deal-process-going-what-challenges-are-you-running-into-in-this-market)

### Due Diligence
- [Due Diligence Checklist - Security Banks](https://www.security-banks.com/blog/due-diligence-checklist-for-small-business-acquisitions)
- [Due Diligence Guide - Quiet Light](https://quietlight.com/your-guide-to-due-diligence-when-buying-a-small-business/)
- [Ultimate Small Business Due Diligence Checklist](https://planwriters.com/blog/the-ultimate-small-business-due-diligence-checklist)

---

**End of Research Document**
