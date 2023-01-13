import base64
import json
from pathlib import Path
from typing import Callable, Dict, List, Sequence, Tuple, TypedDict
from urllib import request
from urllib.error import HTTPError

from dapp_runner.descriptor import DappDescriptor
from dapp_runner.descriptor.dapp import PayloadDescriptor
from dapp_runner.descriptor.parser import load_yamls

from yapapi.payload.vm import _DEFAULT_REPO_SRV, resolve_repo_srv


class DappSizeResolverError(Exception):
    pass


class ResolvedPayloadSizes(TypedDict):
    total_size: int
    payloads: Dict[str, int]


class DappSizeResolver:
    @classmethod
    def resolve_defined_payload_sizes(
        cls, descriptor_paths: Sequence[Path]
    ) -> Tuple[ResolvedPayloadSizes, List[str]]:
        payloads_sizes = {}
        errors = []
        size_resolvers = {
            "vm": cls._resolve_payload_size_for_vm_runtime,
            "vm/manifest": cls._resolve_payload_size_for_vm_manifest_runtime,
        }

        dapp = cls._get_dapp_from_descriptor_paths(descriptor_paths)

        for payload_name, payload in dapp.payloads.items():
            size_resolver: Callable[[PayloadDescriptor], int] = size_resolvers.get(
                payload.runtime, cls._resolve_payload_size_for_unknown_runtime
            )

            try:
                payload_size = size_resolver(payload)
            except DappSizeResolverError as e:
                errors.append(
                    f'Ignoring payload "{payload_name}" as following error occurred:' f" {e}"
                )
            else:
                payloads_sizes[payload_name] = payload_size

        return {
            "total_size": sum(payloads_sizes.values()),
            "payloads": payloads_sizes,
        }, errors

    @classmethod
    def _get_dapp_from_descriptor_paths(cls, descriptor_paths: Sequence[Path]) -> DappDescriptor:
        try:
            dapp_dict = load_yamls(*descriptor_paths)
        except FileNotFoundError as e:
            raise DappSizeResolverError(f"Failed to load descriptor files: {e}")

        try:
            return DappDescriptor.load(dapp_dict)
        except Exception as e:
            raise DappSizeResolverError(f"Failed to validate descriptor files: {e}")

    @classmethod
    def _resolve_payload_size_for_vm_runtime(cls, payload: PayloadDescriptor) -> int:
        try:
            image_hash = payload.params["image_hash"]
        except (TypeError, KeyError):
            raise DappSizeResolverError('Field "image_hash" is not present in payload params!')

        image_url = cls._fetch_image_url_from_image_hash(image_hash)

        return cls._fetch_payload_size_from_image_url(image_url)

    @classmethod
    def _resolve_payload_size_for_vm_manifest_runtime(cls, payload: PayloadDescriptor) -> int:
        try:
            manifest_base64 = payload.params["manifest"]
        except KeyError:
            raise DappSizeResolverError('Field "manifest" is not present in payload params!')

        try:
            manifest = json.loads(base64.b64decode(manifest_base64.encode("utf-8")))
        except Exception:
            raise DappSizeResolverError(
                'Field "manifest" is not properly Base64 encoded JSON object!'
            )

        try:
            image_url = manifest["payload"][0]["urls"][0]
        except (KeyError, IndexError):
            raise DappSizeResolverError("Payload url is not present in manifest!")

        return cls._fetch_payload_size_from_image_url(image_url)

    @classmethod
    def _resolve_payload_size_for_unknown_runtime(cls, payload: PayloadDescriptor) -> int:
        raise DappSizeResolverError(
            f'Size measurement for runtime "{payload.runtime}" is not supported!'
        )

    @classmethod
    def _fetch_image_url_from_image_hash(cls, image_hash: str) -> str:
        repo_url = resolve_repo_srv(_DEFAULT_REPO_SRV)
        repo_package_url = f"{repo_url}/image.{image_hash}.link"

        try:
            return cls._fetch_http_response_body(repo_package_url).decode("utf-8")
        except HTTPError as e:
            raise DappSizeResolverError(
                f'Can\'t fetch image url from image hash "{image_hash}" via url'
                f' "{repo_package_url}": {e}'
            )

    @classmethod
    def _fetch_payload_size_from_image_url(cls, image_url: str) -> int:
        try:
            return int(cls._fetch_http_response_header(image_url, "Content-Length"))
        except HTTPError as e:
            raise DappSizeResolverError(
                f'Can\'t fetch payload size from image url "{image_url}": {e}'
            )

    @classmethod
    def _fetch_http_response_body(cls, url: str) -> bytes:
        with request.urlopen(url) as response:
            return response.read()

    @classmethod
    def _fetch_http_response_header(cls, url: str, header: str) -> bytes:
        with request.urlopen(url) as response:
            return response.headers[header]
