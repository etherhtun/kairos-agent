"""
jobs/ssl_fix.py
===============
Single-source SSL fix for Kairos Agent.

Strategy 1: truststore — injects macOS Keychain into Python's ssl module.
  Works on all Macs (Intel + Apple Silicon) without a bundled CA file.
  Covers regional CAs that certifi's static bundle may miss.

Strategy 2: certifi fallback — patches ssl.create_default_context with
  the certifi Mozilla CA bundle. Used if truststore is unavailable
  (e.g. non-macOS, or truststore import fails).

Call this BEFORE any network import in every entry point.
"""

try:
    import truststore
    truststore.inject_into_ssl()          # uses macOS Security framework
except Exception:
    try:
        import ssl as _ssl
        import certifi as _certifi
        _ca = _certifi.where()
        _orig = _ssl.create_default_context
        def _patch(*args, **kwargs):
            if not any(k in kwargs for k in ('cafile', 'cadata', 'capath')):
                kwargs['cafile'] = _ca
            return _orig(*args, **kwargs)
        _ssl.create_default_context = _patch
    except Exception:
        pass
