import json


def main(input_string: str) -> dict:
    """
    Takes a string as input and returns a JSON response.

    Args:
        input_string: The input string to process

    Returns:
        A dictionary with the input and additional fields
    """
    result = {
        "input": input_string,
        "version": "1.0"
    }
    return result


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        input_text = " ".join(sys.argv[1:])
        result = main(input_text)
        print(json.dumps(result))
    else:
        print("Usage: python main.py <string>")
        sys.exit(1)
