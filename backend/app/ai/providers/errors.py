class ProviderError(Exception):
    eligible_for_fallback: bool = False


class ProviderTimeoutError(ProviderError):
    eligible_for_fallback = True


class ProviderTransportError(ProviderError):
    eligible_for_fallback = True


class ProviderRateLimitError(ProviderError):
    eligible_for_fallback = True


class ProviderServerError(ProviderError):
    eligible_for_fallback = True


class ProviderMisconfiguredError(ProviderError):
    eligible_for_fallback = True


class ProviderInvalidOutputError(ProviderError):
    eligible_for_fallback = True


class ProviderUnavailableError(ProviderError):
    eligible_for_fallback = False
