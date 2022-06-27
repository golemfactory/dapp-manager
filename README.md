# Golem dApp Manager

`dapp-manager` is a purposefully minimalistic manager for decentralized applications running on
Golem. It works together with the [dapp-runner](https://github.com/golemfactory/dapp-runner/).
While the responsibility of the latter is to run a single Golem application, `dapp-manager` takes
care of spawning, interacting with, and stopping the running instances of the `dapp-runner`.

## Quick start

### Yagna daemon

As the `dapp-manager` uses the `dapp-runner`, which in turn requires a properly configured
[yagna](https://github.com/golemfactory/yagna) daemon, you'll need to have it set up.

For now, please follow the ["Requestor development: a quick primer"](https://handbook.golem.network/requestor-tutorials/flash-tutorial-of-requestor-development)
tutorial and ensure that your `yagna` is up and running. Only the first part of this
tutorial is required - you don't need to run the blender example.

Most importantly, make sure you have set the `YAGNA_APPKEY` in your environment, e.g. with:

```bash
export YAGNA_APPKEY=insert-your-32-char-app-key-here
```

or, on Windows:

```bash
set YAGNA_APPKEY=insert-your-32-char-app-key-here
```

and if you don't know what your app-key is, you can always query `yagna` with:

```bash
yagna app-key list
```

### Python environment

First, ensure you have Python 3.8 or later:

```bash
python3 --version
```

[ depending on the platform, it may be just `python` instead of `python3` ]

If your Python version is older, consider using [pyenv](https://github.com/pyenv/pyenv-installer).

Once your python interpreter reports a version 3.8 or later, you can set up your virtual
environment:

```bash
python3 -m venv ~/.envs/dapp-manager
source ~/.envs/dapp-manager/bin/activate
```

or, if you're on Windows:

```shell
python -m venv --clear %HOMEDRIVE%%HOMEPATH%\.envs\dapp-manager
%HOMEDRIVE%%HOMEPATH%\.envs\dapp-manager\Scripts\activate.bat
```

### DApp manager

#### Clone the repository:

```bash
git clone --recurse-submodules https://github.com/golemfactory/dapp-manager.git
```

#### Install the dependencies

```
cd dapp-manager
pip install -U pip poetry
poetry install
```

#### Run an example application:

Make sure your `yagna` daemon is running,
you have initialized the payment driver with `yagna payment init --sender`,
and that you have set the `YAGNA_APPKEY` environment variable.

Then run:

```bash
dapp-manager start --config sample_config.yml dapp-store/apps/webapp.yaml
```

The app is started in a background `dapp-runner` process, and you're returned an application ID in
the form of a hexadecimal string. You can use this ID to query the state and other output streams
using `dapp-manager`'s `read` command, e.g.:

```bash
dapp-manager read state <the-hex-string>
```

will display the contents of the `state` stream of the running app:

```
{"db": {"0": "pending"}}
{"db": {"0": "starting"}}
{"db": {"0": "running"}}
{"db": {"0": "running"}, "http": {"0": "pending"}}
{"db": {"0": "running"}, "http": {"0": "starting"}}
```

In case something goes amiss, `dapp-manager` will output:
```App <the-hex-string> is not running.```

Whatever the reason, you can still query the various streams of a terminated dapp by adding the
`--no-ensure-alive` option, e.g.:

```bash
dapp-manager read stderr <the-hex-string> --no-ensure-alive
```

## Full usage

```
Usage: dapp-manager [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  autocomplete  Enable CLI shell completion for the given shell.
  kill          Stop the given app forcibly.
  list          List known app IDs (both active and dead).
  prune         Remove data for non-running apps.
  read          Read output from the given app.
  start         Start a new app using the provided descriptor and config...
  stop          Stop the given app gracefully.
```

### Start

The `start` command launches a new instance of the `dapp-runner` in a background process and
returns the hexadecimal string that is the identifier of the running `dapp-runner` instance.

```
Usage: dapp-manager start [OPTIONS] DESCRIPTORS...

  Start a new app using the provided descriptor and config files.

Options:
  -c, --config PATH  Path to the file containing yagna-specific config.
                     [required]
  --help             Show this message and exit.
```

Importantly, it requires a config file which contains the parameters used to connect to the `yagna`
daemon and initialize the requestor engine. We're providing a default, sample configuration as
`sample_config.yml` in the root of the `dapp-manager` repository.

Of course, it also requires one or more descriptor files that are used by the `dapp-runner` to
deploy the specified applications on Golem.

### Stop / Kill

The `stop` and `kill` commands terminate the given `dapp-runner` instance, the main difference
being the signal that's sent to do that. Essentially, `stop` should be enough and should give the
`dapp-runner` a chance to shut the app down gracefully, correctly terminating the services,
closing the agreements and paying for them.

In case `stop` is stuck for whatever reason, you might want to resort to `kill` which terminates
the `dapp-runner` immediately without allowing for any graceful shutdown.

### List

The `list` command shows the identifiers of all the previously-started apps, whether they're still
running or not.

### Prune

`prune` causes `dapp-manager` to remove the data for those apps that it had previously identified as
defunct. Consequently, those apps will no longer appear on the list.

Unless an app has been explicitly stopped with a `stop` or `kill` command, the `dapp-manager` 
will not purge it until it has had a chance to notice the termination, e.g. by issuing a `read` 
command to the defunct app.

### Read

The `read` command outputs the full contents of the specified stream. There are five streams as
specified by the usage below:

```
Usage: dapp-manager read [OPTIONS] COMMAND [ARGS]...

  Read output from the given app.

Options:
  --help  Show this message and exit.

Commands:
  data    Read the data stream of the given app.
  log     Read the log stream of a given app.
  state   Read the state stream of the given app.
  stderr  Read the stderr of a given app.
  stdout  Read the stdout of a given app.
```

By default, the stream will only be output if the app is currently running. Otherwise, you'll get
the ```App <the-hex-string> is not running.``` message and no stream.

If you wish to query a stream of a terminated app, add the `--no-ensure-alive` parameter to the
specific `read` command.

### Shell completion

This program supports shell completion for all of its commands, as well as existing dApp IDs (where applicable).

To enable completion, use the `autocomplete` command with your shell of choice:
* **bash**:
    ```
    $ dapp-manager autocomplete bash
    ```

* **zsh**:
    ```
    $ dapp-manager autocomplete zsh
    ```

* **fish**:
    ```
    $ dapp-manager autocomplete fish
    ```

The completion functions are defined in `dapp_manager/autocomplete/scripts`.

Should the entrypoint name ever change, those files will need to be updated as well.

**WARNING** Completion will **NOT WORK** when `autocomplete` is invoked with `python -m dapp_manager`.
Only the installed entrypoint (i.e. `dapp-manager`) is supported. To have it available, run `poetry install`.
