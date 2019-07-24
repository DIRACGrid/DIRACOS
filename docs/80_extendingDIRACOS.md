# Extending DIRACOS

Although DIRACOS tries to address most of the VOs needs, it might be that it does not fulfil everything. DIRACOS comes with some extension capabilities described bellow.

## Requesting a package to be added in DIRACOS

If you think a package (RPMs or python) should be added to DIRACOS, please open a [github issue](https://github.com/DIRACGrid/DIRACOS/issues), which will be marked with the `PackageRequest` tag. If it gathers enough thumbs up (Let say 5 from different VO), we will consider adding it.

Note that it is not a guarantee, because we have to take into account other constraints (for example size).

**Spoiler alert**: if you are asking for a new RPM, opening together the issue with a pull request will greatly serve your cause...


## Adding pure python packages


In case you are extending just pure python packages, you should be able to do it an any machine supported by DIRACOS (SLC6/CC7).

### Initial setup

```
# Install the few tools needed
yum install -y jq python-pip git

# Install the diracos machinery (currently from github)
pip install git+https://github.com/DIRACGrid/DIRACOS.git
```

### Configuration files

The only thing you need is a json configuration file and a pip `requirements.txt` file containing your new packages.

The configuration file contains now only the following lines:

```
{
  "extensionName": <name of your extension>,
  "diracOsVersion": <version of DIRACOS on which to base the build>,
  "version": <version of the extension you are building>,
  "pipRequirements": <path to the pip requirements.txt>
}
```

Please see [ Configuration Grammar](docs/40_grammar.md#configuration-grammar) for more details.

### Building the extension

Simply call
```
dos-build-extension myextension.json
```

This will generate the new archive file.


## Adding RPM packages or compiled python packages

Because there was no usecases yet, this is not implemented, and the simplest is that you build your own DIRACOS with your own json configuration file.

## Removing packages

Because this is such a fragile operation, this is not and will not be supported. Just rebuild DIRACOS with your own json configuration file.


## Using DIRACOS extension in your DIRAC extension

You need to define the following two parameters:

* In the `releases.cfg` as a dependency of your release:
  ```
  DIRACOS = <extensionName>:<extensionVersion>
  ```

* In your project configuration (defined in`DefaultsLocation` used by `dirac-install` )
  ```
  DIRACOS = <the web page where you host the DIRACOS extensions>
  ```
