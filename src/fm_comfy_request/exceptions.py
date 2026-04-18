class FmComfyRequestError(Exception):
    pass


class WorkflowNotFoundError(FmComfyRequestError):
    pass


class WorkflowLoadError(FmComfyRequestError):
    pass


class WorkflowMetaNotFoundError(FmComfyRequestError):
    pass


class WorkflowMetaConflictError(FmComfyRequestError):
    pass


class WorkflowMetaInvalidError(FmComfyRequestError):
    pass


class NodeReferenceError(FmComfyRequestError):
    pass


class NodeReferenceAmbiguousError(NodeReferenceError):
    pass


class NodeReferenceNotFoundError(NodeReferenceError):
    pass


class BindingInputNotFoundError(FmComfyRequestError):
    pass


class WorkflowValidationError(FmComfyRequestError):
    pass


class I2IUnsupportedError(FmComfyRequestError):
    pass


class LoraInsertionError(FmComfyRequestError):
    pass


class LoraClipOutputMissingError(LoraInsertionError):
    pass


class ComfyConnectionError(FmComfyRequestError):
    pass


class ComfyRequestError(FmComfyRequestError):
    pass


class ComfyTimeoutError(FmComfyRequestError):
    pass


class ComfyExecutionError(FmComfyRequestError):
    pass
