# Oppgaver til kandidater

## Oppgave X - Vulns in Worm || Worms in Vulns

Lag et program som finner sårbare pakker i debian bookworm ved hjelp av Open Source Vulnerabilities sin
database (https://osv.dev). For å snevre inn antall pakker noe er det ønskelig å kun undersøke
[main pakke listen for amd64](http://http.us.debian.org/debian/dists/bookworm/main/binary-amd64/Packages.gz),
en kopi av denne filen finnes i dette repositoryet med navn `Packages` i mappen `ressurser/oppgavex`.
Ønsket output fra programmet er en oversikt over alle sårbare pakker funnet med annen nødvendig infromasjon
for å kunne gjøre videre undersøkelser av sårbarheten.

### Eksterne avhengigheter

- Pakkeliste for debian bookworm amd64 main http://http.us.debian.org/debian/dists/bookworm/main/binary-amd64/Packages.gz
- Sårbarhetsinformasjon fra https://osv.dev

## Oppgave X+1 - Log, Stock and Two Smoking Parsers

I denne oppgaven er målet å prosessere og lagre nettverkslogger på en effektiv måte.

### (X+1)^1

Gitt nettverksloggene i `ressurser/oppgavex+1` lag et program som
normaliser loggene slik at man kan gjøre søk på tvers av miljø og loggtype.
Hvilke felter som beholdes og ikke for de normaliserte loggene er opp til
kandidaten selv. Her gjelder det å finne et krysningspunkt mellom
størrelse på de normaliserte loggene og nødvendig informasjon for
å kunne gjøre undersøkelser ved hjelp av loggene.
Under er et eksempel på en normalisert logg:

```json
{
  "timestamp": 1730982417,
  "src_ip": "10.32.12.2",
  "dst_ip": "10.120.49.83",
  "src_port": 34657,
  "dst_port": 53,
  "vlan": 12,
  "source": "azure_nsg"
}
```

#### Loggfil forklaring

Filene ligger under i mappen `ressurser/oppgavex+1`.

- `azure_nsg_flows.log` inneholder logger basert på [Azure flow logger](https://learn.microsoft.com/en-us/azure/network-watcher/nsg-flow-logs-overview).
- `corelight.log` inneholder logger basert på [Corelight](https://github.com/corelight/zeek-cheatsheets/blob/master/Corelight-Zeek-Cheatsheets-3.0.4.pdf).
- `tcpdump.log` inneholder [tcpdump logger](https://www.tcpdump.org) fanget på MacOS.

### (X+1)^2

Lag en PostgreSQL database tabell for å holde disse normaliserte loggene. Fokus på effektiv lagring
og gode søkemuligheter vektlegges i denne oppgave. Ønsket svarform på denne oppgaven er en
PostgreSQL `CREATE TABLE` sql-spørring.

## Oppgave X+2 - A Walk In The Graf!

Lag et program som kan lese strukturert data fra en `nodefil`. Programmet skal tolke innholdet i filen som noder i en urettet [graf](https://no.wikipedia.org/wiki/Grafteori). Formålet med programmet er å finne alle gyldige stier i grafen mellom alle ikke navngitte noder.

- Hver `node` inneholder følgende data:
  - `Navn`: streng // Noder finnes i tre utgaver - Noden(e) uten navn "", Noden(e) som heter "S" og Noden(e) som heter "R"
  - `UnikID`: heltall // Du kan anta at denne alltid er et unikt heltall og strekker seg fra og med 0 til og med 10,000.
  - `Naboer`: sortert array med `UnikID` // Den er alltid sortert eller tom.
    - ""-nodene har maksimalt en nabo av typen "R" eller "S".
    - Både "R"-nodene og "S"-nodene kan ha opptil 256 naboer.
  - `Samlepost`: streng // ""-nodene har en RFC1918 IP-adresse med [subnet mask](https://en.wikipedia.org/wiki/Subnet) /32
    - "S"-nodene bør ha en tallverdi fra og med "2" til og med "4096"
    - "R"-nodene inneholder en gyldig RFC1918 CIDR-range med /20, /21 eller /22 subnet mask.
  - `Kant`: array med heltall indeksert 1:1 med `Naboer`. //Heltall i `Kant[1]` viser altså til kanten mellom den aktuelle noden og noden i
    `Naboer[1]`. Verdien finnes ikke i `nodefil` når filen leses inn. Brukere skal kunne legge til en verdi fra "-100" til "+100" for å vekte
    naboskapet mellom hver node.
    - Har brukeren vektet deler eller hele grafen skal alle gyldige stier sorteres etter vekt.
    - Er vekten mellom stiene lik må programmet sortere stiene entydig.
    - For kanter med udefinerte vekter, anta at vekten er "0".
- En `nodefil` inneholder maksimalt 10,000 noder som er sortert på deres `UnikID`.
  - Programmet skal fungere for en hver `nodefil` som følger beskrivelsen til oppgaven. Det er derfor ikke vedlagt noen fil.
  - Nodene i en `nodefil` kan inngå i en graf.
  - Forskjellige noder kan danne ulike grafer i samme `nodefil`.
- Programmet bør loggføre en passende feilmelding dersom:
  - ""-nodene er nabo med en annen ""-node.
  - Arrayen med naboer inneholder noden sin egne `UnikID` (nabo med seg selv).
  - Dersom "S"-nodene sin `Samlepost` har verdien "1".
  - Dersom det ikke finnes noe gyldig sti.
  - Andre finurligheter som kan være av verdi.
- Stien i grafen er gyldig:
  - Så fremt ingen noder besøkes to ganger i samme sti.
  - Så fremt stien startes på en ""-node, avsluttes på en ""-node og maksimalt inneholder to ""-noder.
  - Fra en hver ""-node til alle "S"-noder og til alle "R"-noder hvor CIDR-rangen i `Samlepost` ikke overlapper hverandre.
  - Fra en hver "S"-node til alle noder, foruten andre "S"-noder med ulik tallverdi i `Samlepost`.
  - Fra en hver "R"-node til alle noder, så fremt ingen nåværende eller fremtdig ""-node i stien ikke overlapper CIDR-rangen til "R"-noden.

Eksempel på innhold i fil:

```
"Navn": "",   "UnikID": 0,    "Naboer": ["2"],            "Samlepost": "10.10.0.34/32"
"Navn": "S",  "UnikID": 1,    "Naboer": ["2", "5"],       "Samlepost": "341"
"Navn": "R",  "UnikID": 2,    "Naboer": ["0", "1", "4"],  "Samlepost": "10.12.0.0/22"
"Navn": "",   "UnikID": 3,    "Naboer": [],               "Samlepost": "10.12.3.211/32"
"Navn": "",   "UnikID": 4,    "Naboer": ["2", "5"],       "Samlepost": "192.168.3.10/32"
"Navn": "S",  "UnikID": 5,    "Naboer": ["1", "4"],       "Samlepost": "2052"
```

- I dette tilfellet finnes det en gyldig sti fra `Unikid`:0 til `UnikID`:4
  - "0->2->4" er en gyldig sti og "4->2->0" anses som den samme stien.
  - `UnikID`:3 har ingen `Naboer` og er derfor ikke koblet til grafen.
  - Selv om "S"-nodene er koblet sammen tillates ikke stiene det skaper, da deres `Samlepost` er ulike. Hadde det vært minst en "R"-node i mellom disse "S"-nodene ville stien også vært tillat.
- Dersom filen istedenfor inneholdt en ""-node med `UnikID`:6 som var nabo med "S"-noden med `UnikID`:1
  - Ville grafen hatt tre gyldige stier "0->2->4", "0->2->1->6" og "6->1->2->4".
  - Er `Samlepost` på `UnikID`:6 eksmpelvis 10.13.0.2/32 er den i rangen til "R"-noden med `UnikID`:2. I dette tilfellet er de to nye stiene ugyldige.
