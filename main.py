import json

import os
import sys
import requests
from github import Github

import pycountry
from urllib.parse import urlencode


def get_country_json(nameOrAlpha: str):
    country = pycountry.lookup(nameOrAlpha)

    countryCode = country.alpha_3

    re = requests.get(
        'https://geodata.ucdavis.edu'
        f'/gadm/gadm4.1/json/gadm41_{countryCode}_0.json'
    )

    if re.status_code != 200:
        sys.exit(5)

    text = re.text

    # the API provides ready prepare data for geoJSON
    open(f'data/{country.alpha_3}.json', 'w').write(text)

    return text


def parse_issue_country(title: str):
    """Parse issue title and return a tuple with (action, <move>)"""
    if title.startswith('locate: '):
        return title[8:]


def main(issue):
    country_name = parse_issue_country(issue.title)

    geojson = get_country_json(country_name)

    insert_json(geojson)


def insert_json(text: str):
    with open('./README.md') as file:
        readme = file.read()
    readme = replace_text_between(readme, 'geoJSON', text)

    table = '|couyntry|link|'
    for country in pycountry.countries:
        issue_link = create_issue_link(country.name)
        table += f'\n|{country.name}|{issue_link}'

    readme = replace_text_between(readme, 'countryList', table)

    with open('README.md', 'w') as file:
        file.write(readme)

# # # # from the1Riddle/Play-Chess


def create_issue_link(country):
    return "https://github.com/{repo}/issues/new?{params}".format(
        repo=os.environ["GITHUB_REPOSITORY"],
        params=urlencode({
            'title': f'locate: {country}',
            'body': 'Do not touch anything just submit the issue',
        }, safe="{}")
    )


def replace_text_between(original_text, markerName, replacement_text):
    """Replace text between `marker['begin']` and `marker['end']`
    with `replacement`"""
    begin = f'<!-- BEGIN {markerName} -->'
    end = f'<!-- END {markerName} -->'

    if original_text.find(begin) == -1 or original_text.find(end) == -1:
        return original_text

    leading_text = original_text.split(begin)[0]
    trailing_text = original_text.split(end)[1]

    return leading_text + begin + replacement_text + end + trailing_text


if __name__ == '__main__':
    repo = Github(
        os.environ['GITHUB_TOKEN']
    ).get_repo(os.environ['GITHUB_REPOSITORY'])
    issue = repo.get_issue(number=int(os.environ['ISSUE_NUMBER']))
    issue_author = '@' + issue.user.login
    repo_owner = '@' + os.environ['REPOSITORY_OWNER']

    ret, reason = main(issue)
