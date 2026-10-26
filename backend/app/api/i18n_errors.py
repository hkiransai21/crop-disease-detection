"""Localize transport errors without changing their HTTP status or detail shape."""
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException
from backend.app.services.i18n import resolve_language, translate_message, messages


def language(request):
    return resolve_language(request.query_params.get('lang'), request.headers.get('accept-language'))


async def http_error(request: Request, exc: HTTPException):
    lang=language(request)
    detail=exc.detail
    if isinstance(detail,str):
        localized=translate_message(detail,lang)
        if localized==detail and lang!='en' and detail not in messages(lang).values():
            generic={401:'Please sign in to continue.',403:'Please sign in to continue.',404:'The requested record was not found.',429:'Too many requests. Please wait and try again.'}.get(exc.status_code,'Check the information you entered.' if exc.status_code<500 else 'The service is unavailable. Please try again later.')
            localized=translate_message(generic,lang)
        detail=localized
    return JSONResponse({'detail':detail},status_code=exc.status_code,headers={**(exc.headers or {}),'Content-Language':lang,'Vary':'Accept-Language'})


async def validation_error(request: Request, exc: RequestValidationError):
    lang=language(request)
    errors=[]
    for error in exc.errors():
        errors.append({'type':error['type'],'loc':error['loc'],'msg':translate_message('Check the information you entered.',lang)})
    return JSONResponse({'detail':errors},status_code=422,headers={'Content-Language':lang,'Vary':'Accept-Language'})


def install_i18n_errors(app):
    app.add_exception_handler(HTTPException,http_error)
    app.add_exception_handler(RequestValidationError,validation_error)
