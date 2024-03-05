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
