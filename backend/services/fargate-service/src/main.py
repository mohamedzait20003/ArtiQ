def main(input_string: str) -> str:
    """
    Takes a string as input and returns it back.
    
    Args:
        input_string: The input string to echo back
        
    Returns:
        The same string that was provided as input
    """
    return input_string


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        input_text = " ".join(sys.argv[1:])
        result = main(input_text)
        print(result)
    else:
        print("Usage: python main.py <string>")
        sys.exit(1)
