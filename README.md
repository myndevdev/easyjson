# measyjson

A small Python library to make storing and manipulating JSON data easier.

Python 3.9 et superieur. Aucune dependance a l'installation.

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

```python
import easyjson
from easyjson import core

chemin = "comptes.json"
```

`write`, `append`, `write_add` et `base_json` sont exportes par `easyjson`.
`read_chaine` et `delete` ne le sont pas, ils s'importent via `easyjson.core`.

### write

Ecrit du contenu brut dans un fichier, en ecrasant l'existant. Aucune validation
JSON, le contenu est ecrit tel quel.

```python
easyjson.write(chemin, '{"Account": {"user": "sionukk", "password": "secret"}}')
```

Retourne `(chemin, contenu)`.

### write_add

Ajoute une cle a un objet JSON existant. La valeur passe par une f-string, elle est
donc toujours stockee comme du texte.

```python
core.write_add(chemin, "ville", "Nimes")
```

Une cle deja presente n'est **pas** remplacee. Le deuxieme element du retour indique
si l'ecriture a eu lieu.

```python
easyjson.write(chemin, "{}")

core.write_add(chemin, "ville", "Nimes")   # (chemin, True,  "Nimes")
core.write_add(chemin, "ville", "Lyon")    # (chemin, False, "Lyon"), le fichier garde "Nimes"
```

Avec une cle vide, la fonction ne fait rien et renvoie `(chemin, "", contenu)`, un
tuple de forme differente des deux chemins ci-dessus.

### append

Pousse un element a la fin d'une liste JSON, puis reecrit le fichier avec une
indentation de 4 espaces.

```python
easyjson.write(chemin, '["Nimes", "Lyon"]')
core.append(chemin, "Marseille")          # ["Nimes", "Lyon", "Marseille"]
```

Le type de la valeur ajoutee est conserve tel quel.

### read_chaine

Retourne la valeur stockee sous une cle, sans modifier le fichier. La fonction
**imprime aussi** la valeur sur la sortie standard.

```python
core.read_chaine(chemin, "ville")          # "Nimes"
```

Le type stocke est conserve : un nombre reste un nombre, une liste reste une liste.

### delete

Supprime une cle d'un objet JSON. Si la cle etait la derniere, le fichier reste
present avec un objet vide `{}`.

```python
core.delete(chemin, "ville")               # (chemin, "ville")
```

Une cle absente leve `KeyError` **avant** l'ouverture du fichier en ecriture, le
fichier n'est donc pas touche.

### base_json

Cree un squelette de compte et vise `data.json` dans le repertoire courant.

```python
data = easyjson.base_json()
# {"Account": {"user": "username", "password": "password"}}
```

Le dict est serialise avec `json.dump(data, f, indent=4)`, donc `data.json` recoit du
JSON valide. La fonction retourne le dict ecrit. Elle leve `OSError` si le repertoire
courant n'est pas inscriptible.

## Exceptions

| Fonction | Condition | Exception |
| --- | --- | --- |
| `write` | dossier inexistant | `OSError` |
| `append` | fichier inexistant | `OSError` |
| `append` | JSON invalide | `json.JSONDecodeError` |
| `append` | JSON pas une liste | `AttributeError` |
| `write_add` | dossier inexistant | `OSError` |
| `write_add` | JSON invalide | `json.JSONDecodeError` |
| `write_add` | JSON pas un objet | `TypeError` |
| `write_add` | cle vide | aucune, no-op |
| `read_chaine` | dossier inexistant | `OSError` |
| `read_chaine` | JSON invalide | `json.JSONDecodeError` |
| `read_chaine` | cle absente | `KeyError` |
| `read_chaine` | JSON pas un objet | `TypeError` |
| `delete` | dossier inexistant | `OSError` |
| `delete` | JSON invalide | `json.JSONDecodeError` |
| `delete` | cle absente | `KeyError` |
| `delete` | JSON pas un objet | `TypeError` |
| `base_json` | repertoire non inscriptible | `OSError` |

`json.JSONDecodeError` herite de `ValueError`. Les blocs `except` de `write`,
`append`, `read_chaine` et `delete` attrapent `ValueError`, donc aussi une erreur de
decodage.

## Tests

```bash
python -m unittest discover -s tests -v
```

or, with [uv](https://docs.astral.sh/uv/):

```bash
uv run pytest
```

Lint et annotations:

```bash
uv run ruff check .
uv run mypy
```

Le CI lance les tests de Python 3.9 a 3.13, et `ruff` et `mypy` sur 3.13 uniquement,
`mypy` exigeant 3.10 minimum.

Voir [docs/index.html](docs/index.html) pour le guide d'ecriture des tests.

## License

MIT
