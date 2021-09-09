import requests
import argparse
import os
import base64

# TODO: burn after read
# TODO: proxies

# max paste length
CHUNKSIZE = 104857600

def main():
    parser = argparse.ArgumentParser(description="create a pastezip file\n"\
                        "note: PASTEBIN_API_KEY must be set as an env var",
                        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("mode", choices=["c", "e"], nargs=1,
                        help="c to archive, e to extract")
    parser.add_argument("file", metavar="FILE", nargs=1,
                        help="file to archive")
    parser.add_argument("--encrypt", metavar="PASS", nargs=1,
                        help="password to encrypt pastes with")
    args = parser.parse_args()

    if args.mode[0] == "c":
        archive(args)
    elif args.mode[0] == "e":
        unarchive(args)


def archive(args):
    PASTEBIN_API_KEY = os.getenv("PASTEBIN_API_KEY")
    if not PASTEBIN_API_KEY:
        exit("$PASTEBIN_API_KEY not set, exiting...")

    urls = []

    f_content = None
    with open(args.file[0], "rb") as f:
        f_content = f.read()
    b64_f_content = base64.b64encode(f_content)

    chunks = len(b64_f_content) // CHUNKSIZE + 1
    for chunk_i in range(chunks):
        chunk_c = b64_f_content[chunk_i: chunk_i + CHUNKSIZE].decode("ascii")
        r_data = {"api_dev_key": PASTEBIN_API_KEY, "api_option": "paste", "api_paste_code": chunk_c}
        if args.encrypt:
            r_data["api_paste_private"] = 2
            r_data["is_password_enabled"] = 1
            r_data["password"] = args.encrypt
        r = requests.post("https://pastebin.com/api/api_post.php", data=r_data)
        if r.status_code != 200:
            exit("request failed, exiting...")
        urls.append(r.text)

    with open(f"{args.file[0]}.pzip", "w") as of:
        [of.write(f"{url}\n") for url in urls]

def unarchive(args):
    with open(args.file[0], "r") as f:
        urls = f.readlines()

    b64_f_content = b""

    for url in urls:
        r = requests.get(url)
        b64_f_content = b64_f_content + r.text

    f_content = base64.b64decode(b64_f_content)
    with open(f"{args.file[0]}.pzip", "w") as f:
        f.write(f"{f_content}")


if __name__ == "__main__":
    main()
