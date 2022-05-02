from yagna_dapp_manager import DappManager

#   New app
dapp = DappManager.start("golem_compose.yml", config="config_file.yml")
print(dapp.raw_data(ensure_alive=True))
print(dapp.raw_state(ensure_alive=True))

#   Old app
app_id = DappManager.list()[0]
dapp = DappManager(app_id)
print(dapp.raw_data(ensure_alive=True))
print(dapp.raw_state(ensure_alive=True))

#   Stop the app
app_id = DappManager.list()[0]
dapp = DappManager(app_id)
if not dapp.stop(timeout=1):
    dapp.kill()

#   Forget about all non-running apps
DappManager.prune()
