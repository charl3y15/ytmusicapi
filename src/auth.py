import os

class AuthHelper:
    @staticmethod
    def get_auth_file_env(required=True):
        value = os.getenv('YTMUSIC_AUTH_FILE', None)
        if required and value is None:
            raise RuntimeError("Missing required environment variable: YTMUSIC_AUTH_FILE")
        return value

    @staticmethod
    def resolve_auth_file(auth_file):
        import os
        if os.path.isabs(auth_file) and os.path.exists(auth_file):
            return auth_file
        if os.path.exists(auth_file):
            return auth_file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        auth_path = os.path.join(script_dir, '..', 'auth', os.path.basename(auth_file))
        if os.path.exists(auth_path):
            return auth_path
        raise RuntimeError(f"Auth file not found: {auth_file}") 