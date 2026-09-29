import json

def write(file, contenue) -> str:
    """Write raw text to a file, overwriting any existing content.

    No JSON validation happens here, the content is written as received.
    Returns the (file, contenue) pair.
    """
    try:
        with open(file, "w", encoding="utf-8") as f:
            f.write(contenue)
    except ValueError as e:
        print(f"Error {e}")
        raise
    return (file, contenue)

def append(file, contenue) -> { str,  bool,  float }:

    """
        Just Try open and read file

        And Append in file

        if valueError -> Raise

        Else Add contenue in file
    """

    try:
        with open(file, "r") as f:
            data = json.load(f)

        data.append(contenue)

        with open(file, "w") as f:
            json.dump(data, f, indent=4)
    except ValueError as e:
        print("Error {e}")
        raise
    return (file, contenue)


def write_add(file, chaine, contenue) -> { str, bool, float }:
    """Add the key chaine with the value contenue to an existing JSON object.

    The value goes through an f-string, so it is always stored as text.
    An existing key is replaced, not merged.
    Returns the (file, chaine, contenue) tuple.
    """
    try:
        if len(chaine) > 0:
            """
            Read File for Add in file...
            """
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)

            data[f"{chaine}"] = f"{contenue}"

            with open(file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        else:
            """
                If chaine > 0  use append()

                Else using write_add()
            """
            # Known bug: append is called with no argument, which raises a
            # TypeError. It should be append(file, contenue).
            append()

    except ValueError as e:
        print(f"Error : {e}")
        raise

    return (file, chaine, contenue)


def base_json() -> { str }:
    """Build an account skeleton and target data.json in the current directory.

    Known bug: f.write expects a string while data is a dict, so this call
    always raises a TypeError. It should be json.dump(data, f, indent=4).
    """
    try:
        data = {
            "Account": {
                "user": "username",
                "password": "password"
            }
        }

        with open("data.json", "w", encoding="utf-8") as f:
            f.write(data)

    except Exception as e:
        print(f"Error {e}")
        raise

    return data
