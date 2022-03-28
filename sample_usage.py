from yagna_dapp_manager import DappManager

#   New app
dm = DappManager.start("golem_compose.yml", config="config_file.yml")
print(dm.data())
print(dm.raw_status())

#   Old app
app_id = DappManager.list()[0]
dm = DappManager(app_id)
print(dm.data())
print(dm.raw_status())

#   Stop the app
app_id = DappManager.list()[0]
dm = DappManager(app_id)
if not dm.stop():
    dm.kill()

#   Forget about all non-running apps
DappManager.prune()
