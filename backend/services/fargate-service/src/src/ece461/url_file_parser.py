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

