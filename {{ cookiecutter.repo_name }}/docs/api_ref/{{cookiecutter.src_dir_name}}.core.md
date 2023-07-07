## Configs

The base classes for step entrypoint configs.

### Base classes

The base classes for step entrypoint configs.

::: {{cookiecutter.src_dir_name}}.core.configs.base

### Argument parsing

The argument parsing helper functions for the script entrypoint arguments.

::: {{cookiecutter.src_dir_name}}.core.configs.argument_parsing

## Settings

The application settings.

::: {{cookiecutter.src_dir_name}}.core.settings

### Importing settings

To use current settings without the need to parse them each time you can use:

```python
import logging

from {{cookiecutter.src_dir_name}}.core.settings import current_settings


# log current environment
logging.info(current_settings.env)  # INFO:dev
```
