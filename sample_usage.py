from dapp_manager import DappManager

#   New app
dapp = DappManager.start("golem_compose.yml", config="config_file.yml")
print(dapp.read_file("data"))
print(dapp.read_file("state"))

#   Old app
app_id = DappManager.list()[0]
dapp = DappManager(app_id)
print(dapp.read_file("data"))
print(dapp.read_file("state"))

#   Stop the app
app_id = DappManager.list()[0]
dapp = DappManager(app_id)
if not dapp.stop(timeout=1):
    dapp.kill()

#   Forget about all non-running apps
DappManager.prune()
