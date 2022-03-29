from yagna_dapp_manager import DappManager

#   New app
dapp = DappManager.start("golem_compose.yml", config="config_file.yml")
print(dapp.data())
print(dapp.raw_status())

#   Old app
app_id = DappManager.list()[0]
dapp = DappManager(app_id)
print(dapp.data())
print(dapp.raw_status())

#   Stop the app
app_id = DappManager.list()[0]
dapp = DappManager(app_id)
if not dapp.stop():
    dapp.kill()

#   Forget about all non-running apps
DappManager.prune()
