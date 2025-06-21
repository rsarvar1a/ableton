
from ableton.ableton import keygen, patcher
from argparse import ArgumentParser
from dotdict import dotdict
from yaml import load as yaml_load, Loader

def main() -> None:
    # Get the configuration.
    parser = ArgumentParser()
    parser.add_argument('--config', default='config.yaml')
    parser.add_argument('--patch', action='store_true')
    parser.add_argument('--revert', action='store_true')
    
    args = parser.parse_args()
    config_path, revert, patch = args.config, args.revert, args.patch

    with open(config_path, 'r') as config_file:
        config = yaml_load(config_file, Loader=Loader)
        config = dotdict(config)

    # Construct the private key with the given specification.
    private_key = keygen.DSAParams(**config.keygen).construct()

    # Generate the .auz file corresponding to the edition and key.
    authorizer = keygen.AuzGenerator(
        version=config.version, 
        edition=config.edition, 
        hardware_id=config.hardware_id
    )
    with open(config.auz_path, 'w', newline='\n') as auz_file:
        lines = authorizer.generate(key=private_key)
        content = '\n'.join(lines)
        auz_file.write(content)

    # Patch the executable to accept authorizations with the new signing key.
    if not (patch or revert):
        return

    replacer = patcher.Patcher(
        application_path=config.application_path, 
        factory=config.patch['factory'], 
        signing=config.patch['signing']
    )
    replacer.patch(revert)

if __name__ == '__main__':
    main()
