import copy

import tests.__stubs__.summarizer_config_template as summarizer_config_template


def make_summarizer_config_plain():
    def make(**rest):
        return copy.deepcopy(
            summarizer_config_template.SUMMARIZER_CONFIG_TEMPLATE
        ) | {**rest}

    return make
