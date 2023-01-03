import base64
import json
from pathlib import Path
from typing import List, TypedDict, Dict, Tuple, Callable, Sequence
from urllib import request

from dapp_runner.descriptor import DappDescriptor
from dapp_runner.descriptor.dapp import PayloadDescriptor
from dapp_runner.descriptor.parser import load_yamls
from yapapi.payload.vm import resolve_repo_srv, _DEFAULT_REPO_SRV

class DappSizeResolverError(Exception):
    pass

class ResolvedPayloadSizes(TypedDict):
    total_size: int
    payloads: Dict[str, int]


class DappSizeResolver:
    @classmethod
    def resolve_payload_size(cls, descriptor_paths: Sequence[Path]) -> Tuple[ResolvedPayloadSizes, List[str]]:
        payloads_sizes = {}
        errors = []
        resolvers = {
            'vm': cls._resolve_payload_size_for_vm_runtime,
            'vm/manifest': cls._resolve_payload_size_for_vm_manifest_runtime,
        }

        dapp = cls._get_dapp_from_descriptor_paths(descriptor_paths)

        for payload_name, payload in dapp.payloads.items():
            resolver: Callable[[PayloadDescriptor], int] = resolvers.get(payload.runtime, cls._resolve_payload_size_for_unknown_runtime)

            try:
                payload_size = resolver(payload)
            except DappSizeResolverError as e:
                errors.append(f'Ignoring payload "{payload_name}" as following error occurred: {e}')
            else:
                payloads_sizes[payload_name] = payload_size

        return {
            'total_size': sum(payloads_sizes.values()),
            'payloads': payloads_sizes,
        }, errors

    @classmethod
    def _get_dapp_from_descriptor_paths(cls, descriptor_paths: Sequence[Path]) -> DappDescriptor:
        dapp_dict = load_yamls(*descriptor_paths)
        return DappDescriptor.load(dapp_dict)

    @classmethod
    def _resolve_payload_size_for_vm_runtime(cls, payload: PayloadDescriptor) -> int:
        try:
            image_hash = payload.params['image_hash']
        except KeyError:
            raise DappSizeResolverError(f'Field "image_hash" is not present in payload params!')

        repo_url = resolve_repo_srv(_DEFAULT_REPO_SRV)
        repo_package_url = f"{repo_url}/image.{image_hash}.link"

        image_url = cls._fetch_image_url_from_repo_package_url(repo_package_url)

        return cls._fetch_payload_size_from_image_url(image_url)

    @classmethod
    def _resolve_payload_size_for_vm_manifest_runtime(cls, payload: PayloadDescriptor) -> int:
        try:
            manifest_hash = payload.params['manifest']
        except KeyError:
            raise DappSizeResolverError('Field "manifest" is not present in payload params!')

        manifest = json.loads(base64.b64decode(manifest_hash.encode('utf-8')))

        try:
            image_url = manifest['payload'][0]['urls'][0]
        except (KeyError, IndexError):
            raise DappSizeResolverError('Payload url is not present in manifest!')

        return cls._fetch_payload_size_from_image_url(image_url)

    @classmethod
    def _resolve_payload_size_for_unknown_runtime(cls, payload: PayloadDescriptor) -> int:
        raise DappSizeResolverError(f'Size measurement for runtime "{payload.runtime}" is not supported!')

    @classmethod
    def _fetch_image_url_from_repo_package_url(cls, repo_package_url: str) -> str:
        return cls._fetch_http_response_body(repo_package_url).decode('utf-8')

    @classmethod
    def _fetch_payload_size_from_image_url(cls, image_url: str) -> int:
        return int(cls._fetch_http_response_header(image_url, 'Content-Length'))

    @classmethod
    def _fetch_http_response_body(cls, url: str) -> bytes:
        with request.urlopen(url) as response:
            return response.read()

    @classmethod
    def _fetch_http_response_header(cls, url: str, header: str) -> bytes:
        with request.urlopen(url) as response:
            return response.headers[header]
