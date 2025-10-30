import sys, time, json

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <some text>")
        sys.exit(1)

    arg = sys.argv[1]
    print(f"Got argument: {arg}")

    # simulate work
    time.sleep(5)

    print(json.dumps({"result": "done", "arg": arg}, indent=2))

if __name__ == "__main__":
    main()