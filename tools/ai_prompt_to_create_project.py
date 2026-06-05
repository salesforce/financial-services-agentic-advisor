Write a python script tools/CreateProject.py
cd into the folder that is the parent of CreateProject.py (using the __file__ keyword).


Use argparse to make this script accept the following arguments
- namespace (string, optional, defaults to "FinServ")
- exclude (string, comment is "comma separated list of types to exclude with no spaces before/after the comma")
- target-directory (string, defaults to $TMPDIR or the equivalent in Windows)
- help
The comment for the the entire parser is "Create a project to called ClonedcNextGenWealth to deploy the next gen wealth project"

Error out if <target-directory>/ClonedNextGenWealth exists
Call the equivalent of `cp -r NextGenWealth <target-directory>`

Then cd NextGenWealth, and call the function build_artifact_map from CreateContents.py.

Now cd to the ClonedNextGenWealth folder you created above.

If namespace is anything other than "FinServ" the replace "FinServ__" in all files with the value of namespace + "__".

Now call find_roots from CreateContents.py to get a list of root artifacts.
If any of these artifact's info.type is one of the types to exclude ignoring case, remove this artifact from the list of root artifacts. The code comment should say "remove excluded artifact and it's children".

Walk the remaining root artifacts, descending into the outgoing for each, and generate package.xml, overwriting the existing one in this tmp location as follows:

```
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <name>type</name>
        <members>name1</members>
        <members>name2</members>
    </types>
    <version>67.0</version>
</Package>
```

Here type comes from artifact's info's type, and name comes from the artifact's info's name.

Now cd ClonedNextGenWealth and zip package.xml and all folders into a file called SinglePackage.zip.

Write to stdout "Created sf project " full path of ClonedNextGenWealth, followed by "Zip file " full path of SinglePackage.zip, followed by the values for namespace and exclude on separate lines.
