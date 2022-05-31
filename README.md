### YAGNA DAPP MANAGER

Manage a dapp.

### Shell completion
This program supports shell completion for all of its commands, as well as existing dApp IDs (where applicable).
To enable completion, use the `autocomplete` command with your shell of choice:
```
$ dapp-manager autocomplete bash
```

**WARNING** Completion will **NOT WORK** when `autocomplete` is invoked with `python -m dapp_manager`.
Only the installed entrypoint (i.e. `dapp-manager`) is supported. To have it available, run `poetry install`.

The actual completion functions are defined in `dapp_manager/autocomplete/scripts`.
Should the entrypoint name ever change, these files will need to be updated as well.
