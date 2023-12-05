from http import HTTPStatus
from pathlib import Path
from typing import Callable

import httpretty
import pytest
import requests
from pytest import MonkeyPatch

from catalog_searcher.search import SearchError
from catalog_searcher.search.alma import AlmaSearch


@httpretty.activate
def test_alma_search(shared_datadir: Path, register_search_url: Callable, alma_search: AlmaSearch):
    register_search_url(body=(shared_datadir / 'alma_response.xml').read_text())

    response = alma_search()

    assert response.total == 108
    assert len(response.results) == 3
    assert response.results[0].title == (
        'Advances in the theory of Riemann surfaces: proceedings of the 1969 Stony Brook conference'
    )
    assert response.results[0].date == '1971'
    assert response.results[0].author == 'Ahlfors, Lars Valerian, 1907-'
    assert response.results[0].description == (
        'Edited by Lars V. Ahlfors [and others]; '
        'Proceedings of the 2d of a series of meetings; '
        'proceedings of the 3d are entered under Conference on Discontinuous Groups and Riemann Surfaces, '
        'University of Maryland, 1973.; '
        'Includes bibliographical references.'
    )


@httpretty.activate
def test_alma_search_bad_request(register_search_url: Callable, alma_search: AlmaSearch):
    register_search_url(status=HTTPStatus.BAD_REQUEST)

    with pytest.raises(SearchError):
        alma_search()


@httpretty.activate
def test_worldcat_search_connection_error(
    alma_search: AlmaSearch,
    monkeypatch: MonkeyPatch,
    raise_connection_error: Callable,
):
    monkeypatch.setattr(requests, 'get', raise_connection_error)

    with pytest.raises(SearchError):
        alma_search()
