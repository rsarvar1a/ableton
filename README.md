
# ableton-patcher

## Install

```sh
git clone git@github.com:rsarvar1a/ableton
poetry install
```

## Usage

1. Put your hardware and version details into a `config.yaml` file (see [here](data/config.example.yaml) for an example).  
Do not touch the keygen or patch sections unless you know what you're doing.

```yaml
application_path: 'C:\path\to\Ableton.exe'
auz_path: 'path\to\output\Authorize.auz'
version: 12 # versions 9 to 12 are supported
edition: Suite # editions Lite, Intro, Standard, Suite are supported
hardware_id: 1111-1111-1111-1111-1111-1111
```

2. Patch your Ableton executable; this also runs the keygen.

```sh
poetry run patcher --config data/config.yaml --patch
```

3. Drag the Authorize.auz file into your Ableton window.


## Uninstall

This removes the patch from your executable, restoring it to factory conditions.

```sh
poetry run patcher --config data/config.yaml --revert
```

## If you just need a key

Run the script without a `--patch` or `--revert` argument.

```sh
poetry run patcher --config data/config.yaml
```