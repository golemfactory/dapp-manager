### YAGNA DAPP MANAGER

Manage a dapp.

### Shell completion
This program supports shell completion for all of its commands, as well as existing dApp IDs (where applicable).
To enable completion, use the `autocomplete` command with your shell of choice:
```
$ yagna_dapp_manager autocomplete bash
```

**WARNING** Completion will **NOT WORK** when `autocomplete` is invoked with `python -m yagna_dapp_manager`.
Only the installed entrypoint (i.e. `yagna_dapp_manager`) is supported. To have it available, run `poetry install`.

The actual completion functions are defined in `yagna_dapp_manager/autocomplete/scripts`.
Should the entrypoint name ever change, these files will need to be updated as well.
