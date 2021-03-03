def entry_point(argv):
    print "Hello, World %s" % argv
    return 0

def target(*args):
    return entry_point
