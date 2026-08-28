import os
import threading

from python_aternos import Client


# ============================================================
# CONFIG
# ============================================================

ATERNOS_SESSION = os.getenv(
    "ATERNOS_SESSION",
    ""
).strip()

ATERNOS_SERVER_ADDRESS = os.getenv(
    "ATERNOS_SERVER_ADDRESS",
    "MACESMP37.aternos.me"
).strip()

_lock = threading.Lock()

_client = None
_account = None
_server = None


# ============================================================
# LOGIN
# ============================================================

def get_client():
    global _client

    with _lock:

        if _client is not None:
            return _client

        if not ATERNOS_SESSION:
            raise RuntimeError(
                "ATERNOS_SESSION غير موجود في Environment Variables"
            )

        client = Client()

        client.login_with_session(
            ATERNOS_SESSION
        )

        _client = client

        return _client


# ============================================================
# SERVER
# ============================================================

def get_server():

    global _account
    global _server

    with _lock:

        if _server is not None:
            return _server

        client = get_client()

        _account = client.account

        servers = _account.list_servers()

        if not servers:
            raise RuntimeError(
                "لم يتم العثور على أي سيرفر في حساب Aternos"
            )

        wanted = ATERNOS_SERVER_ADDRESS.lower()

        # البحث بالعنوان
        for server in servers:

            address = str(
                getattr(
                    server,
                    "address",
                    ""
                )
            ).lower()

            if address == wanted:

                _server = server

                return _server

        # إذا لم يجد العنوان يستخدم أول سيرفر
        _server = servers[0]

        return _server


# ============================================================
# REFRESH SERVER
# ============================================================

def refresh_server():

    global _server

    with _lock:
        _server = None

    return get_server()


# ============================================================
# START
# ============================================================

def start_server():

    server = get_server()

    server.start()

    return get_server_status()


# ============================================================
# STOP
# ============================================================

def stop_server():

    server = get_server()

    server.stop()

    return get_server_status()


# ============================================================
# RESTART
# ============================================================

def restart_server():

    server = get_server()

    server.restart()

    return get_server_status()


# ============================================================
# STATUS
# ============================================================

def get_server_status():

    server = get_server()

    # محاولة تحديث معلومات السيرفر
    try:
        server.update()
    except Exception:
        pass

    status = getattr(
        server,
        "status",
        None
    )

    if status is None:
        status = getattr(
            server,
            "state",
            "unknown"
        )

    return {
        "status": str(status),
        "address": str(
            getattr(
                server,
                "address",
                ATERNOS_SERVER_ADDRESS
            )
        ),
        "software": str(
            getattr(
                server,
                "software",
                "Unknown"
            )
        ),
        "version": str(
            getattr(
                server,
                "version",
                "Unknown"
            )
        )
    }


# ============================================================
# INFORMATION
# ============================================================

def get_server_info():

    server = get_server()

    try:
        server.update()
    except Exception:
        pass

    return {
        "name": str(
            getattr(
                server,
                "name",
                "Unknown"
            )
        ),
        "address": str(
            getattr(
                server,
                "address",
                ATERNOS_SERVER_ADDRESS
            )
        ),
        "status": str(
            getattr(
                server,
                "status",
                "unknown"
            )
        ),
        "software": str(
            getattr(
                server,
                "software",
                "Unknown"
            )
        ),
        "version": str(
            getattr(
                server,
                "version",
                "Unknown"
            )
        )
}
