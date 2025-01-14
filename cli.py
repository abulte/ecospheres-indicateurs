import os

from pathlib import Path

import commentjson
import requests
import yaml

from minicli import cli, run
from slugify import slugify


@cli
def fixtures(env: str = "demo", org_slug: str = "ecospheres-indicateurs-test"):
    base_url = f"https://{env}.data.gouv.fr/api"

    # organization
    r = requests.get(f"{base_url}/1/organizations/{org_slug}/")
    r.raise_for_status()
    org_id = r.json()["id"]

    # datasets
    with open("fixtures.yml") as f:
        datasets = yaml.safe_load(f)["datasets"]

    for dataset in datasets:
        data = {
            "organization": org_id,
            "title": dataset["title"],
            "description": dataset["description"],
            "tags": dataset["tags"],
            "resources": [
                {
                    "title": f"Ressource d'exemple pour {dataset['title']!r}",
                    "url": "https://example.com/data.csv",
                }
            ],
            "temporal_coverage": {
                "start": "2022-01-01",
                "end": "2024-12-31",
            }
        }
        if extras_path := dataset.get("extras"):
            with open(extras_path) as f:
                data.update(commentjson.loads(f.read()))
        if not dataset.get("id"):
            r = requests.post(
                f"{base_url}/1/datasets/",
                json=data,
                headers={"x-api-key": os.environ["DATAGOUVFR_API_KEY"]},
            )
            r.raise_for_status()
            print(f"Created dataset for {dataset['title']!r} @ {r.json()['id']}")
        else:
            r = requests.put(
                f"{base_url}/1/datasets/{dataset['id']}/",
                json=data,
                headers={"x-api-key": os.environ["DATAGOUVFR_API_KEY"]},
            )
            r.raise_for_status()
            print(f"Updated existing dataset: {dataset['id']}")


@cli
def slugify_filters(
    input_file: Path = Path('filters/filters.yml'),
    output_file: Path = Path('filters/filters-slugified.yml'),
):
    with open(input_file, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)

    for filter_item in data['indicators']['filters']:
        if 'values' in filter_item:
            for value in filter_item['values']:
                if 'id' in value:
                    value['id'] = slugify(value['id'])

    with open(output_file, 'w', encoding='utf-8') as file:
        yaml.dump(data, file, allow_unicode=True, sort_keys=False)


if __name__ == "__main__":
    run()
