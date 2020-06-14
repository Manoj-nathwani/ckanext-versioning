"""Datapackage formatting related tests
"""
from nose.tools import assert_equals
from parameterized import parameterized

from ckanext.versioning import datapackage

SHA256 = '0f1128046248f83dc9b9ab187e16fad0ff596128f1524d05a9a77c4ad932f10a'


@parameterized([
    ({"path": "i/have/a/path.csv", "url": "i/also/have/a/url.csv"}, "i/have/a/path.csv"),
    ({"url": "https://example.com/data.csv", "sha256": SHA256, "name": "my-resource", "format": "csv"},
     "https://example.com/data.csv"),
    ({"sha256": SHA256, "name": "my-resource", "format": "csv"},  "my-resource.csv"),
    ({"sha256": SHA256, "name": "MyResource", "format": "csv"},  "myresource.csv"),
    ({"url": "data/myfile.csv"},  "data/myfile.csv"),
    ({"name": "my-resource", "format": "csv"},  None),
])
def test_resource_path_is_added(resource, expected_path):
    result = datapackage.dataset_to_frictionless({"name": "my package", "resources": [resource]})
    assert_equals(result['resources'][0].get('path'), expected_path)


def test_resource_path_multiple_resources():
    dataset = {
        "name": "my package",
        "resources": [{"url": "data/foo.csv", "name": "resource 1"},
                      {"url": "https://example.com/data.csv", "name": "resource 2"},
                      {"path": "an/existing/path.csv", "name": "resource 3"},
                      {"name": "my-resource", "type": "xls", "sha256": SHA256}]
    }
    resources = datapackage.dataset_to_frictionless(dataset)['resources']
    assert_equals(resources[0]['path'], 'data/foo.csv')
    assert_equals(resources[1]['path'], 'https://example.com/data.csv')
    assert_equals(resources[2]['path'], 'an/existing/path.csv')
    assert_equals(resources[3]['path'], 'my-resource.xls')


@parameterized([
    ('/absolute/data.csv', 'absolute/data.csv'),
    ('./relative/data.csv', './relative/data.csv'),
    ('local/with/../../../parent/ref.csv', 'local/with/parent/ref.csv'),
    ('local/with/./././parent/ref.csv', 'local/with/parent/ref.csv'),
    ('../upper/dir/ref.csv', 'upper/dir/ref.csv'),
])
def test_resource_path_relative_dirs_normalization(input, expected):
    result = datapackage.dataset_to_frictionless({"name": "my package", "resources": [{"url": input}]})
    assert_equals(result['resources'][0].get('path'), expected)


def test_resource_path_conflicting_paths_fixed():
    dataset = {
        "name": "my package",
        "resources": [{"url": "data/foo.csv", "name": "resource 1"},
                      {"url": "data/bar.csv", "name": "resource 2"},
                      {"path": "data/foo.csv", "name": "resource 3"},
                      {"name": "data/foo", "type": "csv", "sha256": SHA256},
                      {"path": "../data/foo.csv", "name": "resource 5"}]
    }
    resources = datapackage.dataset_to_frictionless(dataset)['resources']
    assert_equals(resources[0]['path'], 'data/foo.csv')
    assert_equals(resources[1]['path'], 'data/bar.csv')
    assert_equals(resources[2]['path'], 'data/foo-2.csv')
    assert_equals(resources[3]['path'], 'data/foo-3.csv')
    assert_equals(resources[4]['path'], 'data/foo-4.csv')
