#!/bin/env python
""" script to obtain release notes from DIRAC PRs
"""

from collections import defaultdict
from datetime import datetime, timedelta
import argparse
from pprint import pformat
import logging
import textwrap
import requests
from operator import itemgetter
import re
import os.path

try:
  from GitTokens import GITHUBTOKEN
except ImportError:
  raise ImportError(textwrap.dedent("""
                    ***********************
                    Failed to import GITHUBTOKEN please!
                    Point the pythonpath to your GitTokens.py file which contains
                    your "Personal Access Token" for Github

                    I.e.:
                    Filename: GitTokens.py
                    Content:
                    ```
                    GITHUBTOKEN = "e0b83063396fc632646603f113437de9"
                    ```
                    (without the triple quotes)
                    ***********************
                    """),
                    )

SESSION = requests.Session()
SESSION.headers.update({'Authorization': "token %s " % GITHUBTOKEN})

logging.basicConfig(level=logging.WARNING, format='%(levelname)-5s - %(name)-8s: %(message)s')
LOGGER = logging.getLogger('GetReleaseNotes')


def req2Json(url, parameterDict=None, requestType='GET'):
  """Call to github API using requests package."""
  log = LOGGER.getChild("Requests")
  log.debug("Running %s with %s ", requestType, parameterDict)
  req = getattr(SESSION, requestType.lower())(url, json=parameterDict)
  if req.status_code not in (200, 201):
    log.error("Unable to access API: %s", req.text)
    raise RuntimeError("Failed to access API")

  log.debug("Result obtained:\n %s", pformat(req.json()))
  return req.json()


def getCommands(*args):
  """Create a flat list.

  :param *args: list of strings or tuples/lists
  :returns: flattened list of strings
  """
  comList = []
  for arg in args:
    if isinstance(arg, (tuple, list)):
      comList.extend(getCommands(*arg))
    else:
      comList.append(arg)
  return comList


def checkRate():
  """Return the result for check_rate call."""
  rate = req2Json(url="https://api.github.com/rate_limit")
  LOGGER.getChild("Rate").info("Remaining calls to github API are %s of %s",
                               rate['rate']['remaining'], rate['rate']['limit'])


def _parsePrintLevel(level):
  """Translate debug count to logging level."""
  level = level if level <= 2 else 2
  return [logging.WARNING,
          logging.INFO,
          logging.DEBUG,
          ][level]


def getFullSystemName(name):
  """Translate abbreviations to full system names."""
  name = {'API': 'Interfaces',
          'AS': 'AccountingSystem',
          'CS': 'ConfigurationSystem',
          'Config': 'ConfigurationSystem',
          'Configuration': 'ConfigurationSystem',
          'DMS': 'DataManagementSystem',
          'DataManagement': 'DataManagementSystem',
          'FS': 'FrameworkSystem',
          'Framework': 'FrameworkSystem',
          'MS': 'MonitoringSystem',
          'Monitoring': 'MonitoringSystem',
          'RMS': 'RequestManagementSystem',
          'RequestManagement': 'RequestManagementSystem',
          'RSS': 'ResourceStatusSystem',
          'ResourceStatus': 'ResourceStatusSystem',
          'SMS': 'StorageManagamentSystem',
          'StorageManagement': 'StorageManagamentSystem',
          'TS': 'TransformationSystem',
          'TMS': 'TransformationSystem',
          'Transformation': 'TransformationSystem',
          'WMS': 'WorkloadManagementSystem',
          'Workload': 'WorkloadManagementSystem',
          }.get(name, name)
  return name


def parseForReleaseNotes(commentBody):
  """Look for "BEGINRELEASENOTES / ENDRELEASENOTES" and extend releaseNoteList if there are entries."""
  if not all(tag in commentBody for tag in ("BEGINRELEASENOTES", "ENDRELEASENOTES")):
    return ''
  return commentBody.split("BEGINRELEASENOTES")[1].split("ENDRELEASENOTES")[0]


def collateReleaseNotes(prs):
  """Put the release notes in the proper order.

  FIXME: Tag numbers could be obtained by getting the last tag with a name similar to
  the branch, will print out just the base branch for now.
  """
  releaseNotes = ""
  for baseBranch, pr in prs.iteritems():
    releaseNotes += "\n\n"
    systemChangesDict = defaultdict(list)
    for prid, content in pr.iteritems():
      notes = content['comment']
      system = ''
      for line in notes.splitlines():
        line = line.strip()
        if line.startswith("*"):
          system = getFullSystemName(line.strip("*:").strip())
        elif line:
          splitline = line.split(":", 1)
          if splitline[0] == splitline[0].upper() and len(splitline) > 1:
            line = "%s: (#%s) %s" % (splitline[0], prid, splitline[1].strip())
          systemChangesDict[system].append(line)

    for system, changes in systemChangesDict.iteritems():
      if system:
        releaseNotes += "*%s\n\n" % system
      releaseNotes += "\n".join(changes)
      releaseNotes += "\n\n"
    releaseNotes += "\n"

  return releaseNotes

def versionComp( v1, v2 ):
  """ compare version strings, problem is comparing
  v1r8p0 to v02-07-00 e.g. in lcio otherwise we could use normal string comparison
  needed for LCIO
  pre version are older than non-pre version
  """
  if v1 == v2:
    return 0

  pattern = re.compile( 'v([0-9]+)[r]([0-9]+)[-p]([0-9]+)')

  result1 = re.match( pattern, v1 )

  result2 = re.match( pattern, v2 )

  ## matching result1
  if result1 is not None and result2 is not None:
    ## both match, we can use string comparison
    pass
  elif result1 is not None and result2 is None:
    ## only 1 matches, 2 is always assumed to be bigger
    return -1
  elif result1 is None and result2 is not None:
    ## only 2 matches, 1 is considered bigger
    return 1
  else:
    ## neither matches, we can use string comparison
    pass

  if 'pre' in v1 and 'pre' in v2:
    ## use string comparison later
    pass

  elif 'pre' in v1:
    if v1.split('-pre')[0]==v2:
      return -1 # version 2 is not pre, so bigger
    return -1 if v1.split('-pre')[0] < v2 else 1

  elif 'pre' in v2:
    if v1==v2.split('-pre')[0]:
      return 1 # version 1 is not pre, so bigger
    return -1 if v1 <= v2.split('-pre')[0] else 1

  if v1 < v2:
    return -1
  else:
    return 1

class GithubInterface(object):
  """Object to make calls to github API."""

  def __init__(self, owner='diracos', repo='DIRACOS', lastTag=None):
    """Set default values to parse release notes for DIRAC."""
    self.owner = owner
    self.repo = repo
    self.branches = ['master']
    self.openPRs = False
    self.last = False
    self._lastTag = lastTag
    self.latestTagInfo = None
    self.startDate = str(datetime.now() - timedelta(days=14))[:10]
    self.printLevel = logging.WARNING
    LOGGER.setLevel(self.printLevel)
    self._getLatestTagInfo()
    self.newTag = None
    self.versionInfo = ""
    self.PRInfo = ""

  @property
  def _options(self):
    """Return options dictionary."""
    return dict(owner=self.owner, repo=self.repo)

  def parseOptions(self):
    """Parse the command line options."""
    log = LOGGER.getChild('Options')
    parser = argparse.ArgumentParser("Dirac Release Notes",
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("--branches", action="store", default=self.branches,
                        dest="branches", nargs='+',
                        help="branches to get release notes for")

    parser.add_argument("--date", action="store", default=self.startDate, dest="startDate",
                        help="date after which PRs are checked, default (two weeks ago): %s" % self.startDate)

    parser.add_argument("--openPRs", action="store_true", dest="openPRs", default=self.openPRs,
                        help="get release notes for open (unmerged) PRs, for testing purposes")

    parser.add_argument("--last", action="store_true", dest="last", default=self.last,
                        help="collect PRs since the last/latest tag")

    parser.add_argument("-d", "--debug", action="count", dest="debug", help="d, dd, ddd", default=0)

    parser.add_argument("-r", "--repo", action="store", dest="repo", help="Repository to check: [Group/]Repo",
                        default='DiracGrid/DIRACOS')

    parser.add_argument("--newTag", action="store", default=self.newTag, dest="newTag",
                         help="Convert a tag on Github to a release includeing version info")

    parser.add_argument("--versionInfo", action="store", default=self.versionInfo, dest="versionInfo",
                    help="Location of file containing version information")

    parser.add_argument("--PRInfo", action="store", default=self.PRInfo, dest="PRInfo",
                    help="Location of file containing PRInfo")

    parsed = parser.parse_args()

    self.printLevel = _parsePrintLevel(parsed.debug)
    LOGGER.setLevel(self.printLevel)

    self.branches = parsed.branches
    log.info('Getting PRs for: %s', self.branches)
    self.openPRs = parsed.openPRs
    log.info('Also including openPRs?: %s', self.openPRs)

    self.versionInfo = parsed.versionInfo
    self.PRInfo = parsed.PRInfo
    self.newTag = parsed.newTag
    if self.newTag is not None:
      self.createGithubRelease()

    self.last = parsed.last
    self.startDate = parsed.startDate
    if self.last :
      self.startDate = self.latestTagInfo['date'][:10]
    log.info('Starting from: %s', self.startDate)

    repo = parsed.repo
    repos = repo.split('/')
    if len(repos) == 1:
      self.repo = repo
    elif len(repos) == 2:
      self.owner = repos[0]
      self.repo = repos[1]
    else:
      raise RuntimeError("Cannot parse repo option: %s" % repo)

  def _github(self, action):
    """Return the url to perform actions on github.

    :param str action: command to use in the gitlab API, see documentation there
    :returns: url to be used
    """
    log = LOGGER.getChild('GitHub')
    options = dict(self._options)
    options["action"] = action
    ghURL = "https://api.github.com/repos/%(owner)s/%(repo)s/%(action)s" % options
    log.debug('Calling: %s', ghURL)
    return ghURL

  def getGithubPRs(self, state="open", mergedOnly=False, perPage=100):
    """Get all PullRequests from github.

    :param str state: state of the PRs, open/closed/all, default open
    :param bool merged: if PR has to be merged, only sensible for state=closed
    :returns: list of githubPRs
    """
    url = self._github("pulls?state=%s&per_page=%s" % (state, perPage))
    prs = req2Json(url=url)

    if not mergedOnly:
      return prs

    # only merged PRs
    prsToReturn = []
    for pr in prs:
      if pr.get('merged_at', None) is not None:
        prsToReturn.append(pr)

    return prsToReturn

  def getNotesFromPRs(self, prs):
    """Loop over prs, get base branch, get PR comment and collate into dictionary.

    :returns: dict of branch:dict(#PRID, dict(comment, mergeDate))
    """
    rawReleaseNotes = defaultdict(dict)

    for pr in prs:
      baseBranch = pr['base']['label'][len("diracos:"):]
      if baseBranch not in self.branches:
        continue
      comment = parseForReleaseNotes(pr['body'])
      prID = pr['number']
      mergeDate = pr.get('merged_at', None)
      mergeDate = mergeDate if mergeDate is not None else '9999-99-99'
      if mergeDate[:10] < self.startDate:
        continue

      rawReleaseNotes[baseBranch].update({prID: dict(comment=comment, mergeDate=mergeDate)})

    return rawReleaseNotes

  def getReleaseNotes(self):
    """Create the release notes."""
    if self.openPRs:
      prs = self.getGithubPRs(state='open', mergedOnly=False)
    else:
      prs = self.getGithubPRs(state='closed', mergedOnly=True)
    prs = self.getNotesFromPRs(prs)
    releaseNotes = collateReleaseNotes(prs)
    print releaseNotes
    checkRate()

  def getGithubTags( self):
    """ get all tags from github

    u'commit': {u'sha': u'49680c32f9c0734dcbf0efe2f01e2363dab3c64e',
                u'url': u'https://api.github.com/repos/andresailer/Marlin/commits/49680c32f9c0734dcbf0efe2f01e2363dab3c64e'},
    u'name': u'v01-02-01',
    u'tarball_url': u'https://api.github.com/repos/andresailer/Marlin/tarball/v01-02-01',
    u'zipball_url': u'https://api.github.com/repos/andresailer/Marlin/zipball/v01-02-01'},

    :returns: list of tags
    """
    result = req2Json(url=self._github("tags"))
    if isinstance( result, dict ) and 'Not Found' in result.get('message'):
      raise RuntimeError( "Package not found: %s" % str(self) )
    return result

  def _getLatestTagInfo( self ):
    """ fill the information about the latest tag in the repository"""
    log = LOGGER.getChild('LatestTagInfo')
    if self.latestTagInfo is not None:
      log.debug( "Latest Tag Info already filled" )
      return self.latestTagInfo ## already filled
    tags = self.getGithubTags()
    sortedTags = sorted(tags, key=itemgetter("name"), reverse=True, cmp=versionComp)
    if self._lastTag is None:
      di = sortedTags[0]
    else:
      try:
        di = [ tagInfo for tagInfo in tags if tagInfo['name'] == self._lastTag][0]
      except IndexError:
        raise RuntimeError( "LastTag given, but not found in tags for this package")
    self.latestTagInfo = di
    self.latestTagInfo['pre'] = True if 'pre' in di['name'] else False
    self.latestTagInfo['sha'] = di['commit']['sha']
    log.info( "Found latest tag %s", di['name'] )


    if not tags:
      log.warning( "No tags found for %s", self )
      self.latestTagInfo={}
      self.latestTagInfo['date'] = "1977-01-01T"
      self.latestTagInfo['sha'] = "SHASHASHA"
      self.latestTagInfo['name'] = "00-00"
    else:
      commitInfo = req2Json(url=self._github("git/commits/%s" % self.latestTagInfo['sha']))
      self.latestTagInfo['date'] = commitInfo['committer']['date']

    return self.latestTagInfo

  def formatReleaseNotes( self ):
    """ print the release notes """
    PRText = ""
    if os.path.isfile(self.PRInfo):
      PRs = open(self.PRInfo, "r")
      PRText = PRs.read()
    else:
      LOGGER.error("Did not find file containing PRs at path: %s", self.PRInfo)
      exit(1)

    versionText = ""
    if os.path.isfile(self.versionInfo):
      versions = open(self.versionInfo, "r")
      versionText = versions.read()
    else:
      LOGGER.error("Did not find file containing version information at path: %s", self.versionInfo)
      exit(1)
    return "## This release contains the following PRs \n %s## Included versions of packages\n %s" % (PRText, versionText.split("\n",1)[1])


  def createGithubRelease( self ):
    """ make a release on github """

    releaseDict = dict( tag_name=self.newTag,
                       target_commitish="master",
                       name=self.newTag,
                       body=self.formatReleaseNotes(),
                       prerelease=False,
                       draft=False,
                       )

    result = req2Json(url=self._github( "releases" ), parameterDict=releaseDict, requestType='POST')
    return result

if __name__ == "__main__":

  RUNNER = GithubInterface()
  try:
    RUNNER.parseOptions()
  except RuntimeError as e:
    LOGGER.error("Error during argument parsing: %s", e)
    exit(1)

  try:
    RUNNER.getReleaseNotes()
  except RuntimeError as e:
    LOGGER.error("Error during runtime: %s", e)
    exit(1)
