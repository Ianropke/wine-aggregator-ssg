# ⚖️ VibeWine — Juridisk Dokumentationspakke & Compliance Review

Dette dokument indeholder en **komplet juridisk og datamæssig redegørelse** for platformen **VibeWine** (`vibewine.dk`). Dokumentet er udarbejdet, så det direkte kan sendes til review hos ChatGPT (eller en jurist/advokat) for at få en vurdering af lovligheden ved at lancere hjemmesiden.

---

## 📌 1. Baggrund & Formål

- **Projekt:** VibeWine er en uafhængig vin-aggregator og anmeldelsesplatform.
- **Aktuel status:** Non-profit / hobby-projekt.
- **Fremtidig plan:** Mulig kommerciel profilering (f.eks. B2B badge-licensering, affiliate-links eller PR-samarbejde).
- **Kernefunktionalitet:** Platformen indsamler offentligt tilgængelige produktoplysninger (vinnavn, forhandler, pris, årgang, region) via web-scraping/API'er, genererer uafhængige vurderinger (Vibe Score 80–100 og Vibe Value Badges), og henviser forbrugeren til forhandleren via direkte links.

---

## 🔍 2. Dataindsamling & Web-Scraping (Ophavsret & EU-ret)

### 2.1 Hvilke data indsamles?
Via automatiserede scripts indsamles udelukkende **objektive faktuelle oplysninger**:
1. Produktnavn (f.eks. *"Baron de Ley Reserva"*)
2. Årgang (f.eks. `2020`)
3. Forhandlernavn (f.eks. *"SuperBrugsen"*, *"Bordershop"*)
4. Pris per flaske (f.eks. `120 kr.`)
5. Produktside-URL (f.eks. `https://...`)

### 2.2 Relevante juridiske forhold & vurderingspunkter:

- **Rå fakta og priser:** Efter dansk ophavsret (Ophavsretsloven § 1) er rå fakta, priser og produktnavne **ikke ophavsretligt beskyttede**, da de mangler værkshøjde.
- **Katalogreglen (Ophavsretsloven § 71) / Databaseret:** Beskytter fremstilling af større databaser mod væsentlig udnyttelse. VibeWine kopierer ikke hele forhandlerens database-struktur, men udtager udelukkende enkelte offentlige priser mhp. sammenligning.
- **EU DSM-direktivet (Direktiv 2019/790, Art. 3 & 4):** Tillader Text and Data Mining (TDM) af lovligt tilgængeligt indhold, medmindre rettighedshaver udtrykkeligt har taget forbehold herfor i maskinlæsbar form (`opt-out`).
- **Robots.txt & Vilkår:** Scraperne overholder rimelige req-limits og blokerer ikke forhandlerens servere.

---

## 📝 3. Tekst, Indhold & Billeder (Egenproduktion vs. Kopiering)

### 3.1 Tekst og Anmeldelser
- **Ingen kopiering af salgstekster:** VibeWine kopierer **ALDRIG** forhandlernes eller vinhusenes salgstekster, smagsnoter eller beskrivelser.
- **100% Egenproduktion / AI:** Alle Vibe Scores, anmeldelsestekster ("Vibe-drips"), pro/con-lister og madparringer genereres 100% uafhængigt af VibeWine via egne algoritmer og LLM-prompts.

### 3.2 Billeder og Visuals
- **Ingen uautoriseret brug af produktbilleder:** VibeWine benytter **IKKE** forhandlernes ophavsretligt beskyttede produktbilleder uden aftale.
- **Grafisk profil:** Der benyttes udelukkende egne genererede badge-ikoner (*VIBE STEAL*, *SWEET SPOT*, *FAIR DEAL*, *PRESTIGE PICK*), geometriske UI-elementer og egenproduceret grafik.

---

## 🏷️ 4. Varemærkeret & "Nominative Fair Use"

### 4.1 Brug af Brand- & Forhandlernavne
VibeWine nævner specifikke vinhuse (f.eks. *"Château Suduiraut"*, *"Fantini"*) og forhandlere (f.eks. *"Bordershop"*, *"Bilka"*).

### 4.2 Relevante juridiske forhold:
- **Nominativ Fair Use (Varemærkeloven § 14, stk. 1, nr. 3):** Det er fuldt lovligt at benytte en tredjeparts varemærke eller firmanavn, i det omfang det er **nødvendigt for at identificere eller henvise til det pågældende produkt eller den pågældende forhandler**, forudsat at det sker i overensstemmelse med god markedsføringsskik.
- **Ingen Vildledning:** VibeWine udgiver sig **IKKE** for at være officiel repræsentant eller partner for vinhusene eller forhandlerne (medmindre eksplicit aftalt). Der fremgår tydelig disclaimer om uafhængighed i footeren.

---

## 🛒 5. Markedsføringsloven & Sammenlignende Reklame

### 5.1 Prissammenligning & Forbrugeroplysning
- **Markedsføringslovens § 13 (Sammenlignende reklame):** Det er tilladt at sammenligne priser og produkter, så længe sammenligningen:
  1. Ikke er vildledende.
  2. Sammenligner produkter, der opfylder samme behov.
  3. Er objektiv og kan dokumenteres (faktiske scrapede priser).
  4. Ikke virker vanærende eller nedsættende for konkurrenters varemærker.

### 5.2 Gennemskuelighed og Disclaimers
- Hjemmesiden oplyser altid den scrapede pris og linket direkte til forhandleren.
- Hvis et link i fremtiden indeholder affiliate-kodning, vil det blive eksplicit markeret som **"Reklamelink / Affiliate"** jf. Forbrugerombudsmandens retningslinjer for skjult reklame.

---

## 🔒 6. GDPR & Databeskyttelse

- **Ingen Personoplysninger (PII):** VibeWine indsamler eller opbevarer **INGEN** personoplysninger om forbrugerne.
- **Ingen Brugeroprettelse:** Der er intet login-system eller oprettelse af brugerprofiler.
- **Anonym Analytics:** Der benyttes cookieless / anonymiseret basistrafik-måling uden sporing på tværs af domæner.

---

## 🔄 7. Overgang fra Non-Profit til Kommerciel Drift

| Fase | Nuværende Status (Non-Profit) | Fremtidig Plan (Kommerciel Profil) | Juridiske Krav ved Overgang |
|---|---|---|---|
| **Formål** | Uafhængigt hobby-medie & forbrugeroplysning | Kommerciel B2B-licensering & affiliate-indtægter | Oprettelse af CVR-nummer, momsregistrering, regnskabspligt. |
| **Markedsføring** | Ingen annoncer | Affiliate-links eller forhandler-badges | Tydelig reklame-markering ("Reklame/Affiliate") jf. MFL § 6. |
| **B2B Værktøjer** | Gratis badges og halsskilte til forhandlere | Betalt premium B2B-widget eller VIP-features | Skriftlige B2B-betingelser og licensaftaler. |

---

## ❓ 8. Spørgsmål til ChatGPT (Juridisk Reviewer)

Når du gennemgår denne redegørelse, bedes du besvare følgende 6 specifikke spørgsmål:

1. **Lovlighed af scraping:** Er indsamlingen af offentligt tilgængelige produktnavne, priser og forhandler-URL'er fra danske webshops fuldt lovlig efter dansk ophavsret (§ 71) og EU's DSM-direktiv?
2. **Brug af varemærker (Nominativ fair use):** Er vores brug af vin- og forhandlernavne i anmeldelser og prisangivelser fuldt forsvarlig efter Varemærkelovens § 14?
3. **Prissammenligning & Markedsføringslov:** Er der specifikke faldgruber i Markedsføringslovens § 13 (sammenlignende reklame), som vi skal være opmærksomme på, når vi viser forhandlerens pris ved siden af vores Vibe Score?
4. **Billed- og Tekst-rettigheder:** Da vi skriver 100% egne AI/redaktionelle tekster og benytter egne badge-illustrationer (ingen forhandler-fotos), er vi så 100% fri af ophavsretlige krav fra forhandlerne?
5. **Overgang til kommerciel drift:** Hvilke specifikke juridiske forholdsregler (mærkning af affiliate-links, CVR, disclaimers) skal vi implementere den dag, platformen går fra non-profit til kommerciel?
6. **Samlet konklusion & risikovurdering:** Hvad er den samlede juridiske risikoprofil for at udgive VibeWine på en skala fra 1–10 (hvor 1 er lav risiko), og hvad er dine vigtigste anbefalinger?
