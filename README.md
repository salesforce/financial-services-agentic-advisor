# Next Gen Wealth


## Description

This is a repository for next generation wealth and contains artifacts that use the FinServ wealth package. By installing this package you get all of the FinServ artifacts used by NextGenWealth even though you may use only some of them.

Refer to [CONTENTS](CONTENTS.md) to see the contents of this package.

If you use a mix of package and core objects, you may modify the artifacts that get installed.


## Installing

There are 3 ways to install this package.

### sf

Download this GitHub repository to your computer.  Then use sf to log in to an org, then sf project deploy start to deploy it.  Be sure to change the *myalias* to something that makes sense to you.

```
# to log in to an org
sf org login web -d -a myalias -r url

# to list orgs
sf org list

# to deploy the package
cd NextGenWealth
sf project deploy start --manifest package.xml --target-org myalias --ignore-conflicts --ignore-warnings --wait 30
```

### Claude skill

Note: This method is still under development.

Add the [DeployNextGenWealth](skills/DeployNextGenWealth.md) skill to claude then run
```
Deploy the NextGenWealth repository.
```

### Workbench

Download this GitHub repository to your computer.  Run `./tools/createZip` to create a single zip file called NextGenWealth.zip.

Install [workbench from the chrome web store](https://chromewebstore.google.com/detail/workbench/konbmllgicfccombdckckakhnmejjoei?hl=en)

Open Workbench and log in to your org.

Go to Deploy -> Deploy/Retrieve and click Deploy button.  Find the file NextGenWealth.zip and click Run.
