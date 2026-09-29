# measyjson

A small Python library to make storing and manipulating JSON data easier.

## Installation

```bash
python -m pip install measyjson
```

Le paquet s'installe sous le nom `measyjson`, mais le module s'importe toujours
sous le nom `easyjson`.

## Installation depuis les sources

```bash
python -m pip install -e .
```

## Usage

`write` ecrit du contenu brut dans un fichier, `write_add` ajoute une cle a un objet JSON
existant, `append` pousse un element dans une liste JSON.

```python
import easyjson
from easyjson import core

chemin = "comptes.json"

easyjson.write(chemin, '{"Account": {"user": "sionukk", "password": "secret"}}')
core.write_add(chemin, "ville", "Nimes")

easyjson.write(chemin, '["Nimes", "Lyon"]')
core.append(chemin, "Marseille")
```

`write_add` attend un objet JSON et `append` attend une liste JSON.

## Tests

```bash
python -m unittest discover -s tests -v
```

or, with [uv](https://docs.astral.sh/uv/):

```bash
uv run pytest
```

Voir [docs/index.html](docs/index.html) pour le guide d'ecriture des tests.

## License

MIT
