from functools import partial

import inflection

camelcase = partial(inflection.camelize, uppercase_first_letter=False)
