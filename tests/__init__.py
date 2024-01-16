# An empty file such as this one was typically used in the 'olden days' to
# denote a directory as a package that can be imported.
#
# Having an empty __init__.py file is generally no longer necessary for this
# purpose, ever since python introduced 'namespace packages'.
#
# However, a crucial difference between the two is that a package defined with
# an explicit __init__.py file will return this file if the __file__ attribute
# is requested at runtime.
#
# In python 3.6, a namespace package would return an AttributeError if one
# attempted to request the __file__ attribute at runtime. From at least 3.8
# onwards, this returns None instead, without triggerring an error.
#
# Apparently this has caused a regression error with unittest, which still seems
# to rely on the Error behaviour of __file__ to detect namespace packages,
# causing 'discovery' mode to fail (see: https://github.com/tpapastylianou/self-contained-runnable-python-package-template/issues/13)
#
# Thankfully, the fix is as simple as creating this empty __init__.py file,
# which then causes discovery mode to find a __file__ attribute and proceed
# normally.
