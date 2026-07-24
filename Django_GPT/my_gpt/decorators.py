from functools import wraps
from urllib.parse import urlencode

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect


def model_login_required(view_func):
    """
    비로그인 사용자를 로그인 페이지로 보낸다.
    next + required=1 을 함께 전달해 원래 페이지 복귀와 Alert를 지원한다.
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)

        # fetch 요청이면 리다이렉트 대신 JSON으로 알린다.
        if request.headers.get("X-Requested-With") == "fetch":
            return JsonResponse(
                {"error": "로그인 후 이용해주세요."},
                status=401,
            )

        query = urlencode({"next": request.get_full_path(), "required": "1"})
        return redirect(f"{settings.LOGIN_URL}?{query}")

    return wrapper