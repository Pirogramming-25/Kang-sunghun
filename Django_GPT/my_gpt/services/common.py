import torch


def get_pipeline_device():
    """
    실행 환경에 맞는 device 값을 반환한다.
      0     : NVIDIA GPU (CUDA)
      "mps" : Apple Silicon
      -1    : CPU
    """
    if torch.cuda.is_available():
        return 0

    if (
        hasattr(torch.backends, "mps")
        and torch.backends.mps.is_available()
    ):
        return "mps"

    return -1