import PyHussie
import os
import subprocess
import sys
from time import strftime
from datetime import datetime

###############################################################
#OUTPUT ZONE: that's where we get to throw something at user
###############################################################

def read_page(pagenumber, fieldnumber, root = os.curdir):
    """Reads the page. Takes a pagenumber and the number of the field. Negative numbers are special: -3 makes the function print out just a raw contents of the file, -2 prints out a pretty version, -1 just spit the content of each entry in the page list, and -4 throw a pretty version of page's timestamp. Returns nothing."""
    try:
        if fieldnumber == -3: #Wooo, magic!
            sys.stdout.write(PyHussie.get_trans_page(pagenumber, root))
            return
        page = PyHussie.get_parsed_trans_page(pagenumber, root)
        if fieldnumber == -2: #More magic!
            sys.stdout.write("=====" + page[0] + "=====\n")
            sys.stdout.write("Hash/meta: " + page[1] + "\n")
            sys.stdout.write("Date/time: " + datetime.fromtimestamp(int(page[2])).strftime('%Y-%b-%d %H:%M:%S') + "\n")
            sys.stdout.write("Visuals/interactives: " + page[3] + "\n")
            sys.stdout.write("-----BEGIN CONTENT-----\n")
            sys.stdout.write("Visuals/interactives: " + page[4] + "\n")
            sys.stdout.write("-----END CONTENT-----\n")
            sys.stdout.write("Next page/pages: \n")
            sys.stdout.write(page[5] + "\n")
            return
        if fieldnumber == -1: #More magic that is more magic than just magic!
            for field in page: sys.stdout.write(field + "\n")
            return
        if fieldnumber == -4: #FSCKIN' MIRACLES!!11
            sys.stdout.write("Date/time: " + datetime.fromtimestamp(int(page[2])).strftime('%Y-%b-%d %H:%M:%S') + "\n")
            return
        sys.stdout.write(page[fieldnumber] + "\n")
    except TypeError:
        show_page_not_found(pagenumber)

def lspages(act = None, root = os.curdir):
    """Lists the pages. If the act is specified, lists the pages in the act. Returns nothing."""
    if not args.act:
        for entry in PyHussie.list_all_pages(root):
            sys.stdout.write("|".join(entry) + "\n")
    for number in get_act_list(act, root):
        sys.stdout.write(number + "\n")

###############################################################
#LITTLE TWEAKS ZONE: small utilities that are nice to have
###############################################################

def translate_to_fieldnumber(field):
    """A utility function to provide the information about the field we need to read or write to from the command line to the actual function. Takes a field name and returns a number."""
    if field == "all":
        fieldnumber = -1
    elif field == "all-pretty":
        fieldnumber = -2
    elif field == "raw":
        fieldnumber = -3
    elif field == "time-pretty":
        fieldnumber = -4
    elif field == "caption":
        fieldnumber = 0
    elif field == "hash":
        fieldnumber = 1
    elif field == "time":
        fieldnumber = 2
    elif field == "images":
        fieldnumber = 3
    elif field == "text":
        fieldnumber = 4
    elif field == "link":
        fieldnumber = 5
    return fieldnumber #Wow. What a sheetload of fsck. But I had no time to think of something better.

def get_slice(pagenumber, root = os.curdir):
    """Gets a 'slice' of pagenumbers from specified page to the end of repository. Takes a page number, returns a list of page numbers after it."""
    fulllist = []
    for page in PyHussie.list_all_pages(root):
        fulllist.append(page[0])
    try:
        slicelist = fulllist[fulllist.index(pagenumber):]
    except ValueError:
        show_page_not_found(args.page)
    return slicelist

def get_act_list(act, root = os.curdir):
    """Gets a list of pagenumbers from specified act. Returns list of page numbers."""
    fullist = []
    for page in PyHussie.list_all_pages(root):
        fullist.append(page)
    actlist = []
    for page in fullist:
        if page[1] == act:
            actlist.append(page[0])
    return actlist

###############################################################
#DANGER ZONE: this thing writes to real files. Handle with care
###############################################################

def write(pagenumber, fieldnumber, content, root = os.curdir):
    """Writes into the page. Takes a pagenumber, number of the field (-3 is special: it means you want to overwrite the whole page) and the content you want to write. Returns nothing. Raw mode is mildly foolproof, it won't let you write anything that is not structured like MSPA page."""
    try:
        if fieldnumber == -3:
            if PyHussie.check_page_content(content):
                PyHussie.write_page(pagenumber, content, root = os.curdir)
                return
            else:
                show_not_a_page(pagenumber)
                return
        pagelist = PyHussie.get_parsed_trans_page(pagenumber, root)
        pagelist[fieldnumber] = content
        PyHussie.write_page(pagenumber, PyHussie.assemble_page(pagelist), root)
    except TypeError:
        show_page_not_found(pagenumber)

def bulk_remove(pagelist, root = os.curdir, imgdirname = "img"):
    """Removes pages in bulk. Takes the list of pages to delete. Returns nothing."""
    for page in pagelist:
            try:
                PyHussie.delete_page(page, root, imgdirname)
            except TypeError:
                show_page_not_found(page)

def get(pages, act, root = os.curdir, imgdirname = "img"):
    """Gets pages from MS paint Adventures website. Takes list of pagenumbers and the act to place the pages to. Does not let you to get the page if it already exists in the repository."""
    for page in pages:
        try:
            PyHussie.get_trans_page(page, root)
            show_page_exists(page, root)
        except TypeError:
            PyHussie.create_page(page, act, PyHussie.assemble_page(PyHussie.get_parsed_hussies_page(page)), root)
            images = PyHussie.get_hussies_images(page)
            for image in images:
                PyHussie.create_image(image, act, root, imgdirname)

def bulk_move(pagelist, act, root = os.curdir, imgdirname = "img", create = False):
    """Moves pages in bulk. Takes the list of pages to move and the name of the act to move to. Returns nothing."""
    if PyHussie.check_act(act, root, imgdirname) == False:
        if create == False:
            sys.stderr.write("htspagetool: 404: The " + act + " appears not to exist. Check, if it actually does, or if you are in Homestuck Translation Project repository.\n")
            return
    for page in pagelist:
        try:
            PyHussie.move_page(page, act, root, imgdirname)
        except TypeError:
            show_page_not_found(args.page)

def remove_act(act, root = os.curdir, imgdirname = "img", force = False):
    """Removes the act. Takes the name of act to remove. Does not work if act has pages in it, although can be forced to."""
    if force:
        bulk_remove(get_act_list(act), root, imgdirname)
    try:
        PyHussie.drop_act(act, root, imgdirname)
    except OSError as os.errno.ENOTEMPTY:
        show_act_not_empty(act)
    except OSError:
        show_act_not_found(act)

###############################################################
#ERROR MESSAGES ZONE: showing error messages
###############################################################

def show_page_not_found(page):
    """Shows a 'page not found' error message. Takes a page number."""
    sys.stderr.write("htspagetool: Make sure that the page " + page + " actually exists or if you are actually in a Homestuck Translation Project repository. \n")

def show_hussies_page_not_found(page):
    """Shows a 'page not found' error message regarding to MS Paint Adventures website. Takes a page number."""
    sys.stderr.write("htspagetool: remote 404: The page " + page + " does not exist on MS Paint Adventures Website\n")

def show_page_exists(page, root = os.curdir):
    """Shows a 'page already exists' error message, along with the act the page exists in. Takes a page number."""
    sys.stderr.write("htspagetool: The page " + page + " appears to exist in the repository under the " + PyHussie.path_to_act(os.path.dirname(PyHussie.locate_trans_page(page, root)), root) + ". We can't allow for collisions.\n")

def show_act_not_found(act):
    """Shows a 'act not found' error message. Takes an act name."""
    sys.stderr.write("htspagetool: The " + act + " appears not to exist. Check, if it actually does, or if you are in Homestuck Translation Project repository.\n")

def show_act_not_empty(act):
    """Shows a 'act is not empty' error message. Takes an act name."""  
    sys.stderr.write("htspagetool: The " + act + " appears not to be empty. Move the pages somewhere or delete them, or use --force argument.\n")

def show_not_a_page(page):
    """Shows a 'this is not a page' error message. Takes a page number."""
    sys.stderr.write("htspagetool: What you are trying to write to " + page + " does not resemble a MS Paint Adventures page.\n")

###############################################################
#COMMAND PARSER ZONE: yeah, this one is huge
###############################################################

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(prog = 'hstpagetool', description = 'HSTPageTool: A tool for handling Homestuck Translation Project repository. Allows for reading, writing, deleteng and moving pages between acts, as well as creating and deleting the acts themselves. Can also get pages from MS Paint Adventures website. In order for it to work, you must be in the root directory of the repository.', epilog = 'COPYRIGHT NOTICE: MS Paint Adventures website and Homestuck belong to Andrew Hussie and MS Paint Adventures team. The author of this program makes absolutely no profit from it, and distributes it freely. Anyone can grab it and do pretty much what they desire with it, within pretty broad limits of the GPL license. Made with love by dr. Equivalent the Incredible II and the Homestuck (Russian) Translation Project.')
    subparsers = parser.add_subparsers(title = "Commands", dest= 'command')
    parser_rm = subparsers.add_parser('rm', help="remove the page")
    parser_trim = subparsers.add_parser('trim', help="remove all pages starting with specified number")
    parser_slice = subparsers.add_parser('slice', help="move the pages starting with number to a new act")
    parser_mv = subparsers.add_parser('mv', help="move the specified pages to specified act")
    parser_get = subparsers.add_parser('get', help="get the page from MS Paint Adventures website to the specified act")
    parser_read = subparsers.add_parser('read', help="read the content of the specified field of the page")
    parser_write = subparsers.add_parser('write', help="write the content of the specified field to the specified page")
    parser_where = subparsers.add_parser('where', help="get an absolute path to the specified page")
    parser_act = subparsers.add_parser('act', help="get an act of the specified page")
    parser_mkact = subparsers.add_parser('mkact', help="make a new act")
    parser_rmact = subparsers.add_parser('rmact', help="remove an act")
    parser_ls = subparsers.add_parser('ls', help="list the whole repository or the specified act")
    parser_rm.add_argument("page", nargs = "+", help = "full 6-digit number or numbers of page or pages to remove")
    
    parser_trim.add_argument("page", help = "full 6-digit number of page you want to trim to")
    
    parser_slice.add_argument("page", help = "full 6-digit number of page you want to slice from")
    parser_slice.add_argument("act", help = "name of act you want to slice to")

    parser_mv.add_argument("page", nargs = "+", help = "full 6-digit number of page you want to slice from")
    parser_mv.add_argument("act", help = "name of act you want to slice to")
    
    parser_get.add_argument("page", nargs = "+", help = "full 6-digit number of page you want to get")
    parser_get.add_argument("act", help = "name of act you want to place the page to")
    
    parser_read.add_argument("field", choices = ["caption", "hash", "time", "time-pretty", "images", "text", "link", "all", "all-pretty", "raw"], help = "a field to read from. If you choose 'raw', it will give you just a raw file content")
    parser_read.add_argument("page", nargs = "+", help = "full 6-digit number or numbers of page or pages to read")
    
    parser_write.add_argument("field", choices = ["caption", "hash", "time", "images", "text", "link", "raw"], help = "a field to write to. Choose 'raw' to write the whole file content.")
    parser_write.add_argument("page", help = "full 6-digit number of page to write to")
    parser_write.add_argument("content", nargs = "?", help = "the string to write. If you going to input to stdin, leave this argument blank. If contains whitespaces, should be given in quotes")
    
    parser_where.add_argument("page", nargs = "+", help = "full 6-digit number or numbers of page or pages to find")
    
    parser_act.add_argument("page", nargs = "+", help = "full 6-digit number or numbers of page or pages to find")
    
    parser_mkact.add_argument("act", help = "name of the act you want to create")
    
    parser_rmact.add_argument("act", help = "name of the act you want to remove")
    parser_rmact.add_argument("--force", "-f", action = "store_true", help = "remove the act, no matter how full or empty it is")
    
    parser_ls.add_argument("act", nargs = "?", help = "name of the act you want to list. If none, lists the whole repository")
    
    args = parser.parse_args()
    
###############################################################
#COMMAND EXECUTION ZONE: trying to make sense of the mess above
###############################################################
    
    if args.command == "rm":
        bulk_remove(args.page, root = os.curdir, imgdirname = "img")
    
    elif args.command == "trim":
        trimlist = get_slice(args.page)
        bulk_remove(trimlist, root = os.curdir, imgdirname = "img")
    
    elif args.command == "mv":
        bulk_move(args.page, args.act, root = os.curdir, imgdirname = "img")
    
    elif args.command == "slice":
        bulk_move(get_slice(args.page, root = os.curdir), args.act, root = os.curdir, imgdirname = "img", create = True)
    
    elif args.command == "get":
        get(args.page, args.act, root = os.curdir)
    
    elif args.command == "read":
        for element in args.page:
            read_page(element, translate_to_fieldnumber(args.field), root = os.curdir)
    
    elif args.command == "write":
        if args.content == None:
            content = sys.stdin.read().rstrip() #We want to get rid of newline at the end of the stdin
        else:
            content = args.content
        write(args.page, translate_to_fieldnumber(args.field), content, root = os.curdir)

    elif args.command == "where":
        for page in args.page:
            sys.stdout.write(PyHussie.locate_trans_page(page, root = os.curdir) + "\n")

    elif args.command == "act":
        for page in args.page:
            sys.stdout.write(page + "|" + PyHussie.path_to_act(os.path.dirname(PyHussie.locate_trans_page(page, root = os.curdir)), root = os.curdir) + "\n") #Damn...

    elif args.command == "mkact":
        PyHussie.create_act(args.act, root = os.curdir, imgdirname = "img")
    
    elif args.command == "rmact":
        remove_act(args.act, force = args.force)
    
    elif args.command == "ls":
        lspages(act = args.act, root = os.curdir)
