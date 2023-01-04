from email.message import Message
from pathlib import Path
import pytest
from typing import List
from urllib.error import HTTPError, URLError

from dapp_stats.dapp_size_resolver import DappSizeResolver, DappSizeResolverError


@pytest.fixture
def dapp_size_resolver():
    return DappSizeResolver


@pytest.mark.parametrize(
    "descriptor_paths, mocked_sizes, expected_sizes, expected_errors",
    (
        (
            (Path("tests/assets/descriptors/correct_vm_runtime_a.yaml"),),
            ("123",),
            {"total_size": 123, "payloads": {"a": 123}},
            [],
        ),
        (
            (Path("tests/assets/descriptors/correct_vm_runtime_ab.yaml"),),
            ("123", "321"),
            {"total_size": 444, "payloads": {"a": 123, "b": 321}},
            [],
        ),
        (
            (
                Path("tests/assets/descriptors/correct_vm_runtime_a.yaml"),
                Path("tests/assets/descriptors/correct_vm_runtime_b.yaml"),
            ),
            ("123", "321"),
            {"total_size": 444, "payloads": {"a": 123, "b": 321}},
            [],
        ),
    ),
)
def test_resolve_vm_runtime_payload_size(
    dapp_size_resolver,
    descriptor_paths,
    mocked_sizes,
    expected_sizes,
    expected_errors,
    mocker,
):
    mocked_image_url_from_repo_package_url = mocker.Mock(
        **{"read.return_value": b"some_gvmi_link"}
    )

    mocked_urlopen = mocker.patch("dapp_stats.dapp_size_resolver.request.urlopen")
    urlopen_mocks = []
    for mocked_size in mocked_sizes:
        mocked_payload_size_from_image_url = mocker.Mock(
            headers={"Content-Length": mocked_size}
        )

        urlopen_mocks.extend(
            [
                mocked_image_url_from_repo_package_url,
                mocked_payload_size_from_image_url,
            ]
        )

    mocked_urlopen.return_value.__enter__.side_effect = urlopen_mocks

    sizes, errors = dapp_size_resolver.resolve_defined_payload_sizes(descriptor_paths)

    assert errors == expected_errors
    assert sizes == expected_sizes


def test_resolve_vm_runtime_payload_size_missing_image_hash(dapp_size_resolver):
    sizes, errors = dapp_size_resolver.resolve_defined_payload_sizes(
        [Path("tests/assets/descriptors/bad_vm_runtime_without_image_hash.yaml")]
    )

    assert errors == [
        'Ignoring payload "a" as following error occurred: Field "image_hash" is not present in payload params!'
    ]
    assert sizes == {"total_size": 0, "payloads": {}}


def test_resolve_vm_runtime_payload_size_image_hash_not_found_in_repo(
    dapp_size_resolver, mocker
):
    mocked_urlopen = mocker.patch("dapp_stats.dapp_size_resolver.request.urlopen")
    mocked_urlopen.side_effect = HTTPError(
        "some_url", 404, "not found?!", mocker.Mock(), None
    )

    sizes, errors = dapp_size_resolver.resolve_defined_payload_sizes(
        [Path("tests/assets/descriptors/bad_vm_runtime_not_existing_image_hash.yaml")]
    )

    assert len(errors) == 1
    assert "Can't fetch image url from image hash" in errors[0]
    assert sizes == {"total_size": 0, "payloads": {}}


def test_resolve_vm_runtime_payload_size_image_url_not_found(
    dapp_size_resolver, mocker
):
    mocked_urlopen = mocker.patch("dapp_stats.dapp_size_resolver.request.urlopen")
    mocked_urlopen.return_value.__enter__.side_effect = [
        mocker.Mock(**{"read.return_value": b"some_gvmi_link"}),
        HTTPError("some_url", 404, "not found?!", mocker.Mock(), None),
    ]

    sizes, errors = dapp_size_resolver.resolve_defined_payload_sizes(
        [Path("tests/assets/descriptors/bad_vm_runtime_not_existing_image_hash.yaml")]
    )

    assert len(errors) == 1
    assert "Can't fetch payload size from image url" in errors[0]
    assert sizes == {"total_size": 0, "payloads": {}}


@pytest.mark.parametrize(
    "descriptor_paths, mocked_sizes, expected_sizes, expected_errors",
    (
        (
            (Path("tests/assets/descriptors/correct_vm_manifest_runtime_a.yaml"),),
            ("123",),
            {"total_size": 123, "payloads": {"a": 123}},
            [],
        ),
        (
            (Path("tests/assets/descriptors/correct_vm_manifest_runtime_ab.yaml"),),
            ("123", "321"),
            {"total_size": 444, "payloads": {"a": 123, "b": 321}},
            [],
        ),
        (
            (
                Path("tests/assets/descriptors/correct_vm_manifest_runtime_a.yaml"),
                Path("tests/assets/descriptors/correct_vm_manifest_runtime_b.yaml"),
            ),
            ("123", "321"),
            {"total_size": 444, "payloads": {"a": 123, "b": 321}},
            [],
        ),
    ),
)
def test_resolve_vm_manifest_runtime_payload_size(
    dapp_size_resolver,
    descriptor_paths,
    mocked_sizes,
    expected_sizes,
    expected_errors,
    mocker,
):
    mocked_urlopen = mocker.patch("dapp_stats.dapp_size_resolver.request.urlopen")
    mocked_urlopen.return_value.__enter__.side_effect = [
        mocker.Mock(headers={"Content-Length": mocked_size})
        for mocked_size in mocked_sizes
    ]

    sizes, errors = dapp_size_resolver.resolve_defined_payload_sizes(descriptor_paths)

    assert errors == expected_errors
    assert sizes == expected_sizes


def test_resolve_vm_manifest_runtime_payload_size_missing_manifest(dapp_size_resolver):
    sizes, errors = dapp_size_resolver.resolve_defined_payload_sizes(
        [Path("tests/assets/descriptors/bad_vm_manifest_runtime_without_manifest.yaml")]
    )

    assert errors == [
        'Ignoring payload "a" as following error occurred: Field "manifest" is not present in payload params!'
    ]
    assert sizes == {"total_size": 0, "payloads": {}}


def test_resolve_vm_manifest_runtime_payload_size_corrupted_manifest(
    dapp_size_resolver,
):
    sizes, errors = dapp_size_resolver.resolve_defined_payload_sizes(
        [
            Path(
                "tests/assets/descriptors/bad_vm_manifest_runtime_corrupted_manifest.yaml"
            )
        ]
    )

    assert errors == [
        'Ignoring payload "a" as following error occurred: Field "manifest" is not properly Base64 encoded JSON object!'
    ]
    assert sizes == {"total_size": 0, "payloads": {}}


def test_resolve_vm_manifest_runtime_payload_size_no_image_url_in_manifest(
    dapp_size_resolver,
):
    sizes, errors = dapp_size_resolver.resolve_defined_payload_sizes(
        [
            Path(
                "tests/assets/descriptors/bad_vm_manifest_runtime_without_image_url.yaml"
            )
        ]
    )

    assert errors == [
        'Ignoring payload "a" as following error occurred: Payload url is not present in manifest!',
        'Ignoring payload "b" as following error occurred: Payload url is not present in manifest!',
    ]
    assert sizes == {"total_size": 0, "payloads": {}}


def test_resolve_combined_runtime_payload_size(dapp_size_resolver, mocker):
    descriptor_paths = (
        Path("tests/assets/descriptors/correct_vm_runtime_a.yaml"),
        Path("tests/assets/descriptors/correct_vm_manifest_runtime_b.yaml"),
    )
    expected_sizes = {"total_size": 444, "payloads": {"a": 123, "b": 321}}
    expected_errors: List[str] = []

    mocked_image_url_from_repo_package_url = mocker.Mock(
        **{"read.return_value": b"some_gvmi_link"}
    )
    mocked_payload_size_from_image_urls = [
        mocker.Mock(headers={"Content-Length": "123"}),
        mocker.Mock(headers={"Content-Length": "321"}),
    ]

    mocked_urlopen = mocker.patch("dapp_stats.dapp_size_resolver.request.urlopen")

    mocked_urlopen.return_value.__enter__.side_effect = [
        mocked_image_url_from_repo_package_url,
        *mocked_payload_size_from_image_urls,
    ]

    sizes, errors = dapp_size_resolver.resolve_defined_payload_sizes(descriptor_paths)

    assert errors == expected_errors
    assert sizes == expected_sizes


def test_resolve_payload_size_descriptor_not_found(dapp_size_resolver):
    with pytest.raises(DappSizeResolverError, match="Failed to load descriptor files"):
        dapp_size_resolver.resolve_defined_payload_sizes([Path("not existing")])


def test_resolve_payload_size_descriptor_validation_errors(dapp_size_resolver):
    with pytest.raises(
        DappSizeResolverError, match="Failed to validate descriptor files"
    ):
        dapp_size_resolver.resolve_defined_payload_sizes(
            [Path("tests/assets/descriptors/bad_validation.yaml")]
        )


def test_resolve_payload_size_unknown_payload_runtime(dapp_size_resolver):
    sizes, errors = dapp_size_resolver.resolve_defined_payload_sizes(
        [Path("tests/assets/descriptors/unsupported_runtime.yaml")]
    )

    assert errors == [
        'Ignoring payload "a" as following error occurred: Size measurement for runtime "unsupported or something..." is not supported!'
    ]
    assert sizes == {"total_size": 0, "payloads": {}}
