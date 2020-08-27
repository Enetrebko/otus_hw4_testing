#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from datetime import datetime
import logging
import hashlib
import uuid
from scoring import get_interests, get_score
from optparse import OptionParser
from http.server import HTTPServer, BaseHTTPRequestHandler
from store import Store
import re
from settings.api_config import *


class AbstractField(object):
    def __init__(self, required=False, nullable=True):
        self.required = required
        self.nullable = nullable
        self.value = None

    def __get__(self, instance, owner):
        return self.value

    def __set__(self, instance, value):
        if (not self.nullable or self.required) and value is None:
            raise ValueError("Must be not Null: %s" % value)
        self.validate(value)
        self.value = value

    def validate(self, value):
        return


class CharField(AbstractField):
    def validate(self, value):
        if value and not isinstance(value, str):
            raise ValueError("Must be string: %s" % value)


class ArgumentsField(AbstractField):
    def validate(self, value):
        if not isinstance(value, dict):
            raise ValueError("Must be dict: %s" % value)


class EmailField(CharField):
    def validate(self, value):
        super().validate(value)
        if value and not ('@' in value):
            raise ValueError("Must contain @: %s" % value)


class PhoneField(AbstractField):
    def validate(self, value):
        phone_pattern = re.compile('^7.{10}$')
        if not value:
            return
        elif not isinstance(value, (str, int)):
            raise ValueError("Must be str or int: %s" % value)
        elif not phone_pattern.match(str(value)):
            raise ValueError("Not a phone number: %s" % value)


class DateField(AbstractField):
    def validate(self, value):
        if value:
            datetime.strptime(str(value), '%d.%m.%Y')


class BirthDayField(AbstractField):
    def validate(self, value):
        if value and not (datetime.now() - datetime.strptime(str(value), '%d.%m.%Y')).days <= 365 * 70:
            raise ValueError("Must be <=70 years old: %s" % value)


class GenderField(AbstractField):
    def validate(self, value):
        if value and value not in (UNKNOWN, MALE, FEMALE):
            raise ValueError("Must be int 0, 1 or 2: %s" % value)


class ClientIDsField(AbstractField):
    def validate(self, value):
        if not isinstance(value, list) or any(not isinstance(x, int) for x in value):
            raise ValueError("Must be list of ints: %s" % value)
        elif len(value) == 0:
            raise ValueError("Clients list is empty: %s" % value)


class ClientsInterestsRequest(object):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)

    def __init__(self, client_ids, date=None):
        self.client_ids = client_ids
        self.date = date


class OnlineScoreRequest(object):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    def __init__(self, first_name=None, last_name=None, email=None, phone=None, birthday=None, gender=None):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.birthday = birthday
        self.gender = gender

        if not ((phone and email) or (first_name and last_name) or (gender is not None and birthday)):
            raise AttributeError('Must be at least one pair: phone+email or first+last_name or gender+birthday')


class MethodRequest(object):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN

    def __init__(self, login, token, arguments, method, account=None):
        self.account = account
        self.login = login
        self.token = token
        self.arguments = arguments
        self.method = method


def check_auth(request):
    if request.is_admin:
        digest = hashlib.sha512((datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).encode('utf8')).hexdigest()
    else:
        digest = hashlib.sha512((request.account + request.login + SALT).encode('utf8')).hexdigest()
    if digest == request.token:
        return True
    return False


def method_handler(request, ctx, store):
    methods = {
        'online_score' : get_score_handler,
        'clients_interests': get_interests_handler
    }
    try:
        method_request = MethodRequest(**request['body'])
        if check_auth(method_request):
            response, code = methods[method_request.method](method_request, ctx, store)
        else:
            response, code = ERRORS[FORBIDDEN], FORBIDDEN
    except (TypeError, ValueError, AttributeError):
        response, code = ERRORS[INVALID_REQUEST], INVALID_REQUEST
    return response, code


def get_score_handler(method_request, ctx, store):
    score_request = OnlineScoreRequest(**method_request.arguments)
    score = get_score(store,
                      phone=score_request.phone,
                      email=score_request.email,
                      birthday=score_request.birthday,
                      gender=score_request.gender,
                      first_name=score_request.first_name,
                      last_name=score_request.last_name)
    ctx['has'] = method_request.arguments
    return {'score': score}, OK


def get_interests_handler(method_request, ctx, store):
    interests_request = ClientsInterestsRequest(**method_request.arguments)
    ctx['nclients'] = len(interests_request.client_ids)
    return {client_id: get_interests(store, client_id) for client_id in interests_request.client_ids}, OK


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }
    store = Store()

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except Exception:
            code = BAD_REQUEST
        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path]({"body": request, "headers": self.headers}, context, self.store)
                except Exception as e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r).encode('utf8'))
        return


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
