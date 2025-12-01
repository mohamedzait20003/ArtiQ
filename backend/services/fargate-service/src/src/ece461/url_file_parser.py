from typing import List, Optional
import validators, logging, os, sys

class ModelLinks:
    def __init__(self, model: str, dataset: Optional[str] = None, code: Optional[str] = None, model_id: str = "") -> None:
        self.model = model
        self.dataset = dataset
        self.code = code
        self.model_id = model_id

def parse_urls(urls: str) -> List[ModelLinks]:
    links: List[ModelLinks] = []
    
    lines = [urls]

    for line in lines:
        stuff: List[str] = line.strip().split(",")
        if len(stuff) != 3:
            raise IndexError

        code, dataset, model = line.strip().split(",")

        if not model:
            logging.exception("Error: model link not found")
            raise ValueError("Model link is required")
        else:
            validators.url(model)

        if code:
            validators.url(code)

        if dataset:
            validators.url(dataset)

        spl: List[str] = model.split(".co/")[1].split("/")
        model_id: str = spl[0] + "/" + spl[1]
        links.append(ModelLinks(model, dataset if dataset else None, code if code else None, model_id))

    return links


def parse_url_file(path: str) -> List[ModelLinks]:
    """Read CSV-like file (code,dataset,model) and return list of ModelLinks.

    Exits with status 1 when the file does not exist or when a required
    field is missing (tests expect SystemExit for those cases).
    """
    if not os.path.exists(path):
        logging.error("URL file not found: %s", path)
        sys.exit(1)

    links: List[ModelLinks] = []
    with open(path, "r", encoding="utf-8") as f:
        for ln in f:
            line = ln.rstrip("\n")
            if not line.strip():
                continue
            parts = line.split(",")
            if len(parts) != 3:
                raise IndexError
            code, dataset, model = parts

            if not model:
                logging.exception("Error: model link not found")
                sys.exit(1)

            # Validate URLs where present (tests monkeypatch validators.url)
            validators.url(model)
            if code:
                validators.url(code)
            if dataset:
                validators.url(dataset)

            # Extract model_id from huggingface style URL
            try:
                spl = model.split(".co/")[1].split("/")
                model_id = spl[0] + "/" + spl[1]
            except Exception:
                # Let upstream tests catch malformed model strings as IndexError
                raise

            links.append(ModelLinks(model, dataset if dataset else None, code if code else None, model_id))

    return links

