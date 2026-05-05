"""
amb_print.install
=================

App lifecycle hooks — currently handles Chromium binary download for the
Independent PDF Generator so amb_print self-installs its rendering
dependency on `bench install-app` or via a manual setup call.

Split of concerns
-----------------
- OS libs (libnss3, libgbm1, libatk1.0, libxshmfence, …): need root.
  Live in the Docker image (see the apt-get block in the custom-erpnext
  Dockerfile). NOT this module's job.
- Playwright Python wheel: declared in pyproject.toml, installed by
  `bench setup requirements`. NOT this module's job.
- Chromium binary (~270 MB): installed by `playwright install chromium`
  into PLAYWRIGHT_BROWSERS_PATH. THIS module's job. Idempotent — Playwright
  is a no-op when the binary is already at the target path.

Failures here are NEVER fatal to app install. The wkhtmltopdf fallback
in `amb_print.pdf` covers the gap until an operator re-runs setup.
"""

from __future__ import annotations

import os
import subprocess
import sys

import frappe


DEFAULT_BROWSERS_PATH = "/opt/playwright-browsers"


def after_install() -> None:
    """Frappe hook — runs after `bench install-app amb_print` completes.

    Registered via `hooks.py: after_install = "amb_print.amb_print.install.after_install"`.
    """
    print("amb_print: setting up Chromium for Independent PDF Generator...")
    result = install_chromium_binary()
    if result["ok"]:
        print(f"amb_print: Chromium ready at {result['path']}")
    else:
        # Log but don't abort — wkhtmltopdf fallback keeps the button working
        msg = (
            f"Chromium install failed: {result['error']}. "
            "amb_print will use the wkhtmltopdf fallback until an operator "
            "runs `bench --site <site> execute "
            "amb_print.amb_print.install.setup_chromium`."
        )
        try:
            frappe.log_error(message=msg, title="amb_print: Chromium install")
        except Exception:
            pass
        print(f"amb_print: WARNING — {msg}")


@frappe.whitelist()
def setup_chromium() -> dict:
    """Public method to (re)install Chromium on demand.

    Use cases:
        - First-time setup on a fresh bench (e.g. after `docker compose up`
          on a new container, when after_install never ran).
        - Recovery after a Docker image rebuild that didn't include the
          Chromium binary.
        - Switching PLAYWRIGHT_BROWSERS_PATH to a new location.

    Invocation:
        bench --site <site> execute amb_print.amb_print.install.setup_chromium

    Returns
    -------
    dict
        {"ok": bool, "path": str, "error": str | None,
         "playwright_version": str | None}
    """
    return install_chromium_binary()


def install_chromium_binary() -> dict:
    """Run `playwright install chromium`. Idempotent.

    Honors PLAYWRIGHT_BROWSERS_PATH if already set in the environment;
    otherwise falls back to a sensible default per deployment shape:
        - Inside Docker (detected via /.dockerenv): /opt/playwright-browsers
        - Bare metal / dev:                         <bench>/playwright-browsers

    Returns
    -------
    dict
        ok      : True on success
        path    : the resolved PLAYWRIGHT_BROWSERS_PATH (also exported)
        error   : stderr/exception message when ok=False, else None
        playwright_version : "1.59.0" etc. when importable, else None
    """
    browsers_path = os.environ.get("PLAYWRIGHT_BROWSERS_PATH") \
        or _default_browsers_path()
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = browsers_path

    # Probe playwright version (also confirms the wheel is installed)
    pw_version: str | None = None
    try:
        import playwright  # type: ignore
        pw_version = getattr(playwright, "__version__", None)
    except ImportError:
        return {
            "ok": False,
            "path": browsers_path,
            "error": (
                "playwright Python package not installed. Run "
                "`bench setup requirements` (or pip install playwright>=1.50,<2.0) "
                "and retry."
            ),
            "playwright_version": None,
        }

    py = sys.executable
    try:
        result = subprocess.run(
            [py, "-m", "playwright", "install", "chromium"],
            capture_output=True,
            text=True,
            timeout=600,  # ~270MB download — generous but bounded
        )
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "path": browsers_path,
            "error": "playwright install chromium timed out after 10 minutes",
            "playwright_version": pw_version,
        }
    except Exception as e:
        return {
            "ok": False,
            "path": browsers_path,
            "error": f"{type(e).__name__}: {e}",
            "playwright_version": pw_version,
        }

    if result.returncode != 0:
        return {
            "ok": False,
            "path": browsers_path,
            "error": (result.stderr or result.stdout or "unknown")[:2000],
            "playwright_version": pw_version,
        }

    return {
        "ok": True,
        "path": browsers_path,
        "error": None,
        "playwright_version": pw_version,
    }


def _default_browsers_path() -> str:
    """Pick a sensible default PLAYWRIGHT_BROWSERS_PATH if not set."""
    if os.path.exists("/.dockerenv"):
        return DEFAULT_BROWSERS_PATH  # /opt/playwright-browsers
    bench = os.path.expanduser("~/frappe-bench")
    if os.path.isdir(bench):
        return os.path.join(bench, "playwright-browsers")
    return os.path.expanduser("~/playwright-browsers")
