# Modèle de filtrage (lexique pins → local)

Voir le glossaire complet : [dns-lexicon.md](dns-lexicon.md).

## dns-libre — bit `uncensored`

Inspiré de **UncensoredDNS** (#1), **Digitale Gesellschaft** (#2), **Quad9 Unsecured** (#3).

- Pas de blocklists (*keine Sperrlisten*).
- Amonts DoT non censeurs ; réponses *unblocked* (esprit Quad9 `9.9.9.10`, pas `9.9.9.9`).
- Objectif : éviter les « DNS menteurs » opérateur / politiques (*censurfri*).

## dns-secure — bit `threat-local`

Inspiré du **toolkit** NextDNS (#4) : *denylist*, *threat model*, *ads & trackers*, dual *configuration* — **sans** cloud ni contrôle parental.

Listes **uniquement** :

- publicité / trackers
- malware / phishing

**Exclu volontairement** (lexique NextDNS qu’on refuse) : parental, porn blocks, SafeSearch, censure nationale, logs cloud.

Le malware n’est **pas** délégué à Quad9 Secured distant : le filtre vit **ici** (Blocky), comme un Pi-hole local plutôt qu’un « Pi-hole in the cloud ».

Sources typiques (rafraîchies par Blocky + CI) : StevenBlack hosts, AdAway, URLhaus, Spam404.
