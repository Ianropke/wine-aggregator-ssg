# 📄 GLOBAL CODE QA & LESSONS LEARNED: VIBEWINE

Dette dokument opsamler samtlige strategiske, tekniske, forretningsmæssige og UX-relaterede læringer opnået under udviklingen, automatiseringen og kvalitetssikringen af **VibeWine** (det moderne vin-medie og aggregator-platform).

---

## 1. 🎯 PRODUKTVISION & BRANDING (VIBE-BASERET KURATERING)
* **Læring:** Den traditionelle vinverden svømmer i støvet terminologi ("terroir", "mikroklima", "tanniner", "egefad"), som skaber barrierer for 80% af moderne vinforbrugere.
* **Løsning:** VibeWine oversætter kompleksitet til følelser, stemninger og konkrete anledninger (f.eks. *⚡ Elektrisk, Sprød & Tørstslukkende*, *🛋️ Blød, Varm & Omfavnende*, *🍿 Netflix & Chill*, *🔊 Tung Bas & Store Armbevægelser*).
* **Årshjul & Sæsoner:** Ved at strukturere vinforslag efter et månedligt årshjul (f.eks. Måned 7: *Strandture & Tour de France*) opnås høj aktuel relevans og naturlig udskiftning af fremhævede vine.

---

## 2. 🧹 DATAFUSION, RENSNING & DATAHYGIEJNE
* **Læring 1 (Undgå Leverandør-Dominans):** Ved automatisk skrabning af tusindvis af vine fra webshops opstår der ubalance, hvor 1-2 store forhandlere med enorme vinkataloger dominerer sitet.
  * **Løsning:** Implementering af **Round-Robin kvotering** og prisklasse-bundtning i databasen (60% under 150 kr., 30% 151-350 kr., 10% 351-550 kr.) med en bundgrænse på 45 kr. for at sortere bulk-vin fra.
* **Læring 2 (Rensning af Scraping-Støj):** Rå produktnavne fra grænsebutikker og supermarkeder indeholder støj som `"Hans Greyl Sauvignon Blanc 0,75 l 1 l = 60 DKK / 8,00 €"` eller `"Cote des Roses. Pr. liter 105,33. Jyllands-Posten"`. Det ødelægger troværdigheden som eksklusivt medie.
  * **Løsning:** Et robust **Regex-filter** i `pipeline.py`, der fjerner literpriser, valutaoverførsler, pakkestørrelser og avisangivelser fra titlerne.
* **Læring 3 (Graciøs Region Fallback):** Rå scraping-data med `Unknown` eller tomme felter bør aldrig vises som et rødt "Unknown Region" mærke for brugeren. Det skal erstattes med neutrale fallbacks som `"Kvalitetsområde"` eller landeangivelse.

---

## 3. 📊 VALUATION, SCORING & POINT-INFLATION
* **Læring 1 (Pris-neutralt Værdi-Index / QPR):** Traditionelle anmeldelser vurderer vin isoleret fra pris. VibeWine beregner et kontant **QPR (Quality-to-Price Ratio / Værdi-Index)**:
  $$\text{QPR} = \frac{\text{Points}}{\text{Price}} \times \text{QualityBonus}$$
  Dette tal giver forbrugeren et direkte mål for "smag for pengene".
* **Læring 2 (Bekæmpelse af Point-inflation):** Hvis 30% af vinene får 95–100 point, mister skalaen sin differentierende kraft.
  * **Løsning:** Stram statistisk fordeling i pipeline: **Kun top ~3% af vine får $\ge 95$ point**. De fleste kvalitetsvine ligger i det realistiske 86–94 point felt. Det gør 95+ point til et eksklusivt og ægte trofæ.

---

## 4. 🤝 B2B FORHANDLER-INTEGRATION & UX ADSKILLELSE
* **Læring 1 (Højværdi Forhandler-Værktøjer):** Forhandlere vil gerne henvise til anmeldelser, hvis friktionen er nul:
  * **1-klik Citat-boks:** Skarp salgs-punchline (*"VibeWine (95 pts): Den ultimative fredagsvin..."*).
  * **1-klik Embed HTML:** Klar `<iframe ...>` widget til forhandlerens produktside.
  * **Printklart Flaske-Halsskilt:** CSS `@media print` 55×140 mm skilt direkte fra browseren med stiplede udklipslinjer.
* **Læring 2 (Stram UX-adskillelse):** B2B-værktøjer må **ikke** dominere den forbruger-rettede anmeldelse.
  * **Løsning:** B2B-værktøjerne placeres i en diskret, sammenklappelig `<details>` harmonika-sektion nederst på produktsiden samt på en dedikeret `/forhandlere` hub.

---

## 5. 🎨 FRONTEND DESIGN, LAYOUT & PERFORMANCE (ASTRO SSG)
* **Læring 1 (Paginering mod Kognitiv Belastning):** At vise 80+ vinkort på én gang skaber *Choice Paralysis* (beslutningslammelse) og efterlader et enormt tomt hul i skærmens venstre side ved siden af den kortere sticky sidebar.
  * **Løsning:** Startvisning på **16 vine** med en dynamisk `"Vis Flere Vine (X tilbage)"` knap, der udvider griddet efter behov.
* **Læring 2 (Progressive Enhancement for Scroll Animationer):** CSS `.reveal` elementer må ikke være skjulte (`opacity: 0`) uden at tjekke om JavaScript kører. Ellers bliver elementer usynlige i statiske builds, for søgemaskine-crawlere eller på headless screenshots.
  * **Løsning:** Brug `.js .reveal:not(.active)` styling og tilføj `js` classen dynamisk via inline script.
* **Læring 3 (Mikro-interaktioner):** JavaScript `alert()` popups opleves umoderne. Brug i stedet direkte knap-state ændringer (fx grøn `✓ Kopieret til udklipsholder!`) med 2-sekunders nulstilling.
* **Læring 4 (Konkrete Mad- & Anlednings-tags):** Vibe-kategorier styrkes ved at knytte 2 små ikon-tags til hvert vinkort (fx 🍣 *Sushi & Fisk*, ☀️ *Terrasseliv*, 🍕 *Pizza & Pasta*, 🥩 *Grillbøf*, 🍿 *Snacking*).

---

## 6. 🧪 TESTING & AUTOMATISERET DEPLOYMENT (CI/CD)
* **Læring 1 (Pytest for Pipeline-logik):** Datatransformationer, pris-kvotering og titel-rensning skal verificeres med isolerede unit-tests i `tests/python/test_pipeline.py`.
* **Læring 2 (Playwright E2E for Brugerrejser):** Kritiske stier (forside-søgemaskine, Hall of Fame, forhandler-hub, produktside, embed-widget) skal testes med Playwright E2E-tests.
  * *Note:* I sandboxed macOS-miljøer skal Playwright køre med `BypassSandbox: true` på grund af Chromium Mach port tilladelser.
* **Læring 3 (Pagefind Indeksering på Vercel):** Static site search med Pagefind genererer sit indeks under `dist/pagefind`. For at sikre at søgefunktionen fungerer efter deployment på Vercel, skal et bygge-skript kopiere Pagefind-filerne til `.vercel/output/static/pagefind`.

---

## 📜 SAMMENFATTENDE TJEKLISTE TIL FREMTIDIGE PROJEKTER
1. ✅ **Rens altid scraped master-data** for priser, enheder og avis-støj før visning.
2. ✅ **Brug aldrig `alert()`** – anvend inline UI state-changes til kopi-handlinger.
3. ✅ **Begræns kataloger til 12-16 visninger ad gangen** med "Vis flere" for at bevare layout-symmetri.
4. ✅ **Hold B2B-funktioner adskilt** fra forbrugerindhold via `<details>` eller dedikerede sider.
5. ✅ **Verificer altid visuelt** med screenshots og kør 100% grønne E2E & Pytest testsuites før Git Push.
