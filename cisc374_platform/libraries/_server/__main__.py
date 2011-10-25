# boilerplate to allow running as script directly
if __name__ == "__main__" and __package__ is None or __package__ == '':
    import sys, os
    # The following assumes the script is in the top level of the package
    # directory.  We use dirname() to help get the parent directory to add to
    # sys.path, so that we can import the current package.  This is necessary 
    # since when invoked directly, the 'current' package is not automatically
    # imported.
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, parent_dir)
    import _server
    import config
    __package__ = '_server'
    _server.run()