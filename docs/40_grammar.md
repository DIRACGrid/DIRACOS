
# Configuration Grammar

The json formated files is used to describe what packages to build, as well as the environment in which to build it.


## rpmBuild section
This part of the configuration is used to build the RPMs. It is the `rpmBuild` attribute at the root of the json file.

The grammar is very flexible in the sense that no attribute is forbidden. The packages configuration is built by aggregating all the options as explained bellow, and each package is built in turn. There are however a few mandatory parameters.

### Package and PackageGroup

In order to simplify the configuration and make it more readable, the packages to build are organized in a sorted list (rpmBuild), grouped by "packageGroup". The complete package configuration will be the global configuration, on top of which we add the packageGroup configuration, on top of which we add the package specific configuration. For example:

```
{
   "rpmBuild" :
   {
     "opt1" : 1,
     "packageGroups" : [
         {
            "name" : "pkgGrp1",
            "opt1" : 2,
            "packages" : [
                {
                   "name" : "pkg1",
                   "opt2" : "x"
                },
                {
                   "name" : "pkg2",
                   "opt1" : 3
                }
            ]
         }
     ]
  }
}
```

This will give the following packages:

```
{
   "name" : "pkg1",
   "opt1" : 2,
   "opt2" : "x"
}
{
   "name" : "pkg2",
   "opt1" : 3
}
```




#### Mandatory parameters


At the moment, there are no checks, but the program will crash.

* `mockConfig`: mock configuration file to use for the build
* `mockRoot`: root directory where mock will work. WARNING: this value is related to the configuration in mockConfig.
* `name`: The name of the package. Should be unique (CAUTION: no check on that yet). It is only used internaly.
* `packageGroups`: list of package groups. Must be there at the root of the json file.
* `packages`: each packageGroup should have a list of packages
* `patchDir`: directory where to look for the patches
* `repo`: path to the repository where to copy the produced RPMs
* `routineDir`: directory where to look for routines
* `src`: The source of the package. Depending on what is passed here, the build procedure is slightly different. Currently, the src can either be the url of a SRPM, or the name of a fedora package.



#### Optional parameters

* `branch`: usefull only when building fedpkg. This is the branch of the repo to build.
* `buildOnly`: boolean. if True, the RPMs are put in a different folder of the repository and are not considered for installation (unless required as dependency)
* `excludePatterns`: list of patterns against which the produced RPMs are matched. The RPMs matching any of these patterns are not copied to the repository. This is usefull to exclude for example doc or debuginfo RPMs straight after building them. Be careful that sometimes, the doc RPMs are required as dependencies...
* `pkgList`: list of RPMs to copy once the build is done. All the others are not copied.
* `workDir`: directory where the work will be done. Default to `/tmp`

Any other options will be read and passed to the build functions. Usefull examples can be "comment", or any other options your routines may need.

## Other sections and options

* `ignoredPackages`: this list contains the packages that should not be taken for a reason or another when doing the final bundling.
* `mockInstallConfig`: mock configuration file to use for the build of python module and packaging
* `mockInstallRoot`: root directory where mock will work. WARNING: this value is related to the configuration in mockConfig.
* `pipBuildDependencies`: list of rpm packages required to perform the pip install
* `pipRequirements`: url/path to the requirements.txt file to feed pip
* `removedFolders`: list of absolute path of folders that are considered useless and can be removed at the end of the build
* `version`: version of dirac os (or diracos extension) being built (just a tag...)

## Extension specific options

* `extensionName`: name of the extension. This name will be prepended to the extension tarfile
* `diracOsVersion`: version of DIRACOS on top of which to build the extension
