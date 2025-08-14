import sys
from linkedin_api import Linkedin


def main() -> int:
    if len(sys.argv) < 3:
        print("Usage: python scripts/get_linkedin_session_token.py <email> <password>")
        return 1

    email = sys.argv[1]
    password = sys.argv[2]

    client = Linkedin(email, password)

    cookies = client.client.session.cookies.get_dict()
    jsession = cookies.get("JSESSIONID")
    li_at = cookies.get("li_at")

    # Print both tokens in a simple key=value format
    if jsession:
        print(f"JSESSIONID={jsession}")
    else:
        print("JSESSIONID=<not_found>")

    if li_at:
        print(f"li_at={li_at}")
    else:
        print("li_at=<not_found>")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
