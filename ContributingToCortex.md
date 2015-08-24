The cortex wiki is now hosted at https://github.com/ImageEngine/cortex/wiki
#summary How you can contribute to the Cortex project
#labels Featured

# Introduction #

We would like to keep it as simple as possible to contribute to Cortex in order to encourage as much participation as possible. However, in order to maintain quality and robustness we ask you to try and adhere to the following guidelines whilst making your submissions.

## Coding Conventions ##

We realize that everyone has their own style of coding, but in order to keep the libraries consistent, we're documenting the preferred coding conventions for contributions to Cortex. Please try to follow these guidelines, and if in doubt, don't hesitate to post to the [cortexdev group](http://groups.google.com/group/cortexdev).

Here is a [C++ example](CppCodingConventions.md) and a [Python example](PythonCodingConventions.md) which include syntax, documentation, layout, and class/variable naming conventions. In IECoreMaya we try to use as little mel as possible, but if mel necessary, try to follow the C++ guidelines.

We apologize in advance for not following our own guidelines to the letter. We will try to commit such layout fixes as we come across them.

## Bugs ##

Discuss the bug in the [cortexdev group](http://groups.google.com/group/cortexdev), to clarify whether or not the behavior you are experiencing is expected or not, or whether it's already a known issue.

  * Once a bug has been identified, use the Issue Tracker to log it.
  * Where possible, submit a Python unit test case that exercises the bug. Name the test file IssueXXXXXTest.py where XXXXX is the Issue ID. Attach the file to the Issue, and a Project Member will integrate it with the test suite.
  * If you also wish to submit a patch which fixes the bug, please see below.

## Patches ##

Any new major functionality should be first be discussed in the [cortexdev group](http://groups.google.com/group/cortexdev), to ensure that it fits within the spirit of the Cortex project. All patches will be considered for inclusion, but you stand a better chance if following the guidelines:

  * Do not introduce any new unnecessary dependencies (we already link to Boost, OpenEXR, Free Type, libtiff, libjpeg, Python, Maya, Nuke, OpenGL, etc, etc!)
  * Keep different features, bug fixes, etc, in separate patches.
  * Please try and follow the coding style already present in the code base, most notably :
    * Use tabs for indentation, not spaces.
    * Do not assume the width of a tab character, so in some cases it may even be necessary to use a combination of tabs (for indent) and spaces (for formatting) on the same line.
    * Keep curly braces delimiting blocks on a line of their own.
    * Don't leave in any commented-out code, as this can confuse future maintainers
    * When in doubt, copy the style of the surrounding code.
  * Comment / assert / document as much as you can.
  * Try not to disturb any surrounding code unnecessarily.
  * Keep changes to formatting in separate patches to new code.
  * Where applicable, please submit a unit test to exercise the functionality of your patch, ensuring that all tests pass against a recently updated trunk.
  * State which platforms your patch has been tested successfully on. Don't worry if only one platform is available to you, as we can run tests internally on multiple platforms.
  * For optmisations, please try to measure and quantify the performance benefits.

To submit a patch :

  * Open a Issue for it using the Issue Tracker, describing the purpose of the patch as much as possible.
  * From the root directory (where the SConstruct file resides), run "svn diff > XXXXX.patch" where "XXXXX" is the numeric Issue ID.
  * Attach the patch file to the Issue.