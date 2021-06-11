import requests


class NeteaseApi:
    BASE_URL = "https://api.moeblog.vip/163/"

    @classmethod
    def query(cls, **params) -> requests.Response:
        url = cls.BASE_URL + "?" + "&".join([f"{k}={v}" for (k, v) in params.items()])
        return requests.get(url)

    @classmethod
    def url(cls, id: str):
        r = cls.query(type="url", id=id, br="320")
        if not r.status_code == 200:
            raise Exception("Fail to get music file url")
        return r.json()["url"]

    @classmethod
    def lyric(cls, id: str):
        r = cls.query(type="lyric", id=id, br="320")
        if not r.status_code == 200:
            raise Exception("Fail to get song lyrics")
        return r.json()["lyric"]

    # @classmethod
    # def pic(cls)
