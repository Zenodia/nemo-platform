# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Process-wide refcounted async cache for shareable processor resources.

Multiple ``RequestProcessor`` / ``ResponseProcessor`` instances built from the
same factory (e.g. two ``RouteLLMRequestProcessor``s configured with the same
classifier model) need to share expensive resources — GPU-loaded classifiers,
warmed HTTP clients, background pollers — instead of each loading its own
copy. ``ResourceCache`` provides that sharing via a refcounted async-safe map.

Usage from a processor's ``startup()`` / ``shutdown()`` hooks::

    _cache: ResourceCache = ResourceCache()  # process-wide singleton

    class MyProcessor(RequestProcessor):
        def __init__(self, classifier_model: str) -> None:
            self._key = f"my-classifier:{classifier_model}"
            self._classifier: Classifier | None = None

        async def startup(self) -> None:
            self._classifier = await _cache.acquire(self._key, self._load)

        async def shutdown(self) -> None:
            await _cache.release(self._key, self._unload)

        async def _load(self) -> Classifier: ...
        async def _unload(self, value: Classifier) -> None: ...

Concurrency contract:

* Two acquires of the same key receive the same instance; the factory runs
  exactly once even under concurrent contention.
* Releases decrement the refcount; the shutdown callback fires once the
  refcount reaches zero, then the entry is evicted.
* If shutdown raises during a release, the entry is still evicted — we don't
  retry. Eviction is unconditional so a misbehaving shutdown can't leak the
  entry forever.
* Releasing an unknown key raises ``KeyError`` rather than silently no-op'ing
  — that almost always indicates a programming error (mismatched
  acquire/release, double release).

GPU resources
-------------

The cache is GPU-agnostic — it doesn't import torch and doesn't track VRAM.
GPU lifecycle lives in the caller's ``factory`` and ``shutdown`` callbacks::

    class RouteLLMRequestProcessor(RequestProcessor):
        def __init__(self, classifier_model: str) -> None:
            self._key = f"routellm-classifier:{classifier_model}"
            self._model_name = classifier_model
            self._classifier: Classifier | None = None

        async def startup(self) -> None:
            self._classifier = await _cache.acquire(self._key, self._load)

        async def shutdown(self) -> None:
            await _cache.release(self._key, self._unload)
            self._classifier = None

        async def _load(self) -> Classifier:
            model = SomeClassifier.from_pretrained(self._model_name)
            model.to("cuda")
            return model

        async def _unload(self, model: Classifier) -> None:
            del model
            import torch
            torch.cuda.empty_cache()

What this gets you: two ``RouteLLMRequestProcessor`` instances configured
with the same ``classifier_model`` share one GPU copy. The first acquire
loads it; the second is a refcount bump. Both release, the refcount hits
zero, ``_unload`` runs, the model is freed.

Caveats for GPU-backed resources:

* **Cross-key sharing isn't a thing.** Different ``classifier_model``
  strings produce different keys and load independently. Pick the key
  deliberately — usually some hash of the relevant config slice.
* **Eviction is immediate at refcount 0.** No warm cache today. If a
  VirtualModel referencing a classifier is re-upserted in a tight loop
  you re-pay the GPU load each cycle. Acceptable for the SWITCH-167
  RouteLLM use case; revisit if reload latency becomes a problem.
* **Per-key serialisation.** Concurrent acquires for the same key all
  wait on one ``asyncio.Lock`` so the GPU loader runs exactly once —
  but if the load is slow (multi-second for a large classifier), every
  waiter is blocked on it. Mitigation: call ``await pipeline.startup()``
  once at app boot, not on the request hot path.
* **Shutdown holds the per-key lock.** ``torch.cuda.empty_cache()`` and
  similar can be slow; while running, new acquires of that key wait.
  Fine for process teardown; would need rework to support hot-swapping
  models.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

log = logging.getLogger(__name__)


@dataclass
class _Entry:
    value: Any
    refcount: int


class ResourceCache:
    """Refcounted async-safe cache keyed by string."""

    def __init__(self) -> None:
        self._entries: dict[str, _Entry] = {}
        self._key_locks: dict[str, asyncio.Lock] = {}
        # Guards mutations of ``_key_locks`` itself. The per-key locks guard
        # the entries.
        self._registry_lock = asyncio.Lock()

    async def acquire(
        self,
        key: str,
        factory: Callable[[], Awaitable[Any]],
    ) -> Any:
        """Return the cached value for ``key`` or run ``factory()`` once.

        Increments the refcount on every call. The first acquire under a key
        runs ``factory()`` and stores the result; subsequent acquires return
        the stored value without re-running the factory.
        """
        lock = await self._get_key_lock(key)
        async with lock:
            entry = self._entries.get(key)
            if entry is None:
                value = await factory()
                self._entries[key] = _Entry(value=value, refcount=1)
                return value
            entry.refcount += 1
            return entry.value

    async def release(
        self,
        key: str,
        shutdown: Callable[[Any], Awaitable[None]],
    ) -> None:
        """Decrement the refcount; run ``shutdown`` and evict at zero.

        Raises:
            KeyError: ``key`` is not currently held by the cache.
        """
        lock = await self._get_key_lock(key)
        async with lock:
            entry = self._entries.get(key)
            if entry is None:
                raise KeyError(f"ResourceCache: release on unknown key {key!r}")
            entry.refcount -= 1
            if entry.refcount > 0:
                return
            try:
                await shutdown(entry.value)
            except Exception:
                log.exception(
                    "ResourceCache: shutdown raised for key %r; evicting anyway", key
                )
            finally:
                self._entries.pop(key, None)

    def refcount(self, key: str) -> int:
        """Return the current refcount for ``key`` (0 if not held).

        Convenience for tests; not a load-bearing API.
        """
        entry = self._entries.get(key)
        return entry.refcount if entry is not None else 0

    async def _get_key_lock(self, key: str) -> asyncio.Lock:
        async with self._registry_lock:
            lock = self._key_locks.get(key)
            if lock is None:
                lock = asyncio.Lock()
                self._key_locks[key] = lock
            return lock
