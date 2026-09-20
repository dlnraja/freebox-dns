# Site GitHub Pages — freebox-dns

Ce dossier (`site/`) est la **racine publiée** du site statique de documentation.

## Publication

Dans **Settings → Pages** du dépôt GitHub :

- **Source** : Deploy from a branch
- **Branch** : `main` (ou votre branche par défaut)
- **Folder** : `/site`

URL projet : [https://dlnraja.github.io/freebox-dns/](https://dlnraja.github.io/freebox-dns/)

## Structure

| Chemin | Rôle |
| --- | --- |
| `index.html` | Accueil (FR + sous-titre EN) |
| `credits.html` | Crédits et sources tierces |
| `guides/*.html` | Guides illustrés |
| `assets/style.css` | Styles (teal / coral) |
| `assets/site.js` | Navigation mobile + Mermaid |
| `assets/*.svg` | Illustrations |

## Prévisualisation locale

Ouvrir `index.html` dans un navigateur, ou servir le dossier :

```bash
cd site
python3 -m http.server 8080
# → http://localhost:8080/
```

Les liens relatifs (`../assets/…`, `guides/…`) fonctionnent en local et sur GitHub Pages (base `/freebox-dns/`).

## Contenu source

Les guides reprennent les thèmes de `docs/*.md` du dépôt. Pour la version Markdown complète, voir le dépôt GitHub.
