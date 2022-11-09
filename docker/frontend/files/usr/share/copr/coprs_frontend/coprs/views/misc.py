import base64
import datetime
import functools
from functools import wraps
from urllib.parse import urlparse
import flask

from flask import send_file, jsonify

from openid_teams.teams import TeamsRequest

from copr_common.enums import RoleEnum
from coprs import app
from coprs import db
from coprs import helpers
from coprs import models
from coprs import oid
from coprs.logic.complex_logic import ComplexLogic
from coprs.logic.users_logic import UsersLogic
from coprs.exceptions import ObjectNotFound
from coprs.measure import checkpoint_start
from flask_pyoidc import OIDCAuthentication
from flask_pyoidc.provider_configuration import ProviderConfiguration, ClientMetadata
from flask_pyoidc.user_session import UserSession

def fed_raw_name(oidname):
    oidname_parse = urlparse(oidname)
    if not oidname_parse.netloc:
        return oidname
    config_parse = urlparse(app.config["OPENID_PROVIDER_URL"])
    return oidname_parse.netloc.replace(".{0}".format(config_parse.netloc), "")

@app.before_request
def before_request():
    """
    Configure some useful defaults for (before) each request.
    """

    # Checkpoints initialization
    checkpoint_start()

    # Load the logged-in user, if any.
    # https://github.com/PyCQA/pylint/issues/3793
    # pylint: disable=assigning-non-slot
    flask.g.user = username = None
    if "openid" in flask.session:
        username = fed_raw_name(flask.session["openid"])
    elif "krb5_login" in flask.session:
        username = flask.session["krb5_login"]
    elif "oidc" in flask.session:
        username = flask.session["oidc"]

    if username:
        flask.g.user = models.User.query.filter(
            models.User.username == username).first()

auth_params = {'scope': app.config['OIDC_SCOPES']} # specify the scope to request
PROVIDER_CONFIG = ProviderConfiguration(issuer=app.config['OIDC_ISSUER'],
                                         client_metadata=ClientMetadata(app.config['OIDC_CLIENT'], app.config['OIDC_SECRET']), auth_request_params=auth_params)
auth = OIDCAuthentication({app.config['OIDC_PROVIDER_NAME']: PROVIDER_CONFIG}, app)
misc = flask.Blueprint("misc", __name__)


def workaround_ipsilon_email_login_bug_handler(f):
    """
    We are working around an ipislon issue when people log in with their email,
    ipsilon then yields incorrect openid.identity:

      ERROR:root:Discovery verification failure for http://foo@fedoraproject.org.id.fedoraproject.org/

    The error above raises an exception in python-openid thus restarting the login process
    which turns into an infinite loop of requests. Since we drop the openid_error key from flask.session,
    we'll prevent the infinite loop to happen.

    Ref: https://pagure.io/ipsilon/issue/358
    """

    @functools.wraps(f)
    def _the_handler(*args, **kwargs):
        msg = flask.session.get("openid_error")
        if msg and "No matching endpoint found after discovering" in msg:
            # we need to advise to log out because the user will have an active FAS session
            # and the only way to break it is to log out
            logout_url = app.config["OPENID_PROVIDER_URL"] + "/logout"
            message = (
                    "You logged in using your email. <a href=\"https://pagure.io/ipsilon/issue/358\""
                    " target=\"_blank\">This is not supported.</a> "
                    "Please log in with your <em>FAS username</em> instead "
                    "<a href=\"%s\">after logging out here</a>." % logout_url
            )
            flask.session.pop("openid_error")
            flask.flash(message, "error")
            # do not redirect to "/login" since it's gonna be an infinite loop
            return flask.redirect("/")
        return f(*args, **kwargs)
    return _the_handler


@misc.route("/oidc_login/", methods=["GET"])
@auth.oidc_auth(app.config['OIDC_PROVIDER_NAME'])
def oidc_login():
    user_session = UserSession(flask.session)
    flask.session["oidc"] = user_session.userinfo['username']
    zoneinfo = user_session.userinfo['zoneinfo'] if 'zoneinfo' in user_session.userinfo and user_session.userinfo['zoneinfo'] else None
    return create_or_login(user_session.userinfo['username'], user_session.userinfo['email'], zoneinfo, None)

@misc.route("/login/", methods=["GET"])
@workaround_ipsilon_email_login_bug_handler
@oid.loginhandler
def login():
    if not app.config['FAS_LOGIN']:
        if app.config['KRB5_LOGIN']:
            return krb5_login_redirect(next=oid.get_next_url())
        flask.flash("No auth method available", "error")
        return flask.redirect(flask.url_for("coprs_ns.coprs_show"))

    if flask.g.user is not None:
        return flask.redirect(oid.get_next_url())
    else:
        # a bit of magic
        team_req = TeamsRequest(["_FAS_ALL_GROUPS_"])
        return oid.try_login(app.config["OPENID_PROVIDER_URL"],
                             ask_for=["email", "timezone"],
                             extensions=[team_req])

@oid.after_login
def oid_create_or_login(resp):
    team_resp = None
    flask.session["openid"] = resp.identity_url
    fasusername = fed_raw_name(resp.identity_url)
    if "lp" in resp.extensions:
        team_resp = resp.extensions['lp']  # name space for the teams extension

    return create_or_login(fasusername, resp.email, resp.timezone, team_resp)

def create_or_login(username, email, timezone, team_resp=None):
    # kidding me.. or not
    if username and (
            (
                app.config["USE_ALLOWED_USERS"] and
                username in app.config["ALLOWED_USERS"]
            ) or not app.config["USE_ALLOWED_USERS"]):

        user = models.User.query.filter(
            models.User.username == username).first()
        if not user:  # create if not created already
            app.logger.info("First login for user '%s', "
                            "creating a database record", username)
            user = UsersLogic.create_user_wrapper(username, email,
                                                  timezone)
        else:
            user.mail = email
            user.timezone = timezone
        if team_resp:
            user.openid_groups = {"fas_groups": team_resp.teams}

        db.session.add(user)
        db.session.commit()
        flask.flash(u"Welcome, {0}".format(user.name), "success")
        flask.g.user = user

        app.logger.info("%s '%s' logged in",
                        "Admin" if user.admin else "User",
                        user.name)

        if flask.request.url_root == oid.get_next_url():
            return flask.redirect(flask.url_for("coprs_ns.coprs_by_user",
                                                username=user.name))
        return flask.redirect(oid.get_next_url())
    else:
        flask.flash("User '{0}' is not allowed".format(fasusername))
        return flask.redirect(oid.get_next_url())

@misc.route("/logout/")
@auth.oidc_logout
def logout():
    if flask.g.user:
        app.logger.info("User '%s' logging out", flask.g.user.name)
    flask.session.pop("openid", None)
    flask.session.pop("krb5_login", None)
    flask.session.pop("oidc", None)
    flask.flash(u"You were signed out")
    return flask.redirect(oid.get_next_url())


def api_login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        api_login = None
        # flask.g.user can be already set in case a user is using gssapi auth,
        # in that case before_request was called and the user is known.
        if flask.g.user is not None:
            return f(*args, **kwargs)
        if "Authorization" in flask.request.headers:
            base64string = flask.request.headers["Authorization"]
            base64string = base64string.split()[1].strip()
            userstring = base64.b64decode(base64string)
            (api_login, token) = userstring.decode("utf-8").split(":")
        token_auth = False
        if token and api_login:
            user = UsersLogic.get_by_api_login(api_login).first()
            if (user and user.api_token == token and
                    user.api_token_expiration >= datetime.date.today()):
                token_auth = True
                flask.g.user = user
        if not token_auth:
            url = 'https://' + app.config["PUBLIC_COPR_HOSTNAME"]
            url = helpers.fix_protocol_for_frontend(url)

            msg = "Attempting to use invalid or expired API login '%s'"
            app.logger.info(msg, api_login)

            output = {
                "output": "notok",
                "error": "Login invalid/expired. Please visit {0}/api to get or renew your API token.".format(url),
            }
            jsonout = flask.jsonify(output)
            jsonout.status_code = 401
            return jsonout
        return f(*args, **kwargs)
    return decorated_function


def krb5_login_redirect(next=None):
    if app.config['KRB5_LOGIN']:
        # Pick the first one for now.
        return flask.redirect(flask.url_for("apiv3_ns.krb5_login",
                                            next=next))
    flask.flash("Unable to pick krb5 login page", "error")
    return flask.redirect(flask.url_for("coprs_ns.coprs_show"))


def login_required(role=RoleEnum("user")):
    def view_wrapper(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            if flask.g.user is None:
                return flask.redirect(flask.url_for("misc.login",
                                                    next=flask.request.url))

            if role == RoleEnum("admin") and not flask.g.user.admin:
                flask.flash("You are not allowed to access admin section.")
                return flask.redirect(flask.url_for("coprs_ns.coprs_show"))

            return f(*args, **kwargs)
        return decorated_function
    # hack: if login_required is used without params, the "role" parameter
    # is in fact the decorated function, so we need to return
    # the wrapped function, not the wrapper
    # proper solution would be to use login_required() with parentheses
    # everywhere, even if they"re empty - TODO
    if callable(role):
        return view_wrapper(role)
    else:
        return view_wrapper


# backend authentication
def backend_authenticated(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        auth = flask.request.authorization
        if not auth or auth.password != app.config["BACKEND_PASSWORD"]:
            return "You have to provide the correct password\n", 401

        return f(*args, **kwargs)
    return decorated_function


def req_with_copr(f):
    @wraps(f)
    def wrapper(**kwargs):
        coprname = kwargs.pop("coprname")
        if "group_name" in kwargs:
            group_name = kwargs.pop("group_name")
            copr = ComplexLogic.get_group_copr_safe(group_name, coprname, with_mock_chroots=True)
        else:
            username = kwargs.pop("username")
            copr = ComplexLogic.get_copr_safe(username, coprname, with_mock_chroots=True)
        return f(copr, **kwargs)
    return wrapper


def req_with_copr_dir(f):
    @wraps(f)
    def wrapper(**kwargs):
        if "group_name" in kwargs:
            ownername = '@' + kwargs.pop("group_name")
        else:
            ownername = kwargs.pop("username")
        copr_dirname = kwargs.pop("copr_dirname")
        copr_dir = ComplexLogic.get_copr_dir_safe(ownername, copr_dirname)
        return f(copr_dir, **kwargs)
    return wrapper


def send_build_icon(build, no_cache=False):
    """
    Sends a build icon depending on the state of the build.
    We use cache depending on whether it was the last build of a package, where the status can
    change in a minute, or a specific build, where the status will not change.
    :param build: build whose state we are interested in.
    :param no_cache: whether we want to cache the build state icon.
    :return: content of a file.
    """
    if not build:
        response = send_file("static/status_images/unknown.png", mimetype='image/png')
        if no_cache:
            response.headers['Cache-Control'] = 'public, max-age=60'
        return response

    if build.state in ["importing", "pending", "starting", "running"]:
        # The icon is about to change very soon, disable caches:
        # https://help.github.com/articles/about-anonymized-image-urls/
        response = send_file("static/status_images/in_progress.png",
                             mimetype='image/png')
        response.headers['Cache-Control'] = 'no-cache'
        return response

    if build.state in ["succeeded", "skipped"]:
        response = send_file("static/status_images/succeeded.png", mimetype='image/png')
    elif build.state == "failed":
        response = send_file("static/status_images/failed.png", mimetype='image/png')
    else:
        response = send_file("static/status_images/unknown.png", mimetype='image/png')

    if no_cache:
        response.headers['Cache-Control'] = 'no-cache'
        response.headers['Pragma'] = 'no-cache'
    return response


def req_with_pagination(f):
    """
    Parse 'page=' option from GET url, and place it as the argument
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            page = flask.request.args.get('page', 1)
            page = int(page)
        except ValueError as err:
            raise ObjectNotFound("Invalid pagination format") from err
        return f(*args, page=page, **kwargs)
    return wrapper
