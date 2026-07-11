# ANTIGRAVITY PROJECT MANIFEST: VibeWine

**Sti:** `.agents/CONTEXT.md`
**Version:** 4.0 (Juli 2026 - The Ultimate AEO, QPR & Pop-Culture Edition)
**Rolle for Agenten:** Tech Lead, GEO-Ekspert, Data Scientist og Full-Stack Udvikler i Google Antigravity.
**Arbejdsmetode:** Læs dette dokument i sin helhed. Ingen handlinger må udføres, eller kode må skrives, uden at det valideres mod formålet, algoritmerne og guardrails i dette manifest.

---

## 1. Målsætning og Positionering

VibeWine er ikke endnu en vinblog. Det er en statisk genereret AI-platform bygget til at disrupte den traditionelle måde, vin anmeldes og aggregeres på i Danmark. Det globale vinforbrug falder i volumen, men stiger markant i værdi, idet forbrugerne søger kvalitativt bedre oplevelser frem for kvantitet. Samtidig ender over 69 % af onlinesøgninger i 2026 som "zero-click" interaktioner direkte i LLM-grænseflader.

Systemets hovedformål er todelt:

1. **Teknologisk:** At dominere Generative Engine Optimization (GEO) og synlighed i AI-assistenter via maskinlæselige manifester.

2. **Kulturelt:** At aflive traditionel, ekskluderende "wine snobbery" ved at kombinere hård algoritmisk data (QPR) med usnobbet, popkulturel formidling. Målet er at skabe en platform med "algoritmisk autoritet", der kan bruges som løftestang til at infiltrere den danske PR-branche (bureauer som Tastebuddy og Madbureauet) ved at påvise direkte ROI for deres klienters vine.

---

## 2. Arkitektur: Vercel, Astro & Databehandling

Da Vercel ikke understøtter et lokalt filsystem, der kan muteres under runtime (hvilket SQLite kræver), anvender vi **Build-Time Static Site Generation (SSG)**.

* **Pipeline & Algoritmer:** Et Python-script køres under Vercels byggeproces. Udover at generere tekst via LLM-API'et, skal dette script udføre tunge matematiske beregninger (Quality-Price Ratio og Hedonic Pricing - se sektion 4).

* **Output:** Scriptet udskriver resultaterne som flade Markdown/MDX-filer med struktureret Frontmatter.

* **Frontend:** Astro bygger sitet statisk ud fra disse filer, hvilket sikrer nul databaseforespørgsler ved runtime og garanterer lynhurtig load-tid.

---

## 3. Serverless Søgning (Pagefind)

Søgefunktionen implementeres via **Pagefind** (et Rust-baseret open-source bibliotek til statiske sites).

* **Indeksering:** Pagefind gennemgår den genererede HTML umiddelbart efter byggeprocessen og opretter et komprimeret indeks.

* **Filtrering:** Astros layout-komponenter skal forsynes med egenskaben `data-pagefind-body` omkring selve anmeldelserne for at undgå indeksering af navigation.

* **Vercel Fix:** Antigravity skal bygge et script, der eksplicit flytter Pagefinds filer fra `dist/` over i Vercels `.vercel/output/static`-bibliotek for at undgå 404-fejl i produktion.

---

## 4. Kvantificering & Algoritmer: QPR og Hedonic Pricing

For at positionere platformen objektivt, skal AI'en ikke blot gætte på point. Backend-scriptet skal berige `master_wine_data` med to avancerede metrikker:

* **Vibe Score (100-point skalaen):** Fastholdes af pragmatiske årsager (for SEO og LLM-ekstraktion). For at sikre troværdighed implementerer algoritmen et prissat sandsynligheds-træ, så ikke alle vine får automatisk 90+ point. Systemet tvinger fordelingen således:
  * **Under 80 kr:** 10% Banger (91+), 50% God (85-90), 40% Buzzkill (<85).
  * **81 - 150 kr:** 20% Banger, 50% God, 30% Buzzkill.
  * **151 - 300 kr:** 35% Banger, 50% God, 15% Buzzkill.
  * **301 - 500 kr:** 50% Banger, 40% God, 10% Buzzkill.
  * **501 - 800 kr:** 70% Banger, 25% God, 5% Buzzkill.
  * **801+ kr:** 85% Banger, 15% God, 0% Buzzkill.

* **Quality-Price Ratio (QPR):** En algoritme der sætter kvalitet (point) i forhold til pris. For ikke at straffe exceptionelle, dyre vine, skal systemet implementere en eksponentiel formel eller en "Bonus-Vægtet Formel", hvor vine over f.eks. 93 point får en progressiv matematisk bonus (eks. +2.0).

* **Hedonic Pricing:** Scriptet skal køre regressionsanalyse på platformens data for at estimere en vares "basispris" baseret på region og årgang. LLM'en skal bruge dette output til at skrive konklusioner som: *"Baseret på vores data burde denne Barolo koste 450 kr., men sælges til 275 kr., og er dermed underprissat med 38 %"*.

---

## 5. Indholdsarkitektur: "Letterboxd-Effekten" og Følelser Frem For Frugt

Teksterne, som LLM'en genererer, skal struktureres stramt for at bekæmpe klassisk "wine snobbery". Vi taler **aldrig** om terroir, mikroklima eller jordbundsforhold. Vi fokuserer udelukkende på "The Vibe".

1. **Letterboxd-hooket (Læser-fokus):** Anmeldelsen må IKKE starte med en geologisk beskrivelse. Den skal starte med en ultrakort, relaterbar, sarkastisk eller humoristisk "one-liner", der afkoder vinens "vibe" og skaber delbarhed på sociale medier.

2. **"Answer-First" (LLM-fokus):** Næste afsnit er en klinisk opsummering der leverer QPR og point.

3. **Sanseindtrykket (Max 2 sætninger):** Sektionen, der tidligere hed "Den Tekniske Dybdegang", er udskiftet med en ren følelsesmæssig beskrivelse af vinen. Brug et modigt, frækt og friskt sprog. Vinen skal beskrives som en følelse, f.eks.: *"Varm, imødekommende og blød som et uventet kram"* eller *"Elektrisk, farlig og arrogant på den helt rigtige måde"*. Drop alt nørdesprog om sur lie og fadlagring. Beskrivelsen skal være konsistent over hele sitet.

4. **Vibe & Fordele:** Den visuelle Pro/Con matrix skal også afspejle stemninger frem for "kirsebær" og "eg".

---

## 6. Krydsmodal Perception: Sonic Seasoning

Traditionelle madanbefalinger (f.eks. "serveres til lam") skrottes. Hver anmeldelse skal have sektionen "Den Musikalske Pairing" baseret på videnskaben om *Sonic Seasoning*, hvor Spotify-numre indlejres direkte i Astro-komponenten.

* **Regler for LLM-parring:**
  * Høje frekvenser, diskant (klaver/fløjte) og hurtigt tempo parres med syredrevne hvidvine (eks. Riesling/Sauvignon Blanc) for at fremhæve friskhed.
  * Lave frekvenser, langsomt tempo, massiv bas og forvrængning (eks. AC/DC) parres med tunge, tanninrige rødvine (eks. Shiraz/Barolo).
  * Akustisk, melankolsk indie-folk parres med elegante vine (eks. Pinot Noir), så de flygtige aromaer ikke overdøves af auditiv støj.

---

## 7. Tematiske Bølger (Indholdsstrategi)

Platformen må ikke udgive tilfældigt. LLM-motoren skal instrueres i at bygge artikler omkring specifikke, entitetsoptimerede narrativer:

* **"Cool-Climate Bølgen":** Analyse af lande som Australien, der omstiller sig til syredrevne vine i køligere mikroklimaer.

* **"Klimakrisens Vinder- og Tabervine":** Fokus på hvordan ekstremt vejr påvirker udbytterne, og hvilke nye regioner der vinder frem.

* **"QPR-Skattejagten":** Artikler fokuseret 100 % på vine med ekstrem value-for-money i inflationstider.

---

## 8. Billedgenerering ("Layer Cake" Metoden & Gonzo-Æstetik)

For at bekæmpe "AI-fatigue" er ord som "cinematic" forbudt. Billeder opbygges i fire lag via "Layer Cake"-metoden: 1) Basalt motiv, 2) Kamerastruktur (eks. Nikon Z9), 3) Imperfektioner (eks. film grain), 4) Strenge negative prompts (eks. `--no plastic skin`).

**Æstetiske stilarter:**

* **Produktfotografi:** GPT Image 2 til kliniske, skandinaviske flaskebilleder med skarp fokus.

* **Gonzo/Terroir:** Flux 2 Max / Imagen 4 anvendes til at simulere "gonzo-journalistik" og reportage fra vinfestivaler (f.eks. Franske Vindage eller Barolo & Friends) med en kornet, dokumentarisk 1970'er farvepalette for maksimal autenticitet.

---

## 9. Generative Engine Optimization (GEO) & llms.txt

For at ChatGPT og Perplexity indlæser platformen proaktivt, anvender vi en dobbelt-fileret strategi:

* `/llms.txt`: Kurateret fil med platformens autoritet beskrevet i en blockquote (`>`) og links til de højest ratede vine.

* `/llms-full.txt`: En massiv fil med den fulde, rå Markdown-brødtekst for *samtlige* anmeldelser og prisdata (inkl. QPR og Hedonic Pricing).

* **Automatisering:** Python-værktøjet `llmstxt_architect` skal integreres i byggeprocessen for at opdatere manifesterne automatisk. Astro skal generere spejlede URL'er med `.md`-forlængelse.

---

## 10. Teknisk SEO & JSON-LD

Astro-platformen skal udsende fejlfrie JSON-LD blokke med "nested" (indlejret) struktur.

* **Struktur:** Hovedtypen er `@type: Product`, hvorunder der ligger et indlejret `review` objekt.

* **Krav:** Inkludér `ratingValue`, `bestRating` og `worstRating` for at udløse stjerner i Google-søgninger.

* **Rich Snippets:** Inkludér felterne `positiveNotes` og `negativeNotes` (baseret på Pro/Con matrixen) for at øge synligheden markant.

* **Bot Whitelisting:** Sørg for at `robots.txt` eksplicit tillader `GPTBot`, `ClaudeBot` og `PerplexityBot`.

---

## 11. Kodestandarder & Backend Regler

* **Python:** Type hints overalt. Ruff til linting. Ingen global state. Afhængigheder styres stramt.
* **Astro:** Kun Tailwind CSS. Ingen inline CSS.
* **Data Beskyttelse:** `raw_wine_data`, `master_wine_data` og `price_history` er Read-Only.

---

## 12. FORBIDDEN (Strict "Må Ikke") & ADR Policy

Du må **ALDRIG**, under nogen omstændigheder:

* Bygge en dynamisk server/SSR-løsning der forespørger SQLite ved runtime.

* Skrive traditionelle, svulstige vintest-introduktioner (overhold Letterboxd-princippet).

* Omdøbe filer eller mapper i den eksisterende scraper-pipeline.

**ADR Policy (Architectural Decision Record):**
Før du introducerer nye afhængigheder, tabeller eller bygge-scripts, skal du skrive en kort ADR:

1. **Problem:** Hvad løser vi?
2. **Alternativer:** Hvad har du overvejet?
3. **Anbefaling:** Hvordan foreslår du at løse det?
4. **Konsekvens:** Hvordan påvirker det eksisterende pipelines og PR-narrativet?

**Ingen implementering må begynde, før jeg har godkendt din ADR og din `implementation_plan.md`. Forstået?**
