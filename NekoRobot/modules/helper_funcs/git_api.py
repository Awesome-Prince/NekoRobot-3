import json
import urllib.request as url

VERSION = "1.1.0"
APIURL = "https://api.github.com/repos/"


async def vercheck() -> str:
    return str(VERSION)


# Repo-wise stuff


async def getData(repoURL):
    try:
        with url.urlopen(APIURL + repoURL + "/releases") as data_raw:
            repoData = json.loads(data_raw.read().decode())
            return repoData
    except:
        return None


async def getReleaseData(repoData, index):
    if index < len(repoData):
        return repoData[index]
    return None


# Release-wise stuff


async def getAuthor(releaseData):
    if releaseData is None:
        return None
    return releaseData["author"]["login"]


async def getAuthorUrl(releaseData):
    if releaseData is None:
        return None
    return releaseData["author"]["html_url"]


async def getReleaseName(releaseData):
    if releaseData is None:
        return None
    return releaseData["name"]


async def getReleaseTag(releaseData):
    if releaseData is None:
        return None
    return releaseData["tag_name"]


async def getReleaseDate(releaseData):
    if releaseData is None:
        return None
    return releaseData["published_at"]


async def getAssetsSize(releaseData):
    if releaseData is None:
        return None
    return len(releaseData["assets"])


async def getAssets(releaseData):
    if releaseData is None:
        return None
    return releaseData["assets"]


async def getBody(releaseData):  # changelog stuff
    if releaseData is None:
        return None
    return releaseData["body"]


# Asset-wise stuff


async def getReleaseFileName(asset):
    return asset["name"]


async def getReleaseFileURL(asset):
    return asset["browser_download_url"]


async def getDownloadCount(asset):
    return asset["download_count"]


async def getSize(asset):
    return asset["size"]
