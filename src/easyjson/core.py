import json
from typing import Any


def write(file, contenue) -> tuple[str, str]:
    """Write raw text to a file, overwriting any existing content.

    No JSON validation happens here, the content is written as received.
    Returns the (file, contenue) pair.
    """
    try:
        with open(file, "w", encoding="utf-8") as f:
            f.write(contenue)
    except (ValueError, Exception, OSError) as e:
        print(f"Error {e}")
        raise
    return (file, contenue)


def append(file, contenue) -> tuple[str, Any]:

    """
        Just Try open and read file

        And Append in file

        if valueError -> Raise

        Else Add contenue in file
    """

    try:
        with open(file, encoding="utf-8") as f:
            data = json.load(f)

        data.append(contenue)

        with open(file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except (ValueError, OSError) as e:
        print(f"Error {e}")
        raise
    return (file, contenue)


def write_add(file, chaine, contenue) -> tuple[str, bool, Any]:
    """Add the key chaine with the value contenue to an existing JSON object.

    The value goes through an f-string, so it is always stored as text.
    Nothing is ever removed: if chaine already exists, the value is appended
    to a list, so the first call stores a scalar and later calls grow a list.
    Returns the (file, added, contenue) tuple.
    """
    try:
        if len(chaine) > 0:
            with open(file, encoding="utf-8") as f:
                data = json.load(f)

            if chaine in data:
                current = data[chaine]
                if not isinstance(current, list):
                    current = [current]
                if f"{contenue}" not in current:
                    current.append(f"{contenue}")
                data[chaine] = current
            else:
                data[chaine] = f"{contenue}"

            with open(file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            return file, True, contenue

    except (FileNotFoundError, json.JSONDecodeError):
        raise

    return (file, False, contenue)


def read_chaine(file, chaine):
    try:
        with open(file, encoding="utf-8") as f:
            data = json.load(f)
        print(data[chaine])

    except (ValueError, OSError) as e:
        print(f"Error {e}")
        # if want d'ont stop code use return actualy beta else use raise
        # return ""
        raise

    return data[chaine]

def delete(file, chaine) -> tuple[str, str]:
    """Remove the key chaine from an existing JSON object.

    A missing key raises KeyError before the file is reopened for writing,
    so the file stays intact. Removing the last key leaves an empty object.
    Returns the (file, chaine) pair.
    """
    try:
        with open(file, encoding="utf-8") as f:
            data = json.load(f)

        del data[chaine]

        with open(file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except (ValueError, OSError) as e:
        print(f"Error {e}")
        raise

    return (file, chaine)

def base_json() -> dict[str, dict[str, str]]:
    """Build an account skeleton and target data.json in the current directory.

    The object is serialised with json.dump, so data.json receives valid JSON.
    Returns the dict that was written.
    """
    try:
        data = {
            "Account": {
                "user": "username",
                "password": "password"
            }
        }

        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    except (Exception, OSError) as e:
        print(f"Error {e}")
        raise

    return data
